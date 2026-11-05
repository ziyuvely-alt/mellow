#!/usr/bin/env python3
"""v2857: alternative real OBgE 300mL cutout from preserved clean official beige photo.
Abandon v2856 diagonal-clipped contour candidate, do not repeat geometric clipping.
CV GrabCut with probable foreground and hard central product seeds.
Source RGB preserved, no invented packaging or AI-generated product pixels.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from hashlib import sha256
import numpy as np,cv2,json

R=Path("qa-review")
SOURCE=R/"v2670-obge-300ml-distinct-official-photo-qa"/"02-official-beige-packshot-distinct-QA.jpg"
HISTORY=R/"v2670-obge-300ml-distinct-official-photo-qa"/"manifest.json"
OUT=R/"v2857-obge300ml-official-beige-source-true-alpha-recovery-QA"
assert SOURCE.is_file() and HISTORY.is_file() and not OUT.exists()
history=json.loads(HISTORY.read_text())
known=next(x["sha256"] for x in history["frames"] if x["frame"]==2)
sha=lambda p:sha256(p.read_bytes()).hexdigest()
assert sha(SOURCE)==known
source_sha=sha(SOURCE)
with Image.open(SOURCE) as im:
 im.load();assert im.size==(1080,1080) and im.format=="JPEG"
 image=np.array(im.convert("RGB"))
H,W=image.shape[:2]
# Beige-background source: isolate the actual complete 300mL pump and bottle.
# Conservative rectangle includes all pump tip, shoulders and bottle base.
mask=np.zeros((H,W),np.uint8)
mask[159:935,320:775]=cv2.GC_PR_FGD
# sure original product pixels (pump body and central label region)
mask[398:775,468:614]=cv2.GC_FGD
mask[288:360,514:598]=cv2.GC_FGD
mask[212:232,523:626]=cv2.GC_FGD
# central beige background around figure is probable BG, not FG
mask[159:935,320:775][mask[159:935,320:775]==cv2.GC_PR_FGD]=cv2.GC_PR_BGD
# very central hard FG seeds are preserved
mask[398:775,468:614]=cv2.GC_FGD
mask[288:360,514:598]=cv2.GC_FGD
mask[212:232,523:626]=cv2.GC_FGD
bg=np.zeros((1,65),np.float64);fg=np.zeros((1,65),np.float64)
bgr=cv2.cvtColor(image,cv2.COLOR_RGB2BGR)
cv2.grabCut(bgr,mask,None,bg,fg,8,cv2.GC_INIT_WITH_MASK)
foreground=np.where((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD),1,0).astype(np.uint8)
# Keep connected original product only. Mask regions outside original rect remain black.
count,label,stats,cent=cv2.connectedComponentsWithStats(foreground,8)
candidates=[(int(stats[i,cv2.CC_STAT_AREA]),i) for i in range(1,count)]
assert candidates,"No actual product extracted"
size,index=max(candidates)
binary=(label==index).astype(np.uint8)*255
kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
binary=cv2.morphologyEx(binary,cv2.MORPH_CLOSE,kernel,iterations=1)
clean=cv2.GaussianBlur(binary,(5,5),1.0)
# Minor BG alpha edges are softly anti-aliased; no actual RGB modification.
x,y,w,h=cv2.boundingRect((binary>127).astype(np.uint8))
core_alpha=int(clean[550,535])
assert 180<=w<=490 and 520<=h<=850,(x,y,w,h)
assert 350<=x<=525 and 155<=y<=365,(x,y,w,h)
assert core_alpha>=240
assert int(np.count_nonzero(binary[205:360,:]))>=900
assert int(np.count_nonzero(binary[705:880,:]))>=4000
assert size>=40000
product=Image.fromarray(np.dstack([image,clean]),"RGBA")
OUT.mkdir()
png=OUT/"01-OBgE300mL-official-600px-native-packshot-clean-TRUE-ALPHA-QA.png"
product.crop((x-15,y-15,x+w+15,y+h+15)).save(png,optimize=True)
with Image.open(png) as saved:
 saved.load();actual=saved.convert("RGBA")
 assert saved.mode=="RGBA" and max(saved.size)<=1080
canvas=Image.new("RGB",(1080,1080),"white")
fitted=ImageOps.contain(actual,(900,950),Image.Resampling.LANCZOS)
canvas.paste(fitted,((1080-fitted.width)//2,55+(950-fitted.height)//2),fitted.getchannel("A"))
jpg=OUT/"01-OBgE300mL-clean-official-photo-hero-1080-QA.jpg"
canvas.save(jpg,"JPEG",quality=94,optimize=True,subsampling=0)
with Image.open(jpg) as img:
 img.load();assert img.size==(1080,1080)
assert jpg.stat().st_size<2_000_000
font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
f=lambda a,b=False:ImageFont.truetype(bold if b else font,a)
board=Image.new("RGB",(1790,665),"#f3f0ee");d=ImageDraw.Draw(board)
d.text((22,12),"v2857 OBgE 300mL | preserved official photo > mask > new QA hero (NOT SALES)",font=f(23,True),fill="#393139")
original=Image.fromarray(image,"RGB")
for k,obj in enumerate([original,Image.fromarray(binary).convert("RGB"),canvas]):
 preview=ImageOps.contain(obj,(555,550),Image.Resampling.LANCZOS)
 board.paste(preview,(18+595*k+(555-preview.width)//2,65+(550-preview.height)//2))
d.text((20,620),"SOURCE: Native 600px, resized in old QA",font=f(18),fill="#62555f")
d.text((610,620),"GrabCut mask: explicit product geometry",font=f(18),fill="#62555f")
d.text((1215,620),"NEW HERO: complete original product",font=f(18),fill="#62555f")
visual=OUT/"v2857-three-stage-product-visual-QA.jpg"
board.save(visual,"JPEG",quality=85,optimize=True)
assert sha(SOURCE)==source_sha
report={"version":"v2857","baseline":"v2856","family":"pending-22",
"product":"OBgE Max Waterful Sun Cream 300mL",
"prior_v2856_visual_status":"REJECT_FOR_SALES_NEW_ARTIFICIAL_DIAGONAL_RIGHT_SHOULDER",
"replacement_method":"OpenCV GrabCut from genuine preserved official beige-backdrop packshot, not prior shadowed mask",
"source":str(SOURCE),"source_sha256":source_sha,
"source_native_px_reported":[600,600],"qa_cached_source_px":[1080,1080],
"original_RGB_unchanged":True,"new_AI_segmentation_models_used":0,
"mask_algorithm":"grabcut with hard FG seeds and connected-component hold gates",
"mask_bbox_xywh":[x,y,w,h],"foreground_area":int(size),"center_alpha":core_alpha,
"qa_original_PNG":png.name,"qa_original_PNG_sha256":sha(png),
"new_JPG":jpg.name,"JPG_sha256":sha(jpg),"JPG_bytes":jpg.stat().st_size,
"prior_sources_modified":0,"prior_11_sales_approved_families_unchanged":True,
"prior_55_public_URLs_unchanged":True,
"commercial_photo_usage_permission_verified":False,"owned_stock_packaging_verified":False,
"original_round_MK_logo_verified":False,"closeup_visual_QA":"PENDING",
"photo_source_has_been_upscaled_from_native":True,
"sale_approved_new":0,"final_XLSX_shared":False,
"next":"Compare full resolution edges for white/beige halos, confirm native-600 softness and package before any approval."
}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2857","success":True,"box":[x,y,w,h],
"mask_area":size,"jpg_bytes":jpg.stat().st_size,"approved":0}))
