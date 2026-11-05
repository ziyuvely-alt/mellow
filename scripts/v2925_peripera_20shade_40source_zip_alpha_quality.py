#!/usr/bin/env python3
"""v2925: make one immutable 01-20 Peripera JPG/PNG source-option archive (40 originals),
and perform an actual PNG transparency / small-native-source audit. NO 21-26, NO
new sales artwork or approved photo claims, NO old files overwritten.
"""
from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,time

Q=Path("qa-review")
BASE=Q/"v2924-eight-unpacked-stock-family-3five-photo-20option-4clio-source-QA"
OUT=Q/"v2925-peripera-01to20-40immutable-JPG-PNG-and-alpha-native-QA"
assert not OUT.exists()
m=json.loads((BASE/"manifest.json").read_text(encoding="utf-8"))
s=json.loads((BASE/"stock30-incremental-state-v2924.json").read_text(encoding="utf-8"))
assert m["version"]==s["version"]=="v2924" and len(s["families"])==30
assert m["peripera_legacy_option_JPG_PNG_pairs_SHA_verified"]==20
assert m["existing_55_verified_URLs_unchanged"]
variants=m["peripera_legacy_options"]
assert len(variants)==20
assert [x["shade"] for x in variants]==[f"{n:02d}" for n in range(1,21)]
assert m["peripera_no_21_26_options_created"]
def font(sz):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",sz)
 except:return ImageFont.load_default()
def check_file(path,expected_hash,fmt):
 p=Path(path);b=p.read_bytes()
 assert sha256(b).hexdigest()==expected_hash,(str(p),"immutable source mismatch")
 with Image.open(BytesIO(b)) as im:
  im.load()
  assert im.format==fmt
  size=list(im.size)
  rgba=im.convert("RGBA")
  full_alpha=(len(im.getbands())==4 or "transparency" in im.info)
  hist=rgba.getchannel("A").histogram()
  n_pixel=im.size[0]*im.size[1]
  partial=sum(hist[:255])
  transparent=hist[0]
  nonopaque_ratio=round(partial/n_pixel,6)
  transparent_ratio=round(transparent/n_pixel,6)
  preview=ImageOps.exif_transpose(im).convert("RGBA")
 return {"data":b,"bytes":len(b),"pixels":size,"has_alpha_channel":full_alpha,
         "nonopaque_pixel_ratio":nonopaque_ratio,"fully_transparent_pixel_ratio":transparent_ratio,
         "image":preview}

OUT.mkdir(parents=True)
pack=OUT/"PERIPERA_Legacy_01to20_20JPG_20AlphaPNG_OriginalBytes_INTERNAL-QA.zip"
results=[];flagged=[];member_payload=[]
for v in variants:
 shade=v["shade"]
 jpg=check_file(v["JPG"],v["JPG_sha256"],"JPEG")
 png=check_file(v["PNG"],v["PNG_sha256"],"PNG")
 assert jpg["pixels"]==[1080,1080],shade
 assert len(jpg["data"])<2_000_000
 flags=[]
 if min(png["pixels"])<300:flags.append("NATIVE_ALPHA_BELOW_300PX")
 if png["nonopaque_pixel_ratio"]<=0:flags.append("PNG_NO_ACTUAL_ALPHA_TRANSPARENCY")
 if not png["has_alpha_channel"]:flags.append("PNG_WITHOUT_ALPHA_CHANNEL")
 if shade in ("12","13","14","18","19"):flags.append("LEGACY_SOURCE_OR_SHADE_EDITION_HOLD")
 if v.get("known_issue"):flags.append("PRIOR_VISUAL_QA_ISSUE")
 a=f"01to20/{shade}/original_{shade}_legacy-photo_1080.jpg"
 b=f"01to20/{shade}/original_{shade}_legacy-alpha.png"
 member_payload.extend([(a,jpg["data"]),(b,png["data"])])
 record={
  "shade":shade,"legacy_source_only":True,"version_26AD_equivalence_confirmed":False,
  "JPG_original":v["JPG"],"JPG_sha256":v["JPG_sha256"],"JPG_pixels":jpg["pixels"],
  "PNG_original":v["PNG"],"PNG_sha256":v["PNG_sha256"],
  "PNG_pixels":png["pixels"],"PNG_actual_alpha_channel":png["has_alpha_channel"],
  "PNG_nonopaque_ratio":png["nonopaque_pixel_ratio"],
  "PNG_fully_transparent_ratio":png["fully_transparent_pixel_ratio"],
  "archive_entries":[a,b],"flags":flags,"commercial_license_verified":False,
  "physical_stock_shade_match_verified":False,"sale_approved":False}
 results.append(record)
 if flags: flagged.append((record,jpg["image"]))
