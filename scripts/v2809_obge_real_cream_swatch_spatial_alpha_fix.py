#!/usr/bin/env python3
"""v2809 isolated alpha correction: OBgE Oil Control Finisher 5g.
Remove only the off-object white cream swipe left of the actual BEIGE compact,
identified by dense non-white tan/brown product pixels. No object redraw, no
made-up product pixels. Preserve v2808 original 5 official JPG source frames.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import numpy as np,hashlib,base64,json
ROOT=Path("qa-review")
SRC=ROOT/"v2808-obge-oil-finisher-five-official-scenes-true-alpha-QA"
OUT=ROOT/"v2809-obge-finisher-genuine-product-left-swipe-alpha-correction"
assert SRC.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
original=SRC/"01-OBgE-5g-real-transparent-product-cutout-QA.png"
prior_hero=SRC/"01-OBgE-5g-true-alpha-white-hero-1080-QA.jpg"
assert original.is_file() and prior_hero.is_file()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with Image.open(original) as im:
 im.load()
 assert im.format=="PNG" and im.mode=="RGBA"
 rgba=np.array(im)
H,W=rgba.shape[:2]
rgb=rgba[:,:,:3].astype(np.int16)
a=rgba[:,:,3].astype(np.float32)
# Tan/brown compact and dark OBgE puff are visually colored/darker than cream
# smear; use this only to locate body, never to synthesize a new edge.
r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2]
colored=(a>=100)&(
   ((r<235)&(g<224)&(b<213)&((r-b)>12)) |
   ((r<145)&(g<145)&(b<145))
)
count_col=colored.sum(axis=0)
strong=np.where(count_col>=max(9,int(H*.027)))[0]
assert len(strong)>90,"No continuous dense dark beige product component found"
left_edge=int(strong.min())
right_edge=int(strong.max())
# Crop off the white smear left of the verified product's beige case,
# while keeping ~12px margin and 14px smooth alpha edge transition.
cut=max(0,left_edge-12)
assert int(W*.10)<cut<int(W*.53),(W,left_edge,cut)
removed_strong=int(colored[:,:cut].sum())
total_strong=int(colored.sum())
assert removed_strong<=max(500,int(total_strong*.025)),(removed_strong,total_strong,cut)
corrected=rgba.copy()
feather=18
corrected[:,:max(0,cut-feather),3]=0
for x in range(max(0,cut-feather),cut):
 factor=(x-(cut-feather)+1)/(feather+1)
 corrected[:,x,3]=np.uint8(np.rint(corrected[:,x,3].astype(np.float32)*factor))
fixed=Image.fromarray(corrected,"RGBA")
bbox=fixed.getchannel("A").getbbox()
assert bbox
fixed=fixed.crop(bbox)
png=OUT/"01-OBgE-5g-beige-compact-only-transparent-QA.png"
fixed.save(png,optimize=True)
fontfile="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
reg=ImageFont.truetype(fontfile,24)
bold=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",34)
white=Image.new("RGB",(1080,1080),"#ffffff")
d=ImageDraw.Draw(white)
d.rounded_rectangle((55,55,1025,1025),radius=34,outline="#e9e3e0",width=2)
d.text((95,103),"OBgE",font=bold,fill="#342e2a")
d.text((95,161),"Oil Control Finisher 5g",font=reg,fill="#776d68")
fit=ImageOps.contain(fixed,(848,776),Image.Resampling.LANCZOS)
white.paste(fit,((1080-fit.width)//2,214+(777-fit.height)//2),fit)
d.text((95,982),"PHOTO CUTOUT, NO PRODUCT REDRAW | QA ONLY",font=reg,fill="#948b86")
jpg=OUT/"01-OBgE-5g-clean-compact-hero-1080-QA.jpg"
white.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
with Image.open(jpg) as verify:
 verify.load();assert verify.size==(1080,1080) and verify.format=="JPEG"
assert jpg.stat().st_size<2_000_000
comparison=Image.new("RGB",(1510,565),"#f1f0ee")
c=ImageDraw.Draw(comparison)
c.text((20,16),"v2809 OBgE 5g: prior alpha (left) vs spatially corrected product-only candidate (right)",font=reg,fill="#2e2b29")
with Image.open(prior_hero) as im:
 before=im.convert("RGB").resize((480,480),Image.Resampling.LANCZOS)
with Image.open(jpg) as im:
 after=im.convert("RGB").resize((480,480),Image.Resampling.LANCZOS)
comparison.paste(before,(20,58))
comparison.paste(after,(1005,58))
c.text((520,105),f"Product body left x={left_edge}",font=reg,fill="#3a3a38")
c.text((520,152),f"Mask cut boundary x={cut}",font=reg,fill="#3a3a38")
c.text((520,199),f"Removed colored pixels: {removed_strong}",font=reg,fill="#3a3a38")
c.text((520,246),"Original five brand JPGs unchanged",font=reg,fill="#3a3a38")
proof=OUT/"v2809-alpha-before-after.jpg"
comparison.save(proof,"JPEG",quality=84,optimize=True)
(OUT/"v2809-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={
 "version":"v2809","baseline":"v2808","family":"pending-09",
 "source_alpha_png":str(original),"source_alpha_sha256":sha(original),
 "source_JPG_hero":str(prior_hero),"source_JPG_sha256":sha(prior_hero),
 "actual_new_alpha_png":png.name,"actual_new_1080_jpg":jpg.name,
 "new_jpg_sha256":sha(jpg),"new_jpg_bytes":jpg.stat().st_size,
 "source_size":[W,H],"detected_compact_left_x":left_edge,
 "detected_compact_right_x":right_edge,"alpha_removed_at_left_boundary":cut,
 "colored_object_pixels_removed":removed_strong,"colored_object_pixels_total":total_strong,
 "method":"REMOVE_OFF_OBJECT_PALE_LEFT_CREAM_SWIPE_WITH_BEIGE_COMPACT_DENSITY_AND_SOFT_ALPHA_RAMP",
 "not_a_new_independent_photo":True,"product_pixels_fabricated":False,
 "source_5_official_brand_photos_untouched":True,
 "all_11_approved_product_groups_untouched":True,
 "existing_55_public_urls_untouched":True,
 "photo_usage_license_proven":False,
 "owned_inventory_exact_edition_proven":False,
 "MK_original_logo_authenticated":False,
 "retail_approved":False,"human_visual_QA":"NOT_YET_REVIEWED",
 "final_xlsx_shared":False
}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2809","previous_png_preserved":True,
"new_png_saved":png.is_file(),"new_jpg_saved":jpg.is_file(),
"cut_left_x":cut,"strong_object_pixels_removed":removed_strong,"sales_approved":0}))
