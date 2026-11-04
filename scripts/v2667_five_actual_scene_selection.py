#!/usr/bin/env python3
"""v2667 real product-photo scene selection: preserve 5 original JPEG bytes.
No image regeneration, no cropping and no watermark hallucination.
A large visual sheet allows an actual scene-level inspection.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,shutil,base64
ROOT=Path("source/historical/review-JPG-by-family")
OUT=Path("v2667-five-actual-original-photo-select");(OUT/"original-photo-picks").mkdir(parents=True,exist_ok=True)
picks={"pending-05":3,"pending-07":2,"pending-15":5,"pending-22":4,"pending-28":2}
record=[]
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",32)
board=Image.new("RGB",(2220,2570),"#f1f2f4");d=ImageDraw.Draw(board)
d.text((32,12),"v2667 EXACT EXISTING PHOTO FILES | REVIEW ONLY | NO SALES APPROVAL",fill="#1a1a1a",font=font)
for k,(fam,slot) in enumerate(picks.items()):
    candidates=list((ROOT/fam).glob(f"{slot:02d}*.jpg"))
    assert len(candidates)==1,(fam,slot,candidates)
    p=candidates[0]
    raw=p.read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    dest=OUT/"original-photo-picks"/f"{fam}-source-slot{slot:02d}-QA-ONLY.jpg"
    shutil.copy2(p,dest)
    assert hashlib.sha256(dest.read_bytes()).hexdigest()==digest
    with Image.open(dest) as im:
        im.load();assert im.size==(1080,1080) and im.format=="JPEG"
        image=im.convert("RGB")
    # Display entire images, uncut; do not imply a new image was created.
    thumbnail=image.resize((920,440),Image.Resampling.LANCZOS) if False else image.resize((460,460),Image.Resampling.LANCZOS)
    # Scale to 920x460 would deform, so use faithful aspect and 460px originals in pairs.
    x=40+(k%2)*1100;y=75+(k//2)*820
    large=image.resize((740,740),Image.Resampling.LANCZOS)
    board.paste(large,(x,y))
    d.text((x,y+748),fam+" slot"+str(slot).zfill(2),fill="#111111",font=font)
    record.append({"family":fam,"slot":slot,"original_filename":p.name,"copied_file":dest.name,
                   "sha256":digest,"image_bytes":len(raw),"retail_status":"HOLD_REAL_PRODUCT_IDENTITY_RIGHTS_LATEST_V2647"})
# Final image can be taller to fit all rows.
sheet=OUT/"v2667-five-original-scenes-large.jpg"
board.save(sheet,quality=81,optimize=True)
(OUT/"v2667-five-original-scenes-large.b64.txt").write_text(base64.b64encode(sheet.read_bytes()).decode())
(OUT/"manifest.json").write_text(json.dumps({"version":"v2667","family_count":5,"original_jpg_copied":5,
 "new_sales_artwork":0,"source_version":"v2593 historical; v2647 not verified",
 "source_photos":record,"photo_rights_verified":False,"real_stock_edition_verified":False,
 "existing_11_approved_unchanged":True,"existing_55_URLs_unchanged":True,"no_xlsx":True},ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"actual_existing_photos_selected":5,"source_hashes_preserved":5,
 "new_customer_ready_images":0,"proof_bytes":sheet.stat().st_size},ensure_ascii=False))
