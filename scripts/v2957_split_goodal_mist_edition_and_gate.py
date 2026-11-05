#!/usr/bin/env python3
"""Manual-label-informed immutable source split. Never promotes to sale nor modifies original JPGs."""
from pathlib import Path
import json, io, hashlib, zipfile, subprocess
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
PREV=ROOT/"qa-review/v2955-goodal-mist-third-slot-real-photo-correction-20261106/manifest.json"
OUT=ROOT/"qa-review/v2957-goodal-25AD-label-generation-split-and-hard-publish-gate-20261106"
BASELINE={1:"GEN_A_SERUM_MIST_NIACINAMIDE_HYALURONIC_ACID",
          2:"GEN_A_SERUM_MIST_NIACINAMIDE_HYALURONIC_ACID",
          3:"GEN_A_SERUM_MIST_NIACINAMIDE_HYALURONIC_ACID",
          4:"GEN_B_DARK_SPOT_CARE_SERUM_MIST",
          5:"GEN_B_DARK_SPOT_CARE_SERUM_MIST"}
def digest(b):return hashlib.sha256(b).hexdigest()
def read_actual(f):
    path=ROOT/f["source_path"]
    b=path.read_bytes()
    assert digest(b)==f["sha256"],"Never repackage changed source bytes: "+str(path)
    with Image.open(io.BytesIO(b)) as im:
        im.load(); assert im.format=="JPEG" and im.size==(1080,1080) and len(b)<2_000_000, "bad JPG"
    return b
def group_frames(files):
    grouped={}
    for f in files:
        label=BASELINE[f["slot"]]
        grouped.setdefault(label,[]).append(f)
    return grouped
def issue_gate(grouped,pack_shade_verified,photo_rights,authentic_mk):
    if len(grouped)!=1: return "REJECT_MULTIPLE_FRONT_LABEL_PATTERNS"
    if not pack_shade_verified: return "REJECT_EXACT_PHYSICAL_STOCK_GENERATION_UNVERIFIED"
    if not photo_rights: return "REJECT_PHOTO_LICENSE_UNVERIFIED"
    if not authentic_mk: return "REJECT_AUTHENTIC_MK_UNVERIFIED"
    if sum(map(len,grouped.values()))<5: return "REJECT_FIVE_INDEPENDENT_PRODUCT_SCENES_NOT_PROVEN"
    return "STILL_NEEDS_CUSTOMER_JPG_INDEPENDENT_VISUAL_APPROVAL_AND_ANONYMOUS_DEPLOY_HASH"
