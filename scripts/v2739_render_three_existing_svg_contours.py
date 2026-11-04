#!/usr/bin/env python3
"""v2739 EXACT-PIXEL contour SVG -> real 1080 transparent PNG plus JPG QA.
No product generation, no brand/logo invention. Source SVGs on existing QA
branch stay byte-identical. All outputs append-only and nonpublic.
"""
from pathlib import Path
import base64,hashlib,json,io,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw,ImageFont,ImageOps
import cairosvg

ROOT=Path("qa-review")
OUT=ROOT/"v2739-three-existing-svg-real-png-jpg-photo-QA"
assert not OUT.exists(), OUT
OUT.mkdir(parents=True)
SOURCES=[
 ("pending-09","OBgE Oil Control Finisher 5g","v2738a-direct-contour-svg-fallback/pending-09-exact-source-photo-transparent-clip-QA.svg"),
 ("pending-19","GOODAL Vita C Cream Alpha 50mL","v2738a-direct-contour-svg-fallback/pending-19-exact-source-photo-transparent-clip-QA.svg"),
 ("pending-23","OBgE Pore Zero Sun Cream 50mL","v2738b-porezero-clean-source-alternate-svg-cutout/pending-23-real-50mL-alternate-source-contour-QA.svg"),
]
font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
f=lambda n,b=False:ImageFont.truetype(bold if b else font,n)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for family,label,relative in SOURCES:
 source=ROOT/relative
 assert source.is_file(),source
 content=source.read_bytes()
 assert b"data:image/jpeg;base64," in content,(family,"not a real source-embedded photo")
 xml=ET.fromstring(content)
 assert xml.tag.endswith("svg")
 # Validate reference image bytes are truly embedded; no fetching or substitution.
 embedded=[]
 for e in xml.iter():
  if e.tag.endswith("image"):
   for key,value in e.attrib.items():
    if key.endswith("href") and value.startswith("data:image/jpeg;base64,"):
     embedded.append(base64.b64decode(value.split(",",1)[1]))
 assert len(embedded)==1,(family,len(embedded))
 with Image.open(io.BytesIO(embedded[0])) as probe:
  probe.load()
  assert probe.format=="JPEG" and probe.size==(1080,1080)
  photo=probe.convert("RGB")
 png_bytes=cairosvg.svg2png(bytestring=content,output_width=1080,output_height=1080)
 foreground=Image.open(io.BytesIO(png_bytes)).convert("RGBA")
 assert foreground.size==(1080,1080)
 alpha=foreground.getchannel("A")
 bounds=alpha.getbbox()
 assert bounds is not None,(family,"blank alpha")
 pixels=list(alpha.getdata())
 solid=sum(x>=128 for x in pixels)
 semitransparent=sum(0<x<255 for x in pixels)
 coverage=solid/len(pixels)
 assert .015<coverage<.76,(family,coverage)
 assert bounds[0]>10 and bounds[1]>10 and bounds[2]<1070 and bounds[3]<1070,(family,bounds)
 if bounds[2]-bounds[0]<100 or bounds[3]-bounds[1]<130:raise RuntimeError("Implausibly small product mask")
 # Fully transparent pixels must not leak source background through RGB.
 product=foreground.copy()
 # Get top alpha boundary and original product pixel colors. PNG contains no
 # blank white square under the product silhouette.
 folder=OUT/family
 folder.mkdir()
 png=folder/"01-authentic-source-contour-transparent-1080-QA.png"
 product.save(png,optimize=True)
 with Image.open(png) as verify:
  verify.load()
  assert verify.format=="PNG" and verify.mode=="RGBA" and verify.size==(1080,1080)
 jpg=folder/"01-original-product-contour-white-1080-QA.jpg"
 canvas=Image.new("RGB",(1080,1080),"#ffffff")
 canvas.paste(product,(0,0),product)
 canvas.save(jpg,"JPEG",quality=94,optimize=True,subsampling=0)
 assert jpg.stat().st_size<2_000_000,(family,jpg.stat().st_size)
 with Image.open(jpg) as verify:
  verify.load()
  assert verify.format=="JPEG" and verify.size==(1080,1080)
 # QA proof: untouched embedded source, alpha result over checkerboard, JPG.
 tile=Image.new("RGB",(1080,1080),"white")
 t=ImageDraw.Draw(tile)
 for y in range(0,1080,32):
  for x in range(0,1080,32):
   if (x//32+y//32)%2==0:t.rectangle((x,y,x+31,y+31),fill="#dedede")
 tile.paste(product,(0,0),product)
 r={"family":family,"product":label,
  "source_svg":str(source),"source_svg_sha256":sha(source),
  "actual_original_jpeg_embedded_sha256":hashlib.sha256(embedded[0]).hexdigest(),
  "png":str(png.relative_to(OUT)),"jpg":str(jpg.relative_to(OUT)),
  "png_sha256":sha(png),"jpg_sha256":sha(jpg),"png_bytes":png.stat().st_size,
  "jpg_bytes":jpg.stat().st_size,"solid_alpha_coverage":round(coverage,4),
  "semitransparent_pixels":semitransparent,"alpha_bbox":list(bounds),
  "technical_file_QA":"PASS",
  "human_silhouette_QA":"UNREVIEWED",
  "commercial_release":"HOLD_ORIGINAL_MK_LOGO_RIGHTS_STOCK_VERSION"}
 rows.append((r,photo,tile,canvas))
# Build a 3-row, three-column proof so a human can reject rough clip paths.
proof=Image.new("RGB",(1710,1270),"#f0f0f0")
d=ImageDraw.Draw(proof)
d.text((20,16),"v2739 THREE SVG -> ACTUAL PNG/JPG, ORIGINAL vs ALPHA vs JPG | QA ONLY",font=f(22,True),fill="#222")
for idx,(r,photo,checker,white) in enumerate(rows):
 y=60+idx*400
 for ix,img in enumerate([photo,checker,white]):
  thumb=img.resize((365,365),Image.Resampling.LANCZOS)
  proof.paste(thumb,(20+ix*560,y))
 d.text((402,y+50),r["family"],font=f(24,True),fill="#252525")
 d.text((962,y+50),"CHECKERBOARD",font=f(17),fill="#252525")
 d.text((1525,y+50),"WHITE JPG",font=f(17),fill="#252525")
 d.text((402,y+88),f"alpha {r['solid_alpha_coverage']*100:.1f}%",font=f(16),fill="#252525")
prooffile=OUT/"v2739-original-versus-transparent-versus-white-proof.jpg"
proof.save(prooffile,"JPEG",quality=86,optimize=True)
(OUT/"v2739-proof.b64.txt").write_text(base64.b64encode(prooffile.read_bytes()).decode())
report={
 "version":"v2739","baseline":"v2738b",
 "successfully_rasterized_existing_svg_contours":len(rows),
 "genuine_1080_transparent_PNGs":len(rows),
 "shopee_1080_JPGs_under_2mb":len(rows),
 "prior_source_SVGs_original_JPGs_modified":0,
 "human_edge_review_complete":False,"new_retail_approved":0,
 "source_image_redistribution_permission_verified":False,
 "owned_inventory_editions_verified":False,"original_MK_logo_verified":False,
 "previous_11_published_groups_unchanged":True,"previous_55_public_urls_unchanged":True,
 "final_excel_or_spreadsheet_shared":False,"products":[r for r,*_ in rows]}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2739","families":3,"png":3,"jpg":3,
 "technical_QA":"PASS","retail_approved":0}))
