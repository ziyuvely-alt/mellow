#!/usr/bin/env python3
"""Create two ORIGINAL text-only 1080 JPG option cards.
Verified existing photos are read for identity and SHA only. No fake shade swatches,
no redistributed merchant pictures, no claimed exact MK badge, no customer publish.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io,json,hashlib

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa-review/v2979-missha-clio-two-original-shade-name-only-cards-20261106"
MISSHA=ROOT/"qa-review/v2903-missha-BB-21-23-25-best-existing-source-option-QA/manifest.json"
CLIO21=ROOT/"qa-review/v2838-clio-mini5g-21C-21N-five-photo-no-customer-review-QA/manifest.json"
CLIO23=ROOT/"qa-review/v2840-clio-meshglow-mini5g-23N-five-photo-no-reviews-QA/manifest.json"
FONTP="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def f(sz,b=False):return ImageFont.truetype(FONTB if b else FONTP,sz)
def sha(b):return hashlib.sha256(b).hexdigest()
def read_verified(rel,digest):
    data=(ROOT/rel).read_bytes()
    if sha(data)!=digest:raise RuntimeError("Mismatch previously accepted SHA: "+rel)
    with Image.open(io.BytesIO(data)) as im:
        im.load()
        if im.format!="JPEG" or im.size!=(1080,1080) or len(data)>=2_000_000:
            raise RuntimeError("Wrong original JPG dimensions/size: "+rel)
    return {"source":rel,"SHA256":digest,"bytes":len(data),"identity_photo_only":True}
def draw_card(title,subtitle,rows,primary,accent,bg,label):
    im=Image.new("RGB",(1080,1080),bg)
    d=ImageDraw.Draw(im)
    white=(255,255,255)
    muted=(112,111,115)
    d.rectangle((0,0,1080,22),fill=primary)
    d.rounded_rectangle((73,68,1007,1012),radius=43,fill=white,outline=(231,231,233),width=3)
    d.rounded_rectangle((112,109,365,174),radius=23,fill=accent)
    d.text((142,126),"SHADE OPTIONS",font=f(25,True),fill=primary)
    d.text((110,214),title,font=f(40,True),fill=primary)
    d.text((112,274),subtitle,font=f(27),fill=(67,69,73))
    d.line([(112,340),(963,340)],fill=(226,226,230),width=3)
    d.text((113,384),"CHOOSE YOUR OPTION",font=f(31,True),fill=primary)
    for i,entry in enumerate(rows):
        y=459+i*130
        d.rounded_rectangle((112,y,966,y+100),radius=21,fill=(250,250,250),outline=(229,231,233),width=2)
        d.rounded_rectangle((133,y+13,288,y+87),radius=17,fill=accent)
        d.text((157,y+35),entry[0],font=f(27,True),fill=primary)
        d.text((321,y+32),entry[1],font=f(31,True),fill=(45,47,52))
    d.rounded_rectangle((112,886,963,940),radius=17,fill=accent)
    d.text((139,900),"SHADE NAMES ONLY  |  NO COLOR SIMULATION",font=f(21,True),fill=primary)
    d.text((112,962),label+"  |  INTERNAL QA  |  ORIGINAL MK LOGO PENDING",font=f(15),fill=muted)
    return im
def main():
    if OUT.exists():raise RuntimeError("Already produced v2979; do not rebuild")
    old1=json.loads(MISSHA.read_text(encoding="utf-8"))
    old2=json.loads(CLIO21.read_text(encoding="utf-8"))
    old3=json.loads(CLIO23.read_text(encoding="utf-8"))
    if old1.get("version")!="v2903" or old2.get("version")!="v2838" or old3.get("version")!="v2840":
        raise RuntimeError("Unexpected source manifest versions")
    missha_exact=[("No.21","Light Beige"),("No.23","Natural Beige"),("No.25","Warm Beige")]
    clio_exact=[("21C","Lingerie"),("21N","Linen"),("23N","Ginger")]
    if [int(x["shade"]) for x in old1["source_images"]]!=[21,23,25]:
        raise RuntimeError("Missha source shade set changed")
    verified_sources=[]
    for old in old1["source_images"]:
        verified_sources.append(read_verified(old["selected_copy"],old["sha256"]))
    for old in old2["variants"]:
        if old["shade"] not in ("21C","21N"):continue
        first=next(z for z in old["frames"] if z["slot"]==1)
        path="qa-review/v2838-clio-mini5g-21C-21N-five-photo-no-customer-review-QA/"+first["file"]
        verified_sources.append(read_verified(path,first["sha256"]))
    first23=next(z for z in old3["frames"] if z["slot"]==1)
    p23="qa-review/v2840-clio-meshglow-mini5g-23N-five-photo-no-reviews-QA/"+first23["file"]
    verified_sources.append(read_verified(p23,first23["sha256"]))
    if len(verified_sources)!=6:raise RuntimeError("Expected 6 existing verified reference options")
    OUT.mkdir(parents=True)
    cards=[
      {
        "family":"pending-03",
        "title":"M PERFECT COVER BB CREAM",
        "subtitle":"50 mL  |  ORIGINAL FORMULA REFERENCE",
        "rows":missha_exact,
        "name":"pending-03-MISSHA-BB-50mL-No21-23-25-option-names-INTERNAL-QA.jpg",
        "primary":(95,41,53),"accent":(250,235,236),"background":(252,247,246),
        "source":"https://misshaus.com/products/m-perfect-cover-bb-cream-spf-42-pa-50ml-new",
        "caution":"Official shade names from current MISSHA US M Perfect Cover BB Cream 50mL page; legacy physical gold-pump unit not proven by modern catalog",
        "replaces_slot_candidate":5,
        "old_issue":"Archived 5th option graphic only lists No23 and No25; No21 omitted and swatch source not rights-cleared"
      },
      {
        "family":"pending-04",
        "title":"MESH GLOW ESSENTIAL MINI",
        "subtitle":"5 g  |  MINI CUSHION",
        "rows":clio_exact,
        "name":"pending-04-CLIO-mini5g-21C-21N-23N-option-names-INTERNAL-QA.jpg",
        "primary":(93,64,101),"accent":(246,235,248),"background":(252,250,252),
        "source":"https://clubclio.co.kr/shop/goodsView/0000006954",
        "caution":"Official MINI 5g product; labels 21C Lingerie/21N Linen/23N Ginger from independent shade-specific merchant photo manifests. Physical stock generation not proven",
        "replaces_slot_candidate":4,
        "old_issue":"Old frame 4 repeats open-compact view of frame 1, while option identification is missing in legacy 5-photo contact"
      }
    ]
    results=[]
    for card in cards:
        canvas=draw_card(card["title"],card["subtitle"],card["rows"],card["primary"],card["accent"],card["background"],card["family"].upper())
        target=OUT/card["name"]
        canvas.save(target,format="JPEG",quality=94,optimize=True,subsampling=0)
        with Image.open(target) as image:
            image.load()
            if image.format!="JPEG" or image.size!=(1080,1080):raise RuntimeError("Incorrect output JPG")
        if target.stat().st_size>=2_000_000:raise RuntimeError("JPEG exceeds 2MB")
        result={k:v for k,v in card.items() if k not in ("primary","accent","background")}
        result.update({"JPG_path":str(target.relative_to(ROOT)),
          "JPG_SHA256":sha(target.read_bytes()),"JPG_bytes":target.stat().st_size,
          "pixel_dimensions":[1080,1080],
          "original_graphics_text_only":True,
          "third_party_photo_pixels_used":False,
          "simulated_color_swatches":False,"actual_color_match_proven":False,
          "original_circular_MK_logo_included":False,
          "consumer_publish_approved":False,
          "customer_ready_5_distinct_photos":False})
        results.append(result)
    result={
      "version":"v2979","parent":"v2978","project":"Shopee Thumbnail Creator PRO | 82 SKUs / 41 families",
      "date_kst":"2026-11-06","source_option_JPG_shas_validated":verified_sources,
      "original_cards_newly_generated":2,"old_image_bytes_modified":0,
      "results":results,
      "photo_usage_rights_for_source_hero_photos":"NOT_VERIFIED",
      "exact_owned_edition_confirmed":False,
      "original_MellowKR_MK_png_authenticated":False,
      "new_render_image_urls":0,
      "new_sale_approvals":0,
      "prior_published_families_preserved":11,
      "prior_verified_public_urls_preserved":55,
      "important_distinction":"Option name guide is NOT an official color swatch. Do not imply cosmetic shade color accuracy or original logo verification.",
      "next":[
        "For pending-03 reuse original legacy No21/23/25 option JPGs; new original text guide fixes missing No21 option label only.",
        "For pending-04 reuse 21C/21N/23N actual reference photo data without re-labeling shared pink compact as shade-accurate.",
        "When rights and stocked legacy edition and authentic logo are cleared, select only then for public image version.",
        "No further source download/rebuild for either card or 6 confirmed variant reference JPGs."
      ],
      "final_xlsx_shared":False
    }
    (OUT/"manifest.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"version":"v2979","new_JPGs":2,"validated_existing_shade_photos":len(verified_sources),
      "files":[{"family":r["family"],"bytes":r["JPG_bytes"],"sha256":r["JPG_SHA256"]} for r in results],
      "live_approved":0}))
if __name__=="__main__":main()
