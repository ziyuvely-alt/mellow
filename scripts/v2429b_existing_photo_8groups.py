#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,hashlib,csv
S=Path("v2427b-source"); P=Path("v2429-source"); O=Path("v2429b-output");O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=json.loads((P/"BD_photo_audit_queue.json").read_text())
assert len(rows)==8
f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",20)
f2=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",30)
out=[]
for x in rows:
    id=x["id"]; ps=[S/y["path"] for y in x["sources"]]
    assert len(ps)>=1
    im=Image.new("RGB",(1080,1080),(247,245,242));d=ImageDraw.Draw(im)
    d.text((45,36),id+" | Real existing JPG source audit",font=f2,fill=(43,49,44))
    d.text((45,89),"Exact stock / commercial use / image rights: NOT VERIFIED",font=f,fill=(100,80,65))
    for i,p in enumerate(ps):
        assert p.exists() and sha(p)==x["sources"][i]["sha256"]
        with Image.open(p) as a:
            a.load(); a=ImageOps.contain(a.convert("RGB"),(470,700))
            px=42+i*510; im.paste(a,(px+(470-a.width)//2,150+(700-a.height)//2))
        d.text((px,895),p.name[:43],font=f,fill=(65,65,65))
    d.text((44,1010),"Internal QA only - not an approved shade swatch or retail image",font=f,fill=(80,80,80))
    dest=O/(id+"_real_existing_photo_QA_V2429b.jpg"); im.save(dest,"JPEG",quality=90,optimize=True)
    with Image.open(dest) as check: assert check.format=="JPEG" and check.size==(1080,1080)
    assert dest.stat().st_size<2000000
    out.append({"group_id":id,"state":"VISUAL_QA","grade":"UNCLASSIFIED","qa_jpg":dest.name,"sha256":sha(dest),"source_files_verified":len(ps),"sale_approved":False})
with (O/"BD_eight_image_QA_results.json").open("w") as f:json.dump(out,f,indent=2)
q=json.loads((P/"work_queue.json").read_text())
assert len(q["queue"])==30
for entry in q["queue"]:
    if entry["group_id"] in [r["group_id"] for r in out]:
        entry["state"]="VISUAL_QA"
        entry["grade"]="UNCLASSIFIED"
(O/"work_queue.json").write_text(json.dumps(q,ensure_ascii=False,indent=2))
source_count=len(list(S.rglob("*.jpg")))
check={"version":"2.4.29b","processed_additional_existing_photo_groups":8,"new_QA_JPG_count":8,"new_official_swatch_JPG":0,"baseline_source_JPG_count":source_count,"C6_prior_QA_JPG_preserved":6,"workqueue_recovered":30,"public_files_written":0,"sales_approval":0,"rights_verified":0,"pending_previous_C6":True,"next_restart":"Verify original documented C8 shade photos, seek original exact-generation source; then remaining pending-17..30"}
(O/"v2429b_checkpoint.json").write_text(json.dumps(check,ensure_ascii=False,indent=2))
print(json.dumps(check),flush=True)
