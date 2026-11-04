#!/usr/bin/env python3
"""v2793 official CLIO exact product generation and photo source QA for pending05/06/07.

Strict safeguards:
- Official CLUBCLIO category pages only, at most 4 product IDs / 6 file candidates each.
- Product page must match text; never label a bundle or 15g main item as the
  user's single mini 5g product.
- Archived photos stay in QA with rights, edition and shade review HOLD.
- Output changes no old/approved JPG, URL or spreadsheet.
"""
from pathlib import Path
from urllib.parse import urlparse,urljoin
from io import BytesIO
from PIL import Image,ImageOps,ImageDraw,ImageFont
from bs4 import BeautifulSoup
import requests,json,re,hashlib,base64
OUT=Path('qa-review/v2793-three-clio-remaining-families-exact-page-edition-and-photo-proof')
assert not OUT.exists();OUT.mkdir(parents=True)
CASES=[
 {'family':'pending-05','label':'CLIO Kill Cover Founwear Cushion Mini 5g',
  'candidates':[5750,7108], 'must_include_any':['미니','mini'],
  'hold':'Physical user-owned mini edition The New vs The Original or Sanrio unverified; 5g never replace with full-size 15g'},
 {'family':'pending-06','label':'CLIO Kill Cover Mesh Glow Essential Cushion single compact',
  'candidates':[6182], 'must_include_any':['메쉬 글로우 에센셜'],
  'hold':'Current 6182 official page is a promotional set with main 15g + refill and maybe extra gift; not proof of standalone SKU'},
 {'family':'pending-07','label':'CLIO Kill Cover Mesh Blur Cushion single compact',
  'candidates':[6455], 'must_include_any':['메쉬 블러'],
  'hold':'Current 6455 official listing is set main + refill; not proof that user sells whole set'}
]
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
def sha(buf):return hashlib.sha256(buf).hexdigest()
def image_url(pid,name):
 s=f'{pid:04d}';return f'https://clubclio.co.kr/data/mall_data/images/product/00/00/00/{s[:2]}/{s[2:]}/{name}'
