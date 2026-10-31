import json, os, time, hashlib, requests, io
from PIL import Image
from pathlib import Path
PRODUCTS=json.load(open('source-first-16.json',encoding='utf8'))
OUT=Path('source-first-output');OUT.mkdir(exist_ok=True)
rows=[]
HEAD={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36','Accept':'image/avif,image/webp,image/apng,image/*,*/*;q=0.8'}
def save(data,path):
 im=Image.open(io.BytesIO(data));im.load()
 if im.width<200 or im.height<200: raise ValueError('low_resolution_'+str(im.size))
 fmt='png' if im.mode in ('RGBA','LA') else 'jpg'
 out=path.with_suffix('.'+fmt)
 if fmt=='png':im.save(out)
 else:im.convert('RGB').save(out,'JPEG',quality=92)
 return {'filename':str(out),'width':im.width,'height':im.height,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
for p in PRODUCTS:
 record={'id':p['id'],'name':p['name'],'source_url':p['url'],'page':p['page'],'download_status':'not_attempted','screenshot_status':'not_attempted'}
 folder=OUT/p['id'];folder.mkdir(exist_ok=True)
 try:
  r=requests.get(p['url'],headers=HEAD,timeout=15)
  r.raise_for_status()
  record.update(save(r.content,folder/'download'))
  record['download_status']='saved'
 except Exception as exc: record['download_status']='failed: '+str(exc)[:220]
 rows.append(record)
json.dump(rows,open(OUT/'report.json','w'),ensure_ascii=False,indent=2)
# Screenshot fallback uses rendered image element, not an arbitrary webpage screenshot.
try:
 from playwright.sync_api import sync_playwright
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
  for p,record in zip(PRODUCTS,rows):
   # Always inspect product-page image elements for additional independent source candidates.
   page=browser.new_page(viewport={'width':1440,'height':1100},device_scale_factor=1)
   try:
    page.goto(p['page'],wait_until='domcontentloaded',timeout=18000)
    page.wait_for_timeout(1700)
    imgs=page.locator('img')
    candidates=[]
    for j in range(min(imgs.count(),70)):
     img=imgs.nth(j)
     v=img.evaluate('(el)=>({w:el.naturalWidth,h:el.naturalHeight,src:el.currentSrc||el.src})')
     if v['w']>=380 and v['h']>=380 and img.is_visible():
      candidates.append((v['w']*v['h'],img,v['src']))
    if not candidates:raise ValueError('no_large_visible_image')
    candidates.sort(key=lambda x:x[0],reverse=True)
    for j,(_,node,src) in enumerate(candidates[:3]):
     dest=OUT/p['id']/('screenshot_'+str(j+1)+'.png')
     node.screenshot(path=str(dest),timeout=12000)
     with Image.open(dest) as im: im.verify()
     record.setdefault('screenshot_files',[]).append({'file':str(dest),'image_src':src,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
    record['screenshot_status']='saved'
   except Exception as exc:record['screenshot_status']='failed: '+str(exc)[:220]
   finally:page.close()
  browser.close()
except Exception as exc:
 for record in rows:
  if record['screenshot_status']=='not_attempted':record['screenshot_status']='browser_unavailable: '+str(exc)[:180]
json.dump(rows,open(OUT/'report.json','w'),ensure_ascii=False,indent=2)
print('REPORT',json.dumps([{k:r[k] for k in ('id','download_status','screenshot_status')} for r in rows],ensure_ascii=False))
