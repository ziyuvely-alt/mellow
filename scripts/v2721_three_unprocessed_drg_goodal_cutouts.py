#!/usr/bin/env python3
"""v2721: true photographic cutout for previously unprocessed families 17,19,20.
Use restored 2026-10-29 historical source corpus; NEVER invent source objects,
product pixels, shade labels, or unverified MK badge. Archived previous assets
and all 55 approved retail URLs immutable.

All outputs are commercial-use-HOLD, reviewed later with visual contact sheets.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from rembg import remove,new_session
import base64,hashlib,json,re
SRC=Path("historical/review-JPG-by-family")
OUT=Path("qa-review/v2721-three-new-DRG-GOODAL-photo-alpha-scenes")
assert SRC.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
CASES=[
 ("pending-17","Dr.G","Brightening Up Moisture Sun 50mL"),
 ("pending-19","GOODAL","Green Tangerine Vita C Cream Alpha 50mL"),
 ("pending-20","GOODAL","Green Tangerine Vita C Serum Mist 100mL")
]
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def ft(n,b=False):return ImageFont.truetype(BOLD if b else FONT,n)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
model=new_session("isnet-general-use")
results=[]
for family,brand,title in CASES:
 files=sorted((SRC/family).glob("*.jpg"))
 rec={"family":family,"brand":brand,"product":title,"source_candidates":[p.name for p in files],
      "status":"HOLD_NO_VALID_REAL_PRODUCT_SOURCE","approved_for_sale":False}
 try:
  if not files:raise FileNotFoundError("No 2026-10-29 restored family source JPG")
  # Physical packshots are prioritized over fact-only cards; test up to three
  # source frames, move ahead rather than repeatedly using a bad image.
  eligible=sorted(files,key=lambda p:(
    1 if any(s in p.name.lower() for s in ["info","fact","claim","card","swatch","text"]) else 0,
    0 if any(s in p.name.lower() for s in ["real","photo","actual","inv","source"]) else 1,
    p.name))
  for source in eligible[:3]:
   try:
    with Image.open(source) as im:
     im.load()
     if im.format!="JPEG" or min(im.size)<500:continue
     stock=im.convert("RGBA")
    # Strip unverified old MK corner / headings without cropping the product.
    # If actual item is too near the border this must fail visual QA, not pass automatically.
    left=round(.12*stock.width);top=round(.13*stock.height)
    right=round(.86*stock.width);bottom=round(.89*stock.height)
    roi=stock.crop((left,top,right,bottom))
    rgba=remove(roi,session=model,alpha_matting=True,
       alpha_matting_foreground_threshold=230,
       alpha_matting_background_threshold=18,alpha_matting_erode_size=4)
    if rgba.mode!="RGBA":continue
    a=rgba.getchannel("A");bbox=a.getbbox()
    if bbox is None:continue
    ratio=sum(x>=128 for x in a.getdata())/(rgba.width*rgba.height)
    if not(.025<ratio<.80 and bbox[2]-bbox[0]>90 and bbox[3]-bbox[1]>180):continue
    cut=rgba.crop(bbox)
    d=OUT/family;d.mkdir(exist_ok=True)
    png=d/"01-real-transparent-product-cutout-QA.png";cut.save(png,optimize=True)
    jpg=d/"01-real-1080-product-hero-QA.jpg"
    white=Image.new("RGB",(1080,1080),"#ffffff")
    draw=ImageDraw.Draw(white)
    draw.rounded_rectangle((54,54,1025,1027),radius=35,outline="#eee7e9",width=2)
    draw.text((98,98),brand,font=ft(43,True),fill="#373438")
    size=28
    while draw.textbbox((0,0),title,font=ft(size))[2]>880 and size>17:size-=1
    draw.text((98,162),title,font=ft(size),fill="#766b72")
    thumb=ImageOps.contain(cut,(860,780),Image.Resampling.LANCZOS)
    white.paste(thumb,((1080-thumb.width)//2,210+(780-thumb.height)//2),thumb)
    draw.text((98,990),"AUTHENTIC SOURCE PHOTO ALPHA  |  QA ONLY",font=ft(18),fill="#9a9295")
    white.save(jpg,"JPEG",quality=92,optimize=True,subsampling=0)
    if jpg.stat().st_size>=2_000_000:
      jpg.unlink();png.unlink();continue
    rec.update({"status":"REAL_ALPHA_PNG_JPG_STAGED_NEEDS_VISUAL_QA",
       "source_photo":str(source),"source_sha256":digest(source),
       "source_crop":[left,top,right,bottom],"mask_alpha_fraction":round(ratio,4),
       "png":str(png.relative_to(OUT)),"jpg":str(jpg.relative_to(OUT)),
       "jpg_sha256":digest(jpg),"source_file_preserved":True})
    break
   except Exception as e:
    rec["last_skipped_source_error"]=str(e)[:130]
  if not rec.get("jpg"):rec["status"]="HOLD_ALL_CANDIDATE_MASKS_INVALID"
 except Exception as e:
  rec["status"]="HOLD_SOURCE_ACCESS_OR_GEOMETRY";rec["error"]=str(e)[:180]
 results.append(rec)
board=Image.new("RGB",(1500,60+3*475),"#f0f0f0")
draw=ImageDraw.Draw(board)
draw.text((18,14),"v2721 SOURCE vs REAL ALPHA CUTOUT | 3 NEW FAMILIES | QA ONLY",font=ft(25,True),fill="#303030")
for i,row in enumerate(results):
 y=58+i*475
 if row.get("source_photo"):
  with Image.open(row["source_photo"]) as im:
   src=im.convert("RGB").resize((420,420),Image.Resampling.LANCZOS)
  board.paste(src,(17,y))
 draw.text((456,y+16),row["family"],font=ft(31,True),fill="#2e2e2e")
 draw.text((456,y+68),row["status"],font=ft(18),fill="#606060")
 if row.get("jpg"):
  with Image.open(OUT/row["jpg"]) as im:
   img=im.convert("RGB").resize((420,420),Image.Resampling.LANCZOS)
  board.paste(img,(1066,y))
proof=OUT/"v2721-3-original-to-cutout-proof.jpg"
board.save(proof,"JPEG",quality=82,optimize=True)
(OUT/"v2721-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={"version":"v2721","baseline":"v2720",
 "product_families_newly_attempted":3,
 "physically_saved_real_alpha_png_jpg_pairs":sum(bool(x.get("jpg")) for x in results),
 "existing_source_jpgs_reencoded_or_mutated":0,
 "existing_11_approved_families_modified":False,
 "existing_55_public_urls_modified":False,
 "photo_commercial_rights_verified":False,"stock_edition_verified":False,
 "original_MK_logo_verified":False,"new_retail_sale_approvals":0,
 "final_XLSX_shared":False,"products":results}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2721","new_photo_families":3,"actual_alpha_pairs":manifest["physically_saved_real_alpha_png_jpg_pairs"],
"statuses":[x["status"] for x in results],"sales_approved":0}))
