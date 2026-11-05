#!/usr/bin/env python3
"""v2884 OBgE Max Waterful Sun Cream 300mL high-resolution QA of archived
v2857 source and U2/GrabCut alpha. Do NOT regenerate the product, rerun
segmentation, fake 600px native detail, or touch any old JPEG/PNG.
Only new source-locked diagnostic contact and pixel-level edge report.
Retail remains blocked by photo rights, exact owned stock & native 600px.
"""
from pathlib import Path
from hashlib import sha256
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json,numpy as np,copy

R=Path("qa-review")
PRE=R/"v2857-obge300ml-official-beige-source-true-alpha-recovery-QA"
STATE=R/"v2883-missha-peelshot25-15G-vs-15mL-source-label-hold-QA"/"stock30-incremental-state-v2883.json"
OUT=R/"v2884-obge300ml-archived-alpha-native-detail-4-panel-QA"
assert not OUT.exists() and STATE.is_file()
m=json.loads((PRE/"manifest.json").read_text())
assert m["version"]=="v2857" and m["family"]=="pending-22"
source=Path(m["source"])
png=PRE/m["qa_original_PNG"]
oldjpg=PRE/m["new_JPG"]
sha=lambda p:sha256(p.read_bytes()).hexdigest()
for p,key in [(source,"source_sha256"),(png,"qa_original_PNG_sha256"),(oldjpg,"JPG_sha256")]:
 assert p.exists() and sha(p)==m[key],(p,key)
with Image.open(source) as im:
 im.load();assert im.format=="JPEG" and im.size==(1080,1080)
 whole=im.convert("RGB")
with Image.open(png) as im:
 im.load();assert im.mode=="RGBA"
 subject=im.copy()
with Image.open(oldjpg) as im:
 im.load();assert im.size==(1080,1080)
 old_hero=im.convert("RGB")
x,y,w,h=m["mask_bbox_xywh"]
assert subject.size==(w+30,h+30), (subject.size,w,h)
original_crop=np.array(whole.crop((x-15,y-15,x+w+15,y+h+15)),dtype=np.uint8)
rgba=np.asarray(subject)
assert np.array_equal(original_crop,rgba[:,:,:3]), "source RGB pixel alteration"
alpha=rgba[:,:,3]
assert alpha.shape==(h+30,w+30) and alpha.max()==255
# Pixels near transparent edges are anti-aliased; never infer a perfect
# compositing halo threshold from pixel count alone. Surface diagnostic
# backdrop images so visual QA can reject pale beige fringing.
count_nonzero=int((alpha>127).sum())
bbox=subject.getchannel("A").getbbox()
assert bbox and count_nonzero>=150000
# Specific three physical feature coverage gates in the cropped 327x697.
cx=subject.width//2
probes={
 "pump_top_region_visible":int((alpha[5:90]>127).sum()),
 "bottle_shoulder_region_visible":int((alpha[140:245]>127).sum()),
 "base_region_visible":int((alpha[-120:-10]>127).sum()),
 "opaque_body_center_alpha":int(alpha[round(subject.height*.55),cx]),
 "transparent_border_top_left":int(alpha[0,0]),
 "native_source_px_min":min(m["source_native_px_reported"]),
 "total_foreground_px":count_nonzero,
 "fractional_edge_alpha_px":int(((alpha>0)&(alpha<255)).sum()),
}
assert probes["pump_top_region_visible"]>400
assert probes["bottle_shoulder_region_visible"]>6000
assert probes["base_region_visible"]>8000
assert probes["opaque_body_center_alpha"]>=240
assert probes["transparent_border_top_left"]<=30
assert probes["native_source_px_min"]==600

def composite(bg):
 b=Image.new("RGBA",subject.size,bg)
 b.alpha_composite(subject)
 return b.convert("RGB")
