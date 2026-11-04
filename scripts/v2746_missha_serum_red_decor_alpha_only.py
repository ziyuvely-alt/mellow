#!/usr/bin/env python3
"""v2746 targeted alpha correction, NOT another full AI segmentation.
Use v2744 ISNet's actual MISSHA 30mL bottle with intact white dropper.
Remove only the small detached red glass decoration at upper-right,
if it can be safely isolated. If not, HOLD and preserve original.

NO product pixel synthesis, no invented logo, no touching approved source.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import numpy as np,cv2,hashlib,base64,json
ROOT=Path("qa-review")
SRC=ROOT/"v2744-MISSHA-PDRN-30mL-single-official-bottle-two-alpha-qa/isnet_30mL_serum/01-real-serum-bottle-alpha-QA.png"
OUT=ROOT/"v2746-missha-pdrn-serum-red-decoration-alpha-cleanup"
assert SRC.is_file() and not OUT.exists();OUT.mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with Image.open(SRC) as photo:
 photo.load();assert photo.mode=="RGBA"
 source=photo.copy()
arr=np.asarray(source).copy();h,w=arr.shape[:2]
red,green,blue,alpha=[arr[:,:,k] for k in range(4)]
# This red bead is outside the bottle/dropper in the top right of the
# original source, the only region eligible for cleanup. Never cut
# lower red glass or central glass neck.
yy,xx=np.indices((h,w))
elig=(xx>=int(w*.84))&(yy<=int(h*.25))&(alpha>=32)
saturated=(red.astype('int16')-green.astype('int16')>=28)&(red.astype('int16')-blue.astype('int16')>=22)
island=np.uint8(elig&saturated)*255
n,labels,stats,cent=cv2.connectedComponentsWithStats(island,connectivity=8)
islands=[]
for i in range(1,n):
 area=int(stats[i,cv2.CC_STAT_AREA]);x,y,bw,bh=[int(stats[i,k]) for k in (0,1,2,3)]
 if area>=5 and area<=900 and x>int(w*.84):
  islands.append({"label":i,"area":area,"bbox":[x,y,bw,bh]})
entry={"version":"v2746","baseline":"v2744","family":"pending-13","source":str(SRC),
 "original_png_SHA256":sha(SRC),"photo_source_actual_bottle":"v2696 official 30mL serum photo04",
 "red_decor_detection_candidates":islands,
 "status":"HOLD_NO_SAFE_DECOR_REMOVAL","retail_approved":False,
 "full_white_dropper_intact_required":True,
 "commercial_photo_rights_verified":False,
 "exact_owned_stock_packaging_verified":False}
if islands:
 selected=np.uint8(np.isin(labels,[r["label"] for r in islands]))*255
 patch=cv2.dilate(selected,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)),iterations=1)
 # Protect center and bottom by restricting to eligibility mask.
 patch=np.where((xx>=int(w*.84))&(yy<=int(h*.25)),patch,0).astype(np.uint8)
 original_count=int(np.count_nonzero(alpha>=128))
 new_alpha=np.where(patch>0,0,alpha).astype(np.uint8)
 changed=int(np.count_nonzero((alpha>=128)&(new_alpha<128)))
 if 8<=changed<=min(2500,int(original_count*.025)):
  arr[:,:,3]=new_alpha
  result=Image.fromarray(arr,"RGBA")
  png=OUT/"01-real-serum-30mL-small-artifact-clean-transparent-QA.png"
  result.save(png,optimize=True)
  board=Image.new("RGB",(1080,1080),"white")
  d=ImageDraw.Draw(board)
  d.text((88,77),"MISSHA",font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",37),fill="#57333f")
  d.text((88,132),"PDRN NAD+ Firming Repair Serum 30mL",font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",26),fill="#7b6670")
  fit=ImageOps.contain(result,(820,825),Image.Resampling.LANCZOS)
  board.paste(fit,((1080-fit.width)//2,180+(825-fit.height)//2),fit)
  jpg=OUT/"01-serum-dropper-intact-decoration-removed-1080-QA.jpg"
  board.save(jpg,"JPEG",quality=92,optimize=True,subsampling=0)
  assert jpg.stat().st_size<2000000
  entry.update({"status":"SMALL_DECOR_ALPHA_REMOVED_VISUAL_QA_REQUIRED","changed_opaque_px":changed,
    "result_png":png.name,"result_jpg":jpg.name,
    "png_sha256":sha(png),"jpg_sha256":sha(jpg),
    "jpg_bytes":jpg.stat().st_size})
 else:
  entry["reason"]=f"Unsafe alpha change size: {changed}"
else:
 entry["reason"]="No tiny detached red blob meeting restricted upper-right detection"
# Proof shows original transparent alpha vs candidate, preserving original.
proof=Image.new("RGB",(1540,640),"#f0efee");d=ImageDraw.Draw(proof)
f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",21)
d.text((15,13),"v2746 MISSHA 30mL original alpha vs micro-cleaned candidate | NOT RETAIL",font=f,fill="#333333")
for i,(label,media) in enumerate([("UNCHANGED ISNET INPUT",source),("MICRO-CLEANED",Image.open(OUT/entry["result_png"]).convert("RGBA") if entry.get("result_png") else source)]):
 white=Image.new("RGBA",media.size,(255,255,255,255));white.alpha_composite(media)
 photo=ImageOps.contain(white.convert("RGB"),(600,515),Image.Resampling.LANCZOS)
 xx=80+i*750;proof.paste(photo,(xx,70))
 d.text((xx,596),label,font=f,fill="#333333")
contact=OUT/"v2746-micro-cleanup-comparison.jpg"
proof.save(contact,"JPEG",quality=84,optimize=True)
(OUT/"v2746-proof.b64.txt").write_text(base64.b64encode(contact.read_bytes()).decode())
manifest={
 "version":"v2746","family":"pending-13","baseline":"v2744",
 "new_real_photo_alpha_refinement":bool(entry.get("result_png")),
 "no_new_AI_segmentation":True,"old_v2744_cutout_unmodified":True,
 "old_55_public_URLs_unchanged":True,"old_11_approved_product_families_unchanged":True,
 "photo_reuse_rights_verified":False,"MK_original_logo_authenticated":False,
 "new_retail_approval":False,"final_XLSX_shared":False,"attempt":entry}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2746","result":entry["status"],
"artifact_removed":bool(entry.get("result_png")),"sale_approved":False}))
