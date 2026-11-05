#!/usr/bin/env python3
"""v2923 consolidate 9 original five-photo stock family archives (45 JPGs), contact-QA + near-duplicate alerts.
NO new product photos, NO full product-completion claim, NO changes to existing 55 URLs or QA source bytes.
"""
from pathlib import Path
from hashlib import sha256
from io import BytesIO
from zipfile import ZipFile,ZIP_STORED
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,time

Q=Path("qa-review")
PRE=Q/"v2922-five-legacy-stock-family-original-25photo-internal-only-archive-ZIP"
OUT=Q/"v2923-nine-other-pending-family-45archived-source-photo-zip-and-contact-QA"
assert not OUT.exists()
st=json.loads((PRE/"stock30-incremental-state-v2922.json").read_text(encoding="utf-8"))
pre=json.loads((PRE/"manifest.json").read_text(encoding="utf-8"))
assert st["version"]=="v2922" and len(st["families"])==30 and pre["existing_55_public_URLs_unchanged"]
# Paths are all already present in preexisting QA branch and intentionally NOT recopied into public.
FAMILY_DIRS={
 "pending-03":"qa-review/v2780-four-unfinished-missha-obge-photo-first-QA/pending-03",
 "pending-04":"qa-review/v2792-clio-5g-blank-upper-margin-only-cleanup/pending-04",
 "pending-09":"qa-review/v2807-two-official-single-item-product-photo-discovery/pending-09",
 "pending-10":"qa-review/v2780-four-unfinished-missha-obge-photo-first-QA/pending-10",
 "pending-11":"qa-review/v2780-four-unfinished-missha-obge-photo-first-QA/pending-11",
 "pending-13":"qa-review/v2778-missha-pdrn-serum-correct-original-5JPG-QA/pending-13",
 "pending-14":"qa-review/v2779-five-photo-first-product-groups-QA/pending-14",
 "pending-22":"qa-review/v2775-four-photo-first-fiveframe-product-QA/pending-22",
 "pending-26":"qa-review/v2776-four-source-photo-first-fiveframe-QA/pending-26"}
MANUAL_FLAGS={
 "pending-04":{"slot-05":["SCALED_FROM_600_NATIVE_VERIFY_QUALITY"],"all":["5g shade and packaging edition must match seller SKU"]},
 "pending-09":{"all":["Only five of nine source-gallery frames were packed; source rights and package check pending"]},
 "pending-13":{"slot-03":["MODEL_COMMERCIAL_RIGHTS_UNVERIFIED"],"slot-04":["INGREDIENT_OR_EFFICACY_CLAIMS_UNVERIFIED"],"all":["Serum 30 mL and original manufacturer photo claims must match"]},
 "pending-22":{"all":["300 mL physical capacity verification and 600 px source-upscale risk"]},
 "pending-26":{"all":["145 mL generation and bottle label must match; 150 mL not interchangeable"]}}
def font(s):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",s)
 except:return ImageFont.load_default()
def dhash(rgb):
 p=ImageOps.grayscale(ImageOps.fit(rgb,(9,8))).load()
 return "".join("1" if p[x,y]>p[x+1,y] else "0" for y in range(8) for x in range(8))
