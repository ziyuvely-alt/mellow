#!/usr/bin/env python3
"""v2734 - distinct-source model pivot, not a repeat of the prior failed masks.

Only 2 previously failed product families:
 * GOODAL eye cream 30mL: actual single tube on archived slot01 but precision ROI.
 * OBgE finisher 5g: different original slot03 (open compact), not slot05 brown hero.

Uses u2net (not isnet-general-use) with high-resolution foreground approach.
No hallucinated products, recolored photo pixels, invented badges or public writes.
If technical segmentation cannot isolate them, mark that product on HOLD.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from rembg import remove,new_session
import numpy as np
import hashlib,base64,json

R=Path("qa-review")
OUT=R/"v2734-two-failed-families-different-photo-ROI-u2net"
assert not OUT.exists()
OUT.mkdir(parents=True)
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font=lambda n,b=False:ImageFont.truetype(B if b else F,n)
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
SPECS=[
 {"family":"pending-21","product":"GOODAL Green Tangerine Vita C Eye Cream 30mL",
  "title":"GOODAL","src":"v2705-three-recovered-photo-first-family-sets/pending-21/01-original-source-sha-unchanged-QA.jpg",
  "crop":[465,195,925,953],"remediation":"PRECISION_TUBE_ROI_DIFFERENT_MODEL_U2NET"},
 {"family":"pending-09","product":"OBgE Oil Control Finisher 5g",
  "title":"OBgE","src":"v2705-three-recovered-photo-first-family-sets/pending-09/03-original-source-sha-unchanged-QA.jpg",
  "crop":[160,305,948,899],"remediation":"DIFFERENT_SOURCE_SLOT03_COMPACT_OPEN_DIFFERENT_MODEL_U2NET"},
]
rows=[]
model=new_session("u2net")
for c in SPECS:
    source=R/c["src"]
    assert source.is_file(),source
    with Image.open(source) as img:
        img.load()
        assert img.format=="JPEG" and img.size==(1080,1080)
        roi=img.convert("RGBA").crop(c["crop"])
    record={"family":c["family"],"product":c["product"],
      "source_file":str(source),"source_sha256":sha(source),
      "source_crop":c["crop"],"model":"u2net",
      "improvement_method":c["remediation"],
      "status":"HOLD_BEFORE_REAL_ALPHA_VALIDATION","retail_approved":False}
    try:
        # The original RGB is retained. Only alpha removal is changed.
        cut=remove(roi,session=model,alpha_matting=True,
            alpha_matting_foreground_threshold=235,
            alpha_matting_background_threshold=16,
            alpha_matting_erode_size=3)
        assert cut.mode=="RGBA"
        a=np.asarray(cut.getchannel("A"))
        binary=a>=128
        area=float(np.mean(binary))
        bbox=cut.getchannel("A").getbbox()
        assert bbox is not None
        bw=bbox[2]-bbox[0];bh=bbox[3]-bbox[1]
        edge={
         "top":round(float(binary[0].mean()),4),
         "bottom":round(float(binary[-1].mean()),4),
         "left":round(float(binary[:,0].mean()),4),
         "right":round(float(binary[:,-1].mean()),4)}
        # Thin eye tubes require lower width threshold than other packages.
        min_width=65 if c["family"]=="pending-21" else 135
        min_height=260 if c["family"]=="pending-21" else 160
        assert 0.008<area<.82 and bw>=min_width and bh>=min_height,(area,bbox)
        # Exclude obvious full rectangle, product may touch crop boundary
        # when close to edge: don't promote it as passed automatically.
        isolated=cut.crop(bbox)
        folder=OUT/c["family"];folder.mkdir()
        png=folder/"01-real-source-foreground-cutout-u2net-QA.png"
        isolated.save(png,optimize=True)
        jpg=folder/"01-real-original-photo-cutout-1080-QA.jpg"
        canvas=Image.new("RGB",(1080,1080),"#fffefd")
        d=ImageDraw.Draw(canvas)
        d.rounded_rectangle((54,54,1026,1027),radius=36,fill="white",outline="#eae5e7",width=2)
        d.text((94,100),c["title"],font=font(42,True),fill="#39333a")
        size=28
        while d.textbbox((0,0),c["product"],font=font(size))[2]>890 and size>18:size-=1
        d.text((94,162),c["product"],font=font(size),fill="#7a6f77")
        fg=ImageOps.contain(isolated,(858,778),Image.Resampling.LANCZOS)
        canvas.paste(fg,((1080-fg.width)//2,217+(780-fg.height)//2),fg)
        d.text((94,992),"REAL PRODUCT PHOTO FOREGROUND  |  QA ONLY",font=font(18),fill="#93898d")
        canvas.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
        with Image.open(jpg) as verify:
            verify.load()
            assert verify.format=="JPEG" and verify.size==(1080,1080)
        assert jpg.stat().st_size<2_000_000
        record.update({"status":"ACTUAL_ALPHA_JPG_PNG_SAVED_VISUAL_QA_REQUIRED",
          "coverage":round(area,4),"mask_bbox":list(bbox),"crop_boundary_mask_contact":edge,
          "png":str(png.relative_to(OUT)),"jpg":str(jpg.relative_to(OUT)),
          "png_sha256":sha(png),"jpg_sha256":sha(jpg),
          "flag":"BROAD_EDGE_TOUCH" if max(edge.values())>.22 else None})
    except Exception as e:
        record.update({"status":"HOLD_INVALID_NEW_MASK",
         "error_type":type(e).__name__,"error":str(e)[:220]})
    rows.append(record)

proof=Image.new("RGB",(1550,1045),"#f0efef")
d=ImageDraw.Draw(proof)
d.text((14,15),"v2734 TWO DIFFERENT SOURCE/SEGMENTATION TRIALS | NO RETAIL RELEASE",
  font=font(25,True),fill="#2b292b")
for n,x in enumerate(rows):
    yy=62+486*n
    with Image.open(x["source_file"]) as src:
        p=src.convert("RGB").resize((430,430),Image.Resampling.LANCZOS)
    proof.paste(p,(16,yy))
    d.text((470,yy+14),x["family"],font=font(30,True),fill="#393039")
    d.text((470,yy+73),x["status"],font=font(17),fill="#686168")
    if x.get("jpg"):
        with Image.open(OUT/x["jpg"]) as target:
            revised=target.convert("RGB").resize((430,430),Image.Resampling.LANCZOS)
        proof.paste(revised,(1110,yy))
contact=OUT/"v2734-originals-versus-u2net-cutouts.jpg"
proof.save(contact,"JPEG",quality=84,optimize=True)
(OUT/"v2734-proof.b64.txt").write_text(base64.b64encode(contact.read_bytes()).decode())
manifest={"version":"v2734","baseline":"v2733",
 "attempted_failed_families_with_new_methods":2,
 "actual_new_png_JPG_pairs":sum(bool(x.get("jpg")) for x in rows),
 "original_source_photos_changed":0,"previously_approved_product_groups_modified":0,
 "published_55_image_URLs_modified":0,"retail_approved":0,
 "genuine_source_photo_rights_unverified":True,
 "actual_owned_stock_item_versions_unverified":True,
 "original_MK_logo_unavailable":True,
 "never_retry_identical_failed_sources":True,
 "no_final_excel_shared":True,"rows":rows}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2734","tried":2,
 "real_png_jpg_saved":manifest["actual_new_png_JPG_pairs"],
 "states":[r["status"] for r in rows],
 "approved":0}))
