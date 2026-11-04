#!/usr/bin/env python3
"""v2760 two ALTERNATIVE shade-specific Peripera 18/19 real source photos.
Older existing v2753 photos remain intact; v2759 established their clipped
alpha corner is attached to main object so cannot safely prune.

Use separate authenticated shade product source images (old Honey K-Ookie 4g)
and a padded crop for complete bottle and applicator. No invented tubes, no
fabricated colors. Visual QA and rights still mandatory.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from rembg import new_session,remove
from io import BytesIO
import requests,json,hashlib,base64
OUT=Path("qa-review/v2760-peripera-18-19-alternate-actual-photo-alpha")
assert not OUT.exists()
OUT.mkdir(parents=True)
CASES=[
 {"shade":"18","name":"Nude Area",
  "sources":[
    {"page":"https://www.jeevee.com/products/peripera-ink-mood-glowy-tint-honey-k-ookie-collection-18-nude-area-94090",
     "url":"https://stod.jeevee.com/whetstone-products/jeevee_erp/2025-08-10/ec/ec459f1d94eddbb45424608c75bf2eb824c42462"},
    {"page":"https://h5.lazada.com.my/products/peripera-yakgwa-molyip-collection-i3799252793.html",
     "url":"https://my-test-11.slatic.net/p/7adf5f86f378e5df337bbc619d40f9df.jpg"}
   ]},
 {"shade":"19","name":"Mauve Chaos",
  "sources":[
    {"page":"https://www.alpsus.com/products/peripera-ink-mood-glowy-tint-19-mauve-chaos",
     "url":"https://www.alpsus.com/cdn/shop/files/InkMoodGlowyTint019MauveChaos1_1200x1200.jpg?v=1748705496"},
    {"page":"https://shopee.vn/Son-tint-b%C3%B3ng-Peripera-Ink-Mood-Glowy-Tint-4g-i.12964260.21117409525",
     "url":"https://down-vn.img.susercontent.com/file/vn-11134207-7r98o-lpfey50338zy87"}
   ]}
]
HEAD={"User-Agent":"Mozilla/5.0 (compatible; ShopeeQA/1.0)","Accept":"image/jpeg,image/webp,image/png,*/*"}
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def ft(size,b=False):return ImageFont.truetype(BOLD if b else FONT,size)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
model=new_session("isnet-general-use")
items=[]
for c in CASES:
 shade=c["shade"]
 data={"shade":shade,"product":"PERIPERA Ink Mood Glowy Tint old Honey K-Ookie 4g",
   "shade_name":c["name"],"source_attempts":[],"status":"HOLD_NO_NEW_TRUSTED_PHOTO",
   "old_clipped_photo_source_preserved":True,"actual_stock_edition_verified":False,
   "photo_reuse_permission_verified":False,"retail_approved":False}
 for source in c["sources"]:
  a={"page":source["page"],"url":source["url"]}
  try:
   response=requests.get(source["url"],headers=HEAD,timeout=18)
   response.raise_for_status()
   if len(response.content)>7500000:raise ValueError("Source too large")
   original=Image.open(BytesIO(response.content))
   original.load()
   if min(original.size)<480:raise ValueError("Tiny image, cannot use")
   photo=ImageOps.exif_transpose(original).convert("RGB")
   area=photo.convert("RGBA")  # FULL image, never crop bottle at edge.
   cut=remove(area,session=model,alpha_matting=True,
    alpha_matting_foreground_threshold=228,
    alpha_matting_background_threshold=18,
    alpha_matting_erode_size=4)
   assert cut.mode=="RGBA"
   alpha=cut.getchannel("A");bbox=alpha.getbbox()
   if bbox is None:raise ValueError("Empty cutout")
   fraction=sum(v>=128 for v in alpha.getdata())/(cut.width*cut.height)
   w,h=cut.size
   corners=[alpha.getpixel(p) for p in ((0,0),(w-1,0),(0,h-1),(w-1,h-1))]
   if not(.035<fraction<.82 and bbox[2]-bbox[0]>140 and bbox[3]-bbox[1]>200):
    raise ValueError("Invalid alpha geometry: "+str((fraction,bbox)))
   if max(corners)>150:raise ValueError("Alpha touches source corner: "+str(corners))
   isolated=cut.crop(bbox)
   folder=OUT/f"shade-{shade}";folder.mkdir()
   raw=folder/f"{shade}-alternate-actual-photograph.jpg"
   photo.save(raw,"JPEG",quality=92,optimize=True)
   png=folder/f"{shade}-new-source-true-alpha-QA.png"
   isolated.save(png,optimize=True)
   card=Image.new("RGB",(1080,1080),"white")
   d=ImageDraw.Draw(card)
   d.rounded_rectangle((54,53,1026,1028),radius=35,outline="#e9e4e7",width=2)
   d.text((95,95),"PERIPERA",font=ft(42,True),fill="#393139")
   d.text((95,161),f"Old Ink Mood Glowy Tint #{shade} {c['name']}",font=ft(26),fill="#776970")
   cover=ImageOps.contain(isolated,(855,772),Image.Resampling.LANCZOS)
   card.paste(cover,((1080-cover.width)//2,213+(772-cover.height)//2),cover)
   d.text((95,993),"REAL ALTERNATE SOURCE / QA ONLY / NO RELEASE",font=ft(18),fill="#999098")
   jpg=folder/f"{shade}-new-actual-photo-cutout-1080-QA.jpg"
   card.save(jpg,"JPEG",quality=92,optimize=True,subsampling=0)
   assert jpg.stat().st_size<2_000_000
   with Image.open(jpg) as test:
    test.load();assert test.format=="JPEG" and test.size==(1080,1080)
   data.update({"status":"NEW_SOURCE_TRUE_ALPHA_RENDERED_NEEDS_VISUAL_QA",
    "source_page":source["page"],"source_url":source["url"],
    "raw_source_image":str(raw.relative_to(OUT)),
    "new_true_alpha_png":str(png.relative_to(OUT)),
    "new_1080JPG":str(jpg.relative_to(OUT)),
    "sha_png":sha(png),"sha_jpg":sha(jpg),
    "mask_coverage":round(fraction,4),"original_dimensions":list(photo.size),
    "alpha_four_corners":corners,
    "decorative_color_swatch_may_be_included":True,
    "source_photo_bytes_sha256":hashlib.sha256(response.content).hexdigest()})
   a["result"]="SUCCESS_IMAGE_AND_MASK"
   data["source_attempts"].append(a)
   break
  except Exception as e:
   a["result"]="SKIP_FAILED_OR_AMBIGUOUS"
   a["error"]=str(e)[:160]
   data["source_attempts"].append(a)
 items.append(data)
board=Image.new("RGB",(1490,1040),"#f1f0ef")
d=ImageDraw.Draw(board)
d.text((18,16),"v2760 ALTERNATE EXACT SHADE 18/19 SOURCES / NEW CUTOUT / QA ONLY",font=ft(24,True),fill="#343034")
for i,r in enumerate(items):
 y=62+490*i
 d.text((17,y+10),"#"+r["shade"]+" "+r["shade_name"],font=ft(28,True),fill="#41363d")
 d.text((17,y+60),r["status"],font=ft(17),fill="#6c6065")
 if r.get("raw_source_image"):
  with Image.open(OUT/r["raw_source_image"]) as im:
   original=ImageOps.contain(im.convert("RGB"),(410,410),Image.Resampling.LANCZOS)
  board.paste(original,(300+(410-original.width)//2,y+(410-original.height)//2))
 if r.get("new_1080JPG"):
  with Image.open(OUT/r["new_1080JPG"]) as im:
   fixed=im.convert("RGB").resize((410,410),Image.Resampling.LANCZOS)
  board.paste(fixed,(1060,y))
proof=OUT/"v2760-18-19-alternate-source-cutout-review.jpg"
board.save(proof,"JPEG",quality=83,optimize=True)
(OUT/"v2760-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
result={"version":"v2760","baseline":"v2759","family":"pending-08",
 "target_shades":["18","19"],
 "source_mode":"two independent alternate old-edition full product photos, never reprocess v2753 cutouts",
 "new_original_source_photo_cutout_pairs":sum(bool(x.get("new_true_alpha_png")) for x in items),
 "previous_18_successfully_staged_shades_untouched":True,
 "prior_v2759_alpha_edge_holds_untouched":True,
 "old_11_approved_families_untouched":True,"public_55_verified_urls_untouched":True,
 "original_MK_logo_authenticated":False,"commercial_photo_rights_verified":False,
 "actual_owned_stock_edition_confirmed":False,"retail_approved_new":0,
 "final_XLSX_shared":False,"items":items}
(OUT/"manifest.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2760","new_photo_alpha_pairs":result["new_original_source_photo_cutout_pairs"],
 "results":[x["status"] for x in items],"retail_approved":0}))
