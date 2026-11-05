#!/usr/bin/env python3
"""v2983: one newly needed photo-free correction card for the OBgE Double Essence
mixed-bottle source slot. Existing 2026 v2620 retouched photo remains untouched.
Do not infer owned packaging, mimic original MK, or republish merchant photographs.
"""
from pathlib import Path
import json, hashlib
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa-review/v2983-obge-doubleessence-photo-free-dual-formula-replacement-20261106"
EVIDENCE=ROOT/"evidence/latest-qa-checkpoint-v2620-corrected-obge-double-essence-two-formulas-20261104.json"
ROSTER=ROOT/"qa-review/v2982-30-family-restart-with-four-fiveframe-corrections-20261106/manifest.json"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def f(n,b=False):return ImageFont.truetype(BOLD if b else FONT,n)
def h(b):return hashlib.sha256(b).hexdigest()
def main():
    if OUT.exists():raise RuntimeError("v2983 already exists. Refuse repeated generation.")
    prior=json.loads(EVIDENCE.read_text(encoding="utf8"))
    assert prior["version"]=="v2620" and "Step 1 formula correctly shown TONER + ESSENCE" in prior["actual_output"]["change"]
    r=json.loads(ROSTER.read_text(encoding="utf8"))
    assert r["version"]=="v2982" and len(r["pending_product_families"])==30
    OUT.mkdir(parents=True)
    im=Image.new("RGB",(1080,1080),(247,247,243))
    d=ImageDraw.Draw(im);dark=(49,49,44);accent=(108,92,76)
    d.rectangle((0,0,1080,22),fill=(91,77,64))
    d.rounded_rectangle((65,62,1015,1015),radius=48,fill="white",outline=(229,222,214),width=3)
    d.rounded_rectangle((105,101,351,165),radius=22,fill=(237,231,223))
    d.text((140,119),"PRODUCT GUIDE",font=f(25,True),fill=accent)
    d.text((105,208),"OBgE ALL IN ONE",font=f(45,True),fill=dark)
    d.text((105,262),"DOUBLE ESSENCE",font=f(52,True),fill=dark)
    d.text((105,329),"ONE PRODUCT  |  TWO FORMULAS",font=f(26,True),fill=accent)
    d.line([(105,390),(973,390)],fill=(221,216,209),width=3)
    for i,(head,ml,desc,tone) in enumerate([
        ("TONER + ESSENCE","50 mL","FORMULA 01",(240,243,238)),
        ("LOTION + CREAM","50 mL","FORMULA 02",(246,237,224))
    ]):
        top=438+i*205
        d.rounded_rectangle((105,top,971,top+170),radius=25,fill=tone,outline=(223,222,216),width=2)
        d.rounded_rectangle((129,top+21,322,top+64),radius=12,fill=(255,255,255))
        d.text((149,top+31),desc,font=f(18,True),fill=accent)
        d.text((141,top+80),head,font=f(37,True),fill=dark)
        d.text((796,top+90),ml,font=f(31,True),fill=accent)
    d.rounded_rectangle((105,867,973,935),radius=20,fill=(239,238,232))
    d.text((140,886),"TOTAL CONTENT: 100 mL  |  NOT TWO BOTTLES",font=f(24,True),fill=dark)
    d.text((105,957),"INTERNAL QA  |  PHYSICAL EDITION + ORIGINAL MK LOGO PENDING",font=f(15),fill=(128,113,104))
    p=OUT/"pending-11-OBgE-two-formulas-50plus50-ONE-product-INTERNAL-QA.jpg"
    im.save(p,format="JPEG",quality=92,optimize=True,subsampling=0)
    with Image.open(p) as test:
        test.load()
        assert test.format=="JPEG" and test.size==(1080,1080) and p.stat().st_size<2_000_000
    report={"version":"v2983","date_kst":"2026-11-06","parent":"v2982",
      "family":"pending-11","product":"OBgE All In One Double Essence",
      "new_original_JPG":str(p.relative_to(ROOT)),
      "new_original_SHA256":h(p.read_bytes()),"bytes":p.stat().st_size,
      "size":[1080,1080],
      "corrected_detail":"ONE 100mL bottle with 50mL toner+essence and 50mL lotion+cream formulas (not two bottles)",
      "source_prior":"evidence/latest-qa-checkpoint-v2620-corrected-obge-double-essence-two-formulas-20261104.json",
      "source_official_store":"https://www.obge.co.kr/product/detail.html?cate_no=0&display_group=0&product_no=15",
      "source_factual_content":"https://www.ssg.com/item/itemView.ssg?itemId=1000464955759",
      "source_two_formula_text":"https://www.yesstyle.com/en/obge-all-in-one-double-essence-100ml/info.html/pid.1128931980",
      "new_product_photo_recycled":False,
      "new_photo_license_needed_for_this_original_graphic":False,
      "old_v2620_corrected_photo_regenerated":False,
      "old_v2677_archives_regenerated":False,
      "old_image_photography_modified":0,
      "slot_to_replace_in_internal_QA":2,
      "quarantined_slot2_reason":"Prior v2923 visually displays golden/translucent design differing from earlier white dual-chamber hero; actual owned SKU physical package generation unverified",
      "new_independent_product_photograph_count":0,
      "authentic_original_circular_MK_binary_used":False,
      "live_render_publication_allowed":False,
      "commercial_release_approval":False,
      "previous_published_families":11,"previous_verified_urls":55,
      "new_live_urls":0,"final_xlsx_shared":False}
    (OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"version":"v2983","family":"pending-11","new_JPG":str(p.relative_to(ROOT)),
                      "size_bytes":p.stat().st_size,"sha":report["new_original_SHA256"],"new_retail":0}))
if __name__=="__main__":main()
