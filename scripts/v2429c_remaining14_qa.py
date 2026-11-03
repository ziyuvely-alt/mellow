#!/usr/bin/env python3
"""v2.4.29c: audit pending-17..30 from real existing photos, no invented shade charts."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,hashlib,re
S=Path("v2427b-source");Q=Path("v2429b-source");O=Path("v2429c-output");O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
q=json.loads((Q/"work_queue.json").read_text());assert len(q["queue"])==30
all_jpg=sorted(S.rglob("*.jpg"))
F=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",20)
H=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",31)
summ=[]
for n in range(17,31):
    id=f"pending-{n:02d}"
    files=[p for p in all_jpg if "/"+id+"/" in "/"+str(p.relative_to(S))]
    priority=[p for p in files if "/originals-immutable/" in str(p)]
    photos=priority if priority else files
    unique=[]; seen=set()
    for p in photos:
        dig=sha(p)
        if dig not in seen: seen.add(dig);unique.append(p)
    entry={"group_id":id,"existing_JPG_sources":len(unique),"state":"SOURCE_QA_HOLD","QA_file":None,"sha256":None,"blockers":["EXACT_PRODUCT_EDITION_NOT_VERIFIED","RIGHTS_NOT_VERIFIED"],"source_SHA256":[{"path":str(p.relative_to(S)),"sha256":sha(p)} for p in unique[:3]]}
    if unique:
        board=Image.new("RGB",(1080,1080),(248,245,240));d=ImageDraw.Draw(board)
        d.text((36,30),f"{id}  |  Genuine stored JPG review",font=H,fill=(45,46,44))
        d.text((36,79),"No synthetic swatch | source & rights evidence required",font=F,fill=(89,79,74))
        for i,p in enumerate(unique[:4]):
            x=35+(i%2)*510;y=141+(i//2)*428
            with Image.open(p) as im:
                im.load();im=ImageOps.contain(im.convert("RGB"),(480,350),Image.Resampling.LANCZOS)
                board.paste(im,(x+(480-im.width)//2,y+(350-im.height)//2))
            d.text((x,y+357),p.name[:43],font=F,fill=(65,65,65))
        d.text((35,1010),"INTERNAL QA PREVIEW ONLY - not customer-facing image",font=F,fill=(91,87,84))
        path=O/(id+"_actual_source_review_QA_v2429c.jpg")
        board.save(path,"JPEG",quality=89,optimize=True)
        with Image.open(path) as im:assert im.size==(1080,1080) and im.format=="JPEG"
        assert path.stat().st_size<2_000_000
        entry.update({"QA_file":path.name,"sha256":sha(path),"state":"VISUAL_QA"})
        for row in q["queue"]:
            if row["group_id"]==id:row["state"]="VISUAL_QA"
    (O/(id+"_checkpoint.json")).write_text(json.dumps(entry,indent=2,ensure_ascii=False))
    summ.append(entry)
(O/"work_queue.json").write_text(json.dumps(q,indent=2,ensure_ascii=False))
(O/"remaining_14_results.json").write_text(json.dumps(summ,indent=2,ensure_ascii=False))
out={"version":"2.4.29c","groups_attempted":len(summ),"groups_with_actual_QA_JPG":sum(bool(x["QA_file"]) for x in summ),"groups_without_source_JPG":sum(not x["QA_file"] for x in summ),"new_sales_images":0,"new_official_color_charts":0,"existing_source_JPG_count":len(all_jpg),"previous_C6_and_8_QA_preserved_in_own_branches":True,"30_group_queue_preserved":len(q["queue"]),"commercial_rights_verified":0,"FINAL_QA_APPROVED":0,"public_files_changed":0,"next":"Finish official-shade provenance for C8; review 30 group previews individually and verify stock packaging and permissions"}
(O/"v2429c_checkpoint.json").write_text(json.dumps(out,indent=2,ensure_ascii=False))
print(json.dumps(out),flush=True)
