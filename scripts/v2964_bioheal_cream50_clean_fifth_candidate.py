#!/usr/bin/env python3
"""Single-source Bioheal 50mL cream photo candidate; source originals immutable, retail hard HOLD."""
import io,hashlib,json,zipfile,urllib.request
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa-review/v2964-bioheal-cream50-open-jar-fifth-scene-internal-20261106"
BASE=ROOT/"qa-review/v2934-bioheal-cream-four-real-source-scene-QA-only/manifest.json"
SOURCE="https://koreabe.com/cdn/shop/files/2_41_c8f3efe6-71e8-4d55-b84f-c8ddd97bebf8.png?v=1776140965&width=1024"
PAGE="https://koreabe.com/products/bioheal-nad-prizcell-glow-boost-cream-50ml"
def sha(b):return hashlib.sha256(b).hexdigest()
def dh(im):
    v=list(im.convert("L").resize((9,8),Image.Resampling.LANCZOS).getdata())
    return "".join(str(int(v[y*9+x]>v[y*9+x+1])) for y in range(8) for x in range(8))
def main():
    if OUT.exists():raise RuntimeError("Do not repeat: v2964 already exists")
    old=json.loads(BASE.read_text())
    archive=ROOT/old["zip_path"]
    assert sha(archive.read_bytes())==old["zip_sha256"],"archive baseline wrong; refuse to mutate"
    known={r["sha256"]:r for r in old["source_records"]}
    originals={}
    with zipfile.ZipFile(archive) as z:
        for n in z.namelist():
            if n.lower().endswith((".jpg",".jpeg",".png")):
                b=z.read(n)
                if sha(b) in known:originals[sha(b)]=b
    if len(originals)!=4:raise ValueError("Missing a source from v2934 existing archive")
    old_images=[originals[r["sha256"]] for r in old["source_records"]]
    prev_phash=[]
    for b in old_images:
        with Image.open(io.BytesIO(b)) as im: im.load();prev_phash.append(dh(im))
    OUT.mkdir(parents=True)
    m={"version":"v2964","prior":"v2963","family":"pending-25","product":"BIOHEAL BOH NAD-PRIZCELL Glow Boost Cream 50mL",
       "source_page":PAGE,"source_image":SOURCE,"source_type":"Koreabe third-party merchant, NOT brand permissions",
       "expected_visual":"clean open 50mL red jar with pink cream swirl on white ground, no seller badge",
       "previous_4_QA_ZIP":old["zip_path"],"old_original_JPG_modified":0,
       "prior_11_published_families_untouched":True,"prior_55_URLs_untouched":True,
       "licensed_to_republish":False,"owned_50mL_generation_verified":False,
       "original_MK_png_verified":False,"retail_approved":False,"public_JPGs_created":0,"new_verified_urls":0,
       "run_source_attempts":1}
    try:
        req=urllib.request.Request(SOURCE,headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"})
        with urllib.request.urlopen(req,timeout=22) as resp:raw=resp.read(5_000_000)
        if len(raw)<15000 or len(raw)>=5_000_000:raise ValueError("invalid candidate image bytes")
        with Image.open(io.BytesIO(raw)) as im:
            im.load();fmt=im.format; native=im.size
            if min(native)<700:raise ValueError("NATIVE_RES_BELOW_700 "+str(native))
            im=im.convert("RGB");im.thumbnail((1020,1020),Image.Resampling.LANCZOS)
            canvas=Image.new("RGB",(1080,1080),"white")
            canvas.paste(im,((1080-im.width)//2,(1080-im.height)//2))
            buf=io.BytesIO();canvas.save(buf,format="JPEG",quality=93,optimize=True)
        converted=buf.getvalue()
        if len(converted)>=2_000_000:raise ValueError("JPG_TOO_LARGE")
        with Image.open(io.BytesIO(converted)) as im:h=dh(im)
        distances=[sum(a!=b for a,b in zip(h,h0)) for h0 in prev_phash]
        orig=OUT/("pending-25-fifth-Koreabe-original"+{"PNG":".png","JPEG":".jpg","WEBP":".webp"}.get(fmt,".bin"))
        orig.write_bytes(raw)
        jpg=OUT/"pending-25-fifth-open-cream-jar-1080-QA-ONLY.jpg"
        jpg.write_bytes(converted)
        m.update({"candidate_native_px":list(native),"candidate_format":fmt,
          "candidate_native":str(orig.relative_to(ROOT)),"native_sha256":sha(raw),
          "new_JPG":str(jpg.relative_to(ROOT)),"new_JPG_sha256":sha(converted),
          "dhash_distances_to_four_previous":distances,"new_JPG_bytes":len(converted)})
        if min(distances)<=8:raise ValueError("NEAR_DUPLICATE_FIFTH_CANDIDATE")
        photos=old_images+[converted]
        zp=OUT/"pending-25-five-existing-plus-one-NEW-composition-INTERNAL-ONLY.zip"
        with zipfile.ZipFile(zp,"w") as z:
            for i,b in enumerate(photos):
                entry=zipfile.ZipInfo(f"{i+1:02d}-{'new' if i==4 else 'existing'}-BIOHEAL50mL-QA.jpg")
                entry.compress_type=zipfile.ZIP_STORED;entry.external_attr=0o644<<16
                z.writestr(entry,b)
        with zipfile.ZipFile(zp) as z:
            assert all(sha(z.read(n))==sha(b) for n,b in zip(z.namelist(),photos))
        contact=Image.new("RGB",(1380,1050),"#f6f6f7");d=ImageDraw.Draw(contact)
        d.text((20,18),"BIOHEAL BOH NAD-PRIZCELL 50mL | 4 HISTORIC + 1 NEW PROVISIONAL",fill="#24363e")
        d.text((20,46),"INTERNAL QA, NOT RETAIL. Original rights, edition and circular MK still unverified.",fill="#af3c38")
        for i,b in enumerate(photos):
            x=20+(i%3)*455;y=80+(i//3)*462
            d.rounded_rectangle((x,y,x+440,y+430),radius=10,fill="white",outline="#d1d3d4",width=2)
            with Image.open(io.BytesIO(b)) as im:
                im=im.convert("RGB");im.thumbnail((400,375),Image.Resampling.LANCZOS)
                contact.paste(im,(x+(440-im.width)//2,y+10+(375-im.height)//2))
            d.text((x+12,y+397),f"FRAME {i+1} - {'NEW MERCHANT PHOTO' if i==4 else 'ARCHIVED'}",fill="#45515a")
        cp=OUT/"pending-25-open-jar-fifth-source-CONTACT-INTERNAL.jpg"
        contact.save(cp,format="JPEG",quality=91,optimize=True)
        m.update({"outcome":"NEW_SOURCE_CANDIDATE_ARCHIVED_NEEDS_VISUAL_QA",
           "fifth_internal_JPG_zip":str(zp.relative_to(ROOT)),
           "zip_sha256":sha(zp.read_bytes()),"contact":str(cp.relative_to(ROOT)),
           "source_photo_files":5,"five_independent_scenes_claimed":False,
           "candidate_not_sufficient_to_clear_original_1_2_near_duplicate":True})
    except Exception as e:
        m.update({"outcome":"SINGLE_SOURCE_HOLD_NO_REPEAT","error":type(e).__name__+": "+str(e)[:280],
                  "new_customer_image_count":0})
    (OUT/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"version":"v2964","outcome":m["outcome"],
        "five_candidate_photo_zip":bool(m.get("fifth_internal_JPG_zip")),"new_public_urls":0}))
if __name__=="__main__":main()
