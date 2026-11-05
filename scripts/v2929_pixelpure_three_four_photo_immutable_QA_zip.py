#!/usr/bin/env python3
"""v2929: Consolidate 3 non-duplicated existing PixelPure photos added in v2927/v2928.
Build 3 product-first 4/5 QA photo ZIPs from unmodified 1080 JPEG bytes. Do not
fabricate missing fifth scenes or imply commercial photo licensing or packaging approval.
Preserve v2918/v2920/v2922/v2923/v2924/v2925 and published 11 families / 55 URLs.
"""
from pathlib import Path
from zipfile import ZipFile,ZIP_STORED
from io import BytesIO
from hashlib import sha256
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,time

QA=Path("qa-review")
D20=QA/"v2920-six-incomplete-stock-groups-real-original-photo-bytes-internal-ZIP"
D27=QA/"v2927-pixelpure-two-direct-official-source-originals-dedupe-QA"
D28=QA/"v2928-pixelpure-2-known-official-catalogue-images-conditional-new-QA"
LEDGER=QA/"v2926-30family-26sourcezip-qa-state-and-next-action-ledger"
OUT=QA/"v2929-pixelpure-three-four-photo-pack-source-integrity-QA"
assert not OUT.exists()
m20=json.loads((D20/"manifest.json").read_text(encoding="utf-8"))
m27=json.loads((D27/"manifest.json").read_text(encoding="utf-8"))
m28=json.loads((D28/"manifest.json").read_text(encoding="utf-8"))
s=json.loads((D28/"stock30-incremental-state-v2928.json").read_text(encoding="utf-8"))
ledger=json.loads((LEDGER/"manifest.json").read_text(encoding="utf-8"))
assert m28["version"]==s["version"]=="v2928" and m27["version"]=="v2927"
assert m28["new_unique_native_originals_saved"]==1 and m27["new_native_official_photo_candidates_archived"]==2
assert ledger["sha256_and_ZIP_CRC_verified_archives"]==26
assert len(s["families"])==30
def font(n):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",n)
 except:return ImageFont.load_default()
def dhash(img):
 gray=ImageOps.grayscale(ImageOps.fit(img,(9,8))).load()
 return "".join("1" if gray[x,y]>gray[x+1,y] else "0" for y in range(8) for x in range(8))
def hd(a,b):return sum(x!=y for x,y in zip(a,b))
def jpgcheck(data):
 with Image.open(BytesIO(data)) as im:
  im.load()
  assert im.format=="JPEG" and im.size==(1080,1080) and len(data)<2_000_000
  rgb=ImageOps.exif_transpose(im).convert("RGB")
  return rgb,dhash(rgb)
