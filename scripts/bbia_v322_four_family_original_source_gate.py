#!/usr/bin/env python3
"""BBIA v322: Source-first batch for four underfilled families.
Immutable prior images. Per URL hold, no retries, preserve exact downloaded originals,
contact previews and digest-driven duplicate detection for future checkpoints.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image, ImageDraw, ImageOps
from concurrent.futures import ThreadPoolExecutor
import io,json,hashlib
OUT=Path('/tmp/bbia-v322'); OUT.mkdir(parents=True,exist_ok=True)
SELECTED={'1000000056':[3,4,5],'172':[3,4,5],'207':[3,4,5],'1000000151':[3,4,5]}
d=json.loads(Path('evidence/bbia-image-review-input.json').read_text('utf8'))
master={str(x['product_id']):x for x in d['families']}
jobs=[(sku,i,master[sku]['detail_references'][i]) for sku,indices in SELECTED.items() for i in indices]
def download(job):
    sku,i,url=job
    rec={'goodsNo':sku,'family':master[sku]['family'],'source_index':i,'source_url':url}
    try:
        with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0 BBIA QA/1.0'}),timeout=19) as resp:
            data=resp.read(12_000_000)
        image=Image.open(io.BytesIO(data));image.load()
        rec.update({'status':'SOURCE_SAVED','source_sha256':hashlib.sha256(data).hexdigest(),
                    'source_dimensions':list(image.size),'bytes':len(data)})
        name=f'BBIA_{sku}_OFFICIAL_SOURCE_{i}_v322.jpg'
        (OUT/name).write_bytes(data)
        rec['file']=name
        return rec,image.convert('RGB')
    except Exception as err:
        rec.update({'status':'HOLD_SOURCE_UNAVAILABLE','reason':f'{type(err).__name__}: {str(err)[:130]}'})
        return rec,None
with ThreadPoolExecutor(max_workers=8) as pool:
    results=list(pool.map(download,jobs))
board=Image.new('RGB',(1860,4*480+70),'#f7f6f4')
pen=ImageDraw.Draw(board)
pen.text((20,14),'BBIA v322 | 4 UNDERFILLED FAMILIES x 3 NEW SOURCE SLOTS | NO SALES APPROVAL',fill='#242424')
for row,sku in enumerate(SELECTED):
    y=52+row*480
    pen.text((18,y),sku+' '+master[sku]['family'],fill='#262626')
    sub=[z for z in results if z[0]['goodsNo']==sku]
    for col,(meta,img) in enumerate(sub):
        x=10+col*620
        if img is None:
            pen.text((x+10,y+85),'SOURCE HOLD',fill='#aa2222')
            continue
        all_view=img.copy();all_view.thumbnail((240,370),Image.Resampling.LANCZOS)
        board.paste(all_view,(x+10,y+28))
        # Crops of actual source at beginning / middle, no retouch or synthetic products.
        p=img.crop((0,max(0,int(img.height*.38)),img.width,min(img.height,max(0,int(img.height*.38))+1100)))
        p.thumbnail((325,375),Image.Resampling.LANCZOS)
        board.paste(p,(x+270,y+28))
        pen.text((x+10,y+418),f'detail {meta["source_index"]}  {img.width}x{img.height}',fill='#3b3b3b')
board.save(OUT/'BBIA_v322_TWELVE_SOURCE_CONTACT.jpg',quality=89,optimize=True)
success=[r for r,im in results if r['status']=='SOURCE_SAVED']
duplicates={}
for r in success:duplicates.setdefault(r['source_sha256'],[]).append([r['goodsNo'],r['source_index']])
data={'checkpoint':'v322','parent':'v321','requested':len(jobs),'originals_saved':len(success),
      'families':list(SELECTED),'records':[r for r,img in results],
      'same_source_digest_groups':[v for v in duplicates.values() if len(v)>1],
      'existing_published_assets_modified':False,'verified_55_urls_untouched':True,
      'new_selling_images':0,'approved_sales':0}
(OUT/'BBIA_v322_SOURCE_MANIFEST.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('V322_SOURCE_BATCH',json.dumps({'requested':len(jobs),'saved':len(success),'duplicates':data['same_source_digest_groups']},ensure_ascii=False))
