from pathlib import Path
from io import BytesIO
from zipfile import ZipFile
from hashlib import sha256
from urllib.parse import urlparse
import requests,json,time
from PIL import Image,ImageOps
Q=Path('qa-review'); B=Q/'v2938-pixelpure-three-official-detail-product-scene-recovery-QA'; OLD=Q/'v2920-six-incomplete-stock-groups-real-original-photo-bytes-internal-ZIP'; O=Q/'v2939-goodal-100ml-live-citrus-source-QA'
assert not O.exists()
st=json.loads((B/'stock30-incremental-state-v2938.json').read_text())
old=json.loads((OLD/'manifest.json').read_text())
assert st['version']=='v2938' and len(st['families'])==30
rec=next(x for x in old['results'] if x['family']=='pending-20')
zpath=Path(rec['zip_path']);assert sha256(zpath.read_bytes()).hexdigest()==rec['zip_sha256']
def imread(b):
 with Image.open(BytesIO(b)) as im:
  im.load();return ImageOps.exif_transpose(im).convert('RGB'),im.format,im.size
def dhash(im):
 p=ImageOps.grayscale(ImageOps.fit(im,(9,8))).load()
 return ''.join('1' if p[x,y]>p[x+1,y] else '0' for y in range(8) for x in range(8))
def distance(a,b):return sum(x!=y for x,y in zip(a,b))
prior=[];ph=[];sha=set()
with ZipFile(zpath) as z:
 assert len(z.namelist())==3 and z.testzip() is None
 for name in z.namelist():
  b=z.read(name);prior.append(b);sha.add(sha256(b).hexdigest());ph.append(dhash(imread(b)[0]))
page='https://oceanbuy.ca/products/goodal-green-tangerine-vita-c-serum-mist-100ml'
urls=[
 ('CITRUS_STILL','https://oceanbuy.ca/cdn/shop/files/goodalgoodal-green-tangerine-vita-c-serum-mist-100mloceanbuy-beauty-7721846.png?v=1777655591&width=1080'),
 ('CITRUS_WATER','https://oceanbuy.ca/cdn/shop/files/goodalgoodal-green-tangerine-vita-c-serum-mist-100mloceanbuy-beauty-8195066.png?v=1777655591&width=1080')]
sess=requests.Session();sess.headers['User-Agent']='Mozilla/5.0 (image source QA)'
errors=[];verified=False
try:
 r=sess.get(page,timeout=15);r.raise_for_status()
 from bs4 import BeautifulSoup
 t=BeautifulSoup(r.text,'html.parser').title.get_text(' ',strip=True).lower().replace('-',' ')
 name=''.join(t.split());verified=all(a in name for a in ['goodal','serummist','100ml'])
except Exception as e:errors.append('listing: '+str(e)[:140])
O.mkdir(parents=True);found=[]
if verified:
 for label,url in urls:
  try:
   assert urlparse(url).hostname=='oceanbuy.ca'
   r=sess.get(url,timeout=15);r.raise_for_status()
   assert urlparse(r.url).hostname in ('oceanbuy.ca','cdn.shopify.com')
   b=r.content;assert 5000<len(b)<9000000
   rgb,fmt,dims=imread(b);assert fmt in ('JPEG','PNG','WEBP')
   assert min(dims)>=600
   h=dhash(rgb);rawsha=sha256(b).hexdigest()
   dist=min([distance(h,a) for a in ph+[x['_hash'] for x in found]],default=64)
   if rawsha in sha or dist<5:errors.append(label+': near-duplicate');continue
   i=len(found)+1;folder=O/'pending-20';folder.mkdir(exist_ok=True)
   raw=folder/f'{i:02d}-{label}-original.{fmt.lower()}';raw.write_bytes(b)
   ref=folder/f'{i:02d}-{label}-internal-1080.jpg'
   canvas=Image.new('RGB',(1080,1080),'white')
   part=ImageOps.contain(rgb,(1080,1080),Image.Resampling.LANCZOS);canvas.paste(part,((1080-part.width)//2,(1080-part.height)//2))
   canvas.save(ref,'JPEG',quality=90,optimize=True)
   assert ref.stat().st_size<2000000
   found.append({'scene':label,'native_px':list(dims),'native_at_least_900':min(dims)>=900,'url':url,
      'original':str(raw),'original_sha256':rawsha,'qa_ref':str(ref),'qa_sha256':sha256(ref.read_bytes()).hexdigest(),
      'near_scene_distance':dist,'retail_rights':False,'stock_edition_verified':False,'sale_approved':False,'_hash':h})
  except Exception as e:errors.append(label+': '+str(e)[:150])
pack=None
if len(found)==2:
 pack=O/'GOODAL_100ml_five_source_photos_INTERNAL_ONLY.zip'
 images=prior+[Path(x['qa_ref']).read_bytes() for x in found]
 assert len({sha256(b).hexdigest() for b in images})==5
 with ZipFile(pack,'w') as z:
  for i,b in enumerate(images,1):z.writestr(f'{i:02d}-GOODAL-100ml-source-ref.jpg',b)
 with ZipFile(pack) as z:
  assert z.testzip() is None and len(z.namelist())==5
st['families']['pending-20'].update({'last_delta_version':'v2939','release_status':'FIVE_SOURCE_REFERENCES_QA_ONLY_RIGHTS_HOLD' if pack else 'PARTIAL_NEW_SOURCE_REFERENCES_RIGHTS_HOLD','v2939_scene_candidates':len(found),'v2939_source_archive':str(pack) if pack else None,'sale_approved':False})
m={'version':'v2939','baseline':'v2938','generated_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'family':'pending-20','listing_verified':verified,'new_source_photos':len(found),'five_source_target_gap':2-len(found),'source_records':[{k:v for k,v in x.items() if not k.startswith('_')} for x in found],'qa_zip':str(pack) if pack else None,'qa_zip_sha256':sha256(pack.read_bytes()).hexdigest() if pack else None,'errors':errors,'old_55_urls_changed':0,'old_11_family_assets_changed':0,'new_sale_approvals':0,'final_spreadsheet_shared':False}
(O/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
st.update({'version':'v2939','baseline':'v2938','new_sales_approvals':0,'new_public_URLs':0,'final_spreadsheet_shared':False})
(O/'stock30-incremental-state-v2939.json').write_text(json.dumps(st,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'version':'v2939','new':len(found),'target_gap':2-len(found),'qa_zip':bool(pack),'errors':errors}))
