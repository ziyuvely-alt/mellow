#!/usr/bin/env python3
"""v2924 remaining eight pending families: reuse all extant original photos, no false retail approval.
- 3 five-photo immutable QA ZIPs (MISSHA Cover, MISSHA Moist, GOODAL Cream alpha)
- 20 original Peripera option JPG/PNG hash and dimension checks (01..20 only)
- 4 product/variant-specific CLIO/MISSHA mixed-source contact QA (no fabricated shots)
- Prior completed 11 groups + 55 verified public URLs remain unchanged.
"""
from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile, ZIP_STORED
from PIL import Image, ImageOps, ImageDraw, ImageFont
from io import BytesIO
import json, time, re

QA=Path("qa-review")
PRE=QA/"v2923-nine-other-pending-family-45archived-source-photo-zip-and-contact-QA"
OUT=QA/"v2924-eight-unpacked-stock-family-3five-photo-20option-4clio-source-QA"
assert not OUT.exists()
state=json.loads((PRE/"stock30-incremental-state-v2923.json").read_text(encoding="utf-8"))
pre=json.loads((PRE/"manifest.json").read_text(encoding="utf-8"))
assert state["version"]=="v2923" and len(state["families"])==30
assert pre["new_internal_five_source_family_ZIPs"]==9 and pre["prior_55_published_URLs_unchanged"]
FULL={
 "pending-01":"qa-review/v2781-coverlasting-fixed-source-and-goodal-gap-QA/pending-01",
 "pending-02":"qa-review/v2780-four-unfinished-missha-obge-photo-first-QA/pending-02",
 "pending-19":"qa-review/v2792-clio-5g-blank-upper-margin-only-cleanup/pending-19"
}
MIXED={
 "pending-05":{
  "source_paths":[
   "qa-review/v2719-four-unprocessed-clio-missha-real-photo-cutouts/pending-05/01-actual-product-cutout-square-1080-QA.jpg",
   "qa-review/v2793-three-clio-remaining-families-exact-page-edition-and-photo-proof/pending-05/01-official-5750-m-gif-REFERENCE.jpg",
   "qa-review/v2793-three-clio-remaining-families-exact-page-edition-and-photo-proof/pending-05/02-official-5750-b-gif-REFERENCE.jpg",
   "qa-review/v2793-three-clio-remaining-families-exact-page-edition-and-photo-proof/pending-05/03-official-7108-m-gif-REFERENCE.jpg",
   "qa-review/v2793-three-clio-remaining-families-exact-page-edition-and-photo-proof/pending-05/04-official-7108-b-gif-REFERENCE.jpg"],
  "blockers":["Two different product ID sets 5750 and 7108. Do not merge as one shade/edition set without verified 15g+refill package.",
              "v2861 documented possible 21C-vs-21N merchant-source relabel collision","Image rights and options unapproved"]},
 "pending-06":{
  "source_paths":[f"qa-review/v2851-clio-giftset-five-option-variant-photo-QA/pending-06/{c}-merch-exact-shade-JPG1080-QA.jpg" for c in ["19C","19N","21C","21N","23N"]],
  "blockers":["v2861 flagged all 10 shade pairs as near-identical product photos despite different filenames; cannot claim differentiated swatches",
              "Set/re-fill stock pack, source rights and MK verification pending"]},
 "pending-07":{
  "source_paths":[
   *[f"qa-review/v2861-clio-three-shade-option-QA-and-ten-variant-collision-audit/pending-07-CLIO-MeshBlur-{c}-reference-card-1080-QA.jpg" for c in ["19C","19N","21N"]],
   "qa-review/v2719-four-unprocessed-clio-missha-real-photo-cutouts/pending-07/01-actual-product-cutout-square-1080-QA.jpg",
   "qa-review/v2793-three-clio-remaining-families-exact-page-edition-and-photo-proof/pending-07/01-official-6455-m-gif-REFERENCE.jpg"],
  "blockers":["Only 19C,19N,21N shade-specific photo cards, not complete all color options; two extra entries are mixed gallery reference, not validated shade views",
              "Exact mesh-blur 15g x2 set image source and stock generation not proven"]},
 "pending-12":{
  "source_paths":[
   "qa-review/v2719-four-unprocessed-clio-missha-real-photo-cutouts/pending-12/01-actual-product-cutout-square-1080-QA.jpg",
   *[str(p) for p in sorted(Path("qa-review/v2678-missha-clio-two-five-JPG-sets/pending-12").glob("[0-9][0-9]-*.jpg"))[:4]]
  ],
  "blockers":["Label quantity conflict 15g vs 15mL. No image relabel or retail release until official owned stock confirmed",
              "Mixed factual information cards are not five independently proven photographs"]}
}
assert len(MIXED)==4 and all(len(x["source_paths"])==5 for x in MIXED.values())
PERI=QA/"v2762-peripera20-variant-QA-and-missha-serum-hero-upgrade"
p_manifest=json.loads((PERI/"manifest.json").read_text(encoding="utf-8"))
assert p_manifest["shade_option_range"].startswith("01-20") and len(p_manifest["peripera_variants"])==20
assert [x["shade_number"] for x in p_manifest["peripera_variants"]]==[f"{i:02d}" for i in range(1,21)]

