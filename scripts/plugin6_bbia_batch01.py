import json,hashlib,urllib.request,time,io,zipfile
from pathlib import Path
from PIL import Image
base='https://cdn-pro-web-250-115.cdn-nhncommerce.com/sky007com_godomall_com/data/goods/'
candidates={
'over_glaze_stick':'24/02/08/1000000128/1000000128_magnify_011.jpg',
'glow_tint_mini':'25/03/11/1000000163/1000000163_magnify_053.jpg',
'last_velvet_tint_mini':'25/05/22/1000000186/1000000186_magnify_021.jpg',
'leau_tint_mini':'25/05/22/1000000187/1000000187_magnify_016.jpg',
'over_glaze_mini':'25/09/36/1000000208/1000000208_magnify_081.jpg',
'glow_tint':'24/06/25/1000000136/1000000136_magnify_037.jpg',
'last_powder_lipstick':'19/03/13/200/200_magnify_095.jpg',
'ready_to_wear_water_lipstick':'22/09/39/1000000074/1000000074_magnify_041.jpg',
'leau_tint':'23/06/24/1000000113/1000000113_magnify_010.jpg',
'lip_oil_balm_shea':'19/03/13/228/228_magnify_047.jpg',
'nudy_slim_eyeliner':'26/01/05/1000000216/1000000216_magnify_034.jpg',
'aegyosal_pencil':'26/07/27/1000000244/1000000244_magnify_02.jpg',
'last_auto_gel_eyeliner':'19/03/13/206/206_magnify_068.jpg',
'last_auto_gel_slim':'23/05/22/1000000110/1000000110_magnify_046.jpg'}
out=Path('plugin6-bbia-batch01-source');out.mkdir(exist_ok=True)
audit=[]
for slug,path in candidates.items():
    url=base+path;row={'key':slug,'url':url,'status':'FAILED'}
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.bbia.co.kr/'})
        with urllib.request.urlopen(req,timeout=14) as r:data=r.read(10_000_001)
        if not data or len(data)>10_000_000:raise ValueError('byte limit')
        with Image.open(io.BytesIO(data)) as im:
            fmt=im.format;w,h=im.size;im.verify()
        if fmt not in ('JPEG','PNG','WEBP') or min(w,h)<450:raise ValueError('not an eligible source photo')
        ext={'JPEG':'.jpg','PNG':'.png','WEBP':'.webp'}[fmt]
        (out/(slug+ext)).write_bytes(data)
        row.update(status='FILE_OK_PRODUCT_MATCH_PENDING',width=w,height=h,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),filename=slug+ext)
    except Exception as exc:row['error']=str(exc)[:220]
    audit.append(row); print(slug,row['status'],flush=True)
(out/'source_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
with zipfile.ZipFile(out/'BBIA_BATCH01_SOURCES_NOT_SALE_READY.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in out.iterdir():
        if p.is_file() and p.suffix.lower() in ('.jpg','.png','.webp','.json'):z.write(p,p.name)
