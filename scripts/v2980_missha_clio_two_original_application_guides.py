#!/usr/bin/env python3
"""v2980: two product-specific, text/shape-only original HOW TO APPLY 1080 QA cards.
Keep all existing photo bytes unchanged. No artificial swatches or fake user MK.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa-review/v2980-missha-clio-two-original-howto-not-photo-cards-20261106"
V2979=ROOT/"qa-review/v2979-missha-clio-two-original-shade-name-only-cards-20261106/manifest.json"
FREG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FBOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def f(sz,bold=False):return ImageFont.truetype(FBOLD if bold else FREG,sz)
def sha(b):return hashlib.sha256(b).hexdigest()
def draw(title,line2,headline,steps,color,accent,bg,tag):
    x=Image.new("RGB",(1080,1080),bg);d=ImageDraw.Draw(x)
    white=(255,255,255);ink=(39,40,43);muted=(108,108,113)
    d.rectangle((0,0,1080,22),fill=color)
    d.rounded_rectangle((72,70,1007,1010),radius=42,fill=white,outline=(229,231,231),width=3)
    d.ellipse((785,77,1177,465),fill=accent)
    d.rounded_rectangle((111,105,352,170),radius=21,fill=accent)
    d.text((142,125),headline,font=f(25,True),fill=color)
    d.text((111,220),title,font=f(43,True),fill=color)
    d.text((112,286),line2,font=f(28),fill=muted)
    d.line([(112,358),(964,358)],fill=(221,221,224),width=3)
    d.text((112,394),"HOW TO APPLY",font=f(43,True),fill=ink)
    for i,lines in enumerate(steps):
        y=492+i*113
        d.rounded_rectangle((112,y,962,y+89),radius=22,fill=(251,251,252),outline=(232,231,232),width=2)
        d.rounded_rectangle((137,y+12,208,y+77),radius=17,fill=accent)
        d.text((154,y+30),f"{i+1:02d}",font=f(26,True),fill=color)
        d.text((235,y+28),lines,font=f(26),fill=ink)
    d.rounded_rectangle((112,874,961,930),radius=18,fill=accent)
    d.text((145,889),"ORIGINAL ENGLISH INSTRUCTION ART",font=f(24,True),fill=color)
    d.text((112,960),f"{tag} | INTERNAL QA | ORIGINAL MK LOGO PENDING",font=f(16),fill=muted)
    return x
def main():
    if OUT.exists():raise RuntimeError("Existing v2980; refuse to repeat")
    p=json.loads(V2979.read_text(encoding="utf-8"))
    if p["version"]!="v2979" or len(p["results"])!=2:raise RuntimeError("Missing v2979 reference")
    for card in p["results"]:
        img=(ROOT/card["JPG_path"]).read_bytes()
        if sha(img)!=card["JPG_SHA256"]:raise RuntimeError("v2979 original shade card SHA mismatch")
    plans=[
      {
        "family":"pending-03","title":"M PERFECT COVER BB CREAM","line2":"50 mL  |  FACE MAKEUP",
        "headline":"BB CREAM GUIDE",
        "steps":[
          "Apply a small amount to fingers or sponge.",
          "Gently blend over the face.",
          "Layer more if additional coverage is desired."
        ],
        "colors":[(97,47,60),(251,235,237),(254,249,248)],
        "name":"pending-03-MISSHA-BB-50mL-original-apply-guide-INTERNAL-QA.jpg",
        "usage_official_url":"https://misshaus.com/products/m-perfect-cover-bb-cream-spf-42-pa-50ml-new",
        "reference":"MISSHA US current 50mL brand usage instruction: pump an appropriate amount, blend onto skin and layer for coverage",
        "underlying_old_photos_used":0,
        "do_not_claim":"same old gold-pump formula/physical stocked edition without proof"
      },
      {
        "family":"pending-04","title":"MESH GLOW ESSENTIAL MINI","line2":"5 g  |  CUSHION",
        "headline":"CUSHION GUIDE",
        "steps":[
          "Take an appropriate amount with the puff.",
          "Apply evenly over your skin.",
          "Tap gently to blend for an even finish."
        ],
        "colors":[(95,68,101),(247,237,248),(254,250,254)],
        "name":"pending-04-CLIO-mini5g-original-apply-guide-INTERNAL-QA.jpg",
        "usage_official_url":"https://clubclio.co.kr/shop/goodsView/0000006954",
        "reference":"CLUBCLIO 5g Mini label says apply suitable amount evenly over skin; puff is pictured in product photos",
        "underlying_old_photos_used":0,
        "do_not_claim":"specific 21C/21N/23N swatch color or corresponding physical generation without proof"
      }
    ]
    OUT.mkdir(parents=True)
    results=[]
    for c in plans:
        rgb=draw(c["title"],c["line2"],c["headline"],c["steps"],*c["colors"],c["family"].upper())
        pth=OUT/c["name"]
        rgb.save(pth,format="JPEG",quality=94,subsampling=0,optimize=True)
        with Image.open(pth) as im:
            im.load()
            if im.format!="JPEG" or im.size!=(1080,1080):raise RuntimeError("incorrect dimensions")
        if pth.stat().st_size>=2_000_000:raise RuntimeError("image too large")
        results.append({k:v for k,v in c.items() if k!="colors"}|{
            "JPG_path":str(pth.relative_to(ROOT)),"SHA256":sha(pth.read_bytes()),
            "JPG_bytes":pth.stat().st_size,"dimensions":[1080,1080],
            "third_party_photo_pixels":False,"original_mellowkr_MK_used":False,
            "authentic_swatch_colors_imagined":False,"commercial_release_approved":False
        })
    manifest={
      "version":"v2980","previous":"v2979",
      "project":"Shopee Thumbnail Creator PRO 82 SKU / 41 families",
      "new_original_text_JPGs":2,
      "already_verified_option_name_cards":2,"prior_source_photo_files_recreated":0,
      "original_images_modified":0,"new_unlicensed_photo_uploads":0,
      "results":results,
      "next":"One batch-based, 5-slot byte SHA manifest per pending-03/04 with exact 3 shade-specific source photos + 2 new text-only option/application cards. No model face image.",
      "user_owned_stock_generation_verified":False,
      "MellowKR_original_logo_binary_authenticated":False,
      "retail_photo_rights_cleared":False,
      "retail_approved":False,"new_public_URLs":0,
      "original_11_published_families_preserved":True,
      "original_55_verified_public_URLs_preserved":True,
      "final_excel_shared":False
    }
    (OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"version":"v2980","created":[{"family":x["family"],"path":x["JPG_path"],"bytes":x["JPG_bytes"],"sha256":x["SHA256"]} for x in results],"retail":0},ensure_ascii=False))
if __name__=="__main__":main()
