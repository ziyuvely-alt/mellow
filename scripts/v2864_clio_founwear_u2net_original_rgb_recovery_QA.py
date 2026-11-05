#!/usr/bin/env python3
"""v2864: Alternative segmentation-model trial for three distinct original
CLIO Founwear merchant photos after v2862 GrabCut rejected by visual inspection.

Strong mask acceptance gates test opaque WHITE LID + WHITE PUFF explicitly,
which v2862 missed. Source RGB, prior rejected QA and all public URLs immutable.
If model has no reliable mask, keep as HOLD; do not invent transparent product.
"""
from pathlib import Path
from hashlib import sha256
from PIL import Image, ImageOps, ImageDraw, ImageFont
import numpy as np, json, traceback

R=Path("qa-review")
OLD=R/"v2852-founwear-original-five-variant-alternative-merchant-QA"
REJECT=R/"v2863-founwear-v2862-white-lid-puff-rejection"/"manifest.json"
OUT=R/"v2864-founwear-3-white-lid-u2net-native-RGB-check"
assert REJECT.is_file() and not OUT.exists()
rejection=json.loads(REJECT.read_text())
assert rejection["version"]=="v2863"
source=json.loads((OLD/"manifest.json").read_text())
lookup={v["shade"]:v for v in source["variants"]}
sha=lambda p:sha256(p.read_bytes()).hexdigest()
OUT.mkdir(parents=True)
MODEL="u2net"
model=None;model_error=None
try:
 from rembg import remove,new_session
 model=new_session(MODEL)
except Exception as exc:
 model_error=type(exc).__name__+": "+str(exc)[:300]
 print("MODEL_UNAVAILABLE",model_error)
rows=[]
for shade in ("19C","19N","23N"):
 line=lookup[shade]
 p=OLD/line["rendered_file"]
 assert p.is_file() and sha(p)==line["rendered_JPG_sha256"]
 row={"shade":shade,"source":str(p),"source_sha256":sha(p),
      "model":MODEL,"prior_v2862_CV_mask":"REJECT_WHITE_LID_AND_PUFF_HOLES",
      "stock_shade_option_exists":True,"retail_approved":False}
 if model is None:
  row.update(status="HOLD_MODEL_UNAVAILABLE",error=model_error)
  rows.append(row)
  continue
 try:
  with Image.open(p) as photo:
   photo.load();assert photo.size==(1080,1080) and photo.format=="JPEG"
   im=photo.convert("RGB")
  result=remove(im,session=model,alpha_matting=False)
  assert result.mode=="RGBA"
  alpha=np.asarray(result.getchannel("A"))
  assert alpha.shape==(1080,1080)
  def sample(x,y):
   block=alpha[max(0,y-18):min(1080,y+18),max(0,x-18):min(1080,x+18)]
   return float(np.median(block))
  # These original-photo landmarks are deliberately different in location
  # and material: pearlescent pale LID, clean white PUFF, silver-pan, cream smear.
  # A mask that only keeps embossed lettering and skin-toned cream is NOT valid.
  probes={
   "lid_center_A":round(sample(520,480),1),
   "lid_lower_A":round(sample(520,565),1),
   "white_puff_A":round(sample(850,750),1),
   "cushion_pan_A":round(sample(482,705),1),
   "cream_smear_A":round(sample(190,285),1),
   "blank_top_left_A":round(sample(20,20),1),
   "blank_bottom_right_A":round(sample(1060,1060),1)}
  bbox=result.getchannel("A").getbbox()
  assert bbox is not None
  area=int((alpha>127).sum())
  geometric_pass=(90000<area<750000 and 250<bbox[2]-bbox[0]<=1075 and
                  300<bbox[3]-bbox[1]<=1050)
  white_material_pass=(max(probes["lid_center_A"],probes["lid_lower_A"])>=160 and
                       probes["white_puff_A"]>=155 and probes["cushion_pan_A"]>=155)
  background_pass=(probes["blank_top_left_A"]<35 and probes["blank_bottom_right_A"]<35)
  alpha_rgba=Image.fromarray(np.dstack((np.asarray(im),alpha)),"RGBA")
  # Internal diagnostic shows rejected and accepted masks alike, never claims sales ready.
  check=Image.new("RGBA",(1080,1080),"#F7F0F4")
  dd=ImageDraw.Draw(check)
  for y in range(0,1080,32):
   for x in range(0,1080,32):
    if ((x//32)+(y//32))%2:dd.rectangle((x,y,x+31,y+31),fill="#D4D0DC")
  check.alpha_composite(alpha_rgba)
  diagnostic=OUT/f"{shade}-u2net-mask-diagnostic-1080-QA.jpg"
  check.convert("RGB").save(diagnostic,"JPEG",quality=87,optimize=True)
  row.update(model_mask_area_px=area,mask_bbox=list(bbox),
             probe_alpha=probes,geometry_pass=geometric_pass,
             white_material_pass=white_material_pass,
             blank_background_pass=background_pass,
             diagnostic=str(diagnostic),diagnostic_sha256=sha(diagnostic))
  if geometric_pass and white_material_pass and background_pass:
   cropbox=(max(0,bbox[0]-15),max(0,bbox[1]-15),
            min(1080,bbox[2]+15),min(1080,bbox[3]+15))
   cut=alpha_rgba.crop(cropbox)
   png=OUT/f"{shade}-original-RGB-u2net-white-puff-alpha-QA.png"
   cut.save(png,optimize=True)
   fit=ImageOps.contain(cut,(930,930),Image.Resampling.LANCZOS)
   hero=Image.new("RGB",(1080,1080),"white")
   hero.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2),fit.getchannel("A"))
   jpg=OUT/f"{shade}-real-photo-1080-u2net-white-preserved-QA.jpg"
   hero.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
   with Image.open(jpg) as cv:
    cv.load();assert cv.format=="JPEG" and cv.size==(1080,1080)
   assert jpg.stat().st_size<2_000_000 and sha(p)==line["rendered_JPG_sha256"]
   row.update(status="TECHNICAL_ALPHA_CANDIDATE_HOLD_VISUAL_AND_LICENSE",
              png=str(png),png_sha256=sha(png),
              jpg=str(jpg),jpg_sha256=sha(jpg),jpg_bytes=jpg.stat().st_size)
  else:
   row.update(status="HOLD_MODEL_MASK_FAILED_WHITE_MATERIAL_OR_GEOMETRY")
 except Exception as exc:
  row.update(status="HOLD_PROCESS_FAILURE",error=type(exc).__name__+": "+str(exc)[:240])
  print("HOLD",shade,str(exc)[:200])
 rows.append(row)