def contact(grouped,by_slot):
    W,H=1400,1060; canv=Image.new("RGB",(W,H),"#f4f6f7"); d=ImageDraw.Draw(canv)
    d.text((22,18),"GOODAL VITA-C SERUM MIST 100mL | FRONT LABEL GENERATION SPLIT",fill="#1d2c36")
    d.text((22,43),"INTERNAL QA ONLY | observed labels, not manufacturer-confirmed generation names",fill="#af3c34")
    pairs=[(f,BASELINE[f["slot"]]) for f in sorted(sum(grouped.values(),[]),key=lambda x:x["slot"])]
    for n,(f,label) in enumerate(pairs):
        x=20+(n%3)*455;y=85+(n//3)*465
        d.rounded_rectangle((x,y,x+440,y+435),radius=9,fill="white",outline="#bec4c7",width=2)
        with Image.open(io.BytesIO(by_slot[f["slot"]])) as im:
            im=im.convert("RGB");im.thumbnail((395,365),Image.Resampling.LANCZOS)
            canv.paste(im,(x+(440-im.width)//2,y+10+(365-im.height)//2))
        d.text((x+12,y+387),"PHOTO "+str(f["slot"])+("  |  LABEL A" if "GEN_A" in label else "  |  LABEL B"),fill="#28343b")
        d.text((x+12,y+411),"DIFFERENT FRONT LABEL; DO NOT MIX",fill="#9b3b2c")
    d.text((20,1020),"A: 3 files (front images 1 & 2 similar), B: 2 files (600x800 native). Neither verified as 25AD physical unit.",fill="#4d555b")
    canv.save(OUT/"five-frame-two-label-generations-CONTACT-INTERNAL.jpg",quality=93,optimize=True)
def main():
    if OUT.exists():raise RuntimeError("Do not repeat existing v2957; resume from its manifest")
    prev=json.loads(PREV.read_text())
    fs=prev["files"]
    if len(fs)!=5 or set(f["slot"] for f in fs)!={1,2,3,4,5}:raise RuntimeError("unexpected input roster")
    files_by_slot={f["slot"]:read_actual(f) for f in fs}
    groups=group_frames(fs)
    # Assertions deliberately fail when a future operator tries to treat mixed edition images as sale-ready.
    mixed_reject=issue_gate(groups,False,False,False)
    assert mixed_reject=="REJECT_MULTIPLE_FRONT_LABEL_PATTERNS"
    OUT.mkdir(parents=True)
    packages={}
    for label,arr in groups.items():
        short="LABEL_A" if "GEN_A" in label else "LABEL_B"
        zp=OUT/(f"pending-20-{short}-unmodified-JPGs-INTERNAL-QA.zip")
        with zipfile.ZipFile(zp,"w") as z:
            for f in arr:
                entry=zipfile.ZipInfo(f"{f['slot']:02d}-{Path(f['source_path']).name}")
                entry.compress_type=zipfile.ZIP_STORED
                entry.external_attr=0o644<<16
                z.writestr(entry,files_by_slot[f["slot"]])
        with zipfile.ZipFile(zp) as z:
            for f,name in zip(arr,z.namelist()):
                assert digest(z.read(name))==f["sha256"],"ZIP modified original JPG content"
        packages[short]={"observed_label":label,"frames":[f["slot"] for f in arr],"count":len(arr),
            "zip":str(zp.relative_to(ROOT)),"zip_sha256":digest(zp.read_bytes()),
            "zip_bytes":zp.stat().st_size,
            "source_JPG_sha256":[f["sha256"] for f in arr],
            "native_limit":"600x800 for frames 4/5 from v2939; 1080 JPEG is resized, not natively 1080" if short=="LABEL_B" else "Need independent source check",
            "physical_25AD_exact_generation_confirmed":False,
            "licensed_for_sales":False}
    contact(groups,files_by_slot)
    manifest={
     "version":"v2957","baseline":"v2956",
     "project":"Shopee Thumbnail Creator PRO 82SKU 41 families",
     "family_id":"pending-20","product":"GOODAL Green Tangerine Vita-C Serum Mist 100mL 25AD",
     "manual_visual_observation_not_OCR":"Frames 1-3 display SERUM MIST / NIACINAMIDE / HYALURONIC ACID front; frames 4-5 display Dark Spot Care SERUM MIST front",
     "interpretation":"Two different front labels; cannot establish same commercial product generation or 25AD photo identity from image alone.",
     "verified_catalog_metadata":{
        "clubclio_official_product":"https://clubclio.co.kr/shop/goodsView/0000003795",
        "brand_catalog_volume":"100mL",
        "ssg_named_25AD_listing":"https://shinsegaemall.ssg.com/item/itemView.ssg?itemId=1000706462566&salestrNo=6005&siteNo=6004",
        "shilla_listing_SKU":"669210000427",
        "stock_unit_photo_verified":False,
        "retailer_listing_does_not_grant_photo_license":True},
     "prior_mixed_zip_preserved_not_to_use_in_retail":prev["new_zip"],
     "groups":packages,
     "five_existing_jpgs_two_label_groups":True,
     "max_count_same_label":max(len(v) for v in groups.values()),
     "safe_unique_scene_count_GEN_A_estimate":2,
     "safe_unique_scene_count_GEN_B_estimate":2,
     "gate_result":mixed_reject,
     "requires":["proof of exact physical 25AD front label","five truly independent licensed same-generation scenes","authenticated original MK binary","full retail 1080 JPG QA","anonymous Render JPEG SHA256 GET"],
     "old_public_modified":0,"prior_published_families_preserved":11,"prior_verified_urls_preserved":55,
     "new_customer_JPGs":0,"new_sale_approved":0,"new_public_verified_urls":0,
     "no_final_spreadsheet":True,
     "next_actions":["Reject photos with opposite label after physical edition confirmed","Do not repeat old retailer photo sources or mix two labels into a five-picture set","Move to independent families pending-25/27/29/30 while this SKU is on physical edition hold"]
    }
    (OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"version":"v2957","groups":{k:v["count"] for k,v in packages.items()},
                      "gate_result":mixed_reject,"native_source_photos_changed":0,"customer_published":0}))
if __name__=="__main__":main()