with ZipFile(pack,"w",compression=ZIP_DEFLATED,compresslevel=6) as f:
 for name,b in member_payload:f.writestr(name,b)
with ZipFile(pack,"r") as f:
 assert len(f.namelist())==40
 for name,b in member_payload:assert f.read(name)==b,(name,"archive bytes corrupted")
def contact():
 board=Image.new("RGB",(1080,1080),"#f7f8f9")
 d=ImageDraw.Draw(board)
 d.text((24,17),"PERIPERA | FLAGGED LEGACY ORIGINALS v2925",font=font(28),fill="#242424")
 d.text((24,58),"01-20 only • Original SHA verified • No 26AD edition/rights approval",font=font(16),fill="#9a3232")
 for i,(rec,image) in enumerate(flagged[:9]):
  x=18+(i%3)*351;y=112+(i//3)*307
  d.rounded_rectangle((x,y,x+336,y+294),radius=9,fill="white",outline="#d4d4d4",width=2)
  p=ImageOps.contain(image.convert("RGB"),(320,220),Image.Resampling.LANCZOS)
  board.paste(p,(x+168-p.width//2,y+6+(220-p.height)//2))
  d.text((x+9,y+238),"#"+rec["shade"]+"  "+str(rec["PNG_pixels"][0])+"x"+str(rec["PNG_pixels"][1]),font=font(15),fill="#333333")
  why=rec["flags"][0][:35] if rec["flags"] else ""
  d.text((x+9,y+265),why,font=font(12),fill="#a23939")
 d.text((24,1040),"For inspection only. A visually similar shade cannot prove option match.",font=font(16),fill="#555555")
 return board
photo=OUT/"Peripera_flagged_legacy-shade-source_9up_visual-QA.jpg"
contact().save(photo,"JPEG",quality=89,optimize=True,subsampling=0)
with Image.open(photo) as x:assert x.size==(1080,1080) and x.format=="JPEG"
assert photo.stat().st_size<2_000_000
issue_by={}
for row in results:
 for flag in row["flags"]:issue_by.setdefault(flag,[]).append(row["shade"])
st=s["families"]["pending-08"]
st.update({
 "last_delta_version":"v2925","release_status":"20_LEGACY_SHADE_JPG_ALPHA_PNG_VERIFIED_SOURCE_ZIP_RETAIL_NOT_APPROVED",
 "v2925_40_exact_source_images_ZIP":str(pack),
 "v2925_photo_alpha_quality_flags":issue_by,
 "v2925_flagged_shade_contact":str(photo),
 "latest_photo_QA_checkpoint":f"v2925 20 original existing legacy JPG and 20 PNG unmodified bytes verified and archived, {len(flagged)} shades hold native-alpha/edition/visual issues; 21-26 not created. 26AD stock/rights HOLD.",
 "sale_approved":False})
report={"version":"v2925","baseline":"v2924","created_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "peripera_legacy_shades_archived":20,"original_JPGs":20,"original_alpha_PNGs":20,
 "original_byte_verified_images":40,"ZIP_path":str(pack),
 "ZIP_sha256":sha256(pack.read_bytes()).hexdigest(),
 "ZIP_members_integrity_verified":40,
 "flagged_shades":sorted(set(x["shade"] for x,_ in flagged)),
 "issue_shades":issue_by,
 "visual_QA_contact":str(photo),
 "new_original_photos_or_shades_generated":0,
 "shades_21_to_26_created":False,
 "old_PNG_and_JPG_bytes_modified":0,
 "preexisting_11_approved_families_preserved":True,"preexisting_55_public_URLs_preserved":True,
 "new_retail_release_approvals":0,"new_public_URLs":0,
 "final_spreadsheet_shared":False,"variants":results}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
s["version"]="v2925";s["baseline"]="v2924";s["new_sales_approvals"]=0;s["new_public_URLs"]=0;s["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2925.json").write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2925","reused_JPG_PNG_bytes":40,"ZIP_verified":True,"shades":20,
 "quality_issue_shades":issue_by,"new_sales_approvals":0},ensure_ascii=False))
