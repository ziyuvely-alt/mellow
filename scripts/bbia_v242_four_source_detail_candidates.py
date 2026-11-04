#!/usr/bin/env python3
"""BBIA v242: four new distinct official-source detail PHOTO drafts; do not alter historical sets."""
import argparse,concurrent.futures,hashlib,io,json
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw,ImageFont
TASKS=[
 {"id":"1000000135","name":"LAST VELVET TINT","source":0,"crop":(0,1300,1000,2390),"role":"LIP COLOR CAMPAIGN DETAIL"},
 {"id":"1000000136","name":"GLOW TINT","source":1,"crop":(0,1900,1000,3100),"role":"COLOR TEXTURE DETAIL"},
 {"id":"1000000216","name":"NUDY SLIM EYELINER","source":2,"crop":(0,0,1000,1280),"role":"EYE APPLICATION REFERENCE"},
 {"id":"1000000244","name":"UNDER EYE PENCIL","source":2,"crop":(0,0,1000,940),"role":"PENCIL PRODUCT DETAIL"}
]
def font(n,bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-"+("Bold" if bold else "")+".ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",n)
def run(task,families):
    r=dict(task)
    url=families[task["id"]]["detail_references"][task["source"]]
    r["url"]=url
    try:
        with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=22) as resp: data=resp.read(12000000)
        photo=Image.open(io.BytesIO(data)).convert("RGB")
        a,b,c,d=task["crop"];rect=(max(0,a),max(0,b),min(photo.width,c),min(photo.height,d))
        area=photo.crop(rect)
        if min(area.size)<500:raise ValueError("CROP_UNDERSIZED")
        r.update(status="SOURCE_OK",original_source_dimensions=list(photo.size),source_sha256=hashlib.sha256(data).hexdigest(),crop_applied=list(rect))
        return r,area
    except Exception as e:
        r.update(status="SOURCE_HOLD",error=str(e)[:150]);return r,None
def main(out):
    out.mkdir(parents=True,exist_ok=True)
    rows=json.loads(Path("evidence/bbia-image-review-input.json").read_text(encoding="utf-8"))["families"]
    families={str(x["product_id"]):x for x in rows}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        products=list(pool.map(lambda t:run(t,families),TASKS))
    contact=Image.new("RGB",(2200,2300),"#eeeeee")
    dc=ImageDraw.Draw(contact)
    dc.text((20,10),"BBIA v242 - FOUR NEW SECONDARY SCENES (QA / NEVER PUBLISH DIRECTLY)",fill="#222222")
    records=[]
    for index,(r,area) in enumerate(products):
        if area is None:records.append(r);continue
        picture=area.copy();picture.thumbnail((870,765),Image.Resampling.LANCZOS)
        scene=Image.new("RGB",(1080,1080),"#faf9f7")
        d=ImageDraw.Draw(scene)
        d.text((70,45),"BBIA",fill="#332c2c",font=font(52,True))
        d.text((70,122),r["name"],fill="#493b3b",font=font(34,True))
        d.line((70,185,1010,185),fill="#d5cbc5",width=2)
        scene.paste(picture,((1080-picture.width)//2,207+(770-picture.height)//2))
        d.text((70,1008),r["role"],fill="#665b59",font=font(24))
        filename=f"BBIA_{r['id']}_DETAIL_v242_QA_PENDING.jpg"
        dest=out/filename
        scene.save(dest,format="JPEG",quality=90,optimize=True,subsampling=0)
        if dest.stat().st_size>=2_000_000: raise ValueError("JPG_LIMIT"+filename)
        with Image.open(dest) as im:im.verify()
        r.update(status="NEW_DETAIL_DRAFT_VISUAL_QA_PENDING",filename=filename,bytes=dest.stat().st_size,
                 sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),output_size=[1080,1080])
        x=(index%2)*1100;y=(index//2)*1130+50
        contact.paste(scene,(x,y))
        records.append(r)
    contact.save(out/"BBIA_v242_FOUR_DETAIL_CONTACT.jpg",quality=89)
    (out/"BBIA_v242_MANIFEST.json").write_text(json.dumps({"checkpoint":"v242","prior":"v241","new_images_created":sum(x["status"]=="NEW_DETAIL_DRAFT_VISUAL_QA_PENDING" for x in records),
       "existing_public_changed":False,"sales_approved":0,"files":records,
       "warning":"Cropped official marketing source may still contain Korean text or variant differences. Human QA before any promotion."},ensure_ascii=False,indent=2)+"\n")
    print("V242_RESULTS",json.dumps([[r["id"],r["status"]] for r in records]))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True);main(Path(p.parse_args().out))
