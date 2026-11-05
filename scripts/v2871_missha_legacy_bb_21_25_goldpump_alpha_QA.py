#!/usr/bin/env python3
"""v2871 | MISSHA M Perfect Cover BB 50mL legacy RED GOLD-PUMP tube.
Real shade-specific original No.21 and No.25 already archived. Use
proven U2Net model, 1 pass, preserve exact source RGB, make two NEW
technical QA PNGs and white-hero JPGs only when body, shade-label,
gold pump, nozzle and top seal survive. No new downloads and NO sales.
Never repeat No.23 already preserved real cutout; never publish URLs.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageFont,ImageDraw
from hashlib import sha256
import numpy as np,json
R=Path("qa-review")
OUT=R/"v2871-missha-legacy-bb-21-25-gold-pump-u2net-QA"
assert not OUT.exists()
s21=R/"v2869-missha-legacy-gold-pump-21-23-25-exact-shade-photo-QA"
s25=R/"v2870-missha-old-bb-25-new-cdn-source-and-three-shade-contact-QA"
a=json.loads((s21/"manifest.json").read_text())
b=json.loads((s25/"manifest.json").read_text())
assert a["family"]=="pending-03" and b["family"]=="pending-03"
xx=next(x for x in a["new_shade_source_rows"] if x["shade"]=="21")
assert xx["status"].startswith("SOURCE_SAVED")
sha=lambda p:sha256(p.read_bytes()).hexdigest()
SPECS=[
 {"shade":"21","name":"LIGHT BEIGE","path":Path(xx["source_original"]),
  "sha":xx["source_sha256"],"native":(800,800),"center_ratio":(0.50,0.34),
  "top_seal_ratio":(0.50,0.035),"gold_pump_ratio":(0.50,0.71),
  "nozzle_ratio":(0.50,0.875),"bbox_top_max":0.055,
  "bbox_bottom_min":0.91},
 {"shade":"25","name":"WARM BEIGE","path":Path(b["source_record"]["raw_original"]),
  "sha":b["source_record"]["original_sha256"],"native":(1500,1500),
  "center_ratio":(0.50,0.47),"top_seal_ratio":(0.50,0.14),
  "gold_pump_ratio":(0.50,0.77),"nozzle_ratio":(0.50,0.91),
  "bbox_top_max":0.17,"bbox_bottom_min":0.93},
]
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BF="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False:ImageFont.truetype(BF if b else F,n)
# The U2Net model was successfully used on v2864 to rescue pale white parts.
# If model is unavailable we do NOT silently swap a GrabCut mask: previous
# pipeline proved segmentation failures can erase product contours.
session=None;model_error=None
try:
 from rembg import new_session,remove
 session=new_session("u2net")
except Exception as e:model_error=type(e).__name__+": "+str(e)[:240]
OUT.mkdir(parents=True)
rows=[]
for spec in SPECS:
 row={"shade":spec["shade"],"name":spec["name"],"source":str(spec["path"]),
      "source_sha256":spec["sha"],"result":"HOLD_NOT_PROCESSED",
      "new_license_approval":False,"stock_packaging_verified":False,"sale_approved":False}
 try:
  src=spec["path"]
  assert src.exists() and sha(src)==spec["sha"]
  with Image.open(src) as im:
   im.load();assert im.size==spec["native"]
   original=im.convert("RGB")
  if session is None: raise RuntimeError("u2net unavailable: "+str(model_error))
  rgba=remove(original,session=session,alpha_matting=False)
  assert rgba.mode=="RGBA"
  a=np.asarray(rgba.getchannel("A"))
  def pt(frac):
   x=int(frac[0]*original.width);y=int(frac[1]*original.height)
   x0=max(0,x-8);x1=min(original.width,x+9)
   y0=max(0,y-8);y1=min(original.height,y+9)
   return round(float(np.median(a[y0:y1,x0:x1])),2)
  probe={
   "red_labeled_tube":pt(spec["center_ratio"]),
   "top_crimp":pt(spec["top_seal_ratio"]),
   "gold_pump":pt(spec["gold_pump_ratio"]),
   "bottom_nozzle":pt(spec["nozzle_ratio"]),
   "empty_top_left":pt((0.02,0.02)),
   "empty_lower_right":pt((0.98,0.98))}
  bbox=rgba.getchannel("A").getbbox()
  assert bbox
  cov=float(np.mean(a>127))
  row.update(alpha_coverage_ratio=round(cov,4),
             mask_bbox=list(bbox),probes=probe,
             bbox_top_fraction=round(bbox[1]/original.height,4),
             bbox_bottom_fraction=round(bbox[3]/original.height,4))
  # Hard guards keyed to actual product geometry from visual check.
  # If one fails, save a model diagnostic and HOLD rather than calling
  # an incomplete pump or fake background 'complete'.
  success=(
    0.13<cov<0.78
    and probe["red_labeled_tube"]>=215
    and probe["top_crimp"]>=140
    and probe["gold_pump"]>=135
    and probe["bottom_nozzle"]>=60
    and probe["empty_top_left"]<48
    and probe["empty_lower_right"]<48
    and bbox[1]/original.height<=spec["bbox_top_max"]
    and bbox[3]/original.height>=spec["bbox_bottom_min"]
    and bbox[2]-bbox[0]>original.width*.22)
  # Compare entire original and checker under the model alpha even for HOLD.
  bg=Image.new("RGBA",rgba.size,"#F5EDF2")
  d=ImageDraw.Draw(bg)
  step=max(15,original.width//32)
  for yy in range(0,original.height,step):
   for xx in range(0,original.width,step):
    if (xx//step+yy//step)%2:
     d.rectangle((xx,yy,xx+step-1,yy+step-1),fill="#D1C9D5")
  bg.alpha_composite(rgba)
  diag=OUT/f"MISSHA-legacy-No{spec['shade']}-u2net-source-checker-QA.jpg"
  bg.convert("RGB").save(diag,"JPEG",quality=89,optimize=True)
  row.update(status="ALPHA_TECHNICAL_CANDIDATE_HOLD_LICENSE_STOCK" if success else "HOLD_MASK_GEOMETRY_OR_GOLD_PUMP",
             diagnostic=str(diag),diagnostic_sha256=sha(diag),technical_guards_passed=success)
  if success:
   crop=(max(0,bbox[0]-18),max(0,bbox[1]-18),
         min(original.width,bbox[2]+18),min(original.height,bbox[3]+18))
   isolated=rgba.crop(crop)
   png=OUT/f"MISSHA-old-BB-No{spec['shade']}-original-RGB-true-alpha-QA.png"
   isolated.save(png,optimize=True)
   hero=Image.new("RGB",(1080,1080),"white")
   displayed=ImageOps.contain(isolated,(800,965),Image.Resampling.LANCZOS)
   hero.paste(displayed,((1080-displayed.width)//2,(1080-displayed.height)//2),displayed.getchannel("A"))
   jpg=OUT/f"MISSHA-old-BB-No{spec['shade']}-full-gold-pump-1080-QA.jpg"
   hero.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
   assert jpg.stat().st_size<2_000_000
   with Image.open(jpg) as ck:assert ck.format=="JPEG" and ck.size==(1080,1080)
   row.update(png=str(png),png_sha256=sha(png),jpg=str(jpg),jpg_sha256=sha(jpg),
              jpg_bytes=jpg.stat().st_size)
  assert sha(src)==spec["sha"]
 except Exception as e:
  row.update(status="HOLD_PROCESS_ERROR",reason=type(e).__name__+": "+str(e)[:250])
  print("HOLD",spec["shade"],str(e)[:150])
 rows.append(row)
# Comparison sheet retains archived real 23 without making a redundant 23.
contact=Image.new("RGB",(1640,1120),"#F1EEF0")
d=ImageDraw.Draw(contact)
d.text((18,14),"v2871 MISSHA legacy gold pump No21 No25 | PHOTO / ALPHA / HERO | QA ONLY",font=ft(25,True),fill="#473845")
for idx,r in enumerate(rows):
 yy=60+idx*530
 with Image.open(r["source"]) as im:
  orig=ImageOps.contain(im.convert("RGB"),(500,475),Image.Resampling.LANCZOS)
 contact.paste(orig,(15+(500-orig.width)//2,yy+(475-orig.height)//2))
 if r.get("diagnostic"):
  with Image.open(r["diagnostic"]) as im:
   panel=ImageOps.contain(im.convert("RGB"),(500,475),Image.Resampling.LANCZOS)
  contact.paste(panel,(565+(500-panel.width)//2,yy+(475-panel.height)//2))
 if r.get("jpg"):
  with Image.open(r["jpg"]) as im:
   panel=im.convert("RGB").resize((475,475),Image.Resampling.LANCZOS)
  contact.paste(panel,(1130,yy))
 d.text((20,yy+483),"No."+r["shade"]+"  "+r["status"],font=ft(18,True),fill="#493E4E")
 contact.save(OUT/"v2871-missha-legacy-21-25-original-alpha-hero-visual-QA.jpg","JPEG",quality=88,optimize=True)
report={
 "version":"v2871","baseline":"v2870","family":"pending-03",
 "product":"MISSHA M Perfect Cover BB Cream 50ml legacy gold pump",
 "exact_shades_attempted":["21","25"],
 "shade_23_already_existing_approved_QA_cutout_not_redone":True,
 "genuine_original_photographs_new_downloads":0,
 "new_alpha_pngs":sum(bool(x.get("png")) for x in rows),
 "new_JPGs":sum(bool(x.get("jpg")) for x in rows),
 "model":"u2net",
 "read_only_source_sha_locked":True,
 "original_source_RGB_changed":False,
 "rows":rows,"comparison":str(OUT/"v2871-missha-legacy-21-25-original-alpha-hero-visual-QA.jpg"),
 "no_new_public_urls":True,"retail_approved":False,
 "old_11_finished_families_preserved":True,"old_55_verified_URLs_preserved":True,
 "physical_owned_stock_same_packaging_version_verified":False,
 "third_party_original_photo_rights_verified":False,
 "original_round_MK_logo_authenticated":False,
 "final_spreadsheet_shared":False,
 "next":"Open and inspect full-sized masks and gold-pump transparent nozzles. If failure keep family held; do not repeat this same model. Keep No23 previous photo and carry pending02/10/12 edition-spec QA forward."
}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2871","new_pngs":report["new_alpha_pngs"],
                  "new_jpgs":report["new_JPGs"],
                  "statuses":[x["status"] for x in rows],"sales_approved":0}))
