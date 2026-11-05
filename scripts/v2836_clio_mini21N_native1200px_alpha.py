#!/usr/bin/env python3
"""v2836: high-native 21N Linen CLIO Mesh Glow Essential MINI 5g
single-compact foreground trial. Only 21N gets a NEW derivative; old 21C,
prior 21N, v2832 10 JPGs, 11 approved families and 55 URLs are immutable.

Source 1200px-native from merchant 21N variant-linked image (v2834/v2835).
NO source-image license, owned stock edition, or MK original are inferred.
Keep a real transparent PNG and 1080x1080 JPEG as INTERNAL QA ONLY.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from rembg import remove,new_session
import json,hashlib,base64
R=Path("qa-review")
SRC=R/"v2834-clio-meshglow-mini-21N-high-native-resolution-source-probe"
OLD=R/"v2833-clio-meshglow-essential-mini-21C-21N-real-alpha-photo-heroes"
AUDIT=R/"v2835-clio-mini-21N-merchant-variant-image-assignment-audit"
OUT=R/"v2836-clio-mini5g-21N-1200px-isolated-compact-alpha-QA"
assert SRC.is_dir() and OLD.is_dir() and AUDIT.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
src_manifest=json.loads((SRC/"manifest.json").read_text())
audit=json.loads((AUDIT/"manifest.json").read_text())
assert src_manifest["higher_native_source_count"]>=2
assert any(x.get("strong_standalone_21N_image_evidence") and x["merchant"]=="La Cosmetique Australia" for x in audit["merchant_results"])
target_source=SRC/"02-21N-high-native-source-QA.jpg"
old_jpg=OLD/"21N"/"01-21N-mini5g-real-product-source-1080-QA.jpg"
assert target_source.is_file() and old_jpg.is_file()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
f=lambda n,b=False:ImageFont.truetype(BOLD if b else FONT,n)
row={"version":"v2836","baseline":"v2835","family":"pending-04",
 "product":"CLIO Mesh Glow Essential Cushion MINI 5g",
 "shade":"21N Linen",
 "source_merchant":"La Cosmetique Australia",
 "original_native_dimensions":[1200,1200],
 "input_JPG":str(target_source),"source_sha256":digest(target_source),
 "previous_480px_native_cutout_JPG":str(old_jpg),
 "prior_480px_based_qa_remains_unchanged":True,
 "status":"HOLD_ALPHA_FAILED_OR_VISUAL_QA",
 "photo_rights_verified":False,"physical_stock_21N_confirmed":False,
 "MK_original_logo_verified":False,"retail_approved":False}
try:
 with Image.open(target_source) as im:
  im.load();assert im.format=="JPEG" and im.size==(1080,1080)
  raw=im.convert("RGBA")
 # 1200px original photo contains compact left-of-center and a separate
 # teardrop swatch to the right. Source crop excludes right-side swatch AND
 # its 21N sample text; DO NOT infer color shade from pixels.
 region=(135,80,755,810)
 crop=raw.crop(region)
 mask_source=remove(crop,session=new_session("isnet-general-use"),alpha_matting=True,
   alpha_matting_foreground_threshold=230,
   alpha_matting_background_threshold=18,
   alpha_matting_erode_size=4)
 assert mask_source.mode=="RGBA"
 alpha=mask_source.getchannel("A")
 box=alpha.getbbox()
 assert box is not None
 fraction=sum(v>=128 for v in alpha.getdata())/(mask_source.width*mask_source.height)
 assert 0.05<fraction<0.80,(fraction,box)
 assert box[2]-box[0]>210 and box[3]-box[1]>240,(fraction,box)
 cut=mask_source.crop(box)
 transparent=OUT/"01-21N-mini5g-single-product-real-alpha-QA.png"
 cut.save(transparent,optimize=True)
 jpg=OUT/"01-21N-mini5g-1200native-source-1080hero-QA.jpg"
 board=Image.new("RGB",(1080,1080),"white")
 d=ImageDraw.Draw(board)
 d.rounded_rectangle((48,48,1032,1032),radius=33,outline="#eae1e5",width=2)
 d.text((94,96),"CLIO",font=f(43,True),fill="#383239")
 d.text((94,164),"Mesh Glow Essential Cushion Mini 5g",font=f(27),fill="#756a72")
 d.text((94,209),"21N Linen | Merchant variant-linked photograph",font=f(20),fill="#8b7980")
 display=ImageOps.contain(cut,(880,710),Image.Resampling.LANCZOS)
 board.paste(display,((1080-display.width)//2,258+(710-display.height)//2),display)
 d.text((94,995),"REAL 21N PHOTOGRAPHIC CUTOUT  |  QA ONLY",font=f(19),fill="#9a8f94")
 board.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
 assert jpg.stat().st_size<2_000_000
 with Image.open(jpg) as verify:
  verify.load();assert verify.format=="JPEG" and verify.size==(1080,1080)
 row.update({"status":"TRUE_ALPHA_AND_1080_JPG_CREATED_VISUAL_QA_PENDING",
 "extracted_photo_crop":list(region),"mask_bbox":list(box),
 "mask_coverage":round(fraction,5),
 "transparent_PNG":transparent.name,
 "new_1080_JPG":jpg.name,
 "new_1080_JPG_sha256":digest(jpg),
 "new_1080_JPG_bytes":jpg.stat().st_size,
 "source_photo_sha_unchanged_after":digest(target_source)==row["source_sha256"]})
except Exception as exc:
 row.update({"status":"HOLD_NEW_MASK_GEOMETRY_OR_SOURCE_FAILED","error":str(exc)[:250],
 "error_type":type(exc).__name__})
board=Image.new("RGB",(1550,630),"#f2f0ee")
d=ImageDraw.Draw(board)
d.text((15,14),"v2836 21N Linen | old 480px-based vs native 1200px source vs actual isolated compact",font=f(23,True),fill="#28252a")
for i,(path,title) in enumerate([(old_jpg,"PREVIOUS LOW-RES QA"),
 (target_source,"1200-NATIVE SOURCE REFERENCE"),
 (OUT/row["new_1080_JPG"] if row.get("new_1080_JPG") else target_source,"NEW CUTOUT QA" if row.get("new_1080_JPG") else "CUTOUT FAILED")]):
 with Image.open(path) as im:tile=im.convert("RGB").resize((472,472),Image.Resampling.LANCZOS)
 x=20+i*507;board.paste(tile,(x,65))
 d.text((x,554),title,font=f(18,True),fill="#4d454a")
d.text((20,597),"Original source and old approved URLs untouched. Photo rights / owned stock NOT verified.",font=f(17),fill="#675b61")
proof=OUT/"v2836-low-vs-native-vs-cutout.jpg"
board.save(proof,"JPEG",quality=84,optimize=True)
(OUT/"v2836-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
report={
 "version":"v2836","baseline":"v2835","product_family":"pending-04",
 "shade":"21N Linen","high_native_source_verified_by_variant_link":True,
 "new_actual_alpha_cutouts_created":1 if row.get("transparent_PNG") else 0,
 "existing_21C_art_and_QA_sets_mutated":False,
 "existing_21N_v2833_art_mutated":False,
 "source_v2834_v2835_art_mutated":False,
 "old_11_sale_approved_families_unchanged":True,
 "old_55_published_photo_urls_unchanged":True,
 "photo_commercial_reuse_rights_verified":False,
 "owned_stock_generation_and_exact_shade_verified":False,
 "MK_original_logo_authenticated":False,
 "sales_approved_new":0,"final_XLSX_shared":False,
 "candidate":row
}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2836","actual_alpha":report["new_actual_alpha_cutouts_created"],
"status":row["status"],"sale_approved":0}))
