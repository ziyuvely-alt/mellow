#!/usr/bin/env python3
"""v2560: Merge six previously staged, source-backed QA candidates into a separate
review-only 156-JPG corpus. Preserve 150 other photo bytes. Zero public URLs/XLSX.
IMPORTANT: scene diversity is not commercial license / exact edition approval.
"""
import json, hashlib, shutil
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont,ImageStat,ImageChops
from itertools import combinations

BASE=Path("v2560-baseline/review-JPG-by-family")
S=Path("v2560-staged")
OUT=Path("v2560-six-selective-QA-only-corpus")
DEST=OUT/"review-JPG-by-family"
assert BASE.is_dir() and len(list(BASE.glob("pending-*/*.jpg")))==156
shutil.copytree(BASE,DEST)
TARGETS=[
 ("pending-21",5,"goodal21/pending-21-slot05-package-photo-CANDIDATE.jpg"),
 ("pending-16",4,"drg16/pending16-04-original-70ml-jar-carton-CANDIDATE.jpg"),
 ("pending-15",5,"drg15/pending15-05-photo-plus-how-to-apply-CANDIDATE.jpg"),
 ("pending-26",5,"pixelpure26/pending26-05-verified-original-145ml-CANDIDATE.jpg"),
 ("pending-02",4,"missha-goodal/pending-02-slot04-real-photo-info-QA.jpg"),
 ("pending-19",5,"missha-goodal/pending-19-slot05-real-photo-info-QA.jpg")]
rows=[]
F=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",20)
for fam,slot,relative in TARGETS:
    source=S/relative
    assert source.is_file(),f"Missing candidate: {source}"
    src=Image.open(source);src.load()
    assert src.format=="JPEG" and src.size==(1080,1080) and source.stat().st_size<2_000_000
    old=list((DEST/fam).glob(f"{slot:02d}*.jpg"))
    assert len(old)==1,(fam,slot,old)
    oldp=old[0]
    orig=oldp.read_bytes()
    assert orig!=source.read_bytes(),(fam,slot,"candidate equals original")
    prior_img=Image.open(oldp).convert("RGB")
    oldp.unlink()
    dst=DEST/fam/f"{slot:02d}_v2560-REVIEW-ONLY.jpg"
    shutil.copy2(source,dst)
    d=ImageStat.Stat(ImageChops.difference(prior_img.resize((128,128)),src.convert("RGB").resize((128,128)))).mean
    mae=round(sum(d)/3,3)
    assert mae>8,(fam,slot,"candidate too close")
    rows.append({"family":fam,"slot":slot,"prior_file":oldp.name,"candidate":relative,
      "old_sha256":hashlib.sha256(orig).hexdigest(),"new_sha256":hashlib.sha256(dst.read_bytes()).hexdigest(),
      "pixel_mae":mae,"release":"HOLD_PHOTO_RIGHTS_STOCK_EDITION_MK_HUMAN_REVIEW"})
assert len(rows)==6 and len({(x["family"],x["slot"]) for x in rows})==6

all_before={p.parent.name+"/"+p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in BASE.glob("pending-*/*.jpg")}
all_after=list(DEST.glob("pending-*/*.jpg"))
assert len(all_after)==156
before_map={(p.parent.name,int(p.name[:2])):hashlib.sha256(p.read_bytes()).hexdigest() for p in BASE.glob("pending-*/*.jpg")}
after_map={(p.parent.name,int(p.name[:2])):hashlib.sha256(p.read_bytes()).hexdigest() for p in all_after}
changed=sorted([{"family":k[0],"slot":k[1]} for k in before_map if before_map[k]!=after_map[k]],key=lambda x:(x["family"],x["slot"]))
assert changed==sorted([{"family":f,"slot":n} for f,n,_ in TARGETS],key=lambda x:(x["family"],x["slot"])),changed
unchanged=sum(before_map[k]==after_map[k] for k in before_map)
assert unchanged==150

family_counts={}
exact_dup=[];dhash_alert=[]
def dhash(img):
    pix=list(ImageOps.grayscale(img).resize((9,8),Image.Resampling.LANCZOS).getdata())
    value=0
    for y in range(8):
        for x in range(8):
            value=(value<<1)|(pix[y*9+x]>pix[y*9+x+1])
    return value
