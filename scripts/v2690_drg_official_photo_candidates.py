#!/usr/bin/env python3
"""v2690: Select authentic distinct product photo assets from two Dr.G official
product pages, replacing unverified legacy MK-badged scenes in isolated QA only.
Strict same-product page and 50mL identity, never publish without rights and SKU proof.
"""
import json,hashlib,base64,re
from pathlib import Path
from io import BytesIO
from urllib.parse import urljoin,urlparse
from PIL import Image,ImageOps,ImageDraw,ImageFont
from bs4 import BeautifulSoup
import requests
OUT=Path('qa-review/v2690-drg-two-official-photo-source-led-QA')
assert not OUT.exists()
OUT.mkdir(parents=True)
SPECS=[
 {'family':'pending-15','page':'https://www.dr-g.com/our-products/green-mild-up-sun',
  'title_words':['green','mild','up','sun'],'product':'DR.G Green Mild Up Sun Plus 50mL'},
 {'family':'pending-18','page':'https://www.dr-g.com/our-products/brightening-up-sun',
  'title_words':['brightening','up','sun'],'product':'DR.G Brightening Up Sun Plus 50mL'},
]
HEADERS={'User-Agent':'Mozilla/5.0','Accept':'text/html,application/xhtml+xml,image/avif,image/png,image/jpeg,*/*'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dhash(im):
 pix=list(ImageOps.grayscale(im.resize((9,8),Image.Resampling.LANCZOS)).getdata())
 return sum(1<<(y*8+x) for y in range(8) for x in range(8) if pix[y*9+x]>pix[y*9+x+1])
def allowed(url):
 host=(urlparse(url).hostname or '').lower()
 return host in ('www.dr-g.com','dr-g.com') or host.endswith('.dr-g.com') or host.endswith('.wp.com') or host.endswith('.cloudfront.net')
def source_urls(soup,page):
 urls=[]
 for tag in soup.select('meta[property="og:image"],meta[name="twitter:image"]'):
  u=tag.get('content')
  if u:urls.append(urljoin(page,u))
 for image in soup.find_all('img'):
  props=' '.join([str(image.get('alt') or ''),str(image.get('class') or ''),str(image.get('src') or '')]).lower()
  if any(s in props for s in ['product','green mild','brightening','gallery','wp-image','sun+','sun cream']):
   for key in ('src','data-src','data-lazy-src','data-original'):
    url=image.get(key)
    if url:urls.append(urljoin(page,url))
   srcset=image.get('srcset') or ''
   for u in re.findall(r'(https?://[^\s,]+)',srcset):
    urls.append(u)
 seen=set();return [u for u in urls if u.startswith('http') and allowed(u) and not (u in seen or seen.add(u))][:40]
rows=[]
for item in SPECS:
 rec={'family':item['family'],'product':item['product'],'page':item['page'],
      'status':'HOLD_NO_VERIFIED_DISTINCT_OFFICIAL_PHOTO','selected_photos':[],
      'retail_release':False}
 try:
  page=requests.get(item['page'],headers=HEADERS,timeout=18)
  page.raise_for_status()
  soup=BeautifulSoup(page.text,'html.parser')
  title=soup.title.get_text(' ',strip=True) if soup.title else ''
  description=' '.join(x.get_text(' ',strip=True) for x in soup.select('h1,h2')[:8])
  assert all(w in (title+' '+description).lower() for w in item['title_words']),('unmatched product',title)
  assert '50ml' in (title+' '+description).replace(' ','').lower(),('unverified 50 mL',title)
  urls=source_urls(soup,item['page'])
  rec['page_title']=title;rec['urls_considered']=urls[:20]
  chosen=[];hashes=[]
  for url in urls:
   try:
    res=requests.get(url,headers=HEADERS,timeout=12)
    res.raise_for_status()
    if len(res.content)>8000000:continue
    data=Image.open(BytesIO(res.content));data.load()
    if min(data.size)<440:continue
    img=ImageOps.exif_transpose(data).convert('RGB')
    sig=dhash(img)
    if hashes and min((sig^x).bit_count() for x in hashes)<13:continue
    # Only two candidate photos to prevent unrelated gallery items slipping in
    chosen.append((img,url,list(data.size),sig))
    hashes.append(sig)
    if len(chosen)==2:break
   except (OSError,ValueError,requests.RequestException):
    continue
  if not chosen:
   rec['status']='HOLD_NO_DECODED_OFFICIAL_IMAGE'
  else:
   famdir=OUT/item['family'];famdir.mkdir()
   for ix,(im,url,dim,sig) in enumerate(chosen,1):
    image=Image.new('RGB',(1080,1080),'white')
    contained=ImageOps.contain(im,(1040,1040),Image.Resampling.LANCZOS)
    image.paste(contained,((1080-contained.width)//2,(1080-contained.height)//2))
    path=famdir/f'{ix:02d}-DRG-official-no-crop-QA-only.jpg'
    image.save(path,'JPEG',quality=92,optimize=True,subsampling=0)
    assert path.stat().st_size<2000000
    rec['selected_photos'].append({'slot':ix,'url':url,'sha256':sha(path),
          'source_px':dim,'file':path.name})
   rec['status']='OFFICIAL_PHOTO_CANDIDATES_STAGED_VISUAL_REVIEW_REQUIRED'
 except Exception as e:
  rec['status']='HOLD_PAGE_ACCESS_OR_IDENTITY'
  rec['error_type']=type(e).__name__
  rec['error_detail']=str(e)[:180]
 rows.append(rec)
count=sum(len(r['selected_photos']) for r in rows)
if count:
 board=Image.new('RGB',(1300,600*len(rows)+65),'#f5f4f2')
 d=ImageDraw.Draw(board)
 f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',24)
 d.text((20,17),'v2690 DR.G OFFICIAL PHOTO CANDIDATES | NOT RETAIL APPROVED',font=f,fill='#222222')
 for i,r in enumerate(rows):
  for j,p in enumerate(r['selected_photos']):
   with Image.open(OUT/r['family']/p['file']) as im:
    thumb=im.convert('RGB').resize((510,510),Image.Resampling.LANCZOS)
   x=30+j*570;y=70+i*600
   board.paste(thumb,(x,y))
   d.text((x,y+518),r['family']+' / '+str(j+1),font=f,fill='#222222')
 proof=OUT/'v2690-official-photo-contact.jpg'
 board.save(proof,'JPEG',quality=80,optimize=True)
 (OUT/'v2690-contact.b64.txt').write_text(base64.b64encode(proof.read_bytes()).decode())
report={'version':'v2690','base':'v2689','families':rows,'official_source_candidate_jpgs':count,
'licensed_commercial_photos_verified':False,'owned_real_stock_edition_verified':False,
'prior_QA_JPGs_overwritten':0,'approved_11_groups_untouched':True,
'public_55_URLs_untouched':True,'final_xlsx_not_shared':True}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'families_processed':len(rows),'official_photos':count,
'status':[r['status'] for r in rows],'new_retail_approved':0}))
