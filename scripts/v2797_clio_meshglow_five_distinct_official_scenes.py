#!/usr/bin/env python3
"""v2797 CLIO Mesh Glow Essential, five distinct original official scenes + one
real foreground transparent QA candidate, all from exact v2796 1200px
global gallery. No earlier QA files edited. No approval or publication.

Product-first five scenes:
  01 21C authentic official product hero (global catalog source index 03)
  02 compact/puff close-up (index 06)
  03 mesh pickup/detail (index 08)
  04 wear/use photo (index 10)
  05 official 5-shade swatch (index 12)
Colors 19C/19N/21C/21N/23N are official global listing, but owned stock
option match and photo reuse permissions have NOT been validated.

Use a true ISNET foreground segmentation only to add an alternate 01 product
cutout, never replacing original 01 unless direct human visual QA accepts it.
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
from rembg import remove, new_session
import base64, hashlib, json, shutil, numpy as np
ROOT=Path("qa-review")
SRC=ROOT/"v2796-clio-meshglow-essential-global-original-gallery-source"
OUT=ROOT/"v2797-clio-meshglow-five-distinct-official-photo-scenes-and-alpha-qa"
assert SRC.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
pre=json.loads((SRC/"manifest.json").read_text())
assert pre["version"]=="v2796" and len(pre["photo_records"])>=12
def digest(b):return hashlib.sha256(b).hexdigest()
def shafile(p):return digest(p.read_bytes())
SCENES=[
  (1,3,"21C exact product hero","source photo variant 21C Lingerie"),
  (2,6,"compact/puff closeup","actual product and included puff in official illustration"),
  (3,8,"mesh cushion demonstration","original brand explanatory photograph"),
  (4,10,"makeup application scene","official global product model/application scene"),
  (5,12,"five-shade arm swatch","official 19C 19N 21C 21N 23N chart; owned options held")
]
records=[]
for dstslot,sourceslot,role,disambig in SCENES:
 src=SRC/f"{sourceslot:02d}-source-photo-1080-only-QA.jpg"
 native=SRC/f"{sourceslot:02d}-official-global-gallery-NATIVE-original.jpg"
 assert src.exists() and native.exists()
 with Image.open(src) as im:
  im.load()
  assert im.format=="JPEG" and im.size==(1080,1080)
 with Image.open(native) as im:
  im.load()
  assert im.format=="JPEG" and im.size==(1200,1200)
 row=pre["photo_records"][sourceslot-1]
 assert row["QA_SHA256"]==shafile(src)
 assert row["original_source_sha256"]==shafile(native)
 out=OUT/f"{dstslot:02d}-distinct-official-{sourceslot:02d}-photo-SOURCE-QA.jpg"
 shutil.copyfile(src,out)
 assert shafile(src)==shafile(out) and out.stat().st_size<2_000_000
 records.append({
   "slot":dstslot,"origin_global_gallery_index":sourceslot,
   "photo_function":role,"identity_scope":disambig,
   "source_native_1200_photo":str(native),"source_url":row["source_url"],
   "1080_jpg":out.name,"verified_original_1080_sha256":shafile(out),
   "copy_from_v2796_sha_identical":True,"retail_approved":False
 })
# Distinct-source byte identities, not repeated 5 angles under different shade names.
assert len({v["verified_original_1080_sha256"] for v in records})==5
cutout={"status":"HOLD_UNTIL_VISUAL_REVIEW","source_gallery_index":3,
        "uses_original_1200px_photo":True,"not_photo_invented":True}
try:
 source=SRC/"03-official-global-gallery-NATIVE-original.jpg"
 with Image.open(source) as im:
  im.load()
  photo=ImageOps.exif_transpose(im).convert("RGBA")
 # Crop out the source shadow footer and avoid splitting a compact corner;
 # neutral 1200px catalog art; true foreground model performs the extraction.
 bounds=(38,32,1162,1148)
 roi=photo.crop(bounds)
 session=new_session("isnet-general-use")
 isolated=remove(roi,session=session,alpha_matting=True,
      alpha_matting_foreground_threshold=230,
      alpha_matting_background_threshold=18,
      alpha_matting_erode_size=4)
 assert isolated.mode=="RGBA"
 alpha=np.asarray(isolated.getchannel("A"))
 maskcoverage=float(np.mean(alpha>=128))
 bbox=isolated.getchannel("A").getbbox()
 assert bbox is not None
 bw=bbox[2]-bbox[0];bh=bbox[3]-bbox[1]
 assert .055<=maskcoverage<=.73 and bw>=380 and bh>=450,(maskcoverage,bbox)
 object=isolated.crop(bbox)
 png=OUT/"01-alternate-real-transparent-CLIO-object-QA.png"
 object.save(png,optimize=True)
 # A simple white product-first main image, no invented logo/text, preserve actual source pixels.
 white=Image.new("RGB",(1080,1080),"white")
 fitted=ImageOps.contain(object,(940,940),Image.Resampling.LANCZOS)
 white.paste(fitted,((1080-fitted.width)//2,(1080-fitted.height)//2),fitted)
 alt=OUT/"01-alternate-real-segmented-object-1080-QA.jpg"
 white.save(alt,"JPEG",quality=93,optimize=True,subsampling=0)
 assert alt.stat().st_size<2_000_000
 with Image.open(alt) as ver:
  ver.load();assert ver.format=="JPEG" and ver.size==(1080,1080)
 cutout.update({"status":"ACTUAL_1200px_PHOTO_ALPHA_MASK_STAGED_FOR_VISUAL_QA",
    "source_crop":list(bounds),"mask_coverage":round(maskcoverage,4),
    "mask_bbox":list(bbox),"png_file":png.name,"jpg_file":alt.name,
    "jpg_sha256":shafile(alt),
    "source_original_sha256":shafile(source)})
except Exception as e:
 cutout.update({"status":"REJECT_REAL_ALPHA_DUE_TO_MASK_OR_MODEL",
                "reason":str(e)[:220]})
# Contact sheet: five different official real content scenes + optional alpha.
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font=ImageFont.truetype(FONT,20)
board=Image.new("RGB",(1900,1100),"#f2f1ef")
d=ImageDraw.Draw(board)
d.text((20,15),"v2797 CLIO Mesh Glow Essential | Five distinct global official 1200px source scenes | NOT FOR SALE",font=font,fill="#292929")
for i,row in enumerate(records):
 with Image.open(OUT/row["1080_jpg"]) as im:
  tile=im.convert("RGB").resize((330,330),Image.Resampling.LANCZOS)
 x=18+(i%5)*374
 board.paste(tile,(x,65))
 d.text((x,402),f"{i+1}. Gallery {row['origin_global_gallery_index']:02d}",font=font,fill="#292929")
if cutout.get("jpg_file"):
 with Image.open(OUT/cutout["jpg_file"]) as im:
  tile=im.convert("RGB").resize((420,420),Image.Resampling.LANCZOS)
 board.paste(tile,(40,490))
 d.text((40,923),"Alternate true-alpha product hero | 1200px source",font=font,fill="#383838")
else:
 d.text((40,520),"Alternative real-alpha mask failed; original five distinct source photos retained",font=font,fill="#383838")
d.text((520,520),"Stock edition/shades and commercial photo reuse: NOT VERIFIED",font=font,fill="#545454")
d.text((520,560),"Only global gallery shade options 19C, 19N, 21C, 21N, 23N confirmed",font=font,fill="#545454")
proof=OUT/"v2797-distinct-scenes-and-alpha-contact.jpg"
board.save(proof,"JPEG",quality=85,optimize=True)
(OUT/"v2797-contact.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
report={
 "version":"v2797","base":"v2796","family":"pending-06",
 "product":"CLIO Kill Cover Mesh Glow Essential Cushion Foundation",
 "global_official_photo_gallery":"https://clubclio.shop/products/clio-kill-cover-mesh-glow-cushion-set-refill",
 "five_distinct_1080_JPGs_saved":5,
 "all_five_copied_SHA_identical_from_v2796":True,
 "five_distinct_scene_origins_not_five_duplicated_shade_packshots":True,
 "official_variant_list":["19C Light","19N Porcelain","21C Lingerie","21N Linen","23N Ginger"],
 "stock_available_variants_verified":False,
 "exact_owned_stock_bundle_vs_single_unit_verified":False,
 "original_photo_commercial_reuse_permission_verified":False,
 "original_round_MK_logo_verified":False,
 "real_alpha_cutout_candidate":cutout,
 "new_retail_approvals":0,
 "prior_11_approved_families_untouched":True,
 "prior_55_public_URLs_untouched":True,
 "prior_v2796_photos_untouched":True,
 "final_spreadsheet_shared":False,
 "selected_scenes":records
}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2797",
  "five_distinct_saved_official_photos":len(records),
  "alpha_status":cutout["status"],
  "retail_approved":0},ensure_ascii=False))
