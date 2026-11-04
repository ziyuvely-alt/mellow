#!/usr/bin/env python3
"""Independent technical QA of archived v2593 original (not an approval of v2647).
No retail files modified; all output is a report in a new versioned directory.
"""
from pathlib import Path
import hashlib, json, csv, itertools, collections
from PIL import Image, ImageOps
SRC=Path("source/latest/review-JPG-by-family")
OUT=Path("v2649-historical-photo-audit")
OUT.mkdir(exist_ok=True)
EXCLUDE={("pending-07",3),("pending-09",2),("pending-27",5),("pending-28",2),
         ("pending-29",1),("pending-30",1)}
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def dhash(im):
    im=ImageOps.grayscale(im).resize((9,8))
    px=list(im.getdata())
    return sum((1 << (y*8+x)) for y in range(8) for x in range(8) if px[y*9+x]>px[y*9+x+1])
def hd(a,b):
    return (a^b).bit_count()
rows=[]
for p in sorted(SRC.glob("*/*.jpg")):
    fam=p.parent.name
    slot=int(p.name[:2])
    with Image.open(p) as im:
        im.load()
        fmt=im.format
        dims=list(im.size)
        ph=dhash(im)
    rows.append(dict(family=fam,slot=slot,name=p.name,size=p.stat().st_size,
                     sha256=digest(p),dhash=ph,format=fmt,dimensions=dims,
                     compliant=(fmt=="JPEG" and dims==[1080,1080] and p.stat().st_size<2_000_000),
                     superseded_by_later_review=(fam,slot) in EXCLUDE))
assert len(rows)==156, len(rows)
counts=collections.Counter(r["family"] for r in rows)
assert len(counts)==30 and all(counts[f"pending-{i:02d}"]==(6 if i in (1,2,4,5,6,7) else 5) for i in range(1,31)), counts
dups=[]
near=[]
for a,b in itertools.combinations(rows,2):
    if a["sha256"]==b["sha256"]:
        dups.append((a,b))
    elif a["family"]==b["family"] and hd(a["dhash"],b["dhash"])<=5:
        near.append((a,b,hd(a["dhash"],b["dhash"])))
def ref(r):
    return {"family":r["family"],"slot":r["slot"],"name":r["name"],
            "superseded":r["superseded_by_later_review"]}
result={
    "version":"v2649","source":"v2593 physical archive from GitHub Actions run 41764831639",
    "source_is_historical_not_latest_v2647":True,
    "families":len(counts),"jpg_count":len(rows),"technical_failures":[ref(r) for r in rows if not r["compliant"]],
    "exact_binary_duplicates":[{"a":ref(a),"b":ref(b)} for a,b in dups],
    "same_family_close_dhash":[{"a":ref(a),"b":ref(b),"hamming":d} for a,b,d in near],
    "known_later_changed_frames_excluded_from_new_repair_queue":sorted([{"family":f,"slot":s} for f,s in EXCLUDE],key=lambda z:(z["family"],z["slot"])),
    "do_not_publish":True,
    "human_visual_review_needed":True,
    "commercial_photo_rights_not_inferred":True,
    "latest_v2647_156_JPG_not_in_this_archive":True
}
(OUT/"audit.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
with (OUT/"technical-inventory.csv").open("w",newline="") as fp:
    w=csv.DictWriter(fp,fieldnames=["family","slot","name","size","sha256","format","dimensions","compliant","superseded_by_later_review"])
    w.writeheader()
    for r in rows:
        w.writerow({k:(json.dumps(r[k]) if k=="dimensions" else r[k]) for k in w.fieldnames})
print(json.dumps({"photos_examined":len(rows),"families":len(counts),
                  "technical_failures":len(result["technical_failures"]),
                  "duplicate_pairs":len(dups),"near_pairs":len(near),
                  "excluded_reworked_slots":len(EXCLUDE)},ensure_ascii=False))