headers={'User-Agent':'Mozilla/5.0 (compatible; GenuinePhotoQA/1.0)','Accept-Language':'ko-KR,ko;q=0.9'}
records=[]
for case in CASES:
 record={k:v for k,v in case.items()}
 record.update({'official_pages':[],'source_photo_candidates':[],'status':'HOLD_EDITION_OR_SOURCE','retail_approved':False})
 familydir=OUT/case['family'];familydir.mkdir()
 for pid in case['candidates']:
  url=f'https://clubclio.co.kr/shop/goodsView/{pid}'
  doc={'product_id':pid,'url':url,'matched_exact_page':False,'photos_downloaded':0}
  try:
   response=requests.get(url,headers=headers,timeout=15)
   doc['http_status']=response.status_code
   response.raise_for_status()
   soup=BeautifulSoup(response.text,'html.parser')
   text=' '.join(soup.get_text(' ',strip=True).split())
   page_title=soup.title.get_text(' ',strip=True) if soup.title else ''
   doc['title']=page_title[:240]
   wanted=any(x.lower() in text.lower() for x in case['must_include_any'])
   if case['family']=='pending-05':
    wanted=wanted and ('파운웨어' in text or 'founwear' in text.lower()) and ('쿠션' in text or 'cushion' in text.lower())
   if not wanted:
    doc['reason']='Official page does not independently confirm exact user target; skip media';record['official_pages'].append(doc);continue
   # Product-specific section header helps establish exact listing, not a
   # random site's footer suggestions.
   product_headings=[t.get_text(' ',strip=True) for t in soup.select('h1,h2,h3,.goods_name,.goodsName')][:20]
   doc['matching_headings']=product_headings
   doc['has_main_refill_set_words']=bool(re.search(r'기획\s*\[본품\+리필\]|기획세트\s*\[본품\+리필\]',text))
   doc['says_5g_near_visible_text']='5g' in text.lower()
   # Current 6182/6455 are sets; avoid marking reference photo as
   # customer-ready individual cushion.
   doc['matched_exact_page']=True
   seen={}
   for name in ('m.gif','b.gif','l.gif','o.gif','m.jpg','b.jpg'):
    u=image_url(pid,name)
    try:
     rr=requests.get(u,headers={'User-Agent':'Mozilla/5.0','Referer':url},timeout=11)
     if rr.status_code!=200 or len(rr.content)>8000000:continue
     p=Image.open(BytesIO(rr.content));p.load()
     if min(p.size)<450:continue
     digest=sha(rr.content)
     if digest in seen:continue
     seen[digest]=1
     rgb=ImageOps.exif_transpose(p).convert('RGB')
     photo=ImageOps.contain(rgb,(1080,1080),Image.Resampling.LANCZOS)
     board=Image.new('RGB',(1080,1080),'white')
     board.paste(photo,((1080-photo.width)//2,(1080-photo.height)//2))
     path=familydir/f"{len(record['source_photo_candidates'])+1:02d}-official-{pid}-{name.replace('.','-')}-REFERENCE.jpg"
     board.save(path,'JPEG',quality=91,optimize=True,subsampling=0)
     if path.stat().st_size>=2000000:path.unlink();continue
     rec={'product_id':pid,'source_url':u,'source_hash':digest,
       'native_dimensions':list(p.size),'file':str(path.relative_to(OUT)),
       'jpg_hash':sha(path.read_bytes()),
       'commercial_rights_verified':False,
       'physical_stock_photo_edition_verified':False,
       'single_cushion_vs_set_verified':False,
       'retail_approved':False}
     record['source_photo_candidates'].append(rec)
     doc['photos_downloaded']+=1
     if doc['photos_downloaded']>=3:break
    except (requests.RequestException,OSError,ValueError):continue
  except Exception as exc:
   doc['error_type']=type(exc).__name__;doc['error']=str(exc)[:180]
  record['official_pages'].append(doc)
 if record['source_photo_candidates']:
  record['status']='OFFICIAL_PHOTO_REFERENCES_SAVED_HOLD_EDITION'
 else:
  record['status']='NO_EXACT_ITEM_OFFICIAL_PHOTO_RETRIEVED'
 if case['family'] in ('pending-06','pending-07'):
  record['release_blocker']='OFFICIAL_CURRENT_LISTING_BUNDLE_MAIN_PLUS_REFILL_NOT_SINGLE_STOCK'
 if case['family']=='pending-05':
  record['release_blocker']='MINI_CASE_EDITION_5G_NOT_YET_MATCHED_TO_USER_STOCK'
 records.append(record)
# Independent per-product contact sheets. No generic product imagery.
for x in records:
 imgs=x['source_photo_candidates']
 if not imgs:continue
 cols=4;rows=(len(imgs)+3)//4
 board=Image.new('RGB',(1500,78+375*rows),'#f0f0ed')
 draw=ImageDraw.Draw(board)
 draw.text((16,15),f"v2793 {x['family']} CLIO OFFICIAL PAGE PHOTO REFERENCES / HOLD COMMERCE",font=FONT,fill='#272727')
 for n,record in enumerate(imgs):
  with Image.open(OUT/record['file']) as im:
   thumb=im.convert('RGB').resize((305,305),Image.Resampling.LANCZOS)
  px=15+(n%4)*368;py=61+(n//4)*375
  board.paste(thumb,(px,py))
  draw.text((px,py+310),f"OFFICIAL ID {record['product_id']} {record['native_dimensions'][0]}px",font=FONT,fill='#303030')
 contact=OUT/f"v2793-{x['family']}-official-photo-reference.jpg"
 board.save(contact,'JPEG',quality=83,optimize=True)
 (OUT/f"v2793-{x['family']}-proof.b64.txt").write_text(base64.b64encode(contact.read_bytes()).decode())
report={'version':'v2793','baseline':'v2792',
 'target_new_families':3,'product_pages_probed':sum(len(x['official_pages']) for x in records),
 'new_deduplicated_official_reference_JPGs_saved':sum(len(x['source_photo_candidates']) for x in records),
 'photo_rights_proven':False,'exact_physical_stock_edition_proven':False,
 'new_retail_approvals':0,
 'existing_11_approved_groups_untouched':True,
 'existing_55_public_image_urls_untouched':True,
 'all_previous_original_QA_JPGs_untouched':True,
 'no_final_spreadsheet_shared':True,
 'products':records}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'version':'v2793','new_item_families':3,
 'official_exact_item_image_candidates':report['new_deduplicated_official_reference_JPGs_saved'],
 'statuses':[(x['family'],x['status']) for x in records],'new_retail_approvals':0}))
