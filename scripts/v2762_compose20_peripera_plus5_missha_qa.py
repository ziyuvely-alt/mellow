#!/usr/bin/env python3
"""v2762 Production-oriented QA assembly from already saved product photos.

No generated product pixels, new cutouts, invented options or swatches.
20 legacy PERIPERA variant-specific alpha PNG and 1080 JPG candidates are
assembled from exact prior successful artifacts without reencoding.
MISSHA 30ml serum 5-frame QA pack swaps only frame02 to v2761 clean
official product-and-dropper foreground JPG (no decorative red circle).
Other four 5-frame QA JPGs preserve source bytes.
No original photos, product URLs, prior approvals, or XLSX touched.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import shutil,hashlib,base64,json
ROOT=Path("qa-review")
OUT=ROOT/"v2762-peripera20-variant-QA-and-missha-serum-hero-upgrade"
assert not OUT.exists()
OUT.mkdir(parents=True)
SERUM_OLD=ROOT/"v2697-missha-serum-one-product-lifestyle-photo-repair"
SERUM_NEW=ROOT/"v2761-peripera19-no-lip-panel-and-missha30ml-source03-qa/pending-13/serum-exact-photo-detail-1080-QA.jpg"
assert SERUM_OLD.is_dir() and SERUM_NEW.is_file()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def get_pair(n):
 label=f"{n:02d}"
 if n==12:
  base=ROOT/"v2755-only-peripera-12-legacy-alternate-bottle-photo"
  return(base/"12-Warm-gorithm-real-old-product-alpha-QA.png",
         base/"12-Warm-gorithm-true-alpha-1080-JPG-QA.jpg","v2755")
 if n in (13,14):
  base=ROOT/"v2754-peripera-peritage-three-missing-bottle-source-QA"/f"shade-{label}"
  return(base/f"{label}-real-photo-alpha-only-QA.png",
         base/f"{label}-old-peritage-true-alpha-1080-QA.jpg","v2754")
 if n==18:
  base=ROOT/"v2760-peripera-18-19-alternate-actual-photo-alpha/shade-18"
  return(base/"18-new-source-true-alpha-QA.png",
         base/"18-new-actual-photo-cutout-1080-QA.jpg","v2760")
 if n==19:
  base=ROOT/"v2761-peripera19-no-lip-panel-and-missha30ml-source03-qa/shade-19"
  return(base/"19-source-detail-genuine-alpha-QA.png",
         base/"19-exact-photo-detail-1080-QA.jpg","v2761")
 base=ROOT/"v2753-peripera-legacy-17-product-real-alpha-qa"/f"shade-{label}"
 return(base/f"{label}-exact-legacy-product-true-alpha-QA.png",
        base/f"{label}-legacy-real-cutout-1080-JPG-QA.jpg","v2753")
MANUAL_HOLDS={
 12:"Old Peritage Warm-gorithm, require exact owned stock edition confirmation",
 13:"Old Peritage Berry Pretty, ribbon variant may differ from original inventory",
 14:"Old Peritage Follow Rose label; actual owned 014 and 26AD names conflict",
 18:"Nude Area: decorative lipstick swatch remains behind product. Not a bare clean packshot",
 19:"Mauve Chaos: background paint swatch remains attached. Not a bare clean packshot"
}
pdir=OUT/"pending-08-peripera-legacy-01to20";pdir.mkdir()
rows=[]
for number in range(1,21):
 srcpng,srcjpg,source_version=get_pair(number)
 assert srcpng.is_file() and srcjpg.is_file(),(number,srcpng,srcjpg)
 png=pdir/f"{number:02d}-legacy-source-alpha-QA.png"
 jpg=pdir/f"{number:02d}-legacy-product-1080-QA.jpg"
 shutil.copy2(srcpng,png);shutil.copy2(srcjpg,jpg)
 assert sha(srcpng)==sha(png) and sha(srcjpg)==sha(jpg)
 with Image.open(png) as im:
  im.load()
  assert im.format=="PNG" and im.mode=="RGBA", (png,im.mode)
  size=list(im.size)
 with Image.open(jpg) as im:
  im.load()
  assert im.format=="JPEG" and im.size==(1080,1080),jpg
 assert jpg.stat().st_size<2_000_000
 held=number in MANUAL_HOLDS
 rows.append({
  "shade_number":f"{number:02d}","product_family":"pending-08",
  "variant_edition":"LEGACY_PRE_26AD_ONLY",
  "source_QA_version":source_version,
  "png_file":str(png.relative_to(OUT)),"jpg_file":str(jpg.relative_to(OUT)),
  "alpha_dimensions":size,"png_sha256":sha(png),"jpg_sha256":sha(jpg),
  "photo_files_exactly_preserved":True,
  "manual_photo_qa":"HOLD_VISUAL_CONTENT_OR_OPTION_ID" if held else "QA_CANDIDATE_REQUIRES_STOCK_AND_RIGHTS_CHECK",
  "known_issue":MANUAL_HOLDS.get(number),
  "physical_stock_editions_verified":False,
  "licensed_commercial_use_verified":False,
  "retail_approved":False
 })
assert len(rows)==20
# Serum existing 5-frame photo QA with 1 real clearer replacement.
serum_folder=OUT/"pending-13-missha-serum-30ml";serum_folder.mkdir()
oldframes=sorted(SERUM_OLD.glob("[0-9][0-9]-*.jpg"))
assert len(oldframes)==5
serum_rows=[]
for source in oldframes:
 slot=int(source.name[:2])
 chosen=SERUM_NEW if slot==2 else source
 dest=serum_folder/f"{slot:02d}-"+("v2761-official-single-serum-dropper-hero" if slot==2 else "old-source-byte-identical")+".jpg"
 shutil.copy2(chosen,dest)
 assert sha(chosen)==sha(dest)
 with Image.open(dest) as im:
  im.load();assert im.format=="JPEG" and im.size==(1080,1080)
 assert dest.stat().st_size<2000000
 serum_rows.append({"slot":slot,"file":str(dest.relative_to(OUT)),
  "source":str(chosen),"source_sha256":sha(chosen),"new_revision_change":slot==2,
  "source_bytes_identical":True})
assert [x["slot"] for x in serum_rows]==[1,2,3,4,5]
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
regular=ImageFont.truetype(FONT,19)
bold=ImageFont.truetype(BOLD,26)
for page in range(4):
 board=Image.new("RGB",(1870,475),"#eeefec")
 d=ImageDraw.Draw(board)
 d.text((20,13),f"v2762 PERIPERA LEGACY SHADES {page*5+1:02d}-{page*5+5:02d} / SOURCE JPGs UNCHANGED / NOT RETAIL",font=bold,fill="#313131")
 for idx,row in enumerate(rows[page*5:(page+1)*5]):
  with Image.open(OUT/row["jpg_file"]) as image:
   tile=image.convert("RGB").resize((340,340),Image.Resampling.LANCZOS)
  x=15+idx*369
  board.paste(tile,(x,58))
  d.text((x,410),f"#{row['shade_number']} | "+("HOLD DETAIL" if row["known_issue"] else "QA CANDIDATE"),font=regular,fill="#323232")
 proof=OUT/f"v2762-peripera-review-page-{page+1}.jpg"
 board.save(proof,"JPEG",quality=85,optimize=True)
 (OUT/f"v2762-peripera-review-page-{page+1}.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
board=Image.new("RGB",(1870,475),"#eeefec")
d=ImageDraw.Draw(board)
d.text((18,12),"v2762 MISSHA PDRN 30mL / FRAME 02 ONLY UPDATED WITH REAL BOTTLE+DROPPER",font=bold,fill="#313131")
for idx,rec in enumerate(serum_rows):
 with Image.open(OUT/rec["file"]) as im:
  tile=im.convert("RGB").resize((338,338),Image.Resampling.LANCZOS)
 x=15+idx*369
 board.paste(tile,(x,58))
 d.text((x,408),f"FRAME {rec['slot']:02d} | "+("CLEANER NEW HERO" if rec["new_revision_change"] else "PRESERVED"),font=regular,fill="#323232")
preview=OUT/"v2762-missha-5-photo-review.jpg"
board.save(preview,"JPEG",quality=84,optimize=True)
(OUT/"v2762-missha-5-photo-review.b64.txt").write_text(base64.b64encode(preview.read_bytes()).decode())
report={
 "version":"v2762","baseline":"v2761",
 "product_families":["pending-08","pending-13"],
 "legacy_PERIPERA_variant_JPG_and_alpha_pairs_integrated":20,
 "legacy_variant_exact_source_bytes_reused":20,
 "photo_option_26AD_interpolation_performed":False,
 "shade_option_range":"01-20 only; do NOT add 21-26",
 "peripera_photo_source_holds":[f"{i:02d}" for i in MANUAL_HOLDS],
 "missha_serum_new_5frame_QA_set":True,
 "missha_serum_only_one_slot_changed":2,
 "missha_serum_four_original_JPGs_preserved":True,
 "newly_rendered_product_pixel_count":0,
 "licensed_commercial_photo_rights_confirmed":False,
 "actual_stock_edition_matching_proven":False,
 "original_MK_round_logo_verified":False,
 "new_retail_approvals":0,
 "original_11_published_families_unchanged":True,
 "existing_55_public_urls_unchanged":True,
 "prior_v2761_assets_modified":False,
 "final_spreadsheet_shared":False,
 "peripera_variants":rows,
 "missha_serum_frame_sources":serum_rows
}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2762","peripera_variants_copied":20,
 "shade_detail_holds":list(MANUAL_HOLDS),"missha_5frame_set":True,
 "missha_changed_frame":2,"approved_new":0}))
