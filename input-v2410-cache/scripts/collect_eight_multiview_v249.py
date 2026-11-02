#!/usr/bin/env python3
"""Find additional *real image bytes* for eight unfinished Shopee families.

Every output is unapproved evidence. Never creates synthetic product, colors,
final artwork or publishes to public/images. Candidate images must be visually
compared with the exact SKU before any retail design use.
"""
import csv,hashlib,io,json,re
from pathlib import Path
from urllib.parse import urljoin,urlparse
import requests
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
ROSTER=json.loads((ROOT/'evidence/pending-30-v247.json').read_text(encoding='utf-8'))
IDS={'pending-01','pending-02','pending-05','pending-06','pending-07','pending-08','pending-10','pending-22'}
PRODUCTS=[x for x in ROSTER if x['id'] in IDS]
OUT=ROOT/'multi-view-evidence-v249'
OUT.mkdir(exist_ok=True)
HEAD={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36','Accept':'image/avif,image/webp,image/png,image/jpeg,image/*;q=0.8'}
FIELDS=['id','product','page','candidate_url','file','bytes','width','height','sha256','status','note']
rows=[]
def valid(url):
    p=urlparse(url)
    return p.scheme=='https' and bool(p.netloc) and not p.username and not p.password
def capture_url(url,folder,seen):
    if not valid(url):return None
    r=requests.get(url,headers=HEAD,timeout=(8,14),stream=True)
    r.raise_for_status()
    data=io.BytesIO()
    for chunk in r.iter_content(65536):
        data.write(chunk)
        if data.tell()>12_000_000:raise ValueError('over_12MB')
    raw=data.getvalue()
    with Image.open(io.BytesIO(raw)) as im:
        im.load()
        w,h=im.size
        fmt=im.format
    if min(w,h)<330 or fmt not in {'JPEG','PNG','WEBP'}:raise ValueError('small_or_unsupported')
    digest=hashlib.sha256(raw).hexdigest()
    if digest in seen:return None
    seen.add(digest)
    ext={'JPEG':'jpg','PNG':'png','WEBP':'webp'}[fmt]
    target=folder/f'candidate_{len(seen):02d}.{ext}'
    target.write_bytes(raw)
    return str(target.relative_to(OUT)),len(raw),w,h,digest
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
    for p in PRODUCTS:
        folder=OUT/p['id'];folder.mkdir(exist_ok=True)
        seen=set();possible=[]
        if p.get('url'):possible.append(p['url'])
        page_url=p.get('page','')
        status='NO_PAGE'
        if valid(page_url):
            page=browser.new_page(viewport={'width':1440,'height':1000})
            try:
                page.goto(page_url,wait_until='domcontentloaded',timeout=18000)
                page.wait_for_timeout(1100)
                imgs=page.locator('img').evaluate_all('els=>els.map(x=>({url:x.currentSrc||x.src,alt:x.alt||"",w:x.naturalWidth,h:x.naturalHeight}))')
                imgs.sort(key=lambda x:x.get('w',0)*x.get('h',0),reverse=True)
                for im in imgs:
                    u=urljoin(page_url,im['url'])
                    if valid(u) and u not in possible and not any(s in u.lower() for s in ('logo','icon','sprite','avatar','banner')):
                        possible.append(u)
                status=f'PAGE_READ_{len(imgs)}_IMAGES'
            except Exception as e:status=f'PAGE_FAILED_{str(e)[:105]}'
            finally:page.close()
        saved=0
        for u in possible[:28]:
            if saved>=7:break
            try:
                r=capture_url(u,folder,seen)
                if r:
                    fn,n,w,h,sha=r
                    rows.append(dict(id=p['id'],product=p['name'],page=page_url,candidate_url=u,file=fn,bytes=n,width=w,height=h,sha256=sha,status='DOWNLOADED_QA_HOLD',note='Actual bytes; exact SKU/packaging/source rights and image role unverified'))
                    saved+=1
            except Exception:pass
        if saved==0:rows.append(dict(id=p['id'],product=p['name'],page=page_url,candidate_url='',file='',bytes='',width='',height='',sha256='',status='SOURCE_HOLD',note=status))
        print(p['id'],p['name'],'unique_source_photos',saved,'page',status,flush=True)
    browser.close()
with (OUT/'EIGHT_FAMILY_SOURCE_MANIFEST.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
summary={'families_checked':len(PRODUCTS),'photos_downloaded':sum(r['status']=='DOWNLOADED_QA_HOLD' for r in rows),'families_with_bytes':len({r['id'] for r in rows if r['status']=='DOWNLOADED_QA_HOLD'}),'qa_approved':0,'published':0}
(OUT/'SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'README.txt').write_text('Multi-image evidence only. Not all page images represent the actual seller SKU. Manual brand, photo fidelity, options, identity, rights, MK logo QA is required. DO NOT DEPLOY. Previously verified 55 public URLs unaffected.\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
