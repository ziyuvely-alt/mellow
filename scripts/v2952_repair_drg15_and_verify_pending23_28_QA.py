#!/usr/bin/env python3
"""Incremental internal-only QA: a localized blue-background defect repair and two 5-frame byte audits."""
import hashlib, json, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageChops

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa-review/v2952-real-JPG-local-repair-and-two-family-source-QA-20261106"
INPUT=ROOT/"qa-review/v2779-five-photo-first-product-groups-QA/pending-15/03-source-archive-story-QA.jpg"
EXPECTED_GIT_BLOB="248a84df85bf652735dba3fbb52adba24b512edd"
FAMILIES={
    "pending-23":("qa-review/v2776-four-source-photo-first-fiveframe-QA/pending-23/",[
        "01-true-product-photo-alpha-QA.jpg",
        "02-original-lifestyle-or-detail-QA.jpg",
        "03-original-lifestyle-or-detail-QA.jpg",
        "04-original-lifestyle-or-detail-QA.jpg",
        "05-original-lifestyle-or-detail-QA.jpg"]),
    "pending-28":("qa-review/v2775-four-photo-first-fiveframe-product-QA/pending-28/",[
        "01-real-product-cutout-hero-QA.jpg",
        "02-source-photo-story-QA.jpg",
        "03-source-photo-story-QA.jpg",
        "04-source-photo-story-QA.jpg",
        "05-source-photo-story-QA.jpg"])
}
def sha256(b): return hashlib.sha256(b).hexdigest()
def audit(p):
    data=p.read_bytes()
    with Image.open(p) as im:
        im.load()
        dim=list(im.size)
        mode=im.mode
        fmt=im.format
        small=im.convert("L").resize((8,8),Image.Resampling.LANCZOS)
        val=np.asarray(small).astype(np.float32)
        ahash="".join("1" if v>=val.mean() else "0" for v in val.ravel())
    return {"path":str(p.relative_to(ROOT)),"bytes":len(data),"sha256":sha256(data),
            "git_blob_sha1":subprocess.check_output(["git","hash-object",str(p)],cwd=ROOT,text=True).strip(),
            "dimensions":dim,"format":fmt,"mode":mode,"technical_pass":fmt=="JPEG" and dim==[1080,1080] and len(data)<2_000_000,
            "ahash":ahash}
def main():
    if OUT.exists(): raise SystemExit("Refuse to overwrite existing v2952 QA outputs")
    assert subprocess.check_output(["git","hash-object",str(INPUT)],cwd=ROOT,text=True).strip()==EXPECTED_GIT_BLOB, "Prior input SHA altered; never edit"
    OUT.mkdir(parents=True)
    report={"version":"v2952","parent":"v2951","date_kst":"2026-11-06","release_lane":"QA_ONLY_NO_PUBLIC_DEPLOY",
            "prior_published_families":11,"prior_verified_urls":55,"new_retail_approvals":0,
            "new_public_urls":0,"prior_images_modified":0,"families":{}}
    for family,(directory,filenames) in FAMILIES.items():
        scans=[]; missing=[]
        for filename in filenames:
            p=ROOT/directory/filename
            if not p.is_file():
                missing.append(str(p.relative_to(ROOT))); continue
            scans.append(audit(p))
        dupe=[]
        for i in range(len(scans)):
            for j in range(i+1,len(scans)):
                h1=scans[i]["ahash"];h2=scans[j]["ahash"]
                hd=sum(a!=b for a,b in zip(h1,h2))
                if hd<=6: dupe.append({"frames":[i+1,j+1],"aHash_distance":hd,"interpretation":"manual semantic scene check needed"})
        report["families"][family]={"existing_source_frames":len(scans),"missing":missing,
             "frames":scans,"all_1080_small_JPEG":len(scans)==5 and all(x["technical_pass"] for x in scans),
             "visually_similar_ahash_candidate_pairs":dupe,"final_sale_approved":False,
             "remaining_gates":["physical exact stock/edition","commercial photo reuse rights","authenticated original circular MK PNG"]}
    raw=Image.open(INPUT).convert("RGB")
    if raw.size!=(1080,1080): raise SystemExit("Unexpected original frame dimension")
    rgb=np.array(raw,dtype=np.uint8)
    h,s,v=(np.array(raw.convert("HSV"),dtype=np.uint8)[:,:,k] for k in range(3))
    yy,xx=np.indices((1080,1080))
    # Only remove cyan/blue oval: never infer missing product pixels or alter any verified original.
    target=(xx>=260)&(xx<=826)&(yy>=275)&(yy<=982)&(h>=115)&(h<=190)&(s>=13)&(rgb[:,:,2].astype(np.int16)-rgb[:,:,0].astype(np.int16)>11)&(rgb[:,:,1].astype(np.int16)-rgb[:,:,0].astype(np.int16)>6)
    pixels=int(target.sum())
    # Preserve all other pixels including all product label, text and pre-existing logo.
    if not (2500<=pixels<=270000):
        report["pending-15"]={"action":"HALO_PIXEL_CLASSIFIER_HOLD","classified_pixels":pixels,"new_image_saved":False,
          "reason":"Avoid fabricating or broadly erasing exact product artwork when target mask falls outside safe bounds"}
    else:
        mask=Image.fromarray((target*255).astype(np.uint8),"L").filter(ImageFilter.GaussianBlur(radius=4))
        edited=Image.composite(Image.new("RGB",(1080,1080),(255,255,255)),raw,mask)
        targetpath=OUT/"pending-15-frame03-localized-blue-halo-fix-INTERNAL-QA.jpg"
        edited.save(targetpath,format="JPEG",quality=94,optimize=True,subsampling=0)
        result=audit(targetpath)
        assert result["technical_pass"],"Output JPG did not satisfy dimensions, bytes, format"
        report["pending-15"]={"action":"BLUE_BACKGROUND_LOCAL_COLOR_REPAIR","original_git_blob_sha1":EXPECTED_GIT_BLOB,
          "selected_blue_region_pixels":pixels,"new_image_saved":True,"output":result,
          "original_model_and_product_bytes_intact":False,
          "edits_limited_to_softened_blue_color_class_spatial_region":True,
          "visual_approval":"PENDING_INDEPENDENT_VIEWER_QA",
          "commercial_photo_rights":"PENDING","authentic_logo_match":"PENDING",
          "note":"This fixes one already-documented QA visual defect, not a new licensed source photo or a retail-ready image"}
    (OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"created":str(OUT),"pending15":report["pending-15"],
                      "family_pass":{k:v["all_1080_small_JPEG"] for k,v in report["families"].items()}},ensure_ascii=False))
if __name__=="__main__":main()
