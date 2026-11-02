#!/usr/bin/env python3
"""v2.4.11: preserve 80 JPG exactly, audit visual similarity, acquire linked true photo bytes.
Frames generated only from distinct source photos on matching actual product pages.
All new files are unapproved pre-QA candidates, never publish to public/images.
"""
import csv,hashlib,io,json,re,shutil,sys,time
from pathlib import Path
from urllib.parse import urljoin,urlparse
from collections import defaultdict
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageOps, ImageFont, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'production-v2411';OUT.mkdir(exist_ok=True)
CACHE=ROOT/'input-v2410-cache'
QUEUE=json.loads((ROOT/'evidence/pending-30-v247.json').read_text(encoding='utf8'))
SOURCE_PAGES={
 'pending-12':[
  ('https://m.ableshop.kr/product/goods/view-goods?goodsId=BO00114236','미샤 PDRN 리뉴 필 샷 25 15ml'),
  ('https://www.misshajp.com/shop/g/gMS104057/','MISSHA PDRN NAD+ shot 15ml'),
 ],
 'pending-13':[
  ('https://m.ableshop.kr/product/goods/view-goods?goodsId=BO00114237','미샤 PDRN 퍼밍 리페어 세럼 30ml'),
 ],
 'pending-14':[
  ('https://m.ableshop.kr/product/goods/view-goods?goodsId=BO00114238','미샤 PDRN 퍼밍 리페어 크림 70ml'),
 ],
 'pending-17':[
  ('https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000180138','닥터지 브라이트닝 업 모이스처 선 50ml'),
  ('https://shinsegaemall.ssg.com/item/itemView.ssg?itemId=1000692141706','닥터지 브라이트닝 업 모이스처 선 50ml'),
 ],
 'pending-20':[
  ('https://shinsegaemall.ssg.com/item/itemView.ssg?itemId=1000706462566','구달 청귤 비타C 세럼 미스트 100ml 25AD'),
  ('https://www.hwahae.co.kr/goods/구달-청귤-비타C-세럼-미스트-25AD-100ml/74872','구달 청귤 비타C 세럼 미스트 25AD'),
 ],
 'pending-21':[
  ('https://www.oliveyoung.co.kr/store/search/getSearchMain.do?query=구달%20청귤%20비타C%20잡티케어%20아이크림','구달 청귤 비타C 아이크림 25AD'),
 ],
}
HOLD={'pending-26':'145ml versus 150ml packaging conflict; no auto-image production'}
# Exact SHA-256 prefixes manually screened against product imagery; reject adverts,
# unrelated vegan packaging, bundled products, diagrams and model-led frames.
CURATED={
 'pending-12':{'aeee02ac48ee','4166c45da556','f9e33b456bc5'},
 'pending-13':{'4d228780ef6c','ac47ea3f8fde'},
 'pending-14':{'9d197a03300b','5c660ccf24ce','7f391f26af48'},
}

SESSION=requests.Session()
SESSION.headers.update({'User-Agent':'Mozilla/5.0 (compatible; ProductEvidenceAudit/1.0)','Accept-Language':'ko-KR,ko;q=0.9,en;q=0.8'})
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def sha(p):return sha_bytes(p.read_bytes())
def readimg(p):
 with Image.open(p) as im:
  im.load()
  return ImageOps.exif_transpose(im).convert('RGB')
