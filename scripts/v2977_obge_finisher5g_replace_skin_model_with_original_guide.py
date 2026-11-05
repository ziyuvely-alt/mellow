#!/usr/bin/env python3
"""One copyright-clean original informational QA replacement for OBgE Oil Control Finisher.
Replaces photo candidate #5 with original directions card, not new independent photo.
No third-party photo, invented clinical data, fake MK or commercial release.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa-review/v2977-obge-finisher5g-one-original-directions-frame-20261106"
PREV=ROOT/"qa-review/v2905-obge-finisher5g-five-official-no-unverified-MK-internal-QA/manifest.json"
DEJAVU="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
DEJAVUB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def txt(sz,b=False):return ImageFont.truetype(DEJAVUB if b else DEJAVU,sz)
def h(blob):return hashlib.sha256(blob).hexdigest()
def main():
    if OUT.exists():raise RuntimeError("v2977 existed: do not overwrite")
    prev=json.loads(PREV.read_text(encoding="utf8"))
    assert prev["family"]=="pending-09" and len(prev["frames"])==5
    fifth=prev["frames"][4]
    old=ROOT/fifth["copy"]
    assert h(old.read_bytes())==fifth["sha256"],"old model photo SHA mismatch"
    OUT.mkdir(parents=True)
    c=Image.new("RGB",(1080,1080),(253,251,246))
    d=ImageDraw.Draw(c)
    beige=(240,222,195); clay=(177,126,75); ink=(57,45,37); gray=(110,92,75)
    d.rectangle((0,0,1080,22),fill=(102,73,51))
    d.rounded_rectangle((70,65,1010,1010),radius=42,fill=(255,255,255),outline=(227,213,194),width=3)
    d.rounded_rectangle((110,111,327,171),radius=21,fill=(248,237,222))
    d.text((143,124),"FACE CARE",font=txt(25,True),fill=ink)
    d.ellipse((805,112,1110,420),fill=(248,236,219))
    d.ellipse((869,167,1080,386),fill=(236,213,186))
    d.text((112,209),"OIL CONTROL FINISHER",font=txt(45,True),fill=ink)
    d.text((114,286),"APPLICATION GUIDE",font=txt(34,True),fill=clay)
    d.line([(110,362),(960,362)],fill=(227,213,195),width=3)
    d.text((112,405),"HOW TO USE",font=txt(50,True),fill=ink)
    steps=[
      ("01","Lightly sweep the puff over the formula."),
      ("02","Gently tap onto oily areas such as"),
      ("","the T-zone."),
      ("03","Reapply as needed during the day.")
    ]
    d.rounded_rectangle((110,510,963,857),radius=25,fill=(251,246,237),outline=(244,229,209),width=2)
    d.rounded_rectangle((141,548,207,616),radius=22,fill=beige)
    d.text((154,568),"01",font=txt(25,True),fill=ink)
    d.text((225,564),steps[0][1],font=txt(27),fill=ink)
    d.rounded_rectangle((141,644,207,711),radius=22,fill=beige)
    d.text((154,663),"02",font=txt(25,True),fill=ink)
    d.text((225,652),"Gently tap onto oily areas such as",font=txt(27),fill=ink)
    d.text((225,694),"the T-zone.",font=txt(27),fill=ink)
    d.rounded_rectangle((141,760,207,827),radius=22,fill=beige)
    d.text((154,779),"03",font=txt(25,True),fill=ink)
    d.text((225,776),"Reapply as needed during the day.",font=txt(27),fill=ink)
    d.text((112,893),"BRAND CATALOG NET WEIGHT: 5 g",font=txt(28,True),fill=gray)
    d.text((112,958),"INTERNAL QA  |  ORIGINAL MK LOGO PENDING",font=txt(17),fill=(160,116,95))
    path=OUT/"pending-09-frame05-original-English-usage-guide-INTERNAL-QA.jpg"
    c.save(path,format="JPEG",quality=94,optimize=True,subsampling=0)
    jpg=Image.open(path)
    if jpg.size!=(1080,1080) or jpg.format!="JPEG" or path.stat().st_size>=2000000:raise RuntimeError("JPG technical spec failure")
    manifest={
      "version":"v2977","parent":"v2976","family":"pending-09",
      "product":"OBgE Oil Control Finisher 5g single",
      "old_5th_existing_QA_frame":fifth["copy"],"old_5th_SHA256":fifth["sha256"],
      "replacement_strategy":"Original 1080 factual how-to graphic, no borrowed photography, replaces skin-portrait/model reference only in QA candidate roster",
      "created_original_JPG":str(path.relative_to(ROOT)), "JPG_SHA256":h(path.read_bytes()),
      "JPG_bytes":path.stat().st_size,"size":[1080,1080],
      "uses_thirdparty_photography":False,
      "includes_original_MellowKR_MK_logo":False,
      "pretends_original_MK_authentic":False,
      "claimed_36percent_pore_reduction":False,
      "makes_before_after_test_claim":False,
      "number_of_distinct_product_photos_added":0,
      "manufacturer_net_content_reference":"https://obge.co.kr/product/detail.html?product_no=1096",
      "manufacturer_usage_source":"https://obgeglobal.com/products/oil-control-finisher",
      "instructions":"Use built-in puff lightly; tap oily areas like T-zone; reapply when needed",
      "actual_owned_5g_package_confirmed":False,
      "original_MK_logo_binary_authenticated":False,
      "source_media_reuse_rights_1to4":False,
      "final_visual_customer_approval":False,"retail_published":False,
      "existing_11_approved_families_preserved":True,
      "existing_55_public_urls_preserved":True,"old_archives_or_JPGs_modified":0,
      "new_public_urls":0,"spreadsheet_shared":False
    }
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print(json.dumps({"version":"v2977","new_JPG":str(path.relative_to(ROOT)),
       "bytes":manifest["JPG_bytes"],"SHA256":manifest["JPG_SHA256"],"retail_approved":False}))
if __name__=="__main__":main()
