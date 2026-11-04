#!/usr/bin/env python3
"""v2759 SAFE edge correction for ONLY previously failed Peripera shades 18/19.
Use exact existing true alpha PNGs from v2753. On v2758, only these 2 touch
bottom-left corner (alpha=254). Connected-component remove ONLY a detached
small corner island; never erase an integrated foreground object. Keep HOLD
if candidate isn't unambiguously isolated. Previously approved media intact.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import cv2,numpy as np,json,hashlib,base64
ROOT=Path("qa-review")
IN=ROOT/"v2753-peripera-legacy-17-product-real-alpha-qa"
OUT=ROOT/"v2759-peripera-18-19-border-alpha-island-safety"
assert IN.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def ft(s,b=False):return ImageFont.truetype(B if b else F,s)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
res=[]
for shade in ("18","19"):
 src=IN/f"shade-{shade}"/f"{shade}-exact-legacy-product-true-alpha-QA.png"
 assert src.is_file()
 with Image.open(src) as img:
  img.load();assert img.mode=="RGBA";rgba=img.copy()
 data=np.asarray(rgba).copy()
 al=data[:,:,3]
 # The first full-size alpha audit detects the bottom-left corner.
 labels_count,labels,stats,centroids=cv2.connectedComponentsWithStats(
   np.uint8(al>=64),connectivity=8)
 outer=int(labels[-1,0])
 areas=sorted((int(stats[i,cv2.CC_STAT_AREA]),i) for i in range(1,labels_count))
 largest=areas[-1][0] if areas else 0
 contaminated=int(stats[outer,cv2.CC_STAT_AREA]) if outer>0 else 0
 proportion=contaminated/largest if largest else 1
 row={"shade":shade,"original_png":str(src),"original_sha256":sha(src),
   "original_corner_alpha":int(al[-1,0]),
   "component_count":labels_count-1,"main_foreground_area":largest,
   "border_component_area":contaminated,"border_component_vs_largest":round(proportion,5),
   "status":"HOLD_UNSAFE_TO_REMOVE_ATTACHED_OBJECT","actual_new_corrected_png":None,
   "exact_original_source_preserved":True,"retail_approved":False}
 # Only remove small disconnected border island. If it touches main object
 # or has >6% of main object's area, no correction is made.
 if outer>0 and 0<contaminated<largest*.06 and outer!=areas[-1][1]:
  data[:,:,3][labels==outer]=0
  cleaned=Image.fromarray(data,"RGBA")
  a=cleaned.getchannel("A")
  edge=[a.getpixel(p) for p in ((0,0),(cleaned.width-1,0),(0,cleaned.height-1),(cleaned.width-1,cleaned.height-1))]
  if max(edge)<=150 and a.getbbox():
   folder=OUT/f"shade-{shade}";folder.mkdir()
   box=a.getbbox()
   fixed=cleaned.crop(box)
   png=folder/f"{shade}-only-detached-background-island-removed-QA.png"
   fixed.save(png,optimize=True)
   preview=Image.new("RGB",(1080,1080),"white")
   d=ImageDraw.Draw(preview)
   d.rounded_rectangle((54,54,1026,1026),radius=36,outline="#ece6ea",width=2)
   d.text((94,97),"PERIPERA",font=ft(40,True),fill="#383138")
   lbl="18 Nude Area" if shade=="18" else "19 Mauve Chaos"
   d.text((94,163),f"Old Ink Mood Glowy Tint #{lbl}",font=ft(25),fill="#7e717c")
   scaled=ImageOps.contain(fixed,(855,767),Image.Resampling.LANCZOS)
   preview.paste(scaled,((1080-scaled.width)//2,218+(767-scaled.height)//2),scaled)
   d.text((94,991),"ACTUAL ORIGINAL PHOTO FOREGROUND | QA ONLY",font=ft(18),fill="#a39ca2")
   jpg=folder/f"{shade}-island-removed-1080-QA.jpg"
   preview.save(jpg,"JPEG",quality=92,optimize=True,subsampling=0)
   assert jpg.stat().st_size<2_000_000
   row.update({"status":"DEFINITELY_DETACHED_ALPHA_ISLAND_REMOVED_NEEDS_VISUAL_QA",
      "actual_new_corrected_png":str(png.relative_to(OUT)),
      "actual_new_corrected_jpg":str(jpg.relative_to(OUT)),
      "corrected_png_sha256":sha(png),"corrected_jpg_sha256":sha(jpg),
      "corner_alpha_after":edge,"removed_island_pixels":contaminated})
 # Always save original and candidate side by side even on HOLD
 res.append(row)
board=Image.new("RGB",(1550,1030),"#f1f0ee")
d=ImageDraw.Draw(board)
d.text((18,18),"v2759 18/19 ALPHA BORDER ISLAND DECISION | NO PHOTO FABRICATION | QA ONLY",font=ft(24,True),fill="#302930")
for i,r in enumerate(res):
 y=66+480*i
 with Image.open(r["original_png"]) as p:
  src=Image.new("RGBA",p.size,"white");src.alpha_composite(p.convert("RGBA"))
  old=ImageOps.contain(src.convert("RGB"),(410,410),Image.Resampling.LANCZOS)
 board.paste(old,(15+(410-old.width)//2,y+(410-old.height)//2))
 d.text((460,y+10),f"#{r['shade']} BORDER STATUS",font=ft(29,True),fill="#343036")
 d.text((460,y+63),r["status"],font=ft(18),fill="#6d626b")
 d.text((460,y+111),f"Island area {r['border_component_area']}, main {r['main_foreground_area']}",font=ft(19),fill="#6d626b")
 if r.get("actual_new_corrected_jpg"):
  with Image.open(OUT/r["actual_new_corrected_jpg"]) as im:
   new=im.convert("RGB").resize((410,410),Image.Resampling.LANCZOS)
  board.paste(new,(1100,y))
proof=OUT/"v2759-18-19-component-edge-proof.jpg"
board.save(proof,"JPEG",quality=83,optimize=True)
(OUT/"v2759-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
report={"version":"v2759","baseline":"v2758","family":"pending-08",
 "source_shades":["18","19"],"reprocessed_previous_18_other_shades":False,
 "source_alphas_untouched":True,
 "physical_new_corrected_png_jpg_pairs":sum(bool(r.get("actual_new_corrected_png")) for r in res),
 "remaining_alpha_hold_shades":[r["shade"] for r in res if not r.get("actual_new_corrected_png")],
 "color_chart_swatches_fabricated":0,"new_product_photographs_generated":0,
 "old_11_published_approved_groups_unchanged":True,"public_55_urls_unchanged":True,
 "commercial_photo_rights_verified":False,"stock_package_generation_verified":False,
 "retail_approved_new":0,"final_XLSX_shared":False,"records":res}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2759","new_corrected":report["physical_new_corrected_png_jpg_pairs"],
 "holds":report["remaining_alpha_hold_shades"],"sale_approved":0}))
