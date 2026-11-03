#!/usr/bin/env python3
"""v2451b fix only two v2451 layouts after actual visual QA.
Do NOT re-create remaining five. Reuse authentic photographed pixels and prior
byte-verifiable source. Avoid claims of set contents/shade verification.
"""
from PIL import Image,ImageDraw,ImageFont,ImageOps
from pathlib import Path
import hashlib,json,shutil,zipfile
BASE=Path("prior-v2445b");OLD=Path("prior-v2451")
OUT=Path("v2451b-output");OUT.mkdir(exist_ok=True)
old=json.loads((OLD/"v2451_checkpoint.json").read_text())
historical=json.loads((BASE/"v2445b-resumable-checkpoint.json").read_text())
def hash(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def font(n,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
fix={
 "pending-06": {"crop":(475,246,707,780),"title":"Kill Cover Mesh Glow Essential","detail":"Compact Front Detail"},
 "pending-07": {"crop":(175,250,664,783),"title":"Kill Cover Mesh Blur Cushion","detail":"Compact & Puff Detail"}
}
all_rows=[]
for row in old["results"]:
 gid=row["group_id"]
 before=OLD/row["output"];assert before.exists() and hash(before)==row["output_SHA256"]
 if gid in fix:
  src=BASE/row["input_image"];assert hash(src)==row["input_SHA256"]
  f=fix[gid]
  with Image.open(src) as im:
   im.load();p=ImageOps.contain(im.convert("RGB").crop(f["crop"]),(800,635),Image.Resampling.LANCZOS)
  output=Image.new("RGB",(1080,1080),"white")
  d=ImageDraw.Draw(output);ink=(47,64,55)
  d.text((68,52),"CLIO",fill=ink,font=font(37,True))
  n=45
  while n>=25 and d.textbbox((0,0),f["title"],font=font(n,True))[2]>940:n-=1
  d.text((68,117),f["title"],fill=ink,font=font(n,True))
  d.line((68,189,1012,189),fill=(178,192,182),width=2)
  output.paste(p,((1080-p.width)//2,224+(635-p.height)//2))
  d.line((68,909,1012,909),fill=(178,192,182),width=2)
  d.text((68,939),f["detail"],fill=ink,font=font(34,True))
  d.text((68,992),"Cushion",fill=ink,font=font(29))
  dest=OUT/"seven-qa-reviewed-JPGs"/gid/(gid+"_crop_QA_revised_V2451b.jpg")
  dest.parent.mkdir(parents=True,exist_ok=True)
  output.save(dest,"JPEG",quality=94,optimize=True)
  change="ONLY visually rejected crop re-framed from unchanged original photo"
  assert hash(src)==row["input_SHA256"] and hash(dest)!=hash(before)
 else:
  dest=OUT/"seven-qa-reviewed-JPGs"/gid/Path(row["output"]).name
  dest.parent.mkdir(parents=True,exist_ok=True)
  shutil.copyfile(before,dest)
  assert hash(dest)==row["output_SHA256"]
  change="EXACT original v2451 output bytes preserved, not re-created"
 with Image.open(dest) as check:
  check.load();assert check.format=="JPEG" and check.size==(1080,1080) and dest.stat().st_size<2000000
 all_rows.append({"group_id":gid,"file":str(dest.relative_to(OUT)),"SHA256":hash(dest),"status":"VISUAL_DESIGN_QA_CANDIDATE","change":change,"licensed":False,"edition_verified":False,"final_approved":False})
assert len(all_rows)==7 and sum("re-framed" in x["change"] for x in all_rows)==2
report={"version":"2.4.51b","original_run_branch":"production-assets-v2451-seven-new-photo-candidates",
"only_two_visually_defective_crops_repaired":2,"five_other_JPGs_reused_byte_identical":5,
"new_SHA_approved_as_draft":7,"prior_25_JPGs_modified":0,"source_531_JPGs_changed":0,"published_55_URL_paths_changed":0,
"MK_original_logo_generated":False,"commercial_rights_verified":0,"stock_edition_verified":0,"FINAL_SALES_APPROVED":0,
"NO_SPREADSHEETS_CREATED_OR_SHARED":True,"files":all_rows,
"next":"Open the two revised crops, then integrate seven with 25 existing files without rendering prior successes"}
(OUT/"v2451b_checkpoint.json").write_text(json.dumps(report,indent=2,ensure_ascii=False))
with zipfile.ZipFile(OUT/"v2451b_seven_actual_photo_JPGs.zip","w",zipfile.ZIP_DEFLATED) as z:
 for r in all_rows:z.write(OUT/r["file"],arcname=r["file"])
 z.write(OUT/"v2451b_checkpoint.json",arcname="v2451b_checkpoint.json")
with zipfile.ZipFile(OUT/"v2451b_seven_actual_photo_JPGs.zip") as z:assert z.testzip() is None and len(z.namelist())==8
print(json.dumps({"version":"2.4.51b","adjusted_crops":2,"unchanged":5,"total":7},ensure_ascii=False),flush=True)
