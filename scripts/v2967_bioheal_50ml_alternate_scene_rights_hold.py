#!/usr/bin/env python3
"""Compare two new 50mL Bioheal source scenes against archived four.
QA evidence only. No merchant / personal-blog photograph is sale approved.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import io, json, zipfile, hashlib, urllib.request

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa-review/v2967-bioheal-cream50-two-distinct-alternative-scenes-20261106"
BASE=ROOT/"qa-review/v2934-bioheal-cream-four-real-source-scene-QA-only/manifest.json"
CANDIDATES=[
 {"key":"50ml_box","page":"https://www.cosme.net/variations/1239977/",
  "source":"https://fitter.cosme.net/media/product/10291/skuimg_1092450_xl.jpg",
  "description":"red BIOHEAL BOH 50mL cream retail box on white",
  "edition":"JAPANESE_PRODUCT_CATALOG_DONT_ASSUME_KR_STOCK",
  "permission":"THIRD_PARTY_CATALOG_NO_COMMERCIAL_LICENSE"},
 {"key":"50ml_hand_scene","page":"https://ameblo.jp/mari-883/entry-12962548695.html",
  "source":"https://stat.ameba.jp/user_images/20260410/17/mari-883/37/cc/j/o1080108015769965157.jpg",
  "description":"real 50mL red cream jar held in hand, product texture on hand",
  "edition":"BLOG_PHOTO_REAL_JAR_50ML_NEEDS_PHYSICAL_STOCK_MATCH",
  "permission":"BLOG_AUTHOR_PHOTO_NO_COMMERCIAL_LICENSE"}
]
def sha(b): return hashlib.sha256(b).hexdigest()
def dh(im):
    a=list(im.convert("L").resize((9,8),Image.Resampling.LANCZOS).getdata())
    return "".join("1" if a[y*9+x]>a[y*9+x+1] else "0" for y in range(8) for x in range(8))
def read_u(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"})
    with urllib.request.urlopen(req,timeout=18) as rs:
        data=rs.read(4500000)
        typ=rs.headers.get("content-type","")
    if not (12000<len(data)<4500000):raise ValueError("IMAGE_BYTE_SIZE_OR_TRUNCATION_ERROR")
    with Image.open(io.BytesIO(data)) as im:
        im.load();size=im.size;format=im.format
    return data, size, format, typ
def j1080(b):
    with Image.open(io.BytesIO(b)) as im:
        im.load(); im=im.convert("RGB")
        im.thumbnail((1040,1040),Image.Resampling.LANCZOS)
        canvas=Image.new("RGB",(1080,1080),(255,255,255))
        canvas.paste(im,((1080-im.width)//2,(1080-im.height)//2))
        buf=io.BytesIO();canvas.save(buf,"JPEG",quality=92,optimize=True)
        if len(buf.getvalue())>=2_000_000:raise ValueError("JPG_OVER_2_MB")
        return buf.getvalue()
def main():
    if OUT.exists():raise RuntimeError("Refuse to recreate existing v2967")
    prev=json.loads(BASE.read_text())
    oldzip=ROOT/prev["zip_path"]
    assert sha(oldzip.read_bytes())==prev["zip_sha256"],"v2934 archived ZIP drift"
    expected=[r["sha256"] for r in prev["source_records"]]
    blobmap={}
    with zipfile.ZipFile(oldzip) as z:
        for name in z.namelist():
            if name.lower().endswith(".jpg"):
                b=z.read(name)
                if sha(b) in expected:blobmap[sha(b)]=b
    assert len(blobmap)==4,"Original four existing 50mL sources missing"
    old=[blobmap[h] for h in expected]
    oldh=[]
    for b in old:
        with Image.open(io.BytesIO(b)) as im:
            im.load();oldh.append(dh(im))
    OUT.mkdir(parents=True)
    res={"version":"v2967","parent":"v2966","family":"pending-25","product":"BIOHEAL BOH NAD-PRIZCELL Glow Boost Cream 50mL",
     "old_zip_immutable_path":prev["zip_path"],"old_zip_sha256":prev["zip_sha256"],
     "existing_four_hashes_unchanged":expected,
     "prior_11_published_families_preserved":True,"prior_55_verified_urls_preserved":True,
     "old_existing_JPGs_overwritten":0,"new_retail_approved":0,"new_public_urls":0,
     "authentic_mk_logo_verified":False,"stock_generation_verified":False,
     "commercial_reuse_authorizations":0,"candidates":[]}
    qualified=[]
    for c in CANDIDATES:
        item={k:v for k,v in c.items()}
        try:
            raw, sz, fmt, typ=read_u(c["source"])
            if fmt not in ("JPEG","PNG","WEBP"):raise ValueError("WRONG_FORMAT "+str(fmt))
            item.update({"native_dimensions":list(sz),"native_format":fmt,
                         "native_sha256":sha(raw),"HTTP_content_type":typ})
            suffix={"JPEG":".jpg","PNG":".png","WEBP":".webp"}[fmt]
            origin=OUT/(c["key"]+"-original-REFERENCE-NOT-RETAIL"+suffix)
            origin.write_bytes(raw)
            jpg=j1080(raw)
            jpath=OUT/(c["key"]+"-1080-REFERENCE-NOT-RETAIL.jpg")
            jpath.write_bytes(jpg)
            with Image.open(io.BytesIO(jpg)) as im:
                d=dh(im)
            hd=[sum(a!=b for a,b in zip(d,x)) for x in oldh]
            item.update({"status":"ARCHIVED_REFERENCE_RIGHTS_AND_STOCK_HOLD",
               "original_path":str(origin.relative_to(ROOT)),
               "JPG_1080_path":str(jpath.relative_to(ROOT)),
               "JPG_1080_sha256":sha(jpg),
               "JPG_1080_bytes":len(jpg),
               "source_native_sufficient_for_1080_claim":min(sz)>=1000,
               "aHash_distance_to_four":hd,
               "independence_candidate":min(hd)>8,
               "sale_approved":False})
            if min(sz)>=900 and min(hd)>8:
                qualified.append((c["key"],jpg,item))
        except Exception as e:
            item.update({"status":"SOURCE_HOLD_SKIP_NO_REPEAT","error":type(e).__name__+": "+str(e)[:300]})
        res["candidates"].append(item)
    # This is a strictly internal comparison archive, not a 5-for-sale approval.
    six=Image.new("RGB",(1380,1080),"#f5f6f7");draw=ImageDraw.Draw(six)
    draw.text((20,16),"BIOHEAL BOH 50mL | 4 CURRENT + NEW EXTERNAL REFERENCE CANDIDATES",fill="#192d37")
    draw.text((20,42),"INTERNAL ONLY: catalog and blog authors' photos NOT licensed. Packaging/edition not confirmed.",fill="#963d36")
    originals=old+[(OUT/x["JPG_1080_path"].split("/")[-1]).read_bytes() for x in res["candidates"] if x.get("JPG_1080_path")]
    # Preserve exactly six tiles or fewer; do not invent or repeat images if a source failed.
    for i,b in enumerate(originals[:6]):
        x=20+(i%3)*455;y=80+(i//3)*467
        draw.rounded_rectangle((x,y,x+440,y+440),fill="white",outline="#cbd1d4",width=2,radius=10)
        with Image.open(io.BytesIO(b)) as img:
            img=img.convert("RGB");img.thumbnail((398,384),Image.Resampling.LANCZOS)
            six.paste(img,(x+(440-img.width)//2,y+8+(384-img.height)//2))
        draw.text((x+10,y+408),("ARCHIVED 50ML "+str(i+1)) if i<4 else ("NEW REFERENCE "+str(i-3)),fill="#455159")
    cp=OUT/"pending-25-new-alternate-scenes-vs-four-old-CONTACT-INTERNAL.jpg"
    six.save(cp,format="JPEG",quality=92,optimize=True)
    res["contact_sheet"]=str(cp.relative_to(ROOT))
    if qualified:
        key,new,j=qualified[0]
        imgs=old+[new]
        zp=OUT/"pending-25-four-original-plus-one-independent-unlicensed-INTERNAL-QA.zip"
        with zipfile.ZipFile(zp,"w") as z:
            for i,b in enumerate(imgs):
                zi=zipfile.ZipInfo(f"{i+1:02d}-{'NEW' if i==4 else 'PRESERVED'}-BIOHEAL50mL.jpg")
                zi.compress_type=zipfile.ZIP_STORED;zi.external_attr=0o644<<16;z.writestr(zi,b)
        with zipfile.ZipFile(zp) as z:
            assert all(sha(z.read(name))==sha(b) for name,b in zip(z.namelist(),imgs))
        res.update({"new_five_photo_QA_ZIP":str(zp.relative_to(ROOT)),
           "new_ZIP_SHA256":sha(zp.read_bytes()),
           "chosen_fifth_reference":key,
           "JPG_files":5,"independent_photo_count_NOT_verified":True,
           "reason":"Historical slots 1 and 2 near duplicates; permission unavailable for all candidate sources",
           "next_action":"Photo license and exact Korean physical package proof required; don't publish."})
    else:res["new_five_photo_QA_ZIP"]=None
    (OUT/"manifest.json").write_text(json.dumps(res,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"version":"v2967","references_saved":sum(x.get("status")=="ARCHIVED_REFERENCE_RIGHTS_AND_STOCK_HOLD" for x in res["candidates"]),
                       "qa_five_ZIP_created":bool(res["new_five_photo_QA_ZIP"]),"public_urls":0}))
if __name__=="__main__":main()
