#!/usr/bin/env python3
"""One new exact product scene candidate after deduping against v2929 original bytes. Internal QA only."""
from pathlib import Path
import io,json,zipfile,hashlib,urllib.request
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa-review/v2958-pixelpure-serum50-distinct-new-scene-candidate-20261106"
PREV=ROOT/"qa-review/v2929-pixelpure-three-four-photo-pack-source-integrity-QA/manifest.json"
URL="https://web.tradekorea.com/product/858/2334858/pixelpure_aura_radiance_serum_%28Skin_Care%29_4.jpg"
WEBPAGE="https://www.tradekorea.com/product/detail/P828498/pixelpure-aura-radiance-serum--Skin-Care-.html"
def h(b):return hashlib.sha256(b).hexdigest()
def dHash(im):
    pic=im.convert("L").resize((9,8),Image.Resampling.LANCZOS)
    pix=list(pic.getdata())
    return "".join("1" if pix[y*9+x]>pix[y*9+x+1] else "0" for y in range(8) for x in range(8))
def hamming(a,b):return sum(x!=y for x,y in zip(a,b))
def jpeg1080(b):
    with Image.open(io.BytesIO(b)) as im:
        im.load()
        iw,ih=im.size
        if min(iw,ih)<700:raise ValueError("SOURCE_NATIVE_TOO_SMALL "+str((iw,ih)))
        rgb=im.convert("RGB")
        # Fit the entire original image, no inventing or moving objects.
        rgb.thumbnail((1020,1020),Image.Resampling.LANCZOS)
        canvas=Image.new("RGB",(1080,1080),"white")
        canvas.paste(rgb,((1080-rgb.width)//2,(1080-rgb.height)//2))
        out=io.BytesIO();canvas.save(out,format="JPEG",quality=92,optimize=True)
        if out.tell()>=2_000_000:raise ValueError("JPG_EXCEEDS_2MB")
        return out.getvalue(),(iw,ih)
def main():
    if OUT.exists():raise SystemExit("v2958 output exists; refusing rerun")
    prev=json.loads(PREV.read_text())
    fam=next(x for x in prev["results"] if x["family"]=="pending-30")
    oldzip=ROOT/fam["archive_ZIP"]
    if h(oldzip.read_bytes())!=fam["archive_ZIP_sha256"]:
        raise ValueError("Old four-JPG zip hash mismatch")
    expected=[x["sha256"] for x in fam["source_records"]]
    found={}
    with zipfile.ZipFile(oldzip) as z:
        for name in z.namelist():
            if name.lower().endswith(".jpg"):
                blob=z.read(name);s=h(blob)
                if s in expected:found[s]=blob
    if len(found)!=4:raise ValueError("Old archive original four source photos not all present")
    prior=[]
    for x in fam["source_records"]:
        dat=found[x["sha256"]]
        with Image.open(io.BytesIO(dat)) as im:
            im.load();prior.append(dHash(im))
    OUT.mkdir(parents=True)
    manifest={"version":"v2958","baseline":"v2957","family":"pending-30",
      "product":"PIXELPURE Aura Radiance Serum 50mL",
      "candidate_source_page":WEBPAGE,
      "candidate_origin":"TradeKorea third-party Korean seller listing / supplier THE FORTUNE TRADING CO.,LTD.; NOT confirmed brand-hosted",
      "exact_product_seen_in_source_preview":"two floating pink PIXELPURE Aura Radiance Serum 50mL pump bottles",
      "prior_four_image_archive":fam["archive_ZIP"],
      "old_original_JPG_byte_modified":0,
      "prior_approved_families_preserved":11,"prior_URLs_preserved":55,
      "new_public_JPG":0,"new_anonymous_verified_URLs":0,"new_sale_approvals":0,
      "rights_approved":False,"physical_stock_edition_verified":False,
      "original_MK_binary_verified":False,"manual_full_frame_QA":"PENDING",
      "next_action_on_fail":"Do not repeat same failed URL; evaluate a different true original scene/authorised source or another product family."
    }
    try:
        req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0 (compatible; StockVisualQATool/1.0)","Accept":"image/avif,image/webp,image/*"})
        with urllib.request.urlopen(req,timeout=20) as res:
            payload=res.read(5_000_000)
            typ=res.headers.get("Content-Type","")
        if len(payload)<15000:raise ValueError("IMAGE_RESPONSE_TOO_SMALL "+str(len(payload)))
        if len(payload)>=5_000_000:raise ValueError("IMAGE_TOO_LARGE_OR_TRUNCATED")
        with Image.open(io.BytesIO(payload)) as photo:
            photo.load(); fmt=photo.format
        candidate,dims=jpeg1080(payload)
        with Image.open(io.BytesIO(candidate)) as test:
            d=dHash(test)
        distances=[hamming(d,x) for x in prior]
        raw=OUT/"pending-30-new-two-floating-serum-bottles-native-reference.jpg"
        # The new candidate may not be JPEG; save with proper extension if needed.
        if fmt in ("JPEG","JPG"):raw.write_bytes(payload); nativefile=raw
        else:
            suffix={"PNG":".png","WEBP":".webp"}.get(fmt)
            if not suffix:raise ValueError("UNRECOGNIZED_IMAGE_FORMAT "+str(fmt))
            nativefile=raw.with_suffix(suffix);nativefile.write_bytes(payload)
        candidatepath=OUT/"pending-30-candidate-05-two-floating-bottles-1080-INTERNAL-QA.jpg"
        candidatepath.write_bytes(candidate)
        manifest.update({"candidate_native":str(nativefile.relative_to(ROOT)),"native_px":list(dims),
          "native_sha256":h(payload),"candidate_JPG_path":str(candidatepath.relative_to(ROOT)),
          "candidate_JPG_sha256":h(candidate),"distance_hamming_to_four_previous":distances,
          "technical_JPG_valid":True})
        if min(distances)<=8:
            manifest["outcome"]="REJECT_TOO_SIMILAR_TO_ARCHIVE"
            manifest["five_source_JPG_candidate_ZIP_created"]=False
        else:
            manifest["outcome"]="FIFTH_DISTINCT_SCENE_ARCHIVED_INTERNAL_VISUAL_QA_PENDING"
            stage=OUT/"pending-30-five-distinct-scene-candidates-NOT-FOR-RETAIL.zip"
            imgs=[found[x] for x in expected]+[candidate]
            with zipfile.ZipFile(stage,"w") as z:
                for i,data in enumerate(imgs,1):
                    info=zipfile.ZipInfo(f"{i:02d}-{'new' if i==5 else 'existing'}-PIXELPURE-AuraRadianceSerum-QA.jpg")
                    info.compress_type=zipfile.ZIP_STORED;info.external_attr=0o644<<16
                    z.writestr(info,data)
            with zipfile.ZipFile(stage) as z:
                assert all(h(z.read(f))==h(data) for f,data in zip(z.namelist(),imgs))
            report=Image.new("RGB",(1380,1050),"#f4f5f7");draw=ImageDraw.Draw(report)
            draw.text((20,16),"PIXELPURE AURA RADIANCE SERUM 50mL | V2958 4 OLD + 1 NEW",fill="#263238")
            draw.text((20,42),"INTERNAL QA ONLY | TradeKorea candidate, image permission and stock generation still pending",fill="#993333")
            for i,data in enumerate(imgs):
                x=20+(i%3)*455;y=80+(i//3)*462
                draw.rounded_rectangle((x,y,x+440,y+430),radius=10,fill="white",outline="#d0d3d6",width=2)
                with Image.open(io.BytesIO(data)) as im:
                    im=im.convert("RGB");im.thumbnail((396,380),Image.Resampling.LANCZOS)
                    report.paste(im,(x+(440-im.width)//2,y+6+(380-im.height)//2))
                draw.text((x+12,y+397),f"{i+1} | {'NEW TRADEKOREA CANDIDATE' if i==4 else 'EXISTING QA SOURCE'}",fill="#475259")
            report.save(OUT/"pending-30-five-scene-source-review-CONTACT-INTERNAL.jpg",quality=92,optimize=True)
            manifest.update({"five_source_JPG_candidate_ZIP_created":True,
                "candidate_zip":str(stage.relative_to(ROOT)),"candidate_zip_sha256":h(stage.read_bytes()),
                "contact":"qa-review/v2958-pixelpure-serum50-distinct-new-scene-candidate-20261106/pending-30-five-scene-source-review-CONTACT-INTERNAL.jpg",
                "five_photos_count":5,"new_retail_ready_photos":0})
    except Exception as e:
        manifest.update({"outcome":"CANDIDATE_SOURCE_HOLD","error":type(e).__name__+": "+str(e)[:320],
          "five_source_JPG_candidate_ZIP_created":False,"attempted_source_only_once":True})
    (OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"version":"v2958","outcome":manifest["outcome"],"new_source_saved":bool(manifest.get("candidate_native")),
       "zip_created":manifest.get("five_source_JPG_candidate_ZIP_created"),
       "new_public_urls":0}))
if __name__=="__main__":main()
