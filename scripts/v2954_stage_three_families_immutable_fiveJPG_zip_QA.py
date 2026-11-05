#!/usr/bin/env python3
"""Preserve original image bytes; construct incremental internal QA product-first ZIPs.
No public image paths or sale approval are ever written by this script.
"""
import hashlib, io, json, zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa-review/v2954-three-family-five-original-JPG-byteexact-ZIPs-20261106"
V2952=ROOT/"qa-review/v2952-real-JPG-local-repair-and-two-family-source-QA-20261106/manifest.json"
INPUTS={
 "pending-23": [
 "qa-review/v2776-four-source-photo-first-fiveframe-QA/pending-23/01-true-product-photo-alpha-QA.jpg",
 *[f"qa-review/v2776-four-source-photo-first-fiveframe-QA/pending-23/{i:02d}-original-lifestyle-or-detail-QA.jpg" for i in range(2,6)]],
 "pending-28": [
 "qa-review/v2775-four-photo-first-fiveframe-product-QA/pending-28/01-real-product-cutout-hero-QA.jpg",
 *[f"qa-review/v2775-four-photo-first-fiveframe-product-QA/pending-28/{i:02d}-source-photo-story-QA.jpg" for i in range(2,6)]],
 "pending-20": [
 "qa-review/v2779-five-photo-first-product-groups-QA/pending-20/01-prior-verified-real-alpha-hero-QA.jpg",
 "qa-review/v2779-five-photo-first-product-groups-QA/pending-20/02-source-archive-story-QA.jpg",
 "qa-review/v2779-five-photo-first-product-groups-QA/pending-20/03-source-archive-story-QA.jpg",
 "qa-review/v2939-goodal-100ml-live-citrus-source-QA/pending-20/01-CITRUS_STILL-internal-1080.jpg",
 "qa-review/v2939-goodal-100ml-live-citrus-source-QA/pending-20/02-CITRUS_WATER-internal-1080.jpg"]
}
LABELS={
 "pending-23":"OBgE Pore Zero Oil Control Sun Cream 50 mL",
 "pending-28":"PIXEL PURE Glow Cleansing Serum Pads 70 pads / 210 mL",
 "pending-20":"GOODAL Vita-C Serum Mist 25AD 100 mL"}
EXPLICIT_HOLDS={
 "pending-23":["owned stock exact edition", "commercial reuse rights", "genuine private MK logo", "independent customer-facing visual QA"],
 "pending-28":["owned stock exact edition", "commercial reuse rights", "genuine private MK logo", "independent customer-facing visual QA"],
 "pending-20":["owned stock exact 25AD edition", "commercial reuse rights", "genuine private MK logo", "independent customer-facing visual QA", "frame 5 is cropped liquid action scene: detail only"]
}
def sha(b):return hashlib.sha256(b).hexdigest()
def audit(filepath):
    by=filepath.read_bytes()
    with Image.open(io.BytesIO(by)) as im:
        im.load();dims=list(im.size);fmt=im.format
        gray=im.convert("L").resize((8,8),Image.Resampling.LANCZOS)
        bits=list(gray.getdata()); avg=sum(bits)/64
        ahash="".join("1" if v>=avg else "0" for v in bits)
    return by,dict(source=str(filepath.relative_to(ROOT)),bytes=len(by),sha256=sha(by),size=dims,format=fmt,ahash=ahash)
