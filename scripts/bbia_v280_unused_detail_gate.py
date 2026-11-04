#!/usr/bin/env python3
"""v280: inspect unused official photo slots for 3 incomplete existing BBIA families, zero existing changes."""
import concurrent.futures,hashlib,io,json
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw
IDS=['1000000184','1000000239','1000000223']
INDICES=[3,4]
master={str(x['product_id']):x for x in json.loads(Path('evidence/bbia-image-review-input.json').read_text(encoding='utf8'))['families']}
OUT=Path('/tmp/bbia-v280');OUT.mkdir(parents=True,exist_ok=True)
jobs=[(sku,i,master[sku]['detail_references'][i]) for sku in IDS for i in INDICES]
def fetch(task):
    sku,i,url=task; rec={'goodsNo':sku,'detail_index':i,'source_url':url}
    try:
        with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=20) as r:data=r.read(11000000)
        im=Image.open(io.BytesIO(data));im.load()
        fn=f'BBIA_{sku}_UNUSED_DETAIL_{i}_v280.jpg';(OUT/fn).write_bytes(data)
        rec.update(status='SOURCE_RETAINED',sha256=hashlib.sha256(data).hexdigest(),size=[im.width,im.height],file=fn)
        return rec,im.convert('RGB')
    except Exception as e:
        rec.update(status='HOLD_SOURCE',reason=f'{type(e).__name__}: {str(e)[:140]}')
        return rec,None
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as p: rows=list(p.map(fetch,jobs))
contact=Image.new('RGB',(1680,1770),'#f6f5f4');draw=ImageDraw.Draw(contact)
draw.text((15,14),'BBIA v280 | 3 FAMILIES × 2 UNUSED MANUFACTURER DETAILS | CROP GATE',fill='#222222')
for j,sku in enumerate(IDS):
    y=45+j*570;draw.text((15,y),f'{sku} {master[sku]["family"]}',fill='#222222')
    for i,(rec,im) in enumerate([x for x in rows if x[0]['goodsNo']==sku]):
        x=10+i*840
        if im is None:continue
        full=im.copy();full.thumbnail((250,450),Image.Resampling.LANCZOS);contact.paste(full,(x,y+38))
        for k in range(2):
            top=int(im.height*k/2);bot=min(im.height,top+min(900,im.height//2))
            crop=im.crop((0,top,im.width,bot));crop.thumbnail((260,420),Image.Resampling.LANCZOS)
            contact.paste(crop,(x+260+270*k,y+38))
        draw.text((x,y+491),f'SLOT {rec["detail_index"]} | {im.width}×{im.height}',fill='#444444')
contact.save(OUT/'BBIA_v280_SIX_UNREVIEWED_DETAILS.jpg',quality=90)
manifest={'checkpoint':'v280','parent':'v279','family_ids':IDS,'source_attempts':6,'source_success':sum(r['status']=='SOURCE_RETAINED' for r,_ in rows),'records':[r for r,_ in rows],'published_changed':False,'new_sales_approved':0,'new_jpg':0}
(OUT/'BBIA_v280_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('V280_RESULT',json.dumps({'sources_ok':manifest['source_success'],'family_count':len(IDS)}))