# The contact is an internal comparison, even for a mask which failed.
F="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
contact=Image.new("RGB",(1670,600*3+70),"#F0EDEF")
d=ImageDraw.Draw(contact)
d.text((14,12),"v2864 FOUNWEAR SOURCE  vs  U2NET ALPHA  vs  QA HERO / ORIGINAL RGB / NOT SALES",
       font=ImageFont.truetype(F,24),fill="#403544")
for idx,line in enumerate(rows):
 with Image.open(line["source"]) as img:
  orig=img.convert("RGB")
 panels=[orig]
 if line.get("diagnostic"):
  with Image.open(line["diagnostic"]) as pic:panels.append(pic.convert("RGB"))
 else:panels.append(Image.new("RGB",(1080,1080),"#ded8da"))
 if line.get("jpg"):
  with Image.open(line["jpg"]) as img:panels.append(img.convert("RGB"))
 else:panels.append(orig)
 for j,p in enumerate(panels):
  panel=p.resize((510,510),Image.Resampling.LANCZOS)
  x=20+j*550;y=60+idx*600
  contact.paste(panel,(x,y))
 d.text((25,573+idx*600),line["shade"]+" "+line["status"],
        font=ImageFont.truetype(F,18),fill="#423947")
contact_path=OUT/"v2864-three-source-u2net-white-lid-preservation-QA.jpg"
contact.save(contact_path,"JPEG",quality=88,optimize=True)
report={
 "version":"v2864","baseline":"v2863","family":"pending-05",
 "purpose":"Switch from failed v2862 color-prior GrabCut to existing proven U2Net model; explicit white lid/puff acceptance tests.",
 "model":MODEL,"model_session_error":model_error,
 "trial_shades":["19C","19N","23N"],
 "retained_white_material_candidates":sum(x.get("status","").startswith("TECHNICAL") for x in rows),
 "held_traces":sum(not x.get("status","").startswith("TECHNICAL") for x in rows),
 "results":rows,"comparison":str(contact_path),"comparison_sha256":sha(contact_path),
 "previous_11_sale_approved_families_preserved":True,
 "previous_55_verified_URLs_preserved":True,
 "source_original_RGB_preserved":True,"prior_v2862_rejected_masks_preserved":True,
 "commercial_use_rights_verified":False,"exact_user_stock_gift_set_verified":False,
 "authentic_MK_logo_verified":False,"new_sales_approvals":0,"new_public_URLs":0,
 "final_xlsx_shared":False,
 "next":"If candidate exists, inspect its lid, puff and edge at full resolution before use; if failed, quarantine entire Founwear segmentation task, move to other family rather than repeating failed mask approaches."
}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2864","model":MODEL,
  "new_candidate_png_jpg_pairs":report["retained_white_material_candidates"],
  "hold":report["held_traces"],"retail_approved":0},ensure_ascii=False))
