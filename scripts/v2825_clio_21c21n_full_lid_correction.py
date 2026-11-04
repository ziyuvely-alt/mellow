#!/usr/bin/env python3
"""v2825 exact-option CLIO Mini 5g lid-protection photo repair.
Prior 21C and 21N alpha cutouts clipped top of compact when source photo crop
began at y=365. This QA-only second source crop starts at y=145, then removes
peach-color texture swatch only in the top area while preserving real compact
pixels. No generated product data, no fake shade, no old asset changes.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont,ImageFilter
from rembg import remove,new_session
import numpy as np,cv2,json,hashlib,base64
ROOT=Path("qa-review")
OUT=ROOT/"v2825-clio-mini-5g-21C-21N-uncropped-top-edge-repair"
assert not OUT.exists();OUT.mkdir(parents=True)
SPECS=[
 ("21C Lingerie","v2822b-clio-original-mini-5g-21C-exact-variant-gallery-proof","02-21C-Lila-Beauty-exact-variant-QA.jpg","v2823-clio-mini-5g-21C-true-compact-alpha-QA","01-real-21C-mini5g-1080-hero-QA.jpg"),
 ("21N Linen","v2820-clio-mini-5g-Lila-21N-variant-photo-evidence","01-21N-variant-linked-Lila-5g-QA.jpg","v2821-clio-mini-5g-21N-true-compact-alpha-QA","01-real-21N-mini5g-1080-hero-QA.jpg")
]
REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False:ImageFont.truetype(BOLD if b else REG,n)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def render(img,shade,path):
 canvas=Image.new("RGB",(1080,1080),"white")
 d=ImageDraw.Draw(canvas)
 d.rounded_rectangle((52,50,1028,1028),radius=32,outline="#eee8e7",width=2)
 d.text((96,99),"CLIO",font=ft(43,True),fill="#333032")
 d.text((96,163),"THE ORIGINAL MINI 5g  |  "+shade,font=ft(26),fill="#676166")
 contained=ImageOps.contain(img,(870,778),Image.Resampling.LANCZOS)
 canvas.paste(contained,((1080-contained.width)//2,210+(778-contained.height)//2),contained)
 d.text((95,992),"INDEPENDENT SOURCE-PHOTO CUTOUT  |  QA ONLY",font=ft(18),fill="#93888d")
 canvas.save(path,"JPEG",quality=93,optimize=True,subsampling=0)
 assert path.stat().st_size<2000000
 with Image.open(path) as check:assert check.format=="JPEG" and check.size==(1080,1080)
session=new_session("isnet-general-use")
results=[]
for shade,base,srcfile,prior,priorfile in SPECS:
 source=ROOT/base/srcfile
 prev=ROOT/prior/priorfile
 assert source.is_file() and prev.is_file()
 with Image.open(source) as image:
  image.load();assert image.size==(1080,1080) and image.format=="JPEG"
  rgba=image.convert("RGBA")
 # substantially extend above prior y=365. Safely leaves compact lid in ROI.
 roi_xyxy=(130,135,1075,1067)
 roi=rgba.crop(roi_xyxy)
 info={"shade":shade,"source_photo":str(source),"source_sha256":sha(source),
  "previous_cutout":str(prev),"previous_sha256":sha(prev),
  "new_source_crop_xyxy":list(roi_xyxy),"retail_approved":False,
  "source_photo_unchanged":True,"status":"HOLD_CUTOUT_REVIEW"}
 try:
  fg=remove(roi,session=session,alpha_matting=True,
   alpha_matting_foreground_threshold=230,
   alpha_matting_background_threshold=15,
   alpha_matting_erode_size=3)
  if fg.mode!="RGBA":raise ValueError("No transparent cutout")
  rgb=np.asarray(roi.convert("RGB"),dtype=np.uint8)
  hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
  alpha=np.asarray(fg.getchannel("A"),dtype=np.uint8).copy()
  yy,xx=np.indices(alpha.shape)
  source_y=yy+roi_xyxy[1]
  source_x=xx+roi_xyxy[0]
  # The flat peach color fan extends over top-left background. Preserve compact
  # lid (grey/white, low saturation) and all lower cushion shade pixels.
  swatch=(source_y<540)&(hsv[:,:,0]>=3)&(hsv[:,:,0]<=22)&(hsv[:,:,1]>55)&(hsv[:,:,2]>120)
  # Remove only saturated peach area, never cushion surface below ~540px.
  alpha[swatch]=0
  # Remove tiny isolated alpha-only flecks from background. Keep compact and
  # puff as two independent large components if needed.
  binary=(alpha>=80).astype(np.uint8)
  component_count,components,stats,_=cv2.connectedComponentsWithStats(binary,connectivity=8)
  pieces=sorted([(i,int(stats[i,cv2.CC_STAT_AREA])) for i in range(1,component_count)
                 if stats[i,cv2.CC_STAT_AREA]>=100],key=lambda x:x[1],reverse=True)
  if not pieces or pieces[0][1]<12500:raise ValueError("No dominant real compact foreground component")
  keep={i for i,area in pieces if area>=pieces[0][1]*0.085}
  keepmask=np.isin(components,list(keep))
  alpha[~keepmask]=0
  alpha=cv2.GaussianBlur(alpha,(3,3),0)
  if not np.count_nonzero(alpha>25):raise ValueError("Removed all foreground pixels")
  fg_data=np.asarray(fg).copy()
  fg_data[:,:,3]=alpha
  segmented=Image.fromarray(fg_data,"RGBA")
  bbox=segmented.getchannel("A").getbbox()
  if bbox is None:raise ValueError("Empty final bounding box")
  coverage=float(np.mean(alpha>=128))
  # Avoid another falsely reported pass when top source border is still clipped.
  if bbox[1]<=16 or bbox[2]-bbox[0]<220 or bbox[3]-bbox[1]<230 or not(.08<coverage<.80):
    raise ValueError(f"Not safely separated: bbox={bbox}, mask={coverage:.3f}")
  actual=segmented.crop(bbox)
  dir=OUT/("21C" if shade.startswith("21C") else "21N");dir.mkdir()
  png=dir/"01-full-lid-real-compact-alpha-QA.png"
  jpg=dir/"01-corrected-full-lid-1080-JPG-QA.jpg"
  actual.save(png,optimize=True)
  render(actual,shade,jpg)
  info.update({"status":"FULL_LID_ALPHA_STAGED_DIRECT_VISUAL_QA_REQUIRED",
   "mask_coverage":round(coverage,4),"alpha_bbox":list(bbox),"kept_components":len(keep),
   "transparent_png":str(png.relative_to(OUT)),
   "jpg":str(jpg.relative_to(OUT)),"jpg_sha256":sha(jpg),"jpg_bytes":jpg.stat().st_size})
 except Exception as e:
  info.update({"status":"HOLD_MARGINS_OR_SEGMENTATION_FAILED","error_type":type(e).__name__,"error":str(e)[:270]})
 results.append(info)
board=Image.new("RGB",(1570,1080),"#f1f0ee")
d=ImageDraw.Draw(board)
d.text((18,12),"v2825 TOP-LID PHOTO REPAIR: ORIGINAL | PREVIOUS | NEW (QA ONLY)",font=ft(24,True),fill="#282628")
for idx,item in enumerate(results):
 y=62+idx*500
 for col,p in enumerate([Path(item["source_photo"]),Path(item["previous_cutout"]),OUT/item["jpg"] if item.get("jpg") else None]):
  if p is None:continue
  with Image.open(p) as im: tile=im.convert("RGB").resize((470,470),Image.Resampling.LANCZOS)
  board.paste(tile,(15+col*520,y))
 d.text((14,y+472),item["shade"]+" | "+item["status"],font=ft(17),fill="#343434")
proof=OUT/"v2825-original-old-versus-repaired-top-proof.jpg"
board.save(proof,"JPEG",quality=81,optimize=True)
(OUT/"v2825-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={"version":"v2825","baseline":"v2824",
 "variants_attempted":2,"physically_saved_new_cutout_pairs":sum(bool(x.get("jpg")) for x in results),
 "source_existing_originals_unchanged":True,
 "existing_21C_21N_23N_QA_artifacts_unchanged":True,
 "published_11_groups_unchanged":True,"published_55_urls_unchanged":True,
 "photo_redistribution_permissions_verified":False,"stock_editions_verified":False,
 "original_round_MK_logo_verified":False,"new_retail_approved":0,
 "final_xlsx_shared":False,"variants":results}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2825","new_cutout_png_jpg_pairs":manifest["physically_saved_new_cutout_pairs"],
"statuses":[x["status"] for x in results],"retail_approved":0}))