def sheet(family,title,photos):
 can=Image.new("RGB",(1080,1080),"#f4f5f6");d=ImageDraw.Draw(can)
 d.text((25,18),family.upper()+" | FOUR UNMODIFIED SOURCE PHOTOS",font=font(27),fill="#242424")
 d.text((25,58),title[:66],font=font(19),fill="#444444")
 d.text((25,89),"4/5 original source JPGs • 1 photo missing • NOT retail-approved",font=font(18),fill="#a32d2d")
 for i,p in enumerate(photos):
  row,col=divmod(i,2);x=23+col*523;y=134+row*428
  d.rounded_rectangle((x,y,x+504,y+407),radius=10,fill="#fff",outline="#ddd",width=2)
  fit=ImageOps.contain(p["image"],(482,326),Image.Resampling.LANCZOS)
  can.paste(fit,(x+252-fit.width//2,y+11+(326-fit.height)//2))
  d.text((x+12,y+349),f"PHOTO {i+1} | "+("EXISTING" if i<3 else "BRAND-NEW REF"),font=font(18),fill="#333333")
  d.text((x+12,y+378),"STOCK / RIGHTS / AUTHENTIC MK: HOLD",font=font(14),fill="#9d3434")
 d.text((24,1014),"No new original photography or fake fifth slide. Prior public URLs unchanged.",font=font(16),fill="#666666")
 return can

v20={x["family"]:x for x in m20["results"]}
v27={x["family"]:x for x in m27["results"]}
v28={x["family"]:x for x in m28["results"]}
cases=[
 {"family":"pending-27","original":v27["pending-27"]["new_reference"],
  "source":"v2927","role":"Toner + carton on studio background"},
 {"family":"pending-29","original":v28["pending-29"]["new_candidate"],
  "source":"v2928","role":"Closed cream jar official catalogue photo"},
 {"family":"pending-30","original":v27["pending-30"]["new_reference"],
  "source":"v2927","role":"Several serum bottles arranged in studio"}
]
assert all(x["original"] for x in cases)
OUT.mkdir(parents=True)
records=[]
for case in cases:
 fam=case["family"];prior=v20[fam]
 assert prior["actual_original_source_jpgs_in_zip"]==3
 before=Path(prior["zip_path"])
 assert sha256(before.read_bytes()).hexdigest()==prior["zip_sha256"]
 photos=[]
 with ZipFile(before,"r") as z:
  assert len(z.namelist())==3 and z.testzip() is None
  for idx,name in enumerate(z.namelist(),1):
   data=z.read(name);img,px=jpgcheck(data)
   photos.append({"bytes":data,"image":img,"phash":px,"src":f"{before}:{name}",
     "sha256":sha256(data).hexdigest(),"provenance":"v2920_existing_unchanged"})
 latest=case["original"]
 if case["source"]=="v2927":
  path=latest["reference_path"];sig=latest["reference_sha256"]
  native=latest["original_path"];native_sig=latest["original_sha256"]
  dist_prior=latest["near_distance_from_three_previous_sources"]
 else:
  path=latest["reference_1080"];sig=latest["reference_sha256"]
  native=latest["source_original"];native_sig=latest["source_original_sha256"]
  dist_prior=latest["dhash_distance_to_closest_prior"]
 assert dist_prior>=6
 native_bytes=Path(native).read_bytes()
 assert sha256(native_bytes).hexdigest()==native_sig
 newdata=Path(path).read_bytes()
 assert sha256(newdata).hexdigest()==sig
 im,ph=jpgcheck(newdata)
 assert sig not in {p["sha256"] for p in photos}
 # Source images visually passed product identity at previous checkpoints.
 actual_min=min(hd(ph,p["phash"]) for p in photos)
 assert actual_min>=6,("new candidate similar to previously archived scene",fam,actual_min)
 photos.append({"bytes":newdata,"image":im,"phash":ph,"src":path,
  "sha256":sig,"provenance":case["source"]+"_firstparty_source"})
 assert len(photos)==4
 output=OUT/(fam+"-four-valid-photo-source-ONLY-INTERNAL.zip")
 with ZipFile(output,"w",compression=ZIP_STORED) as z:
  for i,p in enumerate(photos,1):z.writestr(f"{i:02d}-{fam}-EXISTING_SOURCE_ONLY_1080.jpg",p["bytes"])
 with ZipFile(output,"r") as z:
  assert len(z.namelist())==4 and z.testzip() is None
  for i,p in enumerate(photos,1):assert z.read(f"{i:02d}-{fam}-EXISTING_SOURCE_ONLY_1080.jpg")==p["bytes"]
 contact=OUT/(fam+"-four-source-photo-COMPARISON-INTERNAL.jpg")
 sheet(fam,s["families"][fam]["product"],photos).save(contact,"JPEG",quality=88,optimize=True,subsampling=0)
 with Image.open(contact) as chk:assert chk.format=="JPEG" and chk.size==(1080,1080)
 assert contact.stat().st_size<2_000_000
 st=s["families"][fam]
 st.update({"last_delta_version":"v2929",
  "release_status":"FOUR_EXISTING_SHA_VERIFIED_SOURCES_IN_INTERNAL_ZIP_ONE_SOURCE_MISSING",
  "v2929_existing_four_source_ZIP":str(output),
  "v2929_four_photo_contact":str(contact),
  "v2929_missing_photo_sources_to_five":1,
  "latest_photo_QA_checkpoint":"v2929 source SHA-validated 3 prior 1080 JPEGs plus one first-party photo, all four byte-for-byte unchanged, internal ZIP & comparison generated. One new authentic source needed; stock/rights/MK unverified.",
  "sale_approved":False})
 records.append({
  "family":fam,"product":st["product"],"archive_ZIP":str(output),
  "archive_ZIP_sha256":sha256(output.read_bytes()).hexdigest(),
  "contact":str(contact),"source_photos":4,"five_photo_shortfall":1,
  "source_records":[{"original_source_path":p["src"],"sha256":p["sha256"],"origin":p["provenance"],
    "license_approved":False,"actual_stock_edition_verified":False,
    "retail_approved":False} for p in photos],
  "latest_new_source_hamming":actual_min,"new_original_photo_bytes_created":0,
  "sale_approved":False})
summary={"version":"v2929","baseline":"v2928",
 "generated_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "pending_product_families_updated":3,"four_source_internal_ZIPs_created":3,
 "new_photo_source_references_reused":3,
 "original_photography_created":0,"old_source_photo_bytes_modified":0,
 "existing_source_photo_JPGs_SHA_checked":12,
 "remaining_five_photo_slots_across_all_6_partial_families":8,
 "original_11_approved_families_unchanged":True,
 "original_55_published_URLs_unchanged":True,
 "prior_26_QA_ZIPs_reused_without_overwriting":True,
 "new_retail_approved":0,"new_public_URLs":0,
 "final_spreadsheet_shared":False,"results":records}
(OUT/"manifest.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
s["version"]="v2929";s["baseline"]="v2928";s["new_sales_approvals"]=0;s["new_public_URLs"]=0;s["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2929.json").write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2929","four_source_ZIPs":3,"verified_photos":12,
 "remaining_missing_eight":8,"commercially_approved":0},ensure_ascii=False))