def dhash(im):
 a=list(ImageOps.grayscale(im).resize((9,8)).getdata())
 return sum(1<<i for i in range(64) if a[(i//8)*9+(i%8)]>a[(i//8)*9+(i%8)+1])
def ahash(im):
 a=list(ImageOps.grayscale(im).resize((8,8)).getdata()); mean=sum(a)/64
 return sum(1<<i for i in range(64) if a[i]>=mean)
def dist(a,b):return (a^b).bit_count()
def font(size):
 try:return ImageFont.truetype(FONT,size)
 except:return ImageFont.load_default()
def legal_url(u,base=None):
 if base:u=urljoin(base,u)
 p=urlparse(u)
 return u if p.scheme=='https' and p.hostname and not p.username and not p.password else None
def fetch_url(url,maxbytes=12_000_000):
 u=legal_url(url)
 if not u:raise ValueError('UNSAFE_URL')
 with SESSION.get(u,timeout=(7,14),stream=True,allow_redirects=True) as r:
  r.raise_for_status()
  if not legal_url(r.url):raise ValueError('BAD_REDIRECT')
  buf=io.BytesIO()
  for part in r.iter_content(65536):
   buf.write(part)
   if buf.tell()>maxbytes:raise ValueError('EXCESSIVE_BYTES')
  return buf.getvalue(),r.headers.get('Content-Type',''),r.url
def potential_images(html,page):
 soup=BeautifulSoup(html,'html.parser')
 items=[]
 # Only images on the exact linked product page, not links to different products.
 for tag in soup.find_all('meta'):
  if tag.get('property') in ('og:image','og:image:secure_url','twitter:image'):
   items.append((tag.get('content',''),'meta'))
 for tag in soup.select('img'):
  src=tag.get('data-src') or tag.get('data-original') or tag.get('src') or ''
  alt=tag.get('alt','')
  if any(k in (src+' '+alt).lower() for k in ('logo','banner','event','member','tracking','icon','coupon')):continue
  items.append((src,'gallery'))
 # Avoid blindly harvesting arbitrary CSS/CDN links and unscoped related product pictures.
 result=[];seen=set()
 for src,kind in items:
  u=legal_url(src,page)
  if u and u not in seen:
   result.append((u,kind));seen.add(u)
 return result[:16]
def capture_framed_photo(source,name,dest):
 pic=readimg(source).convert('RGBA')
 canvas=Image.new('RGB',(1080,1080),(248,238,230))
 d=ImageDraw.Draw(canvas)
 d.rounded_rectangle((36,36,1044,1044),radius=30,outline=(218,218,205),width=2)
 pic.thumbnail((920,815),Image.Resampling.LANCZOS)
 x=(1080-pic.width)//2;y=(830-pic.height)//2+15
 # Opaque photo matte retained. No fake transparency or generic replicated swatches.
 canvas.paste(pic,(x,y),pic)
 f=font(31);start=870;buf=''
 for c in name:
  if d.textbbox((0,0),buf+c,font=f)[2]>930 and buf:
   d.text((65,start),buf,font=f,fill=(43,65,56));start+=46;buf=c
  else:buf+=c
 if buf:d.text((65,start),buf,font=f,fill=(43,65,56))
 canvas.save(dest,'JPEG',quality=88,optimize=True)
 with Image.open(dest) as im:assert im.format=='JPEG' and im.size==(1080,1080)
 assert dest.stat().st_size<2_000_000
def copyold(src,dest):
 with Image.open(src) as im:
  if im.format!='JPEG' or im.size!=(1080,1080) or src.stat().st_size>=2_000_000:return False
 shutil.copy2(src,dest);return True

rows=[];manifest=[];source_log=[];dupes=[];new=0;reused=0;new_fam=0
for item in QUEUE:
 fid=item['id'];name=item['name'];folder=OUT/fid;folder.mkdir(exist_ok=True)
 previous=CACHE/fid
 if previous.exists():
  for p in sorted(previous.glob('*.jpg')):
   if copyold(p,folder/p.name):reused+=1
 prior=list(folder.glob('*.jpg'))
 visual=[]
 for p in prior:
  try:im=readimg(p);visual.append((p,dhash(im),ahash(im)))
  except Exception as e:source_log.append({'family':fid,'source':p.name,'result':'BAD_OLD_JPG','reason':str(e)[:160]})
 for i in range(len(visual)):
  for j in range(i+1,len(visual)):
   a,b=visual[i],visual[j]
   if (dist(a[1],b[1])<=5 and dist(a[2],b[2])<=6):
    dupes.append({'family':fid,'first':a[0].name,'second':b[0].name,'dhash_distance':dist(a[1],b[1]),'ahash_distance':dist(a[2],b[2]),'status':'VISUAL_NEAR_DUPLICATE_REVIEW'})
 source_folder=OUT/'source-evidence'/fid
 added_here=0
 if fid in HOLD:
  source_log.append({'family':fid,'source':'','result':'HOLD','reason':HOLD[fid]})
 elif fid in SOURCE_PAGES:
  source_folder.mkdir(parents=True,exist_ok=True)
  # Actual product pages, in preferred official/known seller order.
  unique_sources=[]
  for page,hint in SOURCE_PAGES[fid]:
   try:
    html,content_type,landed=fetch_url(page,3_500_000)
    if not ('html' in content_type or b'<html' in html[:1000].lower()):
     raise ValueError('NOT_HTML_PRODUCT_PAGE')
    text=BeautifulSoup(html,'html.parser').get_text(' ',strip=True)
    # Search/query page is evidence only, not a product page.
    if '/search/' in urlparse(landed).path:
     source_log.append({'family':fid,'source':page,'result':'SEARCH_PAGE_ONLY','reason':'not direct product evidence'})
     continue
    for src,kind in potential_images(html.decode('utf-8','replace'),landed):
     try:
      raw,mime,final=fetch_url(src)
      with Image.open(io.BytesIO(raw)) as test:
       test.load()
       if test.format not in ('JPEG','PNG','WEBP'):raise ValueError('UNSUPPORTED_FORMAT')
       w,h=test.size
       if min(w,h)<320 or max(w/h,h/w)>2.4:raise ValueError('NOT_PRODUCT_FRAME_DIMENSIONS')
       pic=ImageOps.exif_transpose(test).convert('RGB')
       ph=dhash(pic);ah=ahash(pic)
      if any(dist(ph,p0)<=6 and dist(ah,p1)<=8 for p0,p1 in unique_sources):
       source_log.append({'family':fid,'source':final,'result':'NEAR_DUPLICATE_SOURCE','reason':'visual hash'})
       continue
      sourcehash=sha_bytes(raw)
      if fid in CURATED and sourcehash[:12] not in CURATED[fid]:
       source_log.append({'family':fid,'source':final,'result':'VISUAL_TRIAGE_REJECT','reason':'not exact standalone product imagery'})
       continue
      ext={'JPEG':'.jpg','PNG':'.png','WEBP':'.webp'}[test.format]
      spath=source_folder/(sourcehash[:20]+ext)
      if not spath.exists():spath.write_bytes(raw)
      unique_sources.append((ph,ah))
      source_log.append({'family':fid,'source':final,'result':'SOURCE_BYTES_CAPTURED','reason':'page='+page+';source_sha256='+sourcehash})
      if len(list(folder.glob('*.jpg')))<5:
       output=folder/('SOURCE_%s.jpg'%sourcehash[:12])
       if not output.exists():
        capture_framed_photo(spath,name,output)
        new+=1;added_here+=1
      if len(unique_sources)>=5:break
     except Exception as exc:
      source_log.append({'family':fid,'source':src,'result':'IMAGE_FAILED','reason':str(exc)[:140]})
    if len(unique_sources)>=5:break
   except Exception as exc:
    source_log.append({'family':fid,'source':page,'result':'PAGE_FAILED','reason':str(exc)[:150]})
 if added_here and not prior:new_fam+=1
 files=sorted(folder.glob('*.jpg'))
 if len(files)==0:
  folder.rmdir()
  state='SOURCE_MISMATCH_HOLD' if fid in HOLD else 'SOURCE_PENDING'
 elif len(files)>=5:
  # Five photos do not prove five distinct information roles. Explicitly no release.
  state='FIVE_FRAMES_REQUIRE_INFORMATION_AND_PRODUCT_QA'
 else:state='PARTIAL_FRAMES_FINAL_QA_PENDING'
 for p in files:
  manifest.append({'family':fid,'file':p.name,'sha256':sha(p),'bytes':p.stat().st_size,'existing':p in prior,'technical_valid':True})
 rows.append({'id':fid,'name':name,'jpg':len(files),'new_jpg':added_here,'status':state,'visual_duplicate_pairs':sum(d['family']==fid for d in dupes),'official_swatch_verified':False,'release_complete':False})
 print('FAMILY',fid,'files',len(files),'new',added_here,'status',state,flush=True)
def writecsv(path,lines,headers):
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=headers);w.writeheader();w.writerows(lines)
writecsv(OUT/'family_checkpoint.csv',rows,['id','name','jpg','new_jpg','status','visual_duplicate_pairs','official_swatch_verified','release_complete'])
writecsv(OUT/'frame_sha256_manifest.csv',manifest,['family','file','sha256','bytes','existing','technical_valid'])
writecsv(OUT/'source_capture_results.csv',source_log,['family','source','result','reason'])
writecsv(OUT/'visual_duplicate_pairs.csv',dupes,['family','first','second','dhash_distance','ahash_distance','status'])
summary={'version':'2.4.11','queue':30,'reused_jpg':reused,'new_jpg':new,'unique_sha256_in_artifact':len({f['sha256'] for f in manifest}),'newly_started_families':new_fam,'with_any_jpg':sum(r['jpg']>0 for r in rows),'five_frames_physical':sum(r['jpg']>=5 for r in rows),'production_complete_qa_pending':0,'source_pending':sum(r['jpg']==0 for r in rows),'visual_duplicate_pairs':len(dupes),'source_bytes_captured':sum(x['result']=='SOURCE_BYTES_CAPTURED' for x in source_log),'qa_approved':0,'new_public_urls':0,'existing_public_urls':55,'notes':'No fabricated claims, swatches, logo or packaging. 5 JPG files alone never count as PRODUCTION_COMPLETE_QA_PENDING.'}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
