#!/usr/bin/env python3
"""v2650: inspect only the unresolved same-family historical image pair.
Never alter original images, approved URL paths, spreadsheets, or v2647 files.
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageChops, ImageStat
import json, hashlib
report=json.loads(Path("source/audit/audit.json").read_text())
assert report["version"]=="v2649"
pairs=report["same_family_close_dhash"]
assert len(pairs)==1, f"Expected one historical candidate, got {len(pairs)}"
out=Path("v2650-review");out.mkdir(exist_ok=True)
pair=pairs[0]
def getfile(item):
    p=Path("source/photos/review-JPG-by-family")/item["family"]/item["name"]
    assert p.exists(),p
    return p
left,right=pair["a"],pair["b"]
with Image.open(getfile(left)) as a0, Image.open(getfile(right)) as b0:
    a=ImageOps.exif_transpose(a0).convert("RGB")
    b=ImageOps.exif_transpose(b0).convert("RGB")
    assert a.size==b.size==(1080,1080)
    # Store 2 separate comparison crops plus one non-published side-by-side QA contact sheet
    canvas=Image.new("RGB",(1700,1050),"#e8e9ed")
    da=ImageDraw.Draw(canvas)
    da.text((28,15),"v2650 HISTORICAL QA ONLY - NOT FOR PUBLICATION",fill="#111111")
    for i,(im,obj) in enumerate([(a,left),(b,right)]):
        view=im.resize((800,800),Image.Resampling.LANCZOS)
        x=25+i*850
        canvas.paste(view,(x,90))
        da.text((x,905),f"{obj['family']} / slot {obj['slot']} / {obj['name'][:55]}",fill="#111111")
        da.text((x,935),f"Later edited: {obj['superseded']}",fill="#111111")
    canvas.save(out/"one-pair-visual-comparison.jpg",quality=90)
    # Note simple RGB pixel difference is only historical image comparison, not a product identity guarantee.
    delta=ImageChops.difference(a.resize((240,240)),b.resize((240,240)))
    mean_diff=round(sum(ImageStat.Stat(delta).mean)/3,3)
    (out/"one-pair-pixel-difference.jpg").write_bytes(b"") if False else None
    joined={
      "version":"v2650","baseline":"historical v2593 archive and v2649 similarity audit",
      "pair":{"left":left,"right":right,"dhash_distance":pair["hamming"],
              "mean_RGB_pixel_difference_thumbnail":mean_diff},
      "review": {
        "one_pair_contact_sheet_saved":True,
        "must_compare_product_and_exact_stock_edition_manually":True,
        "one_or_both_frames_superseded_since_baseline":left["superseded"] or right["superseded"],
        "recommendation":("DO_NOT_EDIT_HISTORICAL_SLOT_USE_LATEST_V2647_FIRST"
               if left["superseded"] or right["superseded"] else
                "VISUAL_REVIEW_REQUIRED_BEFORE_SELECTIVE_REPLACEMENT")
      },
      "source_archive_is_latest":False,
      "new_sale_ready_jpg":0,
      "published_urls_changed":0,
      "approved_jpg_changed":0,
      "xlsx_shared":False
    }
(out/"review.json").write_text(json.dumps(joined,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"family":left["family"],"slot_a":left["slot"],"slot_b":right["slot"],
 "distance":pair["hamming"],"superseded":joined["review"]["one_or_both_frames_superseded_since_baseline"],
 "mean_rgb_diff":mean_diff,"decision":joined["review"]["recommendation"]}))
