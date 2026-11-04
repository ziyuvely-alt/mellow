#!/usr/bin/env python3
"""v2768 native 1:1 alpha-edge integrity QA on FOUR already-completed MISSHA
cover-lasting compact shade files. Only create contact proofs and metrics.
Do not regenerate, resize source alpha, edit product pixels, or publish.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json,hashlib,base64
R=Path("qa-review")
OUT=R/"v2768-missha-coverlasting-four-shade-native-edge-inspection"
assert not OUT.exists();OUT.mkdir(parents=True)
FILES={
"21":R/"v2748-missha-coverlasting-21-source01-round-compact-only/01-missha-N21-actual-compact-transparent-QA.png",
"23":R/"v2747-missha-coverlasting-23-source02-round-compact-qa/01-original-pink-compact-N23-transparent-QA.png",
"25":R/"v2750-missha-N25-N27-distinct-official-photo-cutout-QA/shade-25/01-original-25-isnet-true-alpha-QA.png",
"27":R/"v2750-missha-N25-N27-distinct-official-photo-cutout-QA/shade-27/01-original-27-isnet-true-alpha-QA.png"
}
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
f=lambda n,b=False:ImageFont.truetype(BOLD if b else FONT,n)
def checker(size):
 img=Image.new("RGBA",size,"#ffffff")
 d=ImageDraw.Draw(img)
 for y in range(0,size[1],20):
  for x in range(0,size[0],20):
   if ((x//20)+(y//20))%2:d.rectangle((x,y,x+19,y+19),fill="#d7d7d7")
 return img
def native_patch(img,at,sz=220):
 x,y=at
 box=(round(x-sz/2),round(y-sz/2),round(x+sz/2),round(y+sz/2))
 # Pillow transparent crop pads outside, preserves each actual source pixel 1:1.
 region=img.crop(box)
 background=checker((sz,sz))
 background.alpha_composite(region)
 return background.convert("RGB")
overview=Image.new("RGB",(2040,1170),"#f1f1f0")
od=ImageDraw.Draw(overview)
od.text((16,12),"v2768 FOUR EXISTING SHADE CUTOUTS / OVERVIEW SCALED | NO REGENERATION",font=f(23,True),fill="#292929")
detail=Image.new("RGB",(1120,1170),"#eeeeed")
dd=ImageDraw.Draw(detail)
dd.text((16,12),"v2768 TRUE 1:1 SOURCE-PIXEL ALPHA EDGE CROPS",font=f(23,True),fill="#292929")
results=[]
for i,(shade,source) in enumerate(FILES.items()):
 assert source.is_file(),source
 oldsha=sha(source)
 with Image.open(source) as pic:
  pic.load();assert pic.format=="PNG" and pic.mode=="RGBA"
  im=pic.copy()
 box=im.getchannel("A").getbbox()
 assert box is not None
 x0,y0,x1,y1=box
 width,height=im.size
 alpha=im.getchannel("A")
 area=sum(v>=128 for v in alpha.getdata())
 corners=[alpha.getpixel(p) for p in [(0,0),(width-1,0),(0,height-1),(width-1,height-1)]]
 crop_centres=[((x0+x1)//2,y0),((x0+x1)//2,y1-1),(x0,(y0+y1)//2),(x1-1,(y0+y1)//2)]
 res={"shade":shade,"original_source":str(source),"original_png_sha256":oldsha,
      "source_dimensions":[width,height],"mask_bbox":[x0,y0,x1,y1],
      "mask_nontrivial_coverage":round(area/(width*height),5),
      "four_corner_alpha":corners,
      "object_touches_original_pixel_frame":x0==0 or y0==0 or x1==width or y1==height,
      "native_pixel_crops_created":4,
      "retail_approved":False,
      "stock_rights_logo_hold":True}
 # Overview is deliberately marked scaled; copy of visual reference, not native-edge proof.
 bg=checker(im.size)
 bg.alpha_composite(im)
 display=ImageOps.contain(bg.convert("RGB"),(430,430),Image.Resampling.LANCZOS)
 pos=(18+i*505+(435-display.width)//2,70+(455-display.height)//2)
 overview.paste(display,pos)
 od.text((25+i*505,530),f"SHADE {shade} | ORIGINAL PNG {width}x{height}",font=f(21,True),fill="#333333")
 for col,(name,center) in enumerate(zip(["TOP","BOTTOM","LEFT","RIGHT"],crop_centres)):
  patch=native_patch(im,center,220)
  x=14+col*277
  y=68+i*273
  detail.paste(patch,(x,y))
  dd.text((x,y+226),f"N{shade} {name}",font=f(20,True),fill="#333333")
 results.append(res)
 assert sha(source)==oldsha
overview.save(OUT/"v2768-overview-scaled.jpg","JPEG",quality=84,optimize=True)
detail.save(OUT/"v2768-four-shade-native-edge-crops.jpg","JPEG",quality=92,optimize=True)
(OUT/"v2768-native-proof.b64.txt").write_text(base64.b64encode((OUT/"v2768-four-shade-native-edge-crops.jpg").read_bytes()).decode())
manifest={"version":"v2768","baseline":"v2767",
 "native_source_alpha_PNGs_opened_and_inspected_technically":4,
 "true_1_to_1_edge_crops_saved":16,
 "all_photo_original_bytes_unchanged":True,
 "new_product_pixel_generation":False,
 "manual_edge_visual_QA_required":True,
 "existing_11_sale_approved_families_unchanged":True,
 "existing_55_public_URLs_unchanged":True,
 "authentic_MK_original_logo_verified":False,
 "commercial_photo_reuse_license_verified":False,
 "real_21_23_25_27_stock_edition_verified":False,
 "new_retail_approvals":0,"final_XLSX_shared":False,
 "four_shade_results":results}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2768","native_edge_crops":16,"source_files":4,
"touching_frame":[x["shade"] for x in results if x["object_touches_original_pixel_frame"]],
"new_retail_approved":0}))
