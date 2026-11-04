#!/usr/bin/env python3
"""BBIA v293 parallel official product photos for never-used indices 2/3 of four families.
Only source inspection; no finished image file can be overwritten.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw,ImageFont
import json,io,hashlib,concurrent.futures
TARGETS={"1000000125":[2,3],"1000000216":[2,3],"1000000239":[2,3],"1000000223":[2,3]}
OUT=Path("/tmp/bbia-v293")
OUT.mkdir(parents=True,exist_ok=True)
FAMILIES={str(x["product_id"]):x for x in json.loads(Path("evidence/bbia-image-review-input.json").read_text(encoding="utf8"))["families"]}
TASKS=[(sku,i,FAMILIES[sku]["detail_references"][i]) for sku,ind in TARGETS.items() for i in ind]
def fetch(job):
    sku,i,url=job
    row={"goodsNo":sku,"source_index":i,"source_url":url}
    try:
        with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=19) as stream:
            data=stream.read(12_000_000)
        image=Image.open(io.BytesIO(data));image.load()
        if image.width<500:raise ValueError("TOO_SMALL_ORIGINAL")
        fname=f"BBIA_{sku}_SOURCE_{i}_v293.jpg"
        (OUT/fname).write_bytes(data)
        row.update(status="SOURCE_SAVED",dimensions=[image.width,image.height],sha256=hashlib.sha256(data).hexdigest(),original_filename=fname)
        return row,image.convert("RGB")
    except Exception as e:
        row.update(status="SOURCE_HOLD",reason=f"{type(e).__name__}: {str(e)[:125]}")
        return row,None
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    results=list(pool.map(fetch,TASKS))
contact=Image.new("RGB",(1750,1980),"#faf9f7")
d=ImageDraw.Draw(contact)
d.text((12,13),"BBIA v293 | 4 FAMILIES x 2 PREVIOUSLY UNUSED OFFICIAL DETAIL SOURCES",fill="#222222")
for family_idx,sku in enumerate(TARGETS):
    y=50+family_idx*475
    d.text((12,y),sku+"   "+FAMILIES[sku]["family"],fill="#202020")
    subset=[entry for entry in results if entry[0]["goodsNo"]==sku]
    for col,(meta,pic) in enumerate(subset):
        x=col*875+12
        if pic is None:
            d.text((x,y+60),"SOURCE HOLD",fill="#a22");continue
        whole=pic.copy();whole.thumbnail((300,390),Image.Resampling.LANCZOS)
        contact.paste(whole,(x,y+32))
        for v in range(2):
            top=max(0,int(pic.height*(0.12+0.35*v)))
            bottom=min(pic.height,top+min(950,pic.height))
            crop=pic.crop((0,top,pic.width,bottom))
            crop.thumbnail((250,365),Image.Resampling.LANCZOS)
            contact.paste(crop,(x+325+265*v,y+40))
        d.text((x,y+422),f"Source {meta['source_index']}, {pic.width} × {pic.height}",fill="#454545")
contact.save(OUT/"BBIA_v293_EIGHT_UNSEEN_SOURCE_CONTACT.jpg",quality=91)
report={"checkpoint":"v293","parent":"v292","source_attempts":len(TASKS),"sources_saved":sum(x["status"]=="SOURCE_SAVED" for x,_ in results),
        "families":list(TARGETS),"source_rows":[x for x,_ in results],
        "new_product_JPGs":0,"existing_public_images_modified":False,"verified_55_urls_unchanged":True,
        "note":"These are real source scans only. Human source crop/variant QA needed before any finished candidate."}
(OUT/"BBIA_v293_MANIFEST.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print("V293_SOURCE_BATCH",json.dumps({"sources":len(TASKS),"saved":report["sources_saved"]}))
