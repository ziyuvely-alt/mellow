#!/usr/bin/env python3
"""v2860: non-destructive true-alpha mask QA from already SHA-verified CLIO
Mesh Blur 15g+refill merchant shade photos. No source photo download,
fabricated swatches, publication, MK logo or commercial-use approval.
Generate only separate QA images; never overwrite v2849 or published files.
"""
from pathlib import Path
from hashlib import sha256
from PIL import Image, ImageDraw, ImageFont, ImageOps
import json
import cv2
import numpy as np

R = Path("qa-review")
OLD = R/"v2849-clio-meshblur-15g-refill-three-stock-shades-sourceQA"
OUT = R/"v2860-clio-meshblur-three-truealpha-source-variants-QA"
assert not OUT.exists(), "Run must never overwrite previous QA"
manifest=json.loads((OLD/"manifest.json").read_text())
assert manifest["family"]=="pending-07"
by_shade={x["shade"]:x for x in manifest["variants"]}
assert set(by_shade)=={"19C","19N","21N"}
sha=lambda p: sha256(p.read_bytes()).hexdigest()
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def ft(n,b=False):return ImageFont.truetype(BOLD if b else FONT,n)
OUT.mkdir(parents=True)
records=[]
proof_tiles=[]
for shade in ("19C","19N","21N"):
 row=by_shade[shade]
 src=OLD/row["file"]
 data={"shade":shade,"variant_identity":row["shade_name"],"source":str(src),
       "source_sha256_expected":row["jpg_sha256"],"source_modified":False,
       "sales_approved":False,"status":"PENDING"}
 try:
  assert src.is_file() and sha(src)==row["jpg_sha256"]
  with Image.open(src) as im:
   im.load()
   assert im.size==(1080,1080) and im.format=="JPEG"
   original=im.convert("RGB")
  rgb=np.asarray(original).copy()
  mask=np.full((1080,1080),cv2.GC_BGD,np.uint8)
  # The product occupies a known centered portion of the preserved exact-variant
  # 1080px photograph. The large surrounding 100% white pixels are background.
  mask[220:955,175:965]=cv2.GC_PR_BGD
  patch=rgb[220:955,175:965]
  nearwhite=np.min(patch,axis=2)>=251
  colored=(np.min(patch,axis=2)<244)
  cm=mask[220:955,175:965]
  cm[colored]=cv2.GC_PR_FGD
  cm[nearwhite]=cv2.GC_BGD
  # Hard foreground seeds are pixels visibly inside the actual compact/cream,
  # never a hand-drawn product-shaped silhouette.
  for y0,y1,x0,x1 in [
      (360,415,450,650),
      (452,490,400,640),
      (560,615,430,605),
      (670,713,423,555),
      (686,725,700,742),
      (748,780,726,763)]:
   mask[y0:y1,x0:x1]=cv2.GC_FGD
  # Keep pale ring from getting treated as white interior.
  mask[640:670,342:366]=cv2.GC_FGD
  mask[765:790,495:525]=cv2.GC_FGD
  bg=np.zeros((1,65),np.float64)
  fg=np.zeros((1,65),np.float64)
  cv2.grabCut(cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR),mask,None,bg,fg,7,cv2.GC_INIT_WITH_MASK)
  fmask=np.where((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD),255,0).astype(np.uint8)
  n,lab,stat,_=cv2.connectedComponentsWithStats(fmask,8)
  # Product includes compact plus an adjacent independent real cream swipe.
  # Keep only major original-photo components. Do not invent texture.
  valid=[i for i in range(1,n) if stat[i,cv2.CC_STAT_AREA]>=700]
  assert valid,"No usable original foreground"
  binary=np.isin(lab,valid).astype(np.uint8)*255
  # Fill only tiny disconnected holes (<48px) resulting from JPG noise.
  inv=255-binary
  n2,lab2,st2,_=cv2.connectedComponentsWithStats(inv,8)
  for i in range(1,n2):
   if st2[i,cv2.CC_STAT_AREA]<=48:
    binary[lab2==i]=255
  x,y,w,h=cv2.boundingRect((binary>127).astype(np.uint8))
  area=int((binary>127).sum())
  assert 180<=x<=420 and 250<=y<=440,(shade,x,y)
  assert 430<=w<=800 and 360<=h<=700,(shade,w,h)
  assert 80000<=area<=420000,(shade,area)
  assert all(binary[cy,cx]>127 for cy,cx in [(394,550),(580,505),(700,725)]),(shade,"lost central product")
  alpha=cv2.GaussianBlur(binary,(3,3),0.65)
  crop=(max(0,x-20),max(0,y-20),min(1080,x+w+20),min(1080,y+h+20))
  original_rgba=Image.fromarray(np.dstack((rgb,alpha)),"RGBA")
  trim=original_rgba.crop(crop)
  png=OUT/f"CLIO-MeshBlur-{shade}-original-RGB-truealpha-QA.png"
  trim.save(png,optimize=True)
  # On white, preserve exact original source RGB in all opaque product pixels.
  hero=Image.new("RGB",(1080,1080),"white")
  shown=ImageOps.contain(trim,(875,870),Image.Resampling.LANCZOS)
  hero.paste(shown,((1080-shown.width)//2,106+(870-shown.height)//2),shown.getchannel("A"))
  jpg=OUT/f"CLIO-MeshBlur-{shade}-1080-clear-hero-QA.jpg"
  hero.save(jpg,"JPEG",quality=94,optimize=True,subsampling=0)
  assert jpg.stat().st_size<2_000_000
  with Image.open(jpg) as ck:
   assert ck.format=="JPEG" and ck.size==(1080,1080)
  # Contrast-backed QA image detects white-edge halos (NOT public art).
  checker=Image.new("RGBA",(1080,1080),"#f9f1f2")
  dr=ImageDraw.Draw(checker)
  for yy in range(0,1080,30):
   for xx in range(0,1080,30):
    if (xx//30+yy//30)%2:
     dr.rectangle((xx,yy,xx+29,yy+29),fill="#dcdce2")
  layer=Image.new("RGBA",(1080,1080),(0,0,0,0))
  layer.paste(shown,((1080-shown.width)//2,106+(870-shown.height)//2),shown)
  checker.alpha_composite(layer)
  proof=OUT/f"CLIO-MeshBlur-{shade}-edge-checker-QA.jpg"
  checker.convert("RGB").save(proof,"JPEG",quality=88,optimize=True)
  assert sha(src)==row["jpg_sha256"]
  data.update(status="TRUE_ALPHA_TECHNICAL_CANDIDATE_HOLD_VISUAL",
              mask_area_px=area,mask_bbox=[x,y,w,h],
              original_PNG=str(png),png_sha256=sha(png),
              new_1080_JPG=str(jpg),jpg_sha256=sha(jpg),
              jpg_bytes=jpg.stat().st_size,checker_QA=str(proof),
              visual_closeup_review_required=True,
              commercial_photo_reuse_rights_verified=False,
              exact_user_owned_giftset_packaging_verified=False)
  proof_tiles.append((shade, original.copy(), checker.convert("RGB").copy(), hero.copy()))
 except Exception as e:
  data.update(status="HOLD_ALPHA_EXTRACTION_UNRELIABLE",error=str(e)[:250])
  print("HOLD",shade,str(e)[:200])
  # One shade failing never blocks the other real-photo candidates.
 records.append(data)
# Compact proof compares ORIGINAL / MASK / WHITE HERO separately per distinct
# shade, not 3 copies of the same photo or invented shade-color patches.
if proof_tiles:
 board=Image.new("RGB",(1600,len(proof_tiles)*550+90),"#f3f1f2")
 d=ImageDraw.Draw(board)
 d.text((22,10),"v2860 CLIO MESH BLUR: EXACT SHADE ORIGINAL -> ALPHA -> WHITE HERO  |  QA ONLY",
        font=ft(23,True),fill="#363239")
 for i,(shade,orig,checker,hero) in enumerate(proof_tiles):
  y=55+i*550
  for j,pic in enumerate((orig,checker,hero)):
   pv=pic.resize((510,510),Image.Resampling.LANCZOS)
   board.paste(pv,(20+j*525,y))
  d.text((30,y+482),shade+"    SOURCE",font=ft(17,True),fill="#342D39")
  d.text((555,y+482),shade+"    TRUE ALPHA",font=ft(17,True),fill="#342D39")
  d.text((1080,y+482),shade+"    HERO (QA)",font=ft(17,True),fill="#342D39")
 contact=OUT/"v2860-original-alpha-hero-three-shades-comparison-QA.jpg"
 board.save(contact,"JPEG",quality=88,optimize=True)
report={
 "version":"v2860","baseline":"v2859","family":"pending-07",
 "product":"CLIO Kill Cover Mesh Blur Cushion 15g + refill 15g",
 "input_source_manifest":str(OLD/"manifest.json"),
 "actual_stock_shades":["19C","19N","21N"],
 "per_shade":records,
 "output_usable_alpha_candidate_count":sum(r["status"].startswith("TRUE_ALPHA") for r in records),
 "output_held_count":sum(r["status"].startswith("HOLD") for r in records),
 "new_hero_JPGs":sum("new_1080_JPG" in r for r in records),
 "existing_v2849_source_files_rewritten":0,
 "existing_v2859_MISSHA_output_modified":False,
 "previous_11_published_families_unchanged":True,
 "previous_55_public_URLs_unchanged":True,
 "stock_package_or_contents_verified":False,
 "merchant_photo_usage_permission_verified":False,
 "original_round_MK_logo_authenticated":False,
 "new_sales_approved":0,"new_public_URLs":0,
 "final_spreadsheet_shared":False,
 "contact":str(OUT/"v2860-original-alpha-hero-three-shades-comparison-QA.jpg") if proof_tiles else None,
 "next":"Run visual QA at original resolution, especially lavender edges and cream swipe. Hold all retail publication until actual 15g+refill inventory, image reuse rights and original MK mark verified."
}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2860","candidate_shades":[x["shade"] for x in records if x["status"].startswith("TRUE_ALPHA")],
 "held_shades":[x["shade"] for x in records if x["status"].startswith("HOLD")],
 "new_JPGs":report["new_hero_JPGs"],"retail_approved":0},ensure_ascii=False))
