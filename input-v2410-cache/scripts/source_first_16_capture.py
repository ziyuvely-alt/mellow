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
# Fetch independent alternative-source URLs first, keeping each as unapproved evidence.
ALT={"12":"https://dybeauty.de/cdn/shop/files/magic-cushion-moist-up-uvlaznyayushhii-tonalnyi-kuson-missha-ton-23-2821874.webp?v=1778175851&width=533","14":"https://down-sg.img.susercontent.com/file/sg-11134207-7rdxu-mc1h4jshbjji0c","15":"https://d2gfz7wkiigkmv.cloudfront.net/pickin/2/1/2/yFqekpHORc60Vqi1Je3VTg","16":"https://www.dodoskin.com/cdn/shop/files/OBgEPoreZeroFreshAllInOne150ml-1.jpg?v=1761114787","17":"https://oceanbuy.ca/cdn/shop/files/bioheal-boh-bioheal-boh-probioderm-3d-lifting-cream-50ml-oceanbuy-beauty-722829.jpg?v=1748329929&width=1080","18":"https://lushher.ro/cdn/shop/files/BIOHEALBOH-ProbiodermCollagenRemodelingEyePatch.png?v=1747506108","02":"https://beautybuddy.co/cdn/shop/files/peripera-lip-stain-tint-default-title-peripera-ink-mood-glowy-tint-4g-41-pink-spirit-26068196687949.jpg?v=1773732770&width=800","03":"https://nuupbeauty.com/cdn/shop/files/Sintitulo-3_dbd13cd9-62d6-4fd2-91b3-6277f1b78e4c.png?v=1770848397","08":"https://cdn.zochil.shop/7566e0e7-0271-48b9-b798-cff4b3db1b01_t700.jpg","09":"https://cdn-image.oliveyoung.com/prdtImg/1760/c6ee51ec-b18e-4b45-accf-fe9794d443b4.jpg?AR=0&QT=80&RS=1500x1500"}
for rec in rows:
 url=ALT.get(rec['id'])
 if not url: continue
 try:
  resp=requests.get(url,headers=HEAD,timeout=15)
  resp.raise_for_status()
  rec['alt_photo']=save(resp.content,OUT/rec['id']/'alternate')
  rec['alt_source_url']=url
  rec['alternate_status']='saved'
 except Exception as exc: rec['alternate_status']='failed: '+str(exc)[:220]
json.dump(rows,open(OUT/'report.json','w'),ensure_ascii=False,indent=2)
print('ALT',json.dumps([{'id':r['id'],'status':r.get('alternate_status','not_applicable')} for r in rows]))

# Browser captured screenshots already archived in the previous run.


# V2.3.0 second-scene collection. Unapproved discovery, never sell these without visual source checks.
try:
 from playwright.sync_api import sync_playwright
 with sync_playwright() as pw:
  b=pw.chromium.launch(headless=True,args=['--no-sandbox'])
  for p in PRODUCTS:
   page=b.new_page(viewport={'width':1440,'height':1000})
   rec=next(r for r in rows if r['id']==p['id'])
   rec['further_sources']=[]
   try:
    page.goto(p['page'],wait_until='domcontentloaded',timeout=18000)
    page.wait_for_timeout(1300)
    resources=page.locator('img').evaluate_all('(els)=>els.map(e=>({url:e.currentSrc||e.src,alt:e.alt||"",w:e.naturalWidth,h:e.naturalHeight}))')
    resources=[x for x in resources if x['url'].startswith('http') and x['w']>=450 and x['h']>=450 and not any(k in x['url'].lower() for k in ['logo','icon','banner'])]
    unique={x['url']:x for x in resources}
    for j,x in enumerate(sorted(unique.values(),key=lambda a:a['w']*a['h'],reverse=True)[:14]):
     try:
      response=requests.get(x['url'],headers={**HEAD,'Referer':p['page']},timeout=9)
      response.raise_for_status()
      dst=OUT/p['id']/('discovery_'+str(j+1).zfill(2))
      result=save(response.content,dst)
      rec['further_sources'].append({**result,'url':x['url'],'alt':x['alt'][:120]})
     except Exception: pass
    rec['further_source_status']='collected' if rec['further_sources'] else 'no_extra_photos'
   except Exception as e:rec['further_source_status']='failed_'+str(e)[:150]
   finally:page.close()
  b.close()
except Exception as e:
 for r in rows:r['further_source_status']='browser_unavailable_'+str(e)[:150]
json.dump(rows,open(OUT/'report.json','w'),ensure_ascii=False,indent=2)
print('EXTRA_SCENES',json.dumps([{'id':r['id'],'new':len(r.get('further_sources',[]))} for r in rows]))
