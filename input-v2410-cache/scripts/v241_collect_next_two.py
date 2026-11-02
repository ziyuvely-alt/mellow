from pathlib import Path
import requests, re, json, hashlib, mimetypes, time, os, io, zipfile
from bs4 import BeautifulSoup
from PIL import Image
from urllib.parse import urljoin,urlparse,unquote
out=Path('v241_next_two_sources');out.mkdir(exist_ok=True)
targets=[
{'id':'OBGE_COVER_LOTION_50G_10ML','pages':['https://obge.hk/en/products/ncl','https://www.obge.tw/en/products/obge-natural-cover-lotion','https://m.global.oliveyoung.com/product/detail?prdtNo=GA240423330'],'direct':['https://image.coupangcdn.com/image/vendor_inventory/9f88/c0f91b86a95a4b4f1e04fe8d2efc1255ed007fa71718a8b2c13c8172c327.jpg','https://cdn-image.oliveyoung.com/prdtImg/1303/2ec4eaa8-0492-49c7-8f3c-52fbdb3d63ac.jpg']},
{'id':'BIOHEAL_EYE_PATCH_60P','pages':['https://item.rakuten.co.jp/biohealboh/yp3569/','https://global.oliveyoung.com/product/detail?accParam=20&prdtNo=GA240825494'],'direct':['https://tshop.r10s.jp/biohealboh/cabinet/11641876/12371886/yp3569.jpg?fitin=720%3A720','https://down-my.img.susercontent.com/file/sg-11134207-7rfga-m9u9gr4tq27d37']},
]
headers={'User-Agent':'Mozilla/5.0','Accept':'image/avif,image/webp,image/apng,image/*,*/*;q=0.8'}
reports=[]
for product in targets:
 folder=out/product['id'];folder.mkdir(exist_ok=True)
 allurls=[(x,'DIRECT') for x in product['direct']]
 for p in product['pages']:
  try:
   resp=requests.get(p,headers=headers,timeout=22)
   resp.raise_for_status()
   soup=BeautifulSoup(resp.text,'html.parser')
   pageurls=[]
   for t in soup.find_all(['img','meta','source']):
    for key in ('src','data-src','data-original','data-zoom-image','content','srcset','data-srcset','data-large-image'):
     val=t.get(key)
     if not val:continue
     if key in ('srcset','data-srcset'):
      val=val.split(',')[0].strip().split(' ')[0]
     if val.startswith('data:'):continue
     url=urljoin(p,val)
     if url.startswith('https://') and re.search(r'\.(jpg|jpeg|png|webp)(\?|$)|/file/|/prdtImg/|/cabinet/',url,re.I):
      pageurls.append(url)
   allurls.extend((u,p) for u in pageurls[:75])
   print(product['id'],p,'PAGE',resp.status_code,'candidates',len(pageurls),flush=True)
  except Exception as e:print('PAGE_ERROR',product['id'],p,str(e)[:160],flush=True)
 seen=set();count=0
 for url,origin in allurls:
  if url in seen:continue
  seen.add(url)
  if count>=35:break
  try:
   r=requests.get(url,headers={**headers,'Referer':origin if origin.startswith('https://') else product['pages'][0]},timeout=13)
   r.raise_for_status()
   raw=r.content
   if len(raw)<6000 or len(raw)>7000000:continue
   im=Image.open(io.BytesIO(raw));im.load()
   if min(im.size)<350:continue
   if im.width>9000 or im.height>9000:continue
   # preserve pixel data as JPEG preview candidate
   count+=1
   name=f'{count:02}.jpg'
   im.convert('RGB').save(folder/name,'JPEG',quality=91,optimize=True)
   bb=(folder/name).read_bytes()
   reports.append({'product_id':product['id'],'candidate':name,'source_url':url,'source_page':origin,'width':im.width,'height':im.height,'sha256':hashlib.sha256(bb).hexdigest(),'bytes':len(bb),'status':'CANDIDATE_UNVERIFIED_PRODUCT_IDENTITY'})
  except Exception as e:pass
 print(product['id'],'CANDIDATES',count,flush=True)
(out/'manifest.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2))
print('TOTAL',len(reports),flush=True)
