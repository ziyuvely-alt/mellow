#!/usr/bin/env python3
"""PIXEL PURE Soothing Ampoule Toner 200mL, exact one fifth independent photo.
Derived only from saved official page's original-08.jpg (brand image holding bottle above water).
Crop promotional claim headline away, keep 100% genuine source photographic pixels.
No fake packaging, no clinical text, no regenerated other four JPGs.
"""
from pathlib import Path
from PIL import Image
import json,hashlib
SRC=Path("v2465-official-sources/original-08.jpg")
assert SRC.is_file(),"Previously verified official product image unavailable"
O=Path("v2519-pixelpure-toner-fifth-real-photo");O.mkdir(exist_ok=True)
img=Image.open(SRC).convert("RGB")
assert img.size==(860,1087),f"Unexpected source dimensions {img.size}; refrain from blind cropping."
new=img.crop((39,281,822,1064)).resize((1080,1080),Image.Resampling.LANCZOS)
dst=O/"05-real-bottle-held-over-water-200ml.jpg"
new.save(dst,"JPEG",quality=91,optimize=True,subsampling=0)
raw=dst.read_bytes()
assert len(raw)<2_000_000 and Image.open(dst).size==(1080,1080)
manifest={"date":"2026-11-04","family":"pending-27","product":"PIXEL PURE Soothing Ampoule Toner 200mL",
"source_asset":"original-08.jpg","source_from_official_page":"https://www.pixelpure.com/product/detail.html?product_no=24",
"source_actions_run_id":41682843250,"source_artifact_id":13254420828,
"source_pixels_purely_photographic":True,"crop_coordinates":[39,281,822,1064],
"exact_source_image_dimensions":[860,1087],
"removed_ad_claim_headline":True,"original_photography_not_fabricated":True,
"new_JPG":dst.name,"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw),"resolution":[1080,1080],
"previous_4_customer_frames_unchanged":True,"full_5_frame_composition_visual_review_pending":True,
"original_MK_logo_applied":False,"photo_commercial_reuse_rights_confirmed":False,
"physical_owned_stock_edition_checked":False,"published_public_url":False,
"excel_spreadsheet_shared":False}
(O/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"new_exact_real_photo_JPG":dst.name,"size":len(raw),"sha256":manifest["sha256"]}))