def dist(a,b):return sum(x!=y for x,y in zip(a,b))
def overview(fam,product,records):
 canvas=Image.new("RGB",(1080,1080),"#f6f6f8");d=ImageDraw.Draw(canvas)
 d.text((24,13),fam.upper()+" | EXISTING FIVE SOURCE PHOTOS",font(28),fill="#282828")
 d.text((24,52),product[:69],font(18),fill="#444")
 d.text((24,80),"INTERNAL VISUAL QA / edition, rights, MK and claims NOT approved",font(16),fill="#a32c2c")
 for i,row in enumerate(records):
  x=20+(i%3)*350;y=117+(i//3)*433
  d.rounded_rectangle((x,y,x+336,y+413),radius=8,fill="white",outline="#ccc",width=2)
  fit=ImageOps.contain(row["img"],(318,335),Image.Resampling.LANCZOS)
  canvas.paste(fit,(x+168-fit.width//2,y+10+(335-fit.height)//2))
  d.text((x+12,y+350),f"EXISTING SOURCE #{i+1}",font(18),fill="#343434")
  d.text((x+12,y+384),"NOT RETAIL APPROVED",font(15),fill="#a32c2c")
 d.text((23,1036),"Existing source bytes not modified, near-similar scenes remain on QA hold.",font(16),fill="#666")
 return canvas
OUT.mkdir(parents=True)
results=[]
for fam,folder in FAMILY_DIRS.items():
 root=Path(folder)
 assert root.is_dir(),("missing archive directory",str(root))
 paths=sorted(root.glob("[0-9][0-9]-*.jpg"))[:5]
 assert len(paths)==5,(fam,[str(p) for p in paths])
 rows=[];zipdata=[];hashes=set();p_hashes=[]
 for i,p in enumerate(paths):
  b=p.read_bytes();digest=sha256(b).hexdigest()
  assert digest not in hashes,(fam,"exact image duplicate",str(p))
  hashes.add(digest)
  with Image.open(BytesIO(b)) as im:
   im.load()
   assert im.format=="JPEG" and im.size==(1080,1080) and len(b)<2_000_000,(fam,str(p),im.size)
   rgb=ImageOps.exif_transpose(im).convert("RGB")
  h=dhash(rgb)
  near=[k+1 for k,hprev in enumerate(p_hashes) if dist(h,hprev)<6]
  p_hashes.append(h)
  flags=MANUAL_FLAGS.get(fam,{})
  notes=list(flags.get("all",[]))+list(flags.get(f"slot-{i+1:02d}",[]))
  if near:notes.append("PERCEPTUAL_NEAR_DUPLICATE_CANDIDATE_REQUIRES_HUMAN_CHECK")
  record={"slot":i+1,"path":str(p),"sha256":digest,"image_bytes":len(b),
   "pixels":[1080,1080],"original_format":"JPEG",
   "zip_entry":f"{i+1:02d}-{fam}-IMMUTABLE-PHOTO-QA.jpg",
   "near_similarity_to_prior_slots":near,
   "special_review_flags":notes,
   "commercial_license_approved":False,"seller_physical_stock_generation_verified":False,
   "true_MK_logo_asset_verified":False,"retail_ready":False}
  rows.append({"img":rgb,"record":record});zipdata.append((record["zip_entry"],b))
 name=OUT/f"{fam}-five-original-photo-reference-INTERNAL-ONLY.zip"
 with ZipFile(name,"w",compression=ZIP_STORED) as z:
  for n,b in zipdata:z.writestr(n,b)
 with ZipFile(name,"r") as z:
  assert len(z.namelist())==5
  for n,b in zipdata:assert z.read(n)==b
 contact=OUT/f"{fam}-original-five-photo-contact-1080-INTERNAL.jpg"
 overview(fam,st["families"][fam]["product"],rows).save(contact,"JPEG",quality=88,optimize=True,subsampling=0)
 with Image.open(contact) as im:assert im.format=="JPEG" and im.size==(1080,1080)
 assert contact.stat().st_size<2_000_000
 flagged=sum(bool(x["record"]["special_review_flags"]) for x in rows)
 x=st["families"][fam]
 x.update({"last_delta_version":"v2923",
   "release_status":"FIVE_PREEXISTING_1080_SOURCE_JPGS_INTERNAL_ARCHIVE_QA_OWNED_EDITION_RIGHTS_MK_HOLD",
   "v2923_five_source_archive":str(name),
   "v2923_visual_contact":str(contact),
   "v2923_near_image_pair_alerts":sum(len(z["record"]["near_similarity_to_prior_slots"]) for z in rows),
   "latest_photo_QA_checkpoint":f"v2923 5 previously archived 1080 originals hash-validated, internal-only ZIP and contact saved; {flagged} slots flagged for manual photo rights, edition, near-duplicate or marketing claims. Zero retail release.",
   "sale_approved":False})
 results.append({"family":fam,"product":x["product"],
    "old_source_JPGs_integrity_checked":5,
    "reused_exact_existing_image_bytes":True,"new_product_images_rendered":0,
    "zip_path":str(name),"zip_sha256":sha256(name.read_bytes()).hexdigest(),
    "qa_contact_path":str(contact),"near_similar_pair_alerts":x["v2923_near_image_pair_alerts"],
    "all_source_photo_records":[z["record"] for z in rows],"retail_release":False})
assert len(results)==9 and sum(x["old_source_JPGs_integrity_checked"] for x in results)==45
manifest={"version":"v2923","baseline":"v2922",
 "created_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "new_internal_five_source_family_ZIPs":9,"archived_existing_source_JPGs_sha_checked":45,
 "new_1080_internal_contact_images":9,"new_product_original_photos":0,
 "new_sales_approvals":0,"new_public_URLs":0,
 "prior_v2918_2_ZIPs_preserved":True,"prior_v2920_6_ZIPs_preserved":True,"prior_v2922_5_ZIPs_preserved":True,
 "prior_11_published_families_unchanged":True,"prior_55_published_URLs_unchanged":True,
 "all_prior_QA_bytes_unchanged":True,"final_spreadsheet_shared":False,
 "results":results}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
st["version"]="v2923";st["baseline"]="v2922";st["new_sales_approvals"]=0;st["new_public_URLs"]=0;st["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2923.json").write_text(json.dumps(st,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2923","existing_JPGs_SHA_checked":45,"new_family_ZIPs":9,
 "contact_QA":9,"new_product_photos":0,"sales_approved":0},ensure_ascii=False))
