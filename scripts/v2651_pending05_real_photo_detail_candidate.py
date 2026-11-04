#!/usr/bin/env python3
"""v2651: product-photo-derived QA-only alternative for duplicated CLIO Founwear frame.
Historical source is not v2647: do not modify or publish retail files.
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageEnhance, ImageStat, ImageFilter
import hashlib,json,math,shutil
ROOT=Path("source/photos/review-JPG-by-family")
OUT=Path("v2651-pending05-actual-image-candidate")
OUT.mkdir(exist_ok=True)
with open("source/previous-review/review.json") as fp:
    previous=json.load(fp)
assert previous["version"]=="v2650" and previous["pair"]["left"]["family"]=="pending-05"
fam="pending-05"
rows=sorted((ROOT/fam).glob("*.jpg"))
assert len(rows)==6
slot={int(p.name[:2]):p for p in rows}
assert 1 in slot and 5 in slot
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def dhash(img):
    p=list(ImageOps.grayscale(img).resize((9,8)).getdata())
    return sum((1<<(y*8+x)) for y in range(8) for x in range(8) if p[y*9+x]>p[y*9+x+1])
def distance(a,b):return (dhash(a)^dhash(b)).bit_count()
with Image.open(slot[1]) as im: hero=ImageOps.exif_transpose(im).convert("RGB")
with Image.open(slot[5]) as im: base=ImageOps.exif_transpose(im).convert("RGB")
assert hero.size==base.size==(1080,1080)
candidate_sets=[]
# Crops derived only from genuine existing slot05 pixels. No new typography/claims, packaging, swatches, or logos.
# Three non-overzoomed source selections; attention determined by edge/detail & difference from slot01.
for fraction in (0.76,0.68):
    side=int(1080*fraction)
    anchors={"center":(540,540),"top-left":(side//2,side//2),
             "top-right":(1080-side//2,side//2),
             "bottom-left":(side//2,1080-side//2),
             "bottom-right":(1080-side//2,1080-side//2)}
    for anchor,(cx,cy) in anchors.items():
        box=(cx-side//2,cy-side//2,cx-side//2+side,cy-side//2+side)
        crop=base.crop(box).resize((1080,1080),Image.Resampling.LANCZOS)
        # Surface detail measured without any product identity claims.
        edge=ImageStat.Stat(crop.filter(ImageFilter.FIND_EDGES).convert("L")).stddev[0]
        color=ImageStat.Stat(crop.convert("L")).stddev[0]
        separation=distance(hero,crop)
        score=separation+min(edge/6,4)+min(color/18,3)
        candidate_sets.append({"crop":crop,"fraction":fraction,"anchor":anchor,
                               "edge_std":round(edge,3),"gray_std":round(color,3),
                               "distance":separation,"score":round(score,3)})
chosen=max(candidate_sets,key=lambda c:(c["score"],c["distance"]))
result_path=OUT/"pending-05-slot05-distinct-product-detail-CANDIDATE-QA-ONLY.jpg"
chosen["crop"].save(result_path,quality=91,optimize=True,subsampling=0)
assert result_path.stat().st_size<2_000_000
with Image.open(result_path) as chk:
    assert chk.format=="JPEG" and chk.size==(1080,1080)
    actual=distance(hero,chk.convert("RGB"))
sheet=Image.new("RGB",(2350,1050),"#eef0f3");draw=ImageDraw.Draw(sheet)
for i,(im,title) in enumerate([(hero,"01 original hero"),(base,"05 original duplicate"),(chosen["crop"],"05 NEW detail crop (QA only)")]):
    view=im.resize((760,760),Image.Resampling.LANCZOS)
    sheet.paste(view,(15+i*780,100))
    draw.text((15+i*780,55),title,fill="#111111")
draw.text((15,910),"HISTORICAL PHOTO CROPS ONLY - SKU / RIGHTS / LATEST v2647 VERIFY BEFORE RETAIL",fill="#111111")
sheet.save(OUT/"pending-05-before-after-contact-sheet.jpg",quality=85,optimize=True)
report={
  "version":"v2651","family":fam,"source_archive":"v2593 historical 156 JPEG archive (not v2647)",
  "baseline":"v2650 actual pair review", "original_frame01_sha256":sha(slot[1]),
  "original_frame05_sha256":sha(slot[5]),
  "new_candidate_sha256":sha(result_path),"new_candidate_file":result_path.name,
  "candidate_crop_from":"historical frame05 only", "crop_fraction":chosen["fraction"],
  "crop_anchor":chosen["anchor"], "original_01_vs_05_dhash_distance":distance(hero,base),
  "candidate_01_vs_05_dhash_distance":actual,
  "candidate_resolution":[1080,1080],"candidate_bytes":result_path.stat().st_size,
  "candidate_distinct_threshold_passed":actual>=12,
  "no_gen_ai_synthetic_photo":True,
  "no_new_unverified_product_claim":True,
  "retail_ready":False,
  "pending":["Product identity and stock edition manual review","Visual QA of crop content and useful product focus",
             "Source photo commercial permissions", "Must compare latest v2647 current frame 01/05"],
  "preserve":{"legacy_55_public_urls":True,"approved_11_families":True,"latest_v2647_unmodified":True},
  "no_xlsx":True
}
(OUT/"result.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"family":fam,"original_dhash":report["original_01_vs_05_dhash_distance"],
                  "candidate_dhash":actual,"crop":chosen["anchor"],
                  "crop_fraction":chosen["fraction"],
                  "technical_candidate_pass":report["candidate_distinct_threshold_passed"],
                  "candidate_bytes":result_path.stat().st_size,"published":0}))