def contact(files,dest,label):
    TILE_W,TILE_H=440,430
    canvas=Image.new("RGB",(1380,1050),(245,246,247))
    d=ImageDraw.Draw(canvas)
    d.text((22,16),label,fill=(29,40,45))
    d.text((22,44),"SOURCE PHOTOS ONLY | INTERNAL QA, NOT RETAIL APPROVED",fill=(155,46,41))
    for i,(pth,_) in enumerate(files):
        x=22+(i%3)*455;y=85+(i//3)*468
        d.rounded_rectangle((x,y,x+440,y+438),radius=10,fill="white",outline=(206,207,209),width=2)
        with Image.open(pth) as im:
            im=im.convert("RGB");im.thumbnail((400,386),Image.Resampling.LANCZOS)
            canvas.paste(im,(x+(440-im.width)//2,y+12+(386-im.height)//2))
        d.text((x+12,y+400),f"FRAME {i+1} original bytes | SHA-256 in manifest",fill=(77,82,87))
    d.text((22,1016),"No new photo generation. Original files copied without alteration into ZIP. Source license / exact stock / MK open.",fill=(84,88,92))
    canvas.save(dest,quality=91,optimize=True)
def main():
    if OUT.exists():raise SystemExit("Refuse duplicate v2954; keep existing files.")
    old=json.loads(V2952.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True)
    result={"version":"v2954","prior_checkpoint":"v2953","data_provenance":"existing actual JPG bytes on QA archive branch",
      "prior_published_families":11,"prior_verified_url_count":55,
      "old_image_bytes_modified":0,"new_public_jpg":0,"new_render_url_verified":0,
      "new_selling_approvals":0,"new_photo_created":0,"new_qa_contact_sheets":3,
      "qa_zip_original_byte_preserved":True,"families":{}}
    for fam,paths in INPUTS.items():
        inputs=[ROOT/p for p in paths]
        meta=[];files=[]
        for p in inputs:
            by,item=audit(p)
            if item["format"]!="JPEG" or item["size"]!=[1080,1080] or item["bytes"]>=2_000_000:
                raise SystemExit(f"Invalid original frame: {item}")
            files.append((p,by));meta.append(item)
        if fam in ("pending-23","pending-28"):
            expected={v["path"]:v["sha256"] for v in old["families"][fam]["frames"]}
            for row in meta:
                if expected.get(row["source"])!=row["sha256"]:
                    raise SystemExit(f"v2952 baseline digest disagreement: {row['source']}")
        hashes=[x["sha256"] for x in meta]
        if len(set(hashes))!=5:raise SystemExit(f"Duplicate exact JPG data: {fam}")
        similar=[]
        for i in range(5):
            for j in range(i+1,5):
                dist=sum(a!=b for a,b in zip(meta[i]["ahash"],meta[j]["ahash"]))
                if dist<=6: similar.append({"frames":[i+1,j+1],"aHash_hamming":dist})
        path=OUT/f"{fam}-five-immutable-source-JPGs-INTERNAL-QA.zip"
        with zipfile.ZipFile(path,"w") as z:
            for i,(p,by) in enumerate(files,1):
                zi=zipfile.ZipInfo(filename=f"{i:02d}-{p.name}")
                zi.compress_type=zipfile.ZIP_STORED
                zi.external_attr=0o644<<16
                z.writestr(zi,by)
        with zipfile.ZipFile(path) as z:
            for i,(_,by) in enumerate(files,1):
                assert sha(z.read(z.namelist()[i-1]))==sha(by),"ZIP failed original-byte preservation"
        cp=OUT/f"{fam}-five-scenes-CONTACT-INTERNAL.jpg"
        contact(files,cp,LABELS[fam])
        result["families"][fam]={"product":LABELS[fam],"source_original_photos":5,
          "technical_file_checks_pass":True,"byte_exact_zip":str(path.relative_to(ROOT)),
          "zip_sha256":sha(path.read_bytes()),"zip_bytes":path.stat().st_size,
          "contact_sheet":str(cp.relative_to(ROOT)),
          "source_frames":meta,"candidate_near_duplicates_perceptual":similar,
          "internal_QA_stage":"FIVE_SOURCE_JPG_ARCHIVE_NOT_LICENSED_OR_RETAIL_APPROVED",
          "photo_license_verified":False,"physical_stock_edition_verified":False,
          "private_MK_original_verified":False,"sale_approved":False,
          "remaining_gates":EXPLICIT_HOLDS[fam]}
    (OUT/"manifest.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"version":"v2954","staged_families":list(result["families"]),"photo_sources_copied":15,
      "zips_written":3,"contacts_written":3,"near_duplicate_candidates":{k:len(v["candidate_near_duplicates_perceptual"]) for k,v in result["families"].items()},
      "sale_approvals":0},ensure_ascii=False))
if __name__=="__main__":main()
