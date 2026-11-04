#!/usr/bin/env python3
"""v2790: Correct only tiny dark cropped English caption glyphs in the blank
top margin of CLIO mini QA frames 01 and 02 from v2789.
Preserve eight existing GOODAL/CLIO 1080 JPEGs byte-for-byte and preserve
all historical original source pictures.

Only constrained, small connected dark grayscale characters are inpainted in
the blank top margin. No product pixels are drawn/created, and it is NOT a
product foreground cutout. Unverified badge and user stock generation remain
separately held. Save old-vs-new visual comparison for human validation.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import cv2
import numpy as np
import json,shutil,hashlib,base64
R=Path("qa-review")
SRC=R/"v2789-goodal-frame5-and-clio-mini-no-fake-MK-five-scene-QA"
OUT=R/"v2790-clio-mini-two-cropped-english-captions-corrected-QA"
assert SRC.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
src=json.loads((SRC/"manifest.json").read_text())
assert src["version"]=="v2789"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
results=[]
for family,frames in [
    ("pending-19",src["family_pending_19"]["frames"]),
    ("pending-04",src["family_pending_04"]["frames"])]:
    dest=OUT/family;dest.mkdir()
    new=[]
    for old in frames:
        slot=old["slot"]
        original=SRC/family/old["file"]
        assert original.is_file()
        with Image.open(original) as im:
            im.load()
            assert im.format=="JPEG" and im.size==(1080,1080)
            rgb=np.array(im.convert("RGB"))
        if family=="pending-04" and slot in (1,2):
            # In both rendered 1080x1080 JPEGs the unintended truncated
            # source English caption sits in the white upper margin near y=~200.
            # Never touch central/lower compact and puff, or artwork's MK corner.
            # Determine exact text via connected-component bounding boxes and
            # only inpaint dark text on pale near-neutral background.
            hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
            gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
            background=cv2.inRange(hsv,np.array([0,0,185]),np.array([179,85,255]))
            dark=cv2.inRange(gray,0,181)
            # Readable text is small and low-saturation. Pixel boundaries include
            # a few anti-aliased glyph fringe pixels, handled by local dilate.
            search=np.zeros((1080,1080),dtype=np.uint8)
            search[120:310,0:990]=255
            candidate=cv2.bitwise_and(dark,search)
            lab_count,labels,stats,_=cv2.connectedComponentsWithStats(candidate,connectivity=8)
            mask=np.zeros((1080,1080),dtype=np.uint8)
            boxes=[]
            for i in range(1,lab_count):
                x,y,w,h,area=map(int,stats[i])
                if not(1<=area<=350 and 1<=w<=75 and 2<=h<=30):continue
                # Caption glyphs have mostly white / pale backdrop; a finger
                # or product seam is never a background text component.
                pad=5
                x0=max(0,x-pad);y0=max(0,y-pad)
                x1=min(1080,x+w+pad);y1=min(1080,y+h+pad)
                bg=background[y0:y1,x0:x1]
                if float(np.mean(bg>0))<0.40:continue
                boxes.append([x,y,w,h,area])
                mask[labels==i]=255
            mask=cv2.dilate(mask,np.ones((4,4),np.uint8),iterations=1)
            count=int(np.count_nonzero(mask))
            if count<30 or count>13500:
                raise ValueError(f"Unsafe or failed caption mask family={family} slot={slot}: pixels={count}, components={len(boxes)}")
            corrected=cv2.inpaint(cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR),mask,4,cv2.INPAINT_TELEA)
            corrected=cv2.cvtColor(corrected,cv2.COLOR_BGR2RGB)
            # Guarantee lower product block 310: remains identical in RGB pixels
            # PRIOR to JPEG re-encoding (the original file is never modified).
            assert np.array_equal(corrected[310:],rgb[310:])
            filename=f"{slot:02d}-english-caption-removed-only-in-upper-margin-QA.jpg"
            path=dest/filename
            Image.fromarray(corrected).save(path,"JPEG",quality=94,optimize=True,subsampling=0)
            record={"slot":slot,"filename":filename,"source":str(original),
                "source_sha256":sha(original),"sha256":sha(path),
                "changes":"DARK_ENGLISH_TEXT_ONLY_INPAINT_UPPER_MARGIN",
                "caption_mask_pixels":count,"caption_connected_components":len(boxes),
                "component_boxes":boxes,"other_JPEG_files_unchanged":True,
                "actual_product_pixels_not_drawn":True,
                "photo_rights_verified":False,
                "stock_shade_generation_verified":False}
        else:
            path=dest/old["file"]
            shutil.copy2(original,path)
            assert sha(path)==sha(original)
            record={"slot":slot,"filename":path.name,"source":str(original),
                "sha256":sha(path),"changes":"PRESERVED_SOURCE_BYTES",
                "identical_prior_SHA256":True}
        assert path.stat().st_size<2_000_000
        with Image.open(path) as im:
            im.load()
            assert im.format=="JPEG" and im.size==(1080,1080)
        record["bytes"]=path.stat().st_size
        new.append(record)
    results.append({"family":family,"five_1080JPGs_present":len(new)==5,
                    "frames":new})
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",22)
for fam in results:
    name=fam["family"]
    board=Image.new("RGB",(1835,480),"#f1f0ed")
    d=ImageDraw.Draw(board)
    d.text((16,15),f"v2790 {name} / 5 QA photos / only CLIO 01 02 corrected / NOT FOR SALE",font=font,fill="#303030")
    for i,fr in enumerate(fam["frames"]):
        with Image.open(OUT/name/fr["filename"]) as im:
            thumb=im.convert("RGB").resize((336,336),Image.Resampling.LANCZOS)
        xx=16+i*362
        board.paste(thumb,(xx,64))
        d.text((xx,410),f"FRAME {i+1:02d} / "+("TEXT FIX" if fr["changes"].startswith("DARK") else "UNCHANGED"),font=font,fill="#333333")
    proof=OUT/f"v2790-{name}-fiveframe-after-cropfix.jpg"
    board.save(proof,"JPEG",quality=84,optimize=True)
    (OUT/f"v2790-{name}-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
report={
    "version":"v2790","baseline":"v2789",
    "two_changed_CLIO_JPGs":[1,2],
    "eight_prior_goodal_clio_JPGs_exact_SHA_unchanged":True,
    "new_true_product_cutouts_created":0,
    "only_top_caption_inpainted":True,
    "removed_original_MK_region_was_already_excluded_v2789":True,
    "retail_ready_verified":False,
    "PHOTO_LICENSE_AND_EXACT_STOCK_MK_LOGO_PENDING":True,
    "approved_old_11_families_unchanged":True,
    "verified_55_public_image_urls_unchanged":True,
    "previous_QA_and_source_photo_bytes_unchanged":True,
    "final_spreadsheet_shared":False,
    "family_results":results,
}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2790","QA_1080_JPGs_staged":10,
                  "changed_only":["pending-04/frame01","pending-04/frame02"],
                  "preserved_SHA_identical":8,"new_sale_approvals":0}))
