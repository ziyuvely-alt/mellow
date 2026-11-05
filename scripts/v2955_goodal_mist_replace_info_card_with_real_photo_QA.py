#!/usr/bin/env python3
"""Incremental correction of only Goodal 100ml QA source-frame #3; retain v2954 other ZIPs untouched."""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json, zipfile, io

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/"qa-review/v2954-three-family-five-original-JPG-byteexact-ZIPs-20261106/manifest.json"
OUT=ROOT/"qa-review/v2955-goodal-mist-third-slot-real-photo-correction-20261106"
REPLACEMENT="qa-review/v2779-five-photo-first-product-groups-QA/pending-20/04-source-archive-story-QA.jpg"
def sha(x):return hashlib.sha256(x).hexdigest()
def main():
    if OUT.exists():raise SystemExit("v2955 outputs already exist, no re-run")
    old=json.loads(OLD.read_text())
    orig=old["families"]["pending-20"]["source_frames"]
    if len(orig)!=5:raise SystemExit("not 5 prior source slots")
    if "03-source-archive-story-QA.jpg" not in orig[2]["source"]:
        raise SystemExit("Expected third info-only slot not where anticipated")
    newpaths=[x["source"] for x in orig]
    newpaths[2]=REPLACEMENT
    OUT.mkdir(parents=True)
    rows=[]
    for i,p in enumerate(newpaths):
        raw=(ROOT/p).read_bytes()
        with Image.open(io.BytesIO(raw)) as im:
            im.load()
            if im.format!="JPEG" or im.size!=(1080,1080) or len(raw)>=2000000:raise SystemExit("bad source JPG "+p)
        expected=orig[i].get("sha256") if i!=2 else None
        if expected and sha(raw)!=expected:raise SystemExit("baseline original byte mismatch "+p)
        rows.append({"slot":i+1,"source_path":p,"sha256":sha(raw),"bytes":len(raw),"source_type":"independent_existing_photo_not_infocard","raw_bytes":raw})
    if len(set(x["sha256"] for x in rows))!=5:raise SystemExit("exact duplicate JPGs")
    zippath=OUT/"pending-20-FIVE-PHOTO-SOURCES-NO-INFO-CARD-INTERNAL-QA.zip"
    with zipfile.ZipFile(zippath,"w") as z:
        for row in rows:
            zi=zipfile.ZipInfo(f"{row['slot']:02d}-{Path(row['source_path']).name}")
            zi.compress_type=zipfile.ZIP_STORED
            zi.external_attr=0o644<<16
            z.writestr(zi,row["raw_bytes"])
    with zipfile.ZipFile(zippath) as z:
        for row, member in zip(rows,z.namelist()):
            if sha(z.read(member))!=row["sha256"]:raise SystemExit("archive byte mismatch")
    canvas=Image.new("RGB",(1380,1050),(245,246,247))
    d=ImageDraw.Draw(canvas)
    d.text((20,18),"GOODAL 100mL | FIVE EXISTING PRODUCT PHOTO SCENES | v2955",fill=(23,40,45))
    d.text((20,48),"INTERNAL QA: no licensed commercial image approval, true original MK still unresolved",fill=(140,50,44))
    for row in rows:
        i=row["slot"]-1;x=20+(i%3)*455;y=85+(i//3)*465
        d.rounded_rectangle((x,y,x+440,y+438),radius=10,fill="white",outline=(202,205,207),width=2)
        with Image.open(io.BytesIO(row["raw_bytes"])) as im:
            im=im.convert("RGB");im.thumbnail((402,389))
            canvas.paste(im,(x+(440-im.width)//2,y+(389-im.height)//2+7))
        d.text((x+10,y+407),f"#{i+1}: exact original JPEG preserved",fill=(63,70,76))
    canvas.save(OUT/"pending-20-FIVE-PHOTO-SCENES-REVISED-CONTACT-INTERNAL.jpg",quality=91,optimize=True)
    result={
      "version":"v2955","parent":"v2954","project":"82 SKU / 41 families Shopee stock",
      "corrected_family":"pending-20","prior_fault":"v2954 Goodal mist slot 3 was English HOW TO USE info card, not source photograph",
      "prior_qa_zip_to_supersede":"qa-review/v2954-three-family-five-original-JPG-byteexact-ZIPs-20261106/pending-20-five-immutable-source-JPGs-INTERNAL-QA.zip",
      "prior_zip_not_deleted":True,"previous_approved_images_modified":0,"other_v2954_zips_modified":0,
      "replacement_from_existing_exact_product_photo":REPLACEMENT,
      "new_zip":"qa-review/v2955-goodal-mist-third-slot-real-photo-correction-20261106/"+zippath.name,
      "new_zip_sha256":sha(zippath.read_bytes()),"photo_count":5,
      "files":[{k:v for k,v in x.items() if k!="raw_bytes"} for x in rows],
      "technical_pass":True,
      "visual_gate":"PENDING_EXAMINE_NEW_CONTACT; names/photos do not license customer images",
      "sale_permission":False,"authentic_MK_png_validated":False,"physical_stock_edition_verified":False,
      "new_verified_public_urls":0,"old_public_urls_preserved":55,
      "action_after_visual":"Once contact is reviewed, retain FIVE PHOTO status if independent enough and verify usage/stock/logo gates; do not re-fetch known source"
    }
    (OUT/"manifest.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"version":"v2955","corrected_slot":3,"photo_count":5,"zip_bytes":zippath.stat().st_size,"sha256":result["new_zip_sha256"],"old_zip_preserved":True}))
if __name__=="__main__":main()
