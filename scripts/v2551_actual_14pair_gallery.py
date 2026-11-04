#!/usr/bin/env python3
"""v2551: physically inspect 14 v2550 image pairs; compare exact JPG bytes,
render paired scene proof, quantify mean pixel differences, never overwrite.
"""
import json, hashlib
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
from itertools import count
ROOT=Path("v2551-156-input/review-JPG-by-family")
T=Path("v2551-triage-input/triage.json")
O=Path("v2551-14pair-actual-JPG-evidence");O.mkdir(exist_ok=True)
assert ROOT.is_dir() and T.is_file()
triage=json.loads(T.read_text())
assert triage["families"]==30 and triage["source_artifact_manifest_image_count"]==156
results=[]; failures=[]
for fam in triage["priority_review_order"]:
  pairs=triage["by_family"][fam]["similarity_pairs"]
  files={int(p.name[:2]):p for p in (ROOT/fam).glob("*.jpg")}
  for pair in pairs:
    slots=pair["slots"]
    if not all(s in files for s in slots):
      failures.append({"family":fam,"slots":slots,"issue":"MISSING_JPG"});continue
    a,b=[files[s] for s in slots]
    try:
      im1=Image.open(a).convert("RGB"); im2=Image.open(b).convert("RGB")
      assert im1.size==im2.size==(1080,1080)
      small1=im1.resize((256,256)); small2=im2.resize((256,256))
      px1=list(small1.getdata());px2=list(small2.getdata())
      mean_abs=sum(abs(v-w) for p,q in zip(px1,px2) for v,w in zip(p,q))/(len(px1)*3)
      pixels_diff=sum(any(abs(v-w)>=24 for v,w in zip(p,q)) for p,q in zip(px1,px2))/len(px1)
      pairid=f"{fam}-slot{slots[0]:02d}-slot{slots[1]:02d}"
      canvas=Image.new("RGB",(960,640),"white")
      d=ImageDraw.Draw(canvas)
      for ix,im in enumerate((im1,im2)):
        thumb=ImageOps.contain(im,(452,452))
        canvas.paste(thumb,(14+ix*480+(452-thumb.width)//2,24))
      d.text((15,490),f"{fam} | slots {slots[0]} / {slots[1]} | dHash {pair['distance']}",fill="black")
      d.text((15,522),f"Mean RGB difference: {mean_abs:.2f}/255 | Changed pixels: {pixels_diff:.1%}",fill="black")
      d.text((15,556),"MANUAL REVIEW ONLY / NOT SALES APPROVED",fill="black")
      canvas.save(O/(pairid+".jpg"),"JPEG",quality=87,optimize=True)
      results.append({"pair_id":pairid,"family":fam,"slots":slots,
       "dhash_distance":pair["distance"],"pixel_mae_0_255":round(mean_abs,3),
       "changed_pixel_fraction":round(pixels_diff,4),
       "sha256_a":hashlib.sha256(a.read_bytes()).hexdigest(),
       "sha256_b":hashlib.sha256(b.read_bytes()).hexdigest(),
       "review_status":"MANUAL_VISUAL_REQUIRED",
       "action":"DO_NOT_DELETE_OR_REPLACE_WITHOUT_PRODUCT_SCENE_CONFIRMATION"})
    except Exception as e:
      failures.append({"family":fam,"slots":slots,"issue":str(e)})
assert len(results)+len(failures)==triage["candidate_pairs_0_to_6"]+triage["candidate_pairs_7_to_10"]
assert not failures,failures
results.sort(key=lambda z:(z["pixel_mae_0_255"],z["dhash_distance"]))
report={"version":"v2551","status":"PHYSICAL_IMAGE_PAIR_PROOF_READY",
 "source_run_156":41715911900,"source_triage_run":41750229687,
 "total_pairs":len(results),"source_images_edited":0,"original_55_urls_changed":0,
 "xlsx_created":False,"commercial_release_approved":False,
 "pairs_low_pixel_change_le_10":sum(x["pixel_mae_0_255"]<=10 for x in results),
 "pairs":results,"quarantined":failures,
 "note":"Photometric differences and dHash alone do not determine product/photo correctness. Inspect contact sheets visually."}
(O/"pair-evidence.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
(O/"review-queue.md").write_text("# v2551 actual-JPG side-by-side image review queue\n\n"
 +"No source image overwrites, no sales publication, no Excel.\n\n"
 +"| Product group | Slots | dHash distance | Pixel MAE | Changed pixels |\n"
 +"|---|---|---:|---:|---:|\n"
 +"\n".join(f"| {x['family']} | {x['slots'][0]} / {x['slots'][1]} | {x['dhash_distance']} | {x['pixel_mae_0_255']} | {x['changed_pixel_fraction']:.1%} |" for x in results)
 +"\n\nAll pairs require review of supplied side-by-side JPG evidence before any edits.\n")
print(json.dumps({"pairs":len(results),"low_change_le10":report["pairs_low_pixel_change_le_10"],"top_priority":results[:8],"quarantined":len(failures)},ensure_ascii=False))
