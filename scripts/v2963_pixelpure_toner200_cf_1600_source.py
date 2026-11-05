#!/usr/bin/env python3
"""Try a single visibly distinct multi-bottle 200mL toner scene. Preserve old 4-photo ZIP; internal-only candidate."""
import io,json,zipfile,hashlib,urllib.request
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa-review/v2963-pixelpure-toner200-distinct-multibottle-scene-20261106"
PREV=ROOT/"qa-review/v2929-pixelpure-three-four-photo-pack-source-integrity-QA/manifest.json"
URL=("https://bb233c5e161f4bce733cb3df3dcd7423.cdn.bubble.io/cdn-cgi/image/"
     "w%3D1600%2Ch%3D1600%2Cf%3Djpeg%2Cdpr%3D1%2Cfit%3Dcontain/"
     "f1755044080189x354177331539262700/PG0659.jpg")
PAGE="https://kometglobal.com/service/1755044283174x486505495049011200"
def sha(b):return hashlib.sha256(b).hexdigest()
def dh(im):
    v=list(im.convert("L").resize((9,8),Image.Resampling.LANCZOS).getdata())
    return "".join(str(int(v[y*9+x]>v[y*9+x+1])) for y in range(8) for x in range(8))
def convert(b):
    with Image.open(io.BytesIO(b)) as im:
        im.load();sz=im.size;fmt=im.format
        if min(sz)<700:raise ValueError("LOW_NATIVE_RES "+str(sz))
        im=im.convert("RGB");im.thumbnail((1020,1020),Image.Resampling.LANCZOS)
        c=Image.new("RGB",(1080,1080),"white");c.paste(im,((1080-im.width)//2,(1080-im.height)//2))
        o=io.BytesIO();c.save(o,"JPEG",quality=91,optimize=True)
        if len(o.getvalue())>2_000_000:raise ValueError("JPG_NOT_UNDER_2MB")
        return o.getvalue(),sz,fmt
def main():
    if OUT.exists():raise RuntimeError("v2963 previously executed, never repeat")
    old=json.loads(PREV.read_text())
    fam=next(x for x in old["results"] if x["family"]=="pending-27")
    zip_path=ROOT/fam["archive_ZIP"]
    assert sha(zip_path.read_bytes())==fam["archive_ZIP_sha256"],"old zip hash mismatch"
    expect=[x["sha256"] for x in fam["source_records"]]
    sources={}
    with zipfile.ZipFile(zip_path) as z:
        for n in z.namelist():
            if n.lower().endswith(".jpg"):
                b=z.read(n)
                if sha(b) in expect:sources[sha(b)]=b
    assert len(sources)==4
    imgs=[sources[x] for x in expect]
    hs=[]
    for b in imgs:
        with Image.open(io.BytesIO(b)) as im:im.load();hs.append(dh(im))
    OUT.mkdir(parents=True)
    m={"version":"v2963","prior":"v2962","family":"pending-27",
       "product":"PIXELPURE Soothing Ampoule Toner 200mL",
       "source_page":PAGE,"source_url":URL,
       "source_type":"third-party commercial catalog / KometGlobal; not manufacturer approval",
       "expected_visual":"multiple pink 200mL bottles on beige shelf, visibly different from old 4",
       "previous_QA_source_zip":fam["archive_ZIP"],
       "prior_11_published_families_preserved":True,"prior_55_verified_urls_preserved":True,
       "new_sale_approved":False,"rights_verified":False,"physical_edition_verified":False,
       "authentic_MK_verified":False,"new_public_url_count":0,
       "attempted_url_count":1}
    try:
        req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"})
        with urllib.request.urlopen(req,timeout=17) as res:raw=res.read(5_000_000)
        if len(raw)<15000 or len(raw)>=5_000_000:raise ValueError("SOURCE_BYTES_INVALID "+str(len(raw)))
        with Image.open(io.BytesIO(raw)) as im:im.load();native=list(im.size);fmt=im.format
        m.update({"native_dimensions":native,"native_sha256":sha(raw),"decoded_format":fmt})
        qa,sz,fmt=convert(raw)
        with Image.open(io.BytesIO(qa)) as im:hd=dh(im)
        diffs=[sum(x!=y for x,y in zip(hd,v)) for v in hs]
        m["hamming_to_old_four"]=diffs
        if min(diffs)<=8:raise ValueError("SCENE_TOO_SIMILAR_TO_OLDER_PHOTOS")
        ext={"JPEG":".jpg","PNG":".png","WEBP":".webp"}.get(fmt)
        if not ext:raise ValueError("UNSUPPORTED_NATIVE_FORMAT "+str(fmt))
        source_file=OUT/("pending-27-new-multibottle-source-original"+ext)
        source_file.write_bytes(raw)
        qa_file=OUT/"pending-27-new-fifth-source-1080-INTERNAL-QA.jpg"
        qa_file.write_bytes(qa)
        allimgs=imgs+[qa]
        zp=OUT/"pending-27-five-photos-inc-1-new-KometGlobal-INTERNAL-ONLY.zip"
        with zipfile.ZipFile(zp,"w") as z:
            for i,b in enumerate(allimgs):
                entry=zipfile.ZipInfo(f"{i+1:02d}-PIXELPURE-Toner200-photo-{'NEW' if i==4 else 'old'}-QA.jpg")
                entry.compress_type=zipfile.ZIP_STORED;entry.external_attr=0o644<<16;z.writestr(entry,b)
        with zipfile.ZipFile(zp) as z:
            assert all(sha(z.read(n))==sha(b) for n,b in zip(z.namelist(),allimgs))
        sheet=Image.new("RGB",(1380,1050),"#f2f5f6");d=ImageDraw.Draw(sheet)
        d.text((20,16),"PIXELPURE SOOTHING AMPOULE TONER 200mL | 4 OLD + 1 NEW PHOTO CANDIDATE",fill="#203139")
        d.text((20,44),"INTERNAL QA ONLY: native photo, exact stock, legal reuse, MK original all pending",fill="#9f3b32")
        for i,b in enumerate(allimgs):
            x=20+(i%3)*455;y=80+(i//3)*462
            d.rounded_rectangle((x,y,x+440,y+432),radius=10,fill="white",outline="#c5cacf",width=2)
            with Image.open(io.BytesIO(b)) as im:
                im=im.convert("RGB");im.thumbnail((397,380),Image.Resampling.LANCZOS)
                sheet.paste(im,(x+(440-im.width)//2,y+8+(380-im.height)//2))
            d.text((x+10,y+400),f"FRAME {i+1} {'NEW source not licensed' if i==4 else 'old source photo'}",fill="#46535a")
        contact=OUT/"pending-27-fifth-photo-source-COMPARISON-INTERNAL.jpg"
        sheet.save(contact,quality=92,optimize=True)
        m.update({"status":"NEW_DISTINCT_SOURCE_PHOTO_STAGED_VISUAL_QA_PENDING",
                  "native_reference":str(source_file.relative_to(ROOT)),
                  "new_JPG":str(qa_file.relative_to(ROOT)),"new_JPG_sha256":sha(qa),
                  "five_photo_zip":str(zp.relative_to(ROOT)),
                  "five_photo_zip_sha256":sha(zp.read_bytes()),
                  "contact":str(contact.relative_to(ROOT))})
    except Exception as e:
        m.update({"status":"SINGLE_CANDIDATE_ON_HOLD_CONTINUE_OTHERS",
            "error":type(e).__name__+" "+str(e)[:250],
            "new_sale_approved":False,"no_repeat_same_failed_url":True})
    (OUT/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"version":"v2963","status":m["status"],"new_candidate":bool(m.get("new_JPG")),
                      "new_verified_public_urls":0}))
if __name__=="__main__":main()
