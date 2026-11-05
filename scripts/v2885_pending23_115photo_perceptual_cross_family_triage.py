#!/usr/bin/env python3
"""v2885 ONE batch new QA type: perceptual similarity across previously
SHA-archived 23 product-family x 5 existing JPEG scenes = 115 photos.

Do not repeat v2782 hash-dedup work, download photos, regenerate any
approved/pending assets, infer sale rights or classify similarity as proof of
wrong product. Detect near-identical appearances that ordinary distinct
file SHA cannot catch, across and within families. Preserve everything and
add a durable triage file, proof board and v2885 30-family checkpoint.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageFont,ImageDraw
from hashlib import sha256
import json,copy,itertools,numpy as np

R=Path("qa-review")
OUT=R/"v2885-23-pending-family-115-existing-JPG-perceptual-dedupe-QA"
STATE=R/"v2884-obge300ml-archived-alpha-native-detail-4-panel-QA"/"stock30-incremental-state-v2884.json"
EVIDENCE=Path("/tmp/v2885_src_23_family_inventory.json")
assert not OUT.exists() and STATE.exists() and EVIDENCE.exists()
ev=json.loads(EVIDENCE.read_text())
state=json.loads(STATE.read_text())
assert ev["version"]=="v2782" and ev["qa_fiveframe_families_count"]==23
assert state["version"]=="v2884" and len(state["families"])==30
BATCH={
 "v2772":"v2772-goodal-obge-five-frame-photo-QA",
 "v2774":"v2774-bioheal-two-photo-first-fiveframe-QA",
 "v2775":"v2775-four-photo-first-fiveframe-product-QA",
 "v2776":"v2776-four-source-photo-first-fiveframe-QA",
 "v2778":"v2778-missha-pdrn-serum-correct-original-5JPG-QA",
 "v2779":"v2779-five-photo-first-product-groups-QA",
 "v2780":"v2780-four-unfinished-missha-obge-photo-first-QA",
 "v2781":"v2781-coverlasting-fixed-source-and-goodal-gap-QA"}
assert set(ev["qa_families_by_batch"])==set(BATCH)
all_expected=[f for fams in ev["qa_families_by_batch"].values() for f in fams]
assert len(all_expected)==len(set(all_expected))==23
img_rows=[];family_reports=[]
def dhash(img):
 a=np.asarray(img.convert("L").resize((9,8),Image.Resampling.LANCZOS),dtype=np.int16)
 return sum(int(b)<<(i) for i,b in enumerate((a[:,1:] > a[:,:-1]).ravel()))
def phash_hamming(x,y):return (x^y).bit_count()
def asrgb(img):
 return np.asarray(img.convert("RGB").resize((64,64),Image.Resampling.BILINEAR),dtype=np.int16)
def sha(file):return sha256(file.read_bytes()).hexdigest()
for batch,ids in ev["qa_families_by_batch"].items():
 for family in ids:
  folder=R/BATCH[batch]/family
  manifest=folder/"manifest.json"
  fr={"family":family,"batch":batch,"manifest":str(manifest),"usable_photo_count":0,
      "perceptual_nearduplicate_pairs":[],"warnings":[]}
  if not manifest.exists():
   fr["warnings"].append("MISSING_ARCHIVED_MANIFEST")
   family_reports.append(fr);continue
  try:
   m=json.loads(manifest.read_text())
   assert m["family"]==family,(family,m.get("family"))
   src_frames=m.get("frames")
   assert isinstance(src_frames,list) and len(src_frames)==5
  except Exception as e:
   fr["warnings"].append("MANIFEST_PARSE_OR_FIVE_COUNT:"+str(e)[:120])
   family_reports.append(fr);continue
  for entry in src_frames:
   p=Path(entry["path"])
   rec={"family":family,"batch":batch,"slot":entry["slot"],
        "file":str(p),"QA_ONLY":True,
        "role":entry.get("scene") or entry.get("role") or entry.get("descriptive_scene") or entry.get("source_description")}
   try:
    assert p.is_file(), "MISSING_IMAGE"
    assert p.stat().st_size<2_000_000,"OVER_2MB"
    with Image.open(p) as im:
     im.load()
     assert im.format=="JPEG","NOT_JPEG"
     assert min(im.size)>=640,"LOW_FRAME_RES"
     rec.update(width=im.width,height=im.height,
       perceptual_hash_64=f"{dhash(im):016x}",
       raw_RGB_thumbnail_64x64=asrgb(im).tolist(),
       byte_sha256=sha(p))
    rec["status"]="ANALYZED"
    fr["usable_photo_count"]+=1
   except Exception as e:
    rec["status"]="HOLD_UNREADABLE_OR_WRONG_FRAME"
    rec["error"]=str(e)[:140]
    fr["warnings"].append(f"FRAME_{entry['slot']}:{rec['error']}")
   img_rows.append(rec)
  family_reports.append(fr)
processed=[r for r in img_rows if r["status"]=="ANALYZED"]
# all 115 should be available in QA archive, but if one failed, process
# the remaining independently without restarting the entire batch.
comparison=[]
for a,b in itertools.combinations(processed,2):
 ha=int(a["perceptual_hash_64"],16);hb=int(b["perceptual_hash_64"],16)
 hd=phash_hamming(ha,hb)
 if hd>8:continue
 x=np.array(a["raw_RGB_thumbnail_64x64"],dtype=np.int16)
 y=np.array(b["raw_RGB_thumbnail_64x64"],dtype=np.int16)
 mad=float(np.mean(np.abs(x-y)))
 if mad>25:continue
 is_same=a["family"]==b["family"]
 strong=(hd<=3 and mad<=8) or a["byte_sha256"]==b["byte_sha256"]
 possible=(hd<=6 and mad<=15)
 comparison.append({
  "family_a":a["family"],"frame_a":a["slot"],"file_a":a["file"],
  "family_b":b["family"],"frame_b":b["slot"],"file_b":b["file"],
  "same_family":is_same,"visual_dhash_hamming":hd,
  "downsample_RGB_absolute_diff":round(mad,3),
  "byte_exact":a["byte_sha256"]==b["byte_sha256"],
  "possible_near_repeat_for_human_QA":possible,
  "high_confidence_visual_similarity_only":strong,
  "retail_approval_effect":"NONE_UNTIL_PRODUCT_AND_RIGHTS_CHECKED"})
comparison.sort(key=lambda r:(not r["high_confidence_visual_similarity_only"],r["visual_dhash_hamming"],r["downsample_RGB_absolute_diff"]))
for r in comparison:
 if r["possible_near_repeat_for_human_QA"] and r["same_family"]:
  f=next(f for f in family_reports if f["family"]==r["family_a"])
  f["perceptual_nearduplicate_pairs"].append({
    "pair":[r["frame_a"],r["frame_b"]],
    "hamming":r["visual_dhash_hamming"],"RGB_MAD":r["downsample_RGB_absolute_diff"]})
flags=[r for r in comparison if r["possible_near_repeat_for_human_QA"]]
strong=[r for r in comparison if r["high_confidence_visual_similarity_only"]]
# Compact human proof board for top six candidates; when none found,
# make an explicit clean batch QA result rather than copying 115 photos.
OUT.mkdir(parents=True)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
ft=lambda n,b=False:ImageFont.truetype(B if b else F,n)
triage=Image.new("RGB",(1560,1120),"#F1EEF2")
d=ImageDraw.Draw(triage)
d.text((22,18),"v2885 | 23 FAMILIES * 5 PHOTOS | PERCEPTUAL-ONLY CROSS CHECK",font=ft(24,True),fill="#42394A")
if not flags:
 d.text((30,150),"No strong near-duplicate candidates under predefined visual thresholds.",font=ft(27),fill="#5C4E61")
 d.text((30,210),"File uniqueness and photo usage rights are separate tests.",font=ft(18),fill="#6B5D70")
else:
 for i,pair in enumerate(flags[:6]):
  row=i//2;column=i%2
  left=20+column*770
  top=75+row*340
  for n,filename in enumerate([pair["file_a"],pair["file_b"]]):
   with Image.open(filename) as im:
    thumb=ImageOps.contain(im.convert("RGB"),(350,256),Image.Resampling.LANCZOS)
   xx=left+n*367
   triage.paste(thumb,(xx+(350-thumb.width)//2,top+(255-thumb.height)//2))
  caption=f"{pair['family_a']} f{pair['frame_a']} : {pair['family_b']} f{pair['frame_b']}"
  d.text((left+8,top+260),caption,font=ft(15,True),fill="#534757")
  d.text((left+8,top+286),f"dh={pair['visual_dhash_hamming']} / colorMAD={pair['downsample_RGB_absolute_diff']:.1f}  REVIEW ONLY",font=ft(14),fill="#786878")
contact=OUT/"v2885-23family-115scene-perceptual-QA-triage.jpg"
triage.save(contact,"JPEG",quality=88,optimize=True)
# Do not inflate manifest by embedding 115 numpy pixel buffers.
for x in img_rows:x.pop("raw_RGB_thumbnail_64x64",None)
summary={
 "version":"v2885","baseline":"v2884",
 "scope":"23 already archived 5-JPG family sets, new perceptual QA only",
 "expected_source_families":23,"expected_source_JPGs":115,
 "families_scanned":len(family_reports),"JPGs_analyzed":len(processed),
 "JPGs_on_hold_or_unreadable":115-len(processed),
 "near_repeat_comparisons_scanned":len(processed)*(len(processed)-1)//2,
 "visual_candidate_pairs":len(flags),"strong_visual_similarity_pairs":len(strong),
 "within_same_family_potential_pairs":sum(p["same_family"] for p in flags),
 "across_family_potential_pairs":sum(not p["same_family"] for p in flags),
 "incomplete_families":[x for x in family_reports if x["usable_photo_count"]<5],
 "family_reports":family_reports,
 "human_review_top_pairs":comparison[:30],
 "qa_image":str(contact),"qa_image_sha256":sha(contact),
 "no_source_image_rewritten":True,
 "no_auto_reclassification_of_sale_approval":True,
 "photo_usage_license_already_verified":False,
 "actual_user_stock_photo_edition_verified":False,
 "old_11_approved_families_preserved":True,
 "old_55_public_URLs_preserved":True,
 "new_sale_approvals":0,"new_public_URLs":0,
 "final_spreadsheet_shared":False,
 "next":"Review only flagged visual candidates for actual duplicated product view or mislabel, no full regeneration. Continue genuine source/rights/stock validation for unapproved 30."
}
(OUT/"manifest.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
(OUT/"per-frame-perceptual-hashes.json").write_text(json.dumps(img_rows,ensure_ascii=False,indent=2)+"\n")
st=copy.deepcopy(state)
assert len(st["families"])==30
st.update(version="v2885",baseline="v2884",
 last_operation="Batch new perceptual near-repeat QA on all 115 archived family JPGs; no source rework",
 perceptual_23_family_review={"expected":115,"analyzed":len(processed),"flagged_pairs":len(flags),
   "strong_flags":len(strong),"report":str(OUT/"manifest.json")},
 new_sale_approvals=0,new_public_URLs=0,final_spreadsheet_shared=False)
(OUT/"stock30-incremental-state-v2885.json").write_text(json.dumps(st,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2885","families":len(family_reports),"analyzed":len(processed),
 "flagged_pairs":len(flags),"strong":len(strong),"sale_approvals":0}))
