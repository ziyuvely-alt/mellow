#!/usr/bin/env python3
"""v2872: Non-destructive, single-pass geometric alpha trim on v2871 MISSHA
legacy M Perfect Cover BB 50ml No.25 ONLY.

Visual QA identified an unsightly pale/grey residue in No.25 U2Net mask
belonging to a beige product-texture background, not the bottle.
Use old source RGB exactly; change ONLY alpha outside conservative
red-tube and gold-pump envelope. Keep the v2871 rejected source intact,
keep No.21 untouched and don't redo previously-good No.23.
No image-rights claim, sales release, or 55 public URL changes.
"""
from pathlib import Path
from hashlib import sha256
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import json,numpy as np
R=Path("qa-review")
SRC=R/"v2871-missha-legacy-bb-21-25-gold-pump-u2net-QA"
OUT=R/"v2872-missha-bb-no25-background-ghost-geometry-alpha-QA"
assert not OUT.exists()
manifest=json.loads((SRC/"manifest.json").read_text())
assert manifest["version"]=="v2871" and manifest["new_alpha_pngs"]==2
n25=next(x for x in manifest["rows"] if x["shade"]=="25")
n21=next(x for x in manifest["rows"] if x["shade"]=="21")
assert n25["status"]=="ALPHA_TECHNICAL_CANDIDATE_HOLD_LICENSE_STOCK"
sha=lambda p:sha256(p.read_bytes()).hexdigest()
p=Path(n25["png"])
assert p.is_file() and sha(p)==n25["png_sha256"]
with Image.open(p) as im:
 im.load()
 assert im.mode=="RGBA"
 before=im.copy()
rgb=np.asarray(before)[:,:,:3].copy()
old=np.asarray(before.getchannel("A")).copy()
h,w=old.shape
# v2871 crops the old source No25 1500x1500 bbox with 18px padding.
# Coordinates below are in ORIGINAL photo coordinates, converted to the
# immutable cropped alpha frame using the original mask bounding box.
x0=max(0,n25["mask_bbox"][0]-18)
y0=max(0,n25["mask_bbox"][1]-18)
assert (x0,y0)==(277,103),(x0,y0)
assert 900<=w<=950 and 1380<=h<=1410,(w,h)
# Conservatively extend the true old red tube/gold clear pump envelope.
# This is an explicit shape-limited cleanup of BACKGROUND, not a new
# image-generation attempt. The photo RGB/lighting are untouched.
anchors=[
 (100,465,1020),    # just above true cap crimp, generous horizontal margin
 (210,465,1020),    # upper crimson tube
 (380,472,1010),
 (600,495,1000),
 (800,528,990),
 (990,552,959),    # tube taper approaching gold collar
 (1040,572,942),
 (1150,566,940),   # chrome collar + gold pump
 (1420,567,925),   # transparent lower nozzle
 (1500,567,925),
]
rows_orig=np.arange(h,dtype=np.float32)+y0
left=np.interp(rows_orig,[a[0] for a in anchors],[a[1] for a in anchors])-x0
right=np.interp(rows_orig,[a[0] for a in anchors],[a[2] for a in anchors])-x0
# Bilateral 4px feather at silhouette limits, preserving pixel-accurate
# input image RGB; pure white opaque background does not get invented.
x=np.arange(w,dtype=np.float32)[None,:]
allow_l=np.clip((x-left[:,None]+4)/8,0,1)
allow_r=np.clip((right[:,None]-x+4)/8,0,1)
geometry=(allow_l*allow_r).astype(np.float32)
# Keep the absolutely lowest y-pixels of the pump only inside its cone.
after=np.rint(old.astype(np.float32)*geometry).astype(np.uint8)
removed=int(np.count_nonzero((old>127)&(after<127)))
removed_equiv=float(np.sum(old.astype(np.int32)-after.astype(np.int32))/255.)
changed=int(np.count_nonzero(old!=after))
assert changed>10 and removed_equiv>50 and changed<old.size*.27,(changed,removed_equiv)
assert np.array_equal(rgb,np.asarray(before)[:,:,:3])
# Exact label, red tube, chrome collar and center nozzle MUST remain.
probes=[("printed_no25",750,685),("red_tube",760,450),("cap_seal",740,155),
        ("gold_collar",750,1080),("clear_pump_tip",750,1300)]
alpha_probe={}
for name,ox,oy in probes:
 cx=int(ox-x0);cy=int(oy-y0)
 assert 0<=cx<w and 0<=cy<h
 v0=int(old[cy,cx]);v1=int(after[cy,cx])
 alpha_probe[name]={"before":v0,"after":v1}
 assert v0>=75 and v1>=75 and abs(v0-v1)<=1,(name,v0,v1)
