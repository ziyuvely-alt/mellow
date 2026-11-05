#!/usr/bin/env python3
"""v2840: 23N Ginger CLIO Mesh Glow Essential Cushion Mini 5g QA gallery.
Existing 21C/21N galleries, 11 approved families and 55 URLs immutable.
Source exact 23N reference v2830 and 2 generic v2838 references.
Retrieve 2 EXPLICIT SHADE-ASSIGNED merchant photos from v2835 catalog only.
No customer review photos, guessed swatches, or retail approval.
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
from io import BytesIO
import requests, hashlib, json, shutil, base64

R=Path("qa-review")
P30=R/"v2830-clio-meshglow-essential-mini5g-five-distinct-physical-photo-QA"
P35=R/"v2835-clio-mini-21N-merchant-variant-image-assignment-audit"
P38=R/"v2838-clio-mini5g-21C-21N-five-photo-no-customer-review-QA"
OUT=R/"v2840-clio-meshglow-mini5g-23N-five-photo-no-reviews-QA"
assert all(p.is_dir() for p in (P30,P35,P38)) and not OUT.exists()
OUT.mkdir(parents=True)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def copy_checked(src,dst):
    assert src.is_file(),str(src)
    before=digest(src)
    shutil.copy2(src,dst)
    assert before==digest(dst)
    return {"file":str(dst.relative_to(OUT)),"sha256":digest(dst),"source":str(src),"bytes_identical":True}
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def f(n,b=False):return ImageFont.truetype(BOLD if b else FONT,n)
cat=json.loads((P35/"manifest.json").read_text())
previous=json.loads((P38/"manifest.json").read_text())
assert previous["21C_21N_rebuilt_internal_QA_photo_sets"]==2
assert previous["customer_review_photos_in_new_QA_sets"]==0
assert all(x["shade"] in ["21C","21N"] for x in previous["variants"])
cmap={x["merchant"]:x for x in cat["merchant_results"]}
frames=[]
src1=P30/"05-23N-Ginger-exact-mini5g-merchant-reference-QA.jpg"
dst1=OUT/"01-23N-GINGER-EXACT-SHADE-SOURCE-QA.jpg"
a=copy_checked(src1,dst1)
a.update(slot=1,role="EXACT_23N_GINGER_REFERENCE",review_photo=False,rights_verified=False)
frames.append(a)
for slot,name in [(2,"02-PRESERVED_COMMON_UNASSIGNED_SHADE_PACKSHOT-QA.jpg"),(3,"03-PRESERVED_COMMON_UNASSIGNED_SHADE_OPEN_COMPACT-QA.jpg")]:
    src=P38/"21C"/name
    dst=OUT/(f"{slot:02d}-COMMON-REAL-PRODUCT-NO-SHADE-QA.jpg")
    a=copy_checked(src,dst)
    a.update(slot=slot,role="COMMON_UNASSIGNED_SHADE",review_photo=False,rights_verified=False)
    frames.append(a)
for slot, merchant in [(4,"W Cosmetics Australia"),(5,"La Cosmetique Australia")]:
    rows=cmap[merchant]["all_variant_rows"]
    matches=[r for r in rows if str(r["shade_title"]).strip().lower().startswith("23n")]
    assert len(matches)==1,(merchant,matches)
    info=matches[0]; u=info["linked_photo_url"]
    assert u.startswith("https://cdn.shopify.com/")
    assert all(row["linked_photo_url"]!=u for row in rows if row is not info)
    data={"slot":slot,"merchant":merchant,"url":u,"source_variant":info["shade_title"],
          "merchant_variant_id":info["variant_id"],
          "role":"EXACT_23N_MERCHANT_PHOTO","review_photo":False,
          "rights_verified":False,"status":"HOLD_NOT_FETCHED"}
    try:
        response=requests.get(u,timeout=22,headers={"User-Agent":"Mozilla/5.0","Accept":"image/png,image/jpeg,image/webp,*/*"})
        response.raise_for_status()
        assert 1000<len(response.content)<8_000_000
        with Image.open(BytesIO(response.content)) as im:
            im.load()
            original_size=list(im.size)
            assert min(im.size)>=700,original_size
            im=ImageOps.exif_transpose(im).convert("RGB")
            fitted=ImageOps.contain(im,(1080,1080),Image.Resampling.LANCZOS)
            canvas=Image.new("RGB",(1080,1080),"white")
            canvas.paste(fitted,((1080-fitted.width)//2,(1080-fitted.height)//2))
        dest=OUT/(f"{slot:02d}-23N-MERCHANT-{'W' if slot==4 else 'LACOSMETIQUE'}-QA.jpg")
        canvas.save(dest,format="JPEG",quality=93,optimize=True,subsampling=0)
        with Image.open(dest) as ch:
            ch.load()
            assert ch.format=="JPEG" and ch.size==(1080,1080)
        assert dest.stat().st_size<2_000_000
        data.update({"file":str(dest.relative_to(OUT)),"sha256":digest(dest),
                     "source_native_pixels":original_size,
                     "status":"EXACT_23N_VARIANT_SOURCE_STAGED_QA_ONLY"})
    except Exception as e:
        data["status"]="HOLD_FETCH_OR_IMAGE_VALIDATION"
        data["error"]=str(e)[:240]
    frames.append(data)
count=sum(1 for x in frames if x.get("file"))
valid_sha=[x["sha256"] for x in frames if x.get("sha256")]
assert len(valid_sha)==len(set(valid_sha)), "non-unique 23N photographs; do not accept"
assert count>=3
for fr in frames:
    if fr.get("file"):
        im=Image.open(OUT/fr["file"]);im.load()
        assert im.format=="JPEG" and im.size==(1080,1080)
        assert (OUT/fr["file"]).stat().st_size<2_000_000
board=Image.new("RGB",(1840,495),"#f1f0ed");d=ImageDraw.Draw(board)
d.text((14,12),"v2840 23N Ginger | 5 original-photo references | REVIEW FREE | QA ONLY",font=f(23,True),fill="#2b282b")
for fr in frames:
    x=12+(fr["slot"]-1)*366
    if fr.get("file"):
        with Image.open(OUT/fr["file"]) as source:
            thumb=source.convert("RGB").resize((335,335),Image.Resampling.LANCZOS)
            board.paste(thumb,(x,58))
    else:
        d.rectangle((x,58,x+335,393),outline="#b9b2b4",width=3)
        d.text((x+19,200),"IMAGE HOLD",font=f(24,True),fill="#8c787e")
    d.text((x,402),"EXACT 23N" if fr["slot"] in (1,4,5) else "COMMON",font=f(19,True),fill="#463c42")
    d.text((x,439),"Commercial rights: unverified",font=f(14),fill="#695c63")
contact=OUT/"v2840-23N-contact-visual-QA.jpg"
board.save(contact,"JPEG",quality=85,optimize=True)
(OUT/"v2840-proof.b64.txt").write_text(base64.b64encode(contact.read_bytes()).decode())
report={
 "version":"v2840","prior_success":"v2838","pending_family":"pending-04",
 "product":"CLIO Kill Cover Mesh Glow Essential Mini 5g",
 "shade":"23N Ginger","gallery_status":"FIVE_REAL_PHOTO_QA_ONLY" if count==5 else "PARTIAL_HOLD",
 "original_real_photo_JPGs_staged":count,"unique_source_photos":len(set(valid_sha)),
 "customer_review_photo_frames":0,"all_physical_jpg_1080_and_under_2MB":True,
 "photo_reuse_rights_verified":False,"physical_owned_stock_edition_verified":False,
 "genuine_MK_logo_authenticated":False,"new_retail_approved":0,
 "old_11_approved_families_unchanged":True,
 "old_55_verified_public_URLs_unchanged":True,
 "prior_21C_21N_QA_sets_unchanged":True,
 "prior_source_JPG_files_modified":False,
 "final_excel_shared":False,
 "frames":frames,
 "next":"Direct visual QA on contact; get photo rights and actual stock validation before publication. Do not turn merchant proof into final seller rights."
}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2840","shade":"23N","staged":count,"distinct":len(set(valid_sha)),
    "status":report["gallery_status"],"retail_approved":0}))
