#!/usr/bin/env python3
"""v2806: select actual visually inspected CLIO Mesh Glow B cutout without
redoing alpha segmentation. Assemble QA five-frame variant from four
SHA-identical v2797 official gallery JPGs and saved v2799 B foreground.
Never change source images, 11 sale-approved families, or 55 public URLs.
Photo-license, owned shade/kit, and MK logo remain hard retail holds.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,shutil,base64
R=Path("qa-review")
BASE=R/"v2797-clio-meshglow-five-distinct-official-photo-scenes-and-alpha-qa"
ALPHA=R/"v2799-clio-reflection-spatial-right-edge-preserving-alpha-QA"
OUT=R/"v2806-clio-meshglow-b-foreground-four-distinct-real-photo-qa"
assert BASE.is_dir() and ALPHA.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((BASE/"manifest.json").read_text())
assert len(old["selected_scenes"])==5
replacement=ALPHA/"01-B-stronger-lower-left-reflection-1080-QA.jpg"
png=ALPHA/"01-B-stronger-lower-left-reflection-true-alpha-QA.png"
assert replacement.is_file() and png.is_file()
frames=[]
for item in old["selected_scenes"]:
 n=item["slot"]
 if n==1:
  src=replacement
  name="01-selected-B-verified-lower-left-reflection-clean-product-QA.jpg"
  role="B variant of existing true alpha compact source, selected after source/A/B visual inspection"
 else:
  src=BASE/item["1080_jpg"]
  name=f"{n:02d}-source-official-photo-sha-preserved-QA.jpg"
  role=item["photo_function"]+"; original v2797 SHA preserved"
 assert src.is_file(),src
 dest=OUT/name
 shutil.copy2(src,dest)
 assert sha(dest)==sha(src)
 with Image.open(dest) as img:
  img.load()
  assert img.format=="JPEG" and img.size==(1080,1080), (dest,img.format,img.size)
 assert dest.stat().st_size<2_000_000
 frames.append({"slot":n,"file":name,"role":role,"source":str(src),
                "sha256":sha(dest),"bytes":dest.stat().st_size,
                "exact_bytes_preserved":True,"source_gallery_index":item["origin_global_gallery_index"]})
assert len({f["sha256"] for f in frames})==5
destpng=OUT/"01-B-selected-transparent-photo-source-QA.png"
shutil.copy2(png,destpng)
assert sha(destpng)==sha(png)
with Image.open(destpng) as im:
 im.load()
 assert im.format=="PNG" and im.mode=="RGBA" and im.size[0]>200 and im.size[1]>200
report={
 "version":"v2806","previous_v2805_untouched":True,"base_qa":"v2797","selected_alpha_variant":"v2799 B stronger lower-left reflection reduction",
 "family":"pending-06","product":"CLIO Kill Cover Mesh Glow Essential Cushion",
 "actual_five_physical_JPGs_saved":True,"alpha_png_present":True,
 "original_v2797_four_JPGs_SHA_preserved_exactly":True,
 "new_cutouts_regenerated":0,"real_product_pixel_inventions":0,
 "QA_visual_decision":"PREFERRED_B_PHOTO_FOREGROUND_FOR_INTERNAL_QA_NOT_RETAIL",
 "selection_basis":"Source, A and B candidate side by side in v2799 proof; B retains transparent compact right edge and removes excess lower-left floor reflection",
 "five_shade_photo_is_official_reference_not_user_stock_proof":True,
 "owned_21C_or_19C_19N_21N_23N_variants_verified":False,
 "single_item_vs_set_refill_unit_verified":False,
 "photo_redistribution_rights_verified":False,
 "original_approved_MK_logo_verified":False,
 "customer_retail_approved":False,
 "approved_11_product_families_unchanged":True,
 "prior_55_verified_public_URLs_unchanged":True,
 "previous_v2797_and_v2799_original_JPGs_untouched":True,
 "final_XLSX_shared":False,
 "frames":frames,
 "next_sales_QA":["Confirm purchased stock variant and whether set/refill contents match",
 "Do not show all five official swatches as stock availability",
 "Secure licensed image use and original round MK logo before any storefront publish",
 "Check 1080px single frame edge on real device"]
}
(OUT/"manifest.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",23)
board=Image.new("RGB",(1830,505),"#f0efed")
d=ImageDraw.Draw(board)
d.text((16,17),"v2806 CLIO MESH GLOW | B REAL ALPHA + 4 DISTINCT OFFICIAL PHOTO SCENES | QA ONLY",fill="#292929",font=font)
for f in frames:
 with Image.open(OUT/f["file"]) as im:
  thumb=im.convert("RGB").resize((339,339),Image.Resampling.LANCZOS)
 x=15+(f["slot"]-1)*365
 board.paste(thumb,(x,66))
 d.text((x,421),f"FRAME {f['slot']}  "+("SELECTED B" if f["slot"]==1 else "SOURCE SAVED"),font=font,fill="#292929")
preview=OUT/"v2806-five-frame-contact.jpg"
board.save(preview,"JPEG",quality=85,optimize=True)
(OUT/"v2806-contact.b64.txt").write_text(base64.b64encode(preview.read_bytes()).decode())
print(json.dumps({"version":"v2806","five_photo_JPGs":5,"chosen_cutout_variant":"B",
 "source_JPGs_preserved":4,"alpha_png_preserved":True,"retail_approved":0}))
