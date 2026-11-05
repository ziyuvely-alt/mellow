#!/usr/bin/env python3
"""v2854: Correct two 5-frame QA review bundles solely from immutable earlier JPGs.

Never redo segmentation, generate a fictitious product photo, alter original JPG,
or publish URLs. Record hashes, real photo count, flawed predecessor quarantine
and exact outstanding release blockers.
"""
from pathlib import Path
from hashlib import sha256
from PIL import Image, ImageDraw, ImageFont
import json, shutil

R=Path("qa-review")
OUT=R/"v2854-missha30-obge300-recovered-existing-artwork-QA"
assert not OUT.exists()
OUT.mkdir(parents=True)
def h(p):return sha256(p.read_bytes()).hexdigest()
def J(p):
    assert p.is_file(),str(p)
    with Image.open(p) as im:
        im.load()
        assert im.format=="JPEG" and im.size==(1080,1080),(p,im.format,im.size)
    assert p.stat().st_size<2_000_000,str(p)

missha_manifest=json.loads((R/"v2801-missha-pdrn-serum-30ml-real-single-bottle-alpha-and-five-frame-QA"/"manifest.json").read_text())
obge_manifest=json.loads((R/"v2670-obge-300ml-distinct-official-photo-qa"/"manifest.json").read_text())
old_obge=json.loads((R/"v2722-thirty-family-file-backed-cutout-queue"/"manifest.json").read_text())
obge_row=next(x for x in old_obge["source_status_by_family"] if x["family"]=="pending-22")
assert obge_row["selected_QA_pair"]["folder"]=="v2712-3-failed-cutouts-high-quality-recovery"
assert missha_manifest["five_real_JPG_QA_frames_saved"]==5

sources={
"pending-13":{
 "product":"MISSHA Camellia PDRN + NAD+ Firming Repair Serum 30mL",
 "slots":[
  {"src":"v2801-missha-pdrn-serum-30ml-real-single-bottle-alpha-and-five-frame-QA/01-final-QA-real-single-serum-photo.jpg","role":"real-single-bottle-hero","expected":missha_manifest["5_frame_set"][0]["sha256"]},
  *[{"src":"v2801-missha-pdrn-serum-30ml-real-single-bottle-alpha-and-five-frame-QA/"+rec["file"],
       "role":"previous-original-photo-or-information","expected":rec["sha256"]}
    for rec in missha_manifest["5_frame_set"][1:]]
 ],
 "rejected":[
  {"source":"v2839 failed Actions run","reason":"incorrectly fixed reference image dimensions to 500x500"},
  {"source":"v2840 failed Actions run","reason":"image processing succeeded but git rebase lacked user identity"},
  {"source":"v2756 alternative image","reason":"red decorative background artifact remained in foreground alpha"}],
 "visual_hold":["small decoration residue visible beside serum dropper cap in v2801 hero; do not call clean approved cutout",
  "model/lifestyle image photo rights and exact retail claims not confirmed",
  "owned SKU edition and authorized MK logo not independently verified"]
},
"pending-22":{
 "product":"OBgE Max Waterful Sun Cream 300mL",
 "slots":[
  {"src":"v2712-3-failed-cutouts-high-quality-recovery/pending-22/01-full-product-high-quality-cutout-1080-QA.jpg",
   "role":"full-bottle-no-cut-base-photo-hero","expected":obge_row["selected_QA_pair"]["jpg_sha256"]},
  *[{"src":"v2670-obge-300ml-distinct-official-photo-qa/"+rec["file"],
      "role":"official-distinct-packshot" if rec["frame"]==2 else "existing-factual-information",
      "expected":rec["sha256"]}
    for rec in obge_manifest["frames"][1:]]
 ],
 "rejected":[
  {"source":"v2670 first image","reason":"black or transparent-placeholder background visible, unsuitable for sales hero"},
  {"source":"v2711 early alpha JPG","reason":"bottle base cut off in first segmentation preview"}],
 "visual_hold":["v2712 pump shadow edge needs close human review; no new segmentation performed",
 "v2670 2nd 600px native source is a beige product photo, not native 1080",
 "only 2 different real-product photo slots; 3 factual information frames are not distinct real photos",
 "source copyright/reuse rights, exact stock label and MK logo unverified"]
}
}
result={
 "version":"v2854","baseline":"v2853",
 "purpose":"Recovered exact old QA source assets for 30mL serum and 300mL sunscreen without re-rendering",
 "new_segmentation_runs":0,"new_real_photo_downloads":0,"old_11_approved_families_unchanged":True,
 "old_55_published_URLs_unchanged":True,"source_originals_modified":False,
 "commercial_photo_rights_verified":False,"actual_owned_stock_editions_verified":False,
 "authentic_MK_logo_verified":False,"new_sale_approvals":0,"final_xlsx_shared":False,
 "families":[]}
fontname="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
fontbold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False:ImageFont.truetype(fontbold if b else fontname,n)
for family,info in sources.items():
    sub=OUT/family;sub.mkdir()
    m={"family":family,"product":info["product"],"photo_reuse_mode":"BYTE_EXACT_COPY_FROM_PRESERVED_QA",
       "rejected_predecessors":info["rejected"],"visual_hold":info["visual_hold"],
       "image_revision_required":False,"human_sales_QA":"HOLD","slots":[]}
    source_shas={}
    for i,row in enumerate(info["slots"],1):
        src=R/row["src"]
        J(src)
        source_shas[str(src)]=h(src)
        assert h(src)==row["expected"],(src,h(src),row["expected"])
        dest=sub/(f"{i:02d}-REUSED-PHOTO-QA.jpg")
        shutil.copyfile(src,dest)
        J(dest)
        assert h(dest)==h(src)
        m["slots"].append({"slot":i,"role":row["role"],"source":str(src),"file":str(dest.relative_to(OUT)),
          "sha256":h(dest),"source_bytes_identical":True,"jpg_bytes":dest.stat().st_size,
          "verified_1080_square_under_2MB":True})
    # no loss, no overwritten or regenerated source
    for p,d in source_shas.items():assert h(Path(p))==d
    digests=[x["sha256"] for x in m["slots"]]
    m["distinct_file_sha256_count"]=len(set(digests))
    assert len(digests)==5 and len(set(digests))==5
    board=Image.new("RGB",(1600,435),"#f4f1f0")
    d=ImageDraw.Draw(board)
    d.text((15,14),info["product"]+" | 5 existing files | technical QA only",font=ft(21,True),fill="#373037")
    for idx,slot in enumerate(m["slots"]):
        with Image.open(OUT/slot["file"]) as im:
            thumb=im.resize((302,302),Image.Resampling.LANCZOS)
            board.paste(thumb,(14+idx*318,59))
        d.text((20+idx*318,367),str(idx+1).zfill(2)+"  "+slot["role"][:24],font=ft(15),fill="#60545e")
    board.save(sub/"source-five-slot-comparison-QA.jpg","JPEG",quality=88,optimize=True)
    m["commercial_release"]="HOLD_RIGHTS_STOCK_EDITION_MK_VISUAL"
    (sub/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
    result["families"].append({"id":family,"copied_verified_JPGs":5,"sha_unique":5,
      "source_manifest":str(sub/"manifest.json"),"retail_approved":False})
(result_path:=OUT/"manifest.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2854","families":result["families"],"new_segmentation":0,
  "published":0},ensure_ascii=False))
