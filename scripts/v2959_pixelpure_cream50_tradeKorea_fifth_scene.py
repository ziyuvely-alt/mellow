#!/usr/bin/env python3
"""Only new 50mL cream photo candidate against 4 immutable originals. No sales rights inferred."""
import io,json,zipfile,hashlib,urllib.request
from pathlib import Path
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa-review/v2959-pixelpure-cream50-fifth-tradekorea-photo-20261106"
PREV=ROOT/"qa-review/v2929-pixelpure-three-four-photo-pack-source-integrity-QA/manifest.json"
URL="https://web.tradekorea.com/product/866/2334866/pixelpure_radiance_aqua_soothing_cream_50ml_%28Skin_Care%29_4.jpg"
SOURCE_PAGE="https://www.tradekorea.com/product/detail/P849301/pixelpure-radiance-aqua-soothing-cream-50ml--Skin-Care-.html"
def sha(b):return hashlib.sha256(b).hexdigest()
def dh(im):
    x=list(im.convert("L").resize((9,8),Image.Resampling.LANCZOS).getdata())
    return "".join("1" if x[row*9+col]>x[row*9+col+1] else "0" for row in range(8) for col in range(8))
def clean_1080(data):
    with Image.open(io.BytesIO(data)) as original:
        original.load()
        dims=original.size
        if min(dims)<700:raise ValueError("native source below 700px: "+str(dims))
        copy=original.convert("RGB")
    copy.thumbnail((1030,1030),Image.Resampling.LANCZOS)
    c=Image.new("RGB",(1080,1080),"white")
    c.paste(copy,((1080-copy.width)//2,(1080-copy.height)//2))
    o=io.BytesIO();c.save(o,quality=93,optimize=True)
    if o.tell()>=2000000:raise ValueError("resized candidate exceeds 2MB")
    return o.getvalue(),dims
def main():
    if OUT.exists():raise RuntimeError("Previously executed v2959, never repeat or overwrite")
    old=json.loads(PREV.read_text())
    fam=next(x for x in old["results"] if x["family"]=="pending-29")
    archive=ROOT/fam["archive_ZIP"]
    assert sha(archive.read_bytes())==fam["archive_ZIP_sha256"],"baseline ZIP changed"
    expected=[x["sha256"] for x in fam["source_records"]]
    sources={}
    with zipfile.ZipFile(archive) as z:
        for filename in z.namelist():
            if filename.lower().endswith(".jpg"):
                blob=z.read(filename)
                if sha(blob) in expected:sources[sha(blob)]=blob
    if len(sources)!=4:raise ValueError("Not all 4 previously checked source JPGs found")
    old_bytes=[sources[x] for x in expected]
    old_dhs=[]
    for b in old_bytes:
        with Image.open(io.BytesIO(b)) as im:im.load();old_dhs.append(dh(im))
    OUT.mkdir(parents=True)
    manifest={"version":"v2959","baseline":"v2958","product":"Pixelpure Radiance Aqua Soothing Cream 50mL",
      "family":"pending-29","candidate_page":SOURCE_PAGE,"candidate_source_url":URL,
      "product_source_type":"TradeKorea Korean seller product photo; not brand-hosted and not licensed",
      "candidate_scene_expected":"three cream jars in different angles with one exposed cream swirl",
      "prior_zip_preserved":fam["archive_ZIP"],"old_source_images_overwritten":0,
      "prior_published_families_preserved":11,"prior_verified_urls_preserved":55,
      "sale_approved":False,"commercial_photo_rights":False,"owned_stock_version_proven":False,
      "original_mk_png_proven":False,"new_public_jpgs":0,"new_verified_urls":0}
    try:
        req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"})
        with urllib.request.urlopen(req,timeout=22) as resp:
            raw=resp.read(5_000_000)
        if len(raw)<15000 or len(raw)>=5_000_000:raise ValueError("bad source payload size")
        with Image.open(io.BytesIO(raw)) as im:
            im.load();form=im.format
        if form!="JPEG":raise ValueError("not a JPEG native source")
        candidate, native_size=clean_1080(raw)
        with Image.open(io.BytesIO(candidate)) as im:od=dh(im)
        distances=[sum(a!=b for a,b in zip(od,d)) for d in old_dhs]
        orig=OUT/"pending-29-new-three-jar-scene-native-SOURCE-NOT-LICENSED.jpg"
        orig.write_bytes(raw)
        jp=OUT/"pending-29-five-photo-new-candidate-1080-INTERNAL-QA.jpg"
        jp.write_bytes(candidate)
        manifest.update({"candidate_saved":True,"native_file":str(orig.relative_to(ROOT)),
          "native_px":list(native_size),"native_sha256":sha(raw),
          "new_reference_JPG":str(jp.relative_to(ROOT)),"new_reference_SHA256":sha(candidate),
          "dhash_distance_vs_prior_four":distances})
        if min(distances)<=8:
            manifest["outcome"]="TOO_SIMILAR_NO_FIFTH_PHOTO_COUNT"
        else:
            manifest["outcome"]="DISTINCT_FIFTH_SCENE_SOURCE_STAGED_FOR_VISUAL_QA"
            imgs=old_bytes+[candidate]
            zp=OUT/"pending-29-five-real-photograph-source-candidates-INTERNAL-ONLY.zip"
            with zipfile.ZipFile(zp,"w") as z:
                for i,data in enumerate(imgs):
                    entry=zipfile.ZipInfo(f"{i+1:02d}-{'old' if i<4 else 'new'}-PixelpureRadianceCream50-QA.jpg")
                    entry.compress_type=zipfile.ZIP_STORED;entry.external_attr=0o644<<16
                    z.writestr(entry,data)
            with zipfile.ZipFile(zp) as z:
                assert all(sha(z.read(n))==sha(b) for n,b in zip(z.namelist(),imgs))
            manifest["new_internally_staged_five_source_zip"]=str(zp.relative_to(ROOT))
            manifest["new_zip_sha256"]=sha(zp.read_bytes())
            sheet=Image.new("RGB",(1380,1050),"#f5f6f7");draw=ImageDraw.Draw(sheet)
            draw.text((20,18),"PIXELPURE RADIANCE AQUA SOOTHING CREAM 50 mL  |  4 HISTORIC + 1 NEW",fill="#172e32")
            draw.text((20,47),"INTERNAL SOURCE QA ONLY | TradeKorea image rights and packaging not approved",fill="#9b3b3b")
            for i,data in enumerate(imgs):
                x=20+(i%3)*455;y=85+(i//3)*463
                draw.rounded_rectangle((x,y,x+440,y+433),radius=10,fill="white",outline="#cbd0d1",width=2)
                with Image.open(io.BytesIO(data)) as im:
                    im=im.convert("RGB"); im.thumbnail((395,385),Image.Resampling.LANCZOS)
                    sheet.paste(im,(x+(440-im.width)//2,y+8+(385-im.height)//2))
                draw.text((x+10,y+400),"#"+str(i+1)+(" NEW UNLICENSED SOURCE" if i==4 else " EXISTING SOURCE"),fill="#394950")
            contact=OUT/"pending-29-five-scene-source-review-CONTACT-INTERNAL.jpg"
            sheet.save(contact,quality=92,optimize=True)
            manifest["contact"]=str(contact.relative_to(ROOT))
    except Exception as e:
        manifest.update({"outcome":"SINGLE_SOURCE_FAILED_CONTINUE_OTHER_FAMILIES","error":type(e).__name__+": "+str(e)[:260],
            "attempts":1,"candidate_saved":False})
    (OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"v":"v2959","outcome":manifest["outcome"],"one_new_candidate":manifest.get("candidate_saved",False),
      "new_staged_five_zip":bool(manifest.get("new_internally_staged_five_source_zip")),"retail_approved":False},ensure_ascii=False))
if __name__=="__main__":main()