for n in range(1,31):
    fam=f"pending-{n:02d}"
    photos=sorted((DEST/fam).glob("*.jpg"))
    count=6 if n in (1,2,4,5,6,7) else 5
    assert len(photos)==count,(fam,len(photos))
    family_counts[fam]=count
    hashes=[];phashes=[]
    for p in photos:
        img=Image.open(p);img.load()
        assert img.format=="JPEG" and img.size==(1080,1080) and p.stat().st_size<2_000_000
        hashes.append((p.name,hashlib.sha256(p.read_bytes()).hexdigest()))
        phashes.append((p.name,dhash(img)))
    for a,b in combinations(hashes,2):
        if a[1]==b[1]:exact_dup.append([fam,a[0],b[0]])
    for a,b in combinations(phashes,2):
        dist=(a[1]^b[1]).bit_count()
        if dist<=6:dhash_alert.append({"family":fam,"a":a[0],"b":b[0],"distance":dist})
assert not exact_dup,exact_dup
for r in rows:
    fam=r["family"];slot=r["slot"]
    r["post_merge_dhash_alerts"]=[x for x in dhash_alert if x["family"]==fam and (int(x["a"][:2])==slot or int(x["b"][:2])==slot)]
    if r["post_merge_dhash_alerts"]:
        r["release"]="QUARANTINE_SAME_FAMILY_PERCEPTUAL_SIMILARITY_PLUS_RIGHTS_STOCK_LOGO"

# Six before/after visual proofs, and six-family preview board.
board=Image.new("RGB",(1530,1040),"#f4f5f4")
d=ImageDraw.Draw(board)
for i,r in enumerate(rows):
    fam=r["family"];slot=r["slot"]
    original=[p for p in (BASE/fam).glob(f"{slot:02d}*.jpg")]
    updated=[p for p in (DEST/fam).glob(f"{slot:02d}*.jpg")]
    assert len(original)==len(updated)==1
    left=ImageOps.contain(Image.open(original[0]).convert("RGB"),(220,220))
    right=ImageOps.contain(Image.open(updated[0]).convert("RGB"),(220,220))
    col=i%3;row=i//3;x=col*510;y=row*520
    board.paste(left,(x+15+(220-left.width)//2,y+50+(220-left.height)//2))
    board.paste(right,(x+265+(220-right.width)//2,y+50+(220-right.height)//2))
    d.text((x+16,y+15),f"{fam} slot {slot} | old / QA proposal",fill="#222",font=F)
    d.text((x+20,y+286),f"Difference: {r['pixel_mae']}/255",fill="#333",font=F)
    d.text((x+20,y+320),"NO RELEASE | RIGHTS + STOCK HOLD",fill="#444",font=F)
board.save(OUT/"six-candidate-before-after.jpg","JPEG",quality=90,optimize=True)

report={"version":"v2560","base_run":41715911900,"base_images":156,
"source_candidate_runs":[41751173910,41752270122,41752451326,41752643604,41753049285],
"images_changed_in_SEPARATE_QA_COPY":len(rows),"other_images_preserved_sha_identical":unchanged,
"total_QA_images":156,"families":30,"family_counts":family_counts,"merge_changes":rows,
"exact_hash_duplicates":0,"perceptual_duplicate_candidates_total":len(dhash_alert),
"perceptual_candidates":dhash_alert,
"baseline_artifact_unchanged":True,"original_public_55_urls_modified":0,
"new_public_urls":0,"xlsx_created_or_shared":False,"sales_approved":False,
"commercial_photo_rights_verified":False,"stock_edition_confirmed":False,
"original_mk_logo_applied":False,
"NO_APPROVAL":"All six candidates remain draft pending human scene, photo rights, exact stock and logo checks."}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"updated_only_in_QA_copy":6,"source_sha_identical":unchanged,"total":156,"families":30,"similarity_alerts":len(dhash_alert),"target_warnings":sum(bool(r["post_merge_dhash_alerts"]) for r in rows),"released":False}))