# If the material in original background near smear remains foreground,
# record ratio; no automated approval. This check is intentionally coarse.
smear=[(350,790),(1110,760),(1020,980),(400,1050)]
background_probes={}
for ox,oy in smear:
 cx=int(ox-x0);cy=int(oy-y0)
 if 0<=cx<w and 0<=cy<h:
  background_probes[f"{ox},{oy}"]={"before":int(old[cy,cx]),"after":int(after[cy,cx])}
OUT.mkdir(parents=True)
corrected=Image.fromarray(np.dstack((rgb,after)),"RGBA")
png=OUT/"MISSHA-No25-legacy-red-gold-full-original-RGB-ghost-trim-alpha-QA.png"
corrected.save(png,optimize=True)
bbox=corrected.getchannel("A").getbbox()
assert bbox and bbox[1]<70 and bbox[3]>h-80
isolated=corrected.crop(bbox)
fit=ImageOps.contain(isolated,(850,950),Image.Resampling.LANCZOS)
hero=Image.new("RGB",(1080,1080),"white")
hero.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2),fit.getchannel("A"))
jpg=OUT/"MISSHA-No25-legacy-ghost-clean-1080-QA.jpg"
hero.save(jpg,"JPEG",quality=94,subsampling=0,optimize=True)
with Image.open(jpg) as test:
 test.load();assert test.format=="JPEG" and test.size==(1080,1080)
assert jpg.stat().st_size<2_000_000
# Dark/light checker proof shows faint residual hue which white hero hides.
def checker(image):
 canvas=Image.new("RGBA",image.size,"#F4EEF3")
 d=ImageDraw.Draw(canvas)
 step=max(18,image.width//34)
 for y in range(0,image.height,step):
  for x in range(0,image.width,step):
   if (x//step+y//step)%2:d.rectangle((x,y,x+step-1,y+step-1),fill="#BEB9C9")
 canvas.alpha_composite(image)
 return canvas.convert("RGB")
F="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n:ImageFont.truetype(F,n)
board=Image.new("RGB",(1650,695),"#F3EFF2")
d=ImageDraw.Draw(board)
d.text((16,12),"v2872 No.25  |  ORIGINAL RGB  |  RESIDUE TRIM  |  WHITE HERO  |  QA ONLY",font=ft(24),fill="#403546")
pictures=[checker(before),checker(corrected),hero]
for i,img in enumerate(pictures):
 tile=ImageOps.contain(img,(515,580),Image.Resampling.LANCZOS)
 board.paste(tile,(22+545*i+(515-tile.width)//2,62+(580-tile.height)//2))
d.text((22,650),f"Alpha changed {changed} px | removed ~{int(removed_equiv)} opaque equivalents | no retouch RGB",font=ft(18),fill="#63566B")
contact=OUT/"v2872-legacy-no25-original-vs-clean-vs-white-qa.jpg"
board.save(contact,"JPEG",quality=90,optimize=True)
assert sha(p)==n25["png_sha256"]
assert sha(Path(n21["png"]))==n21["png_sha256"]
report={"version":"v2872","baseline":"v2871","family":"pending-03",
 "product":"MISSHA M Perfect Cover BB Cream 50mL No.25 legacy red gold pump",
 "attempt":"single deterministic alpha-only background residue geometry cleanup",
 "new_png":str(png),"new_png_sha256":sha(png),
 "new_JPG_1080":str(jpg),"new_JPG_sha256":sha(jpg),
 "new_jpg_bytes":jpg.stat().st_size,
 "original_v2871_No25_png_SHA256":n25["png_sha256"],
 "original_v2871_No21_png_SHA256":n21["png_sha256"],
 "input_original_RGB_untouched":True,"all_older_assets_preserved":True,
 "alpha_changed_pixels":changed,"removed_opaque_pixels":removed,
 "removed_alpha_255_equivalent":round(removed_equiv,2),
 "product_foreground_probes":alpha_probe,"background_artifact_probes":background_probes,
 "QA_contact":str(contact),"QA_contact_SHA256":sha(contact),
 "visual_edge_review_pending":True,"current_status":"TECHNICAL_ALPHA_REVISION_HOLD_FINAL_VISUAL",
 "owned_edition_verified":False,"commercial_photo_license_verified":False,
 "original_MK_logo_verified":False,"sale_approved":False,
 "new_public_URLs":0,"existing_55_public_URLs_unchanged":True,
 "existing_11_approved_families_preserved":True,
 "final_spreadsheet_shared":False,
 "next":"Review checker background residue and gold nozzle at 100%. If any haze persists, don't re-run geometric trim; move to clean No25 image with licensed source. Then prepare separate No21/No23/No25 source-verified option QA cards without revisiting original search."}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
print(json.dumps({"v":"v2872","new_png":str(png),"new_JPG":str(jpg),
 "alpha_changed":changed,"removed":removed,"source_changed":0,"approved":False}))