def font(sz):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",sz)
 except:return ImageFont.load_default()

def checked_image(path,expected=None):
 p=Path(path); b=p.read_bytes();digest=sha256(b).hexdigest()
 if expected is not None: assert digest==expected,("old source bytes mutated",str(p))
 with Image.open(BytesIO(b)) as im:
  im.load()
  fmt=im.format;native=im.size
  assert fmt in ("JPEG","PNG","WEBP") and min(native)>=300 and max(native)<=6000
  rgb=ImageOps.exif_transpose(im).convert("RGB")
 return {"path":str(p),"sha256":digest,"bytes":len(b),"format":fmt,"pixels":list(native),"rgb":rgb,"original_bytes":b}
def draw_card(family,title,items,notes):
 sheet=Image.new("RGB",(1080,1080),"#f5f6f7");draw=ImageDraw.Draw(sheet)
 draw.text((24,17),family.upper()+" | v2924 REUSED SOURCE QA",font=font(28),fill="#303030")
 draw.text((24,59),title[:70],font=font(19),fill="#444444")
 draw.text((24,88),"NOT FOR RETAIL: confirm exact owned stock, rights, shade and original MK",font=font(16),fill="#a13535")
 for idx,item in enumerate(items[:5]):
  col=idx%3;row=idx//3;x=23+col*350;y=131+row*423
  draw.rounded_rectangle((x,y,x+332,y+400),radius=12,fill="white",outline="#cecece",width=2)
  im=ImageOps.contain(item["rgb"],(314,320),Image.Resampling.LANCZOS)
  sheet.paste(im,(x+166-im.width//2,y+8+(320-im.height)//2))
  draw.text((x+10,y+346),f"SRC {idx+1} {item['pixels'][0]}x{item['pixels'][1]}",font=font(17),fill="#373737")
  draw.text((x+10,y+374),"QA ONLY",font=font(14),fill="#a13535")
 draw.text((23,1006),notes[:90],font=font(14),fill="#a13535")
 return sheet

OUT.mkdir(parents=True)
packed=[];partial=[]
for fam,directory in FULL.items():
 files=sorted(Path(directory).glob("[0-9][0-9]-*.jpg"))
 assert len(files)==5,(fam,len(files))
 images=[checked_image(p) for p in files]
 for x in images:assert x["format"]=="JPEG" and x["pixels"]==[1080,1080] and x["bytes"]<2_000_000
 assert len({x["sha256"] for x in images})==5,(fam,"duplicate JPG")
 zip_path=OUT/(fam+"-5photo-source-byte-exact-INTERNAL-ONLY.zip")
 with ZipFile(zip_path,"w",compression=ZIP_STORED) as z:
  for idx,item in enumerate(images,1):z.writestr(f"{idx:02d}-{fam}-archived-source-UNCHANGED-QA.jpg",item["original_bytes"])
 with ZipFile(zip_path,"r") as z:
  for idx,item in enumerate(images,1):assert z.read(f"{idx:02d}-{fam}-archived-source-UNCHANGED-QA.jpg")==item["original_bytes"]
 contact=OUT/(fam+"-five-archived-photo-CONTACT-1080-INTERNAL.jpg")
 draw_card(fam,state["families"][fam]["product"],images,"Five old photo files do NOT mean five stock/edition or commercial approvals").save(contact,"JPEG",quality=88,optimize=True)
 assert contact.stat().st_size<2_000_000
 blockers=["Current user physical inventory and exact edition not documented","Commercial source photo rights and genuine MK owner logo not verified"]
 if fam=="pending-01": blockers.append("Only 23 cushion hero grounded; missing color #21,#25,#27 independent images")
 if fam=="pending-02": blockers.append("Korean-vs-regional generation/photo conflict unresolved")
 if fam=="pending-19": blockers.append("25AD Alpha formula and regional set photos require source and batch verification")
 st=state["families"][fam]
 st.update({"last_delta_version":"v2924","release_status":"EXISTING_FIVE_SOURCE_PHOTOS_ARCHIVED_NO_OWNED_EDITION_RIGHTS_APPROVAL",
  "v2924_internal_5source_zip":str(zip_path),"v2924_source_QA_contact":str(contact),
  "sale_approved":False,
  "latest_photo_QA_checkpoint":f"v2924 reused and SHA-verified five 1080 existing photos for {fam}, stored internal-only ZIP/contact. All sale rights and exact product options/packaging HOLD."})
 packed.append({"family":fam,"product":st["product"],"photo_count":5,
   "original_source_files":[{"path":x["path"],"sha256":x["sha256"],"pixels":x["pixels"],"bytes":x["bytes"]} for x in images],
   "internal_zip":str(zip_path),"zip_sha256":sha256(zip_path.read_bytes()).hexdigest(),
   "internal_contact":str(contact),"blockers":blockers,"sale_approved":False})
for fam,cfg in MIXED.items():
 items=[];errors=[]
 for p in cfg["source_paths"]:
  try:items.append(checked_image(p))
  except Exception as e:errors.append({"path":p,"error":str(e)[:130]})
 contact=OUT/(fam+"-mixed-option-sources-contact-INTERNAL.jpg") if items else None
 if contact:
  draw_card(fam,state["families"][fam]["product"],items,"MIXED media, some options unresolved; not a five-photo product pack").save(contact,"JPEG",quality=87,optimize=True)
  assert contact.stat().st_size<2_000_000
 st=state["families"][fam]
 st.update({"last_delta_version":"v2924","sale_approved":False,
  "release_status":"MIXED_CUSHION_OR_TREATMENT_SOURCE_REFERENCES_STOCK_VARIANT_OR_VOLUME_BLOCK",
  "v2924_mixed_reference_count":len(items),"v2924_mixed_contact":str(contact) if contact else None,
  "latest_photo_QA_checkpoint":f"v2924 scanned {len(items)} previously archived hero/option/source images; {len(errors)} unreadable, mixed product edition/volumes/option-photo risk. No five-photo retail pack or original images changed."})
 partial.append({"family":fam,"product":st["product"],"reference_count":len(items),
  "unreadable_count":len(errors),"errors":errors,"reference_paths":[{"path":x["path"],"sha256":x["sha256"],"pixels":x["pixels"],"format":x["format"]} for x in items],
  "internal_contact":str(contact) if contact else None,
  "blockers":cfg["blockers"],"retail_approved":False})

# Verify all legacy Peripera shade artwork without creating any new shade, swatch or synthetic product photo.
variants=[];views=[];hseen={};photo_source_warnings=[]
for item in p_manifest["peripera_variants"]:
 n=item["shade_number"]
 src_jpg=PERI/item["jpg_file"];src_png=PERI/item["png_file"]
 a=checked_image(src_jpg,item["jpg_sha256"]);b=checked_image(src_png,item["png_sha256"])
 assert a["format"]=="JPEG" and a["pixels"]==[1080,1080],(n,"JPG")
 assert b["format"]=="PNG" and b["pixels"]==item["alpha_dimensions"],(n,"PNG")
 assert n not in hseen
 hseen[n]={"jpg":a["sha256"],"png":b["sha256"]}
 flag="BRAND_EDITION_IMAGE_IDENTITY_UNVERIFIED"
 if n in ["12","13","14","18","19"]:flag="EXPLICIT_LEGACY_PHOTO_SOURCE_HOLD"
 variants.append({"shade":n,"JPG":str(src_jpg),"JPG_sha256":a["sha256"],"PNG":str(src_png),"PNG_sha256":b["sha256"],
   "legacy_edition_only":True,"known_issue":item.get("known_issue"),
   "status":flag,"commercial_photo_rights_approved":False,"26AD_photo_proven":False,"retail_approved":False})
 views.append((n,a["rgb"]))
for idx in range(21,27):
 assert f"{idx:02d}" not in hseen

sheet=Image.new("RGB",(1080,1080),"#f7f7f8");draw=ImageDraw.Draw(sheet)
draw.text((27,12),"PERIPERA 01-20 | LEGACY OPTION REUSE AUDIT v2924",font=font(25),fill="#222")
draw.text((27,47),"SHA verified; 26AD renewal and commercial usage NOT approved",font=font(16),fill="#9d3333")
for i,(n,img) in enumerate(views):
 col=i%5;row=i//5;x=15+col*211;y=81+row*236
 box=(x,y,x+204,y+227)
 draw.rounded_rectangle(box,radius=8,fill="white",outline="#ddd",width=1)
 small=ImageOps.contain(img,(192,192),Image.Resampling.LANCZOS)
 sheet.paste(small,(x+102-small.width//2,y+2+192//2-small.height//2))
 draw.text((x+83,y+199),n,font=font(15),fill="#9b3030" if n in ("12","13","14","18","19") else "#333")
draw.text((22,1033),"Red shade IDs: known source-photo holds. 21-26 were NOT generated.",font=font(16),fill="#444")
pcontact=OUT/"peripera-01to20-legacy-source-20shade-INTERNAL-CONTACT.jpg"
sheet.save(pcontact,"JPEG",quality=90,optimize=True)
with Image.open(pcontact) as test:assert test.size==(1080,1080) and test.format=="JPEG"
assert pcontact.stat().st_size<2_000_000
state["families"]["pending-08"].update({"last_delta_version":"v2924",
 "release_status":"LEGACY_20SHADE_PNG_JPG_HASH_AUDIT_26AD_MISMATCH_AND_PHOTO_RIGHTS_HOLD",
 "v2924_verified_legacy_option_pairs":20,"v2924_legacy_variant_contact":str(pcontact),
 "v2924_explicit_high_risk_shades":["12","13","14","18","19"],
 "latest_photo_QA_checkpoint":"v2924 source SHA/dimensions verified for 01-20 legacy JPG+alpha pairs. Five source-photo hold shades 12,13,14,18,19. No 21-26 addition, no 26AD label equivalence, no retail rights.",
 "sale_approved":False})
assert len(packed)==3 and len(partial)==4 and len(variants)==20
manifest={"version":"v2924","baseline":"v2923","created_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "remaining_pending_families_scanned":8,
 "three_five_photo_archive_zips_created":3,"existing_JPGs_repacked_verbatim":15,
 "four_mixed_source_family_technical_contact_QAs":sum(bool(x["internal_contact"]) for x in partial),
 "peripera_legacy_option_JPG_PNG_pairs_SHA_verified":20,
 "peripera_total_original_source_images_verified":40,
 "peripera_known_hold_shades":["12","13","14","18","19"],
 "peripera_no_21_26_options_created":True,
 "new_internal_peripera_20shade_contact":str(pcontact),
 "new_product_photo_originals":0,"original_source_pixels_changed":0,
 "prior_v2918_2_ZIPs_preserved":True,"prior_v2920_6_ZIPs_preserved":True,
 "prior_v2922_5_ZIPs_preserved":True,"prior_v2923_9_ZIPs_preserved":True,
 "approved_11_commercial_families_unchanged":True,"existing_55_verified_URLs_unchanged":True,
 "new_sale_approved_images":0,"new_public_image_URLs":0,
 "final_spreadsheet_shared":False,"full_reused_5photo_archives":packed,
 "mixed_option_sources":partial,"peripera_legacy_options":variants}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
state["version"]="v2924";state["baseline"]="v2923";state["new_sales_approvals"]=0;state["new_public_URLs"]=0;state["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2924.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2924","full_existing_5JPG_packs":3,"mixed_option_families_scanned":4,
 "peripera_legacy_SHA_verified":20,"peripera_held_five_shades":[12,13,14,18,19],
 "retail_release_count":0},ensure_ascii=False))
