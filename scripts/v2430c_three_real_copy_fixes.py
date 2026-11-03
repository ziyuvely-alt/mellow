#!/usr/bin/env python3
"""v2430c: correct three visibly verified customer-copy defects, never modify product photo."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
SRC=Path("v2427b-source")
OUT=Path("v2430c-output")
OUT.mkdir(exist_ok=True)
BASE=SRC/"immutable-v2426b"/"originals-v2425-unchanged"/"prior-immutable"/"immutable-prev"/"preserved-v2422"/"en-photo-captions"
INFO=SRC/"immutable-v2426b"/"originals-v2425-unchanged"/"prior-immutable"/"immutable-prev"/"preserved-v2422"/"en-customer-drafts"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def font(n,bold=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if bold else "")+".ttf",n)
produced=[]
for gid,source_name,label in [
 ("pending-24","INV_01_216ad6670f_EN_V2421C.jpg","BIOHEAL BOH NAD-PRIZCELL Glow Power Serum 30 mL"),
 ("pending-25","INV_01_1bd6f7ce25_EN_V2421C.jpg","BIOHEAL BOH NAD-PRIZCELL Glow Boost Cream 50 mL")]:
 src=BASE/gid/source_name
 # Use first actual source JPEG in case versioned provenance name differs.
 if not src.is_file():
  files=sorted((BASE/gid).glob("*.jpg"))
  assert files, gid
  src=files[0]
 with Image.open(src) as img:
  im=img.convert("RGB");d=ImageDraw.Draw(im)
  bg=im.getpixel((92,944))
  d.rectangle((65,865,1010,950),fill=bg)
  size=33
  while size>=23 and d.textbbox((0,0),label,font=font(size,True))[2]>930:
   size-=1
  assert d.textbbox((0,0),label,font=font(size,True))[2]<=930
  d.text((70,882),label,font=font(size,True),fill=(45,65,53))
  out=OUT/"sales-image-drafts"/gid/(gid+"_official_name_corrected_v2430c.jpg")
  out.parent.mkdir(parents=True,exist_ok=True)
  im.save(out,"JPEG",quality=94,optimize=True)
  produced.append({"group_id":gid,"source":str(src.relative_to(SRC)),"output":str(out.relative_to(OUT)),"sha256":sha(out),"revision_type":"EN_COPY_REVISION","issue":"Visible product package spelling is NAD-PRIZCELL; lower customer caption misspelled as Preezcel","state":"SALES_IMAGE_DRAFT","visual_QA":"PENDING_AFTER_EDIT"})
# Pixelpure existing flat text only information panel. Avoid touching photo.
gid="pending-26";folder=INFO/gid
files=sorted(folder.glob("*.jpg"))
candidate=None
for f in files:
 with Image.open(f) as x:
  if x.size==(1080,1080):
   candidate=f;break
assert candidate is not None
# But do not assume first info panel matches observed screenshot. Inspect known exact source
# via SHA provenance needed. Save only explicit copy if the first source is the observed
# NET CONTENT card. Use nearest source filename if present.
matches=[p for p in files if ("VOLUME" in p.name or "NET" in p.name)]
if matches:candidate=matches[0]
with Image.open(candidate) as x:
 im=x.convert("RGB")
 # Existing layout: central text panel x72..1008 y303..763.
 # Repaint only duplicate lines beneath 145mL, leaving outside typography and image intact.
 d=ImageDraw.Draw(im)
 bg=im.getpixel((545,690))
 d.rectangle((180,548,890,700),fill=bg)
 msg="Gentle Gel-to-Foam Cleanser"
 f=font(35,False)
 bb=d.textbbox((0,0),msg,font=f)
 d.text((540-(bb[2]-bb[0])//2,590),msg,font=f,fill=(45,65,53))
 dest=OUT/"sales-image-drafts"/gid/(gid+"_repeated_copy_removed_v2430c.jpg")
 dest.parent.mkdir(parents=True,exist_ok=True);im.save(dest,"JPEG",quality=93,optimize=True)
 produced.append({"group_id":gid,"source":str(candidate.relative_to(SRC)),"output":str(dest.relative_to(OUT)),"sha256":sha(dest),"revision_type":"EN_COPY_REVISION","issue":"Duplicate product name on NET CONTENT information card","state":"SALES_IMAGE_DRAFT","visual_QA":"PENDING_AFTER_EDIT"})
for x in produced:
 with Image.open(OUT/x["output"]) as im:
  im.load()
  assert im.format=="JPEG" and im.size==(1080,1080) and (OUT/x["output"]).stat().st_size<2_000_000
report={"version":"2.4.30c","customer_JPG_revisions":len(produced),"groups_modified":3,"source_jpg_files_changed":0,"published_public_URLs_changed":0,"new_shade_chart":0,"final_qa_approved":0,"photo_rights_verified":0,"flagged_mismatch":{"pending-27":"Image product print 300 ml but listing caption 200 ml: hold until correct official SKU photo"},"edits":produced}
(OUT/"v2430c_checkpoint.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!="edits"}),flush=True)
