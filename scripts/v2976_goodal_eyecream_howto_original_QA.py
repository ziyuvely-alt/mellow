#!/usr/bin/env python3
"""Create ONE original, no-third-party-photo, non-retail informational frame.
The official MK original is NOT accessible here; never fabricate a lookalike.
Does not replace existing asset; produces append-only internal QA JPG and manifest.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa-review/v2976-goodal-eyecream-one-original-howto-frame-no-photo-20261106"
BASE=ROOT/"qa-review/v2975-actual-frame-quarantine-and-unit-contract-20261106/manifest.json"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def font(s,bold=False):
    return ImageFont.truetype(BOLD if bold else FONT,s)
def sha(b):return hashlib.sha256(b).hexdigest()
def line(draw,points,fill,width=2):draw.line(points,fill=fill,width=width)
def main():
    if OUT.exists():raise SystemExit("No duplicate v2976 outputs or overwrites")
    past=json.loads(BASE.read_text(encoding="utf-8"))
    if past["version"]!="v2975" or not past["manual_archived_photograph_duplicate_confirmed"]["visual_scene_same"]:
        raise RuntimeError("This targeted replacement requires v2975 duplicate evidence")
    OUT.mkdir(parents=True)
    w=h=1080
    im=Image.new("RGB",(w,h),(251,250,246))
    d=ImageDraw.Draw(im)
    ink=(38,56,48)
    muted=(82,102,89)
    soft=(224,234,208)
    green=(61,105,69)
    yellow=(246,220,112)
    white=(255,255,255)
    d.rectangle((0,0,1080,24),fill=green)
    d.ellipse((730,62,1250,590),fill=(245,245,218))
    d.ellipse((850,140,1300,620),fill=(248,239,194))
    d.rounded_rectangle((74,67,1006,1013),radius=45,fill=white,outline=(229,232,221),width=3)
    d.rounded_rectangle((115,111,328,171),radius=25,fill=(238,247,235))
    d.text((145,124),"SKINCARE",font=font(26,True),fill=green)
    d.text((117,208),"GREEN TANGERINE",font=font(35,True),fill=green)
    d.text((117,255),"VITA-C DARK SPOT CARE",font=font(40,True),fill=ink)
    d.text((117,312),"EYE CREAM",font=font(59,True),fill=ink)
    line(d,[(120,395),(960,395)],fill=(214,225,205),width=3)
    d.text((117,430),"HOW TO USE",font=font(43,True),fill=ink)
    steps=[
     ("01","Take a small amount of eye cream."),
     ("02","Gently spread around the eye area."),
     ("03","Tap lightly to help it absorb.")
    ]
    for i,(num,txt) in enumerate(steps):
        top=515+i*112
        d.rounded_rectangle((117,top,193,top+76),radius=24,fill=(233,242,230))
        d.text((138,top+21),num,font=font(27,True),fill=green)
        d.text((220,top+20),txt,font=font(30),fill=ink)
    d.rounded_rectangle((117,856,961,925),radius=22,fill=(255,247,216))
    d.text((144,872),"CATALOG SIZE: 30 mL",font=font(29,True),fill=muted)
    d.text((118,949),"INTERNAL IMAGE QA  |  AUTHENTIC MK LOGO PENDING",font=font(18),fill=(147,108,78))
    out=OUT/"pending-21-frame04-original-English-how-to-no-photo-INTERNAL-QA.jpg"
    im.save(out,format="JPEG",quality=93,optimize=True,subsampling=0)
    img=Image.open(out)
    if img.format!="JPEG" or img.size!=(1080,1080) or out.stat().st_size>=2_000_000:raise RuntimeError("JPG format specs failed")
    manifest={
       "version":"v2976","parent":"v2975","date_kst":"2026-11-06","project":"Shopee Thumbnail Creator PRO stock / 82 SKU 41 families",
       "family":"pending-21","brand":"GOODAL","product":"Green Tangerine Vita-C Dark Spot Care Eye Cream",
       "proposal":"Replace duplicate reference PHOTO #4 with ORIGINAL INFORMATION FRAME, not with an extra independent photo",
       "created_original_JPG":str(out.relative_to(ROOT)),"image_SHA256":sha(out.read_bytes()),
       "image_dimensions":[1080,1080],"JPG_bytes":out.stat().st_size,
       "is_original_typography_and_shapes_only":True,
       "external_product_photography_used":False,
       "manufacturer_logo_or_original_MK_used":False,
       "original_MK_asset_pending":True,
       "commercial_release_approved":False,
       "product_catalog_net":"30 mL (not independently confirmed against physically owned unit)",
       "instruction_provenance":"GOODAL Green Tangerine Vita C Dark Spot Care Eye Cream 30mL, Olive Young US",
       "instruction_source_url":"https://us.oliveyoung.com/products/UA96443780",
       "instructions_paraphrased_not_product_claims":True,
       "new_frame_usage":"INTERNAL_QA_ONLY_UNTIL_AUTHENTIC_MK_AND_PHYSICAL_STOCK_CONFIRMED",
       "do_not_count_as_fifth_independent_product_photo":True,
       "old_original_04_unchanged":True,
       "old_verified_jpg_source_sha256":{
         "3":"bbb6087b45ad160d209033a9045d4b3bc6dee88d3e834e6518834dd65bf8e182",
         "4":"e27828d7573b2a20ff968c1640347095ae96fe1f7de2dfd19ccec0540d8b0ebb"},
       "next_action":"Only after owned 30mL unit, photo rights and exact MK original binary become available, make clean retail-ready story; replace only frame 4 and keep all validated image sources",
       "original_live_11_families_preserved":True,"original_live_55_URLs_preserved":True,
       "other_family_work_modified":False,"new_verified_live_URLs":0,"final_xlsx_shared":False
    }
    (OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"created":str(out.relative_to(ROOT)),"sha256":manifest["image_SHA256"],
      "bytes":out.stat().st_size,"old_jpgs_changed":0,"render_url_verified":0}))
if __name__=="__main__":main()