light=composite("#FFFFFF")
dark=composite("#30303B")
check=Image.new("RGBA",subject.size,"#E5DDE5")
dd=ImageDraw.Draw(check)
for py in range(0,subject.height,20):
 for px in range(0,subject.width,20):
  if (px//20+py//20)%2:
   dd.rectangle((px,py,px+19,py+19),fill="#55535B")
check.alpha_composite(subject)
checker=check.convert("RGB")
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
ft=lambda n,b=False:ImageFont.truetype(B if b else F,n)
OUT.mkdir(parents=True)
canvas=Image.new("RGB",(1610,1230),"#F0ECEF")
d=ImageDraw.Draw(canvas)
d.text((18,14),"v2884 OBgE 300mL | EXACT v2857 ALPHA ON THREE BACKDROPS | QA ONLY",font=ft(22,True),fill="#4C414C")
panels=[("SOURCE NATIVE 600px UP-SAMPLED",whole),
        ("LIGHT BACKGROUND",light),
        ("DARK BACKGROUND / PALE HALO CHECK",dark),
        ("CHECKER / REFERENCE EDGE",checker)]
for i,(name,im) in enumerate(panels):
 x0=16+(i%4)*398
 fit=ImageOps.contain(im,(378,770),Image.Resampling.LANCZOS)
 canvas.paste(fit,(x0+(378-fit.width)//2,70+(770-fit.height)//2))
 d.text((x0,857),name[:34],font=ft(13,True),fill="#5D535D")
# IMPORTANT source is 600 native, data artificially upscaled to 1080.
# 3x nearest crop is a diagnostic to expose pixel/nozzle defects, not
# a new super-resolution asset or synthetic detail.
for i,(name,box) in enumerate([
 ("PUMP AND CAP / NATIVE PIXEL ZOOM",(30,0,subject.width-22,205)),
 ("FULL BOTTLE BASE / NATIVE PIXEL ZOOM",(30,subject.height-166,subject.width-22,subject.height))]):
 z=checker.crop(box)
 tile=ImageOps.contain(z,(730,295),Image.Resampling.NEAREST)
 xpos=20+i*795
 canvas.paste(tile,(xpos+(730-tile.width)//2,906+(295-tile.height)//2))
 d.text((xpos+7,1196),name,font=ft(14,True),fill="#4F424D")
contact=OUT/"v2884-obge300-source-light-dark-checker-edge-QA.jpg"
canvas.save(contact,"JPEG",quality=91,optimize=True)
with Image.open(contact) as checkimg:
 assert checkimg.size==(1610,1230)
# Two separate exact-size QA contrasts to spot halo hidden by white canvas.
subject_view=Image.new("RGB",(1080,1080),"#FAF8F9")
d=ImageDraw.Draw(subject_view)
d.text((39,29),"OBgE 300mL | CHECKER ALPHA VALIDATION (NOT SALES)",font=ft(23,True),fill="#544957")
fit=ImageOps.contain(checker,(800,940),Image.Resampling.LANCZOS)
subject_view.paste(fit,((1080-fit.width)//2,76+(940-fit.height)//2))
checker_path=OUT/"v2884-obge300-full-checker-1080-true-alpha-QA.jpg"
subject_view.save(checker_path,"JPEG",quality=92,optimize=True)
with Image.open(checker_path) as test:
 assert test.size==(1080,1080) and test.format=="JPEG"
for p,key in [(source,"source_sha256"),(png,"qa_original_PNG_sha256"),(oldjpg,"JPG_sha256")]:
 assert sha(p)==m[key]
state=json.loads(STATE.read_text())
assert state["version"]=="v2883" and len(state["families"])==30
families=copy.deepcopy(state["families"])
families["pending-22"].update(
 last_delta_version="v2884",
 latest_photo_QA_checkpoint="v2884 original RGB pixel identity, pump/shoulder/base alpha probes and white/dark checker visible; source actually 600px, no commercial approval",
 technical_alpha_pixel_integrity_verified=True,
 qa_detail_comparison_done=True,
 source_native_px=600,
 release_status="HOLD_LOW_NATIVE_RES_RIGHTS_STOCK",
 sale_approved=False,
 open_blockers=["source native 600px and softness","license for commercial photo not confirmed","owned 300mL packaging edition not inspected","original MK mark not authenticated"])
assert all(z.get("sale_approved") is False for z in families.values())
newstate={**state,"version":"v2884","baseline":"v2883","families":families,
 "last_operation":"v2884 OBgE 300mL 4-panel native pixel alpha QA diagnostics, no product regeneration",
 "old_11_families_preserved":True,"old_55_URLs_preserved":True,
 "new_sales_approvals":0,"new_public_URLs":0,"final_spreadsheet_shared":False}
checkpoint=OUT/"stock30-incremental-state-v2884.json"
checkpoint.write_text(json.dumps(newstate,ensure_ascii=False,indent=2)+"\n")
report={"version":"v2884","baseline":"v2883","family":"pending-22",
 "product":"OBgE Max Waterful Sun Cream 300mL",
 "source_version":"v2857","source_native_px":[600,600],
 "archived_source_RGB_preserved":True,
 "exact_mask_RGB_equals_archived_photo_pixels":True,
 "transparent_alpha_feature_probes":probes,
 "original_source_SHA256":m["source_sha256"],
 "original_png_SHA256":m["qa_original_PNG_sha256"],
 "original_hero_SHA256":m["JPG_sha256"],
 "new_diagnostic_JPGs":2,
 "new_diagnostic":[{"path":str(contact),"sha256":sha(contact)},
   {"path":str(checker_path),"sha256":sha(checker_path)}],
 "photo_quality_release_status":"TECHNICAL_ALPHA_REFERENCE_ONLY_NATIVE_600px_SALES_HOLD",
 "fullres_halo_human_review_still_required":True,
 "commercial_image_rights_verified":False,"owned_exact_stock_verified":False,
 "no_prior_image_rewrites":True,"public_55_URLs_untouched":True,
 "commercial_11_group_unchanged":True,
 "new_sale_approvals":0,"new_public_URLs":0,
 "checkpoint":str(checkpoint),"final_spreadsheet_shared":False,
 "next":"Do not loop failed GrabCut/morphology. Use owned or licensed higher resolution exact 300mL photo if available. Move to Goodal 25AD eye and Dr.G vintage edition QA."}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2884","new_qa_JPGs":2,
  "native_px":600,"foreground_px":count_nonzero,
  "source_RGB_unchanged":True,"retail_approved":0}))
