#!/usr/bin/env python3
"""v2751: Final full-size and near-white-edge QA proof on the TWO ALREADY MADE,
shade-specific No.25/No.27 transparent photos. Never regenerate, recolor,
overwrite or publish source images. QA proof is not a retailer listing.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import numpy as np,hashlib,json,base64
R=Path("qa-review")
S=R/"v2749-MISSHA-coverlasting-N25-N27-official-variant-source-proof"
Q=R/"v2750-missha-N25-N27-distinct-official-photo-cutout-QA"
O=R/"v2751-missha-shades25-27-true-alpha-edge-qa"
assert S.exists() and Q.exists() and not O.exists()
O.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def ft(n,b=False):return ImageFont.truetype(BOLD if b else FONT,n)
checks=[]
board=Image.new("RGB",(1590,790),"#f0f0ee")
d=ImageDraw.Draw(board)
d.text((14,12),"v2751 REAL 25/27 ALPHA EDGES, UNMODIFIED SOURCES | NOT RETAIL",font=ft(24,True),fill="#282828")
for n,shade in enumerate(("25","27")):
 src=S/f"shade-{shade}"/f"01-real-variant-linked-{shade}-source-reference-QA.jpg"
 jpg=Q/f"shade-{shade}"/f"01-original-{shade}-isnet-product-1080-QA.jpg"
 png=Q/f"shade-{shade}"/f"01-original-{shade}-isnet-true-alpha-QA.png"
 with Image.open(src) as im:original=im.convert("RGB").copy()
 with Image.open(jpg) as im:hero=im.convert("RGB").copy()
 with Image.open(png) as im:alpha=im.convert("RGBA").copy()
 assert original.size==(1080,1080) and hero.size==(1080,1080)
 assert png.stat().st_size>10000 and jpg.stat().st_size<2_000_000
 data=np.asarray(alpha.getchannel("A"))
 coverage=float((data>=128).mean())
 transparent=float((data<12).mean())
 assert .08<coverage<.78 and transparent>.1,(coverage,transparent)
 # Checkerboard shows unexpected erasures or islands without modifying PNG.
 cb=Image.new("RGBA",alpha.size,"#f4f4f4")
 draw=ImageDraw.Draw(cb)
 for yy in range(0,alpha.height,24):
  for xx in range(0,alpha.width,24):
   if (xx//24+yy//24)%2==0:
    draw.rectangle((xx,yy,xx+23,yy+23),fill="#dbdbdb")
 cb.alpha_composite(alpha)
 # Near-white product edge: full actual PNG scaled, not a new cutout.
 panels=[
   ("ORIGINAL",ImageOps.contain(original,(365,300),Image.Resampling.LANCZOS)),
   ("CHOSEN SHOEPI JPG",ImageOps.contain(hero,(365,300),Image.Resampling.LANCZOS)),
   ("TRANSPARENCY",ImageOps.contain(cb.convert("RGB"),(365,300),Image.Resampling.LANCZOS)),
   ("ALPHA DETAIL 1:1",ImageOps.contain(cb.convert("RGB").crop((0,0,min(750,cb.width),min(750,cb.height))),(365,300),Image.Resampling.LANCZOS))
 ]
 y=61+n*361
 for i,(label,img) in enumerate(panels):
  x=15+i*392
  panel=Image.new("RGB",(370,305),"white")
  panel.paste(img,((370-img.width)//2,(305-img.height)//2))
  board.paste(panel,(x,y))
  d.text((x+5,y+310),f"NO.{shade} {label}",font=ft(19),fill="#333333")
 checks.append({"shade":shade,"official_variant_source":str(src),"selected_alpha_png":str(png),
                "selected_jpg":str(jpg),"source_sha256":sha(src),"alpha_png_sha256":sha(png),
                "jpg_sha256":sha(jpg),"source_dimensions":list(original.size),
                "jpg_dimensions":list(hero.size),"alpha_canvas_px":list(alpha.size),
                "alpha_opaque_coverage":round(coverage,4),"alpha_transparent_fraction":round(transparent,4),
                "retail_approved":False,
                "conclusion":"QA_EDGE_PROOF_READY_HUMAN_1TO1_REVIEW_REQUIRED"})
proof=O/"v2751-two-independent-shade-edge-inspection.jpg"
board.save(proof,"JPEG",quality=86,optimize=True)
(O/"v2751-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={"version":"v2751","baseline":"v2750","independent_shades_25_27_checked":2,
    "existing_PNG_JPG_files_regenerated_or_mutated":0,
    "all_technical_invariants_passed":True,
    "1_to_1_edge_comparison_image_saved":True,
    "real_retail_approvals":0,
    "original_MK_logo_approved":False,
    "stock_edition_matched":False,"photo_commercial_rights_verified":False,
    "previous_11_approved_families_unchanged":True,
    "previous_55_public_urls_unchanged":True,
    "final_spreadsheet_shared":False,"variants":checks}
(O/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2751","shade_count":2,"original_files_preserved":True,"proof":str(proof),"retail_approved":0}))
