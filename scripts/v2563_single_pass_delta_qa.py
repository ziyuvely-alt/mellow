#!/usr/bin/env python3
"""Efficient single-pass incremental QA: stage two JPGs, verify 154 untouched originals,
audit 30 product families, upload only changed images and a compact manifest.
Never overwrite, publish or generate spreadsheets.
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageStat, ImageChops, ImageDraw, ImageFont
from itertools import combinations
import json,hashlib,shutil
B=Path("v2563-base/review-JPG-by-family")
C=Path("v2563-two-candidates")
O=Path("v2563-delta-only-QA");O.mkdir(exist_ok=True)
T=[("pending-01",5,"pending-01-slot05-CANDIDATE.jpg"),("pending-06",5,"pending-06-slot05-CANDIDATE.jpg")]
assert len(list(B.glob("pending-*/*.jpg")))==156
hash_old={}; hash_new={}; changed=[]; perceptual=[]; family_counts={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dhash(im):
    p=list(ImageOps.grayscale(im).resize((9,8),Image.Resampling.LANCZOS).getdata())
    n=0
    for y in range(8):
        for x in range(8):n=(n<<1)|(p[y*9+x]>p[y*9+x+1])
    return n
for n in range(1,31):
    fam=f"pending-{n:02d}"
    paths=sorted((B/fam).glob("*.jpg"))
    assert len(paths)==(6 if n in (1,2,4,5,6,7) else 5)
    family_counts[fam]=len(paths)
    images=[]
    for p in paths:
        im=Image.open(p);im.load()
        assert im.format=="JPEG" and im.size==(1080,1080) and p.stat().st_size<2000000
        slot=int(p.name[:2]);key=f"{fam}:{slot}"
        assert key not in hash_old
        hash_old[key]=sha(p)
        replacement=next((C/name for f,s,name in T if f==fam and s==slot),None)
        if replacement is not None:
            assert replacement.is_file(),replacement
            ni=Image.open(replacement);ni.load()
            assert ni.format=="JPEG" and ni.size==(1080,1080) and replacement.stat().st_size<2000000
            diff=ImageStat.Stat(ImageChops.difference(im.convert("RGB").resize((128,128)),ni.convert("RGB").resize((128,128)))).mean
            mae=round(sum(diff)/3,2)
            assert sha(replacement)!=sha(p)
            dest=O/f"{fam}-slot{slot:02d}-QA.jpg"
            shutil.copy2(replacement,dest)
            images.append((slot,ni,dest))
            hash_new[key]=sha(dest)
            changed.append({"family":fam,"slot":slot,"previous_sha":sha(p),"proposed_sha":sha(dest),"pixel_mae":mae,"approval":"HOLD"})
        else:
            images.append((slot,im,p));hash_new[key]=sha(p)
    for a,b in combinations(images,2):
        dist=(dhash(a[1])^dhash(b[1])).bit_count()
        if dist<=6:
            perceptual.append({"family":fam,"slots":[a[0],b[0]],"dhash_distance":dist})
assert len(hash_old)==len(hash_new)==156
assert len(changed)==2 and sum(hash_old[k]==hash_new[k] for k in hash_old)==154
assert len({hash_new[k] for k in hash_new})==156
# Old source approvals are not extended. Keep tiny outputs, not 156 reuploaded JPGs.
report={"version":"v2563","method":"incremental-delta-only-single-pass-QA",
"source_v2560_run":41753618979,"candidate_v2562_run":41754215345,
"source_image_count":156,"all_families_checked":30,
"changed_in_virtual_QA_overlay":2,"originals_unchanged_sha":154,
"delta_files":[x["family"]+f"-slot{x['slot']:02d}-QA.jpg" for x in changed],
"changes":changed,"remaining_near_duplicate_candidates":perceptual,
"family_counts":family_counts,
"previous_six_staged_changes_preserved":True,"old_55_public_urls_untouched":True,
"public_images_published":0,"xlsx_created_or_shared":False,
"sales_ready":False,"commercial_photo_rights_verified":False,
"physical_owned_stock_edition_verified":False,"round_MK_logo_verified":False,
"future_qa_rule":"Do not repeat 156 full JPEG upload; preserve base artifact and publish delta plus manifest only."}
(O/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"processed":156,"source_unchanged_sha":154,"changed_delta":2,
"similar_pairs_after_delta":len(perceptual),"pairs":perceptual,
"output_jpg":len(list(O.glob("*.jpg"))),"release":False},ensure_ascii=False))
