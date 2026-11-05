#!/usr/bin/env python3
"""v2965 four-family evidence QA, technical alpha repair of Bioheal v2964 fifth source only."""
import io,json,hashlib,zipfile
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa-review/v2965-bioheal-alpha-repair-and-four-family-gate-20261106"
def h(b):return hashlib.sha256(b).hexdigest()
INPUT={
 "pending-27":"qa-review/v2963-pixelpure-toner200-distinct-multibottle-scene-20261106/manifest.json",
 "pending-29":"qa-review/v2961-pixelpure-cream50-fifth-tradekorea-photo-20261106/manifest.json",
 "pending-30":"qa-review/v2958-pixelpure-serum50-distinct-new-scene-candidate-20261106/manifest.json",
 "pending-25":"qa-review/v2964-bioheal-cream50-open-jar-fifth-scene-internal-20261106/manifest.json"
}
def verified(path,sha):
    by=(ROOT/path).read_bytes()
    if h(by)!=sha:raise ValueError("Source digest drift: "+path)
    return by
def bioheal_alpha_repair(m):
    raw=verified(m["candidate_native"],m["native_sha256"])
    with Image.open(io.BytesIO(raw)) as native:
        native.load()
        nativebands=native.getbands()
        hasalpha="A" in nativebands or "transparency" in native.info
        pix=native.convert("RGBA")
        alpha=pix.getchannel("A")
        hist=alpha.histogram()
        transparent_count=sum(hist[:250])
        total=pix.width*pix.height
        ratio=transparent_count/total
        obs={"native_type":native.format,"native_size":list(native.size),
             "has_alpha_or_transparency":hasalpha,
             "alpha_below_250_fraction":round(ratio,5),
             "old_bad_JPG_sha256":m["new_JPG_sha256"],
             "old_bad_JPG_kept":True,"retail_approved":False}
        if not hasalpha or ratio<0.08:
            obs.update({"status":"HOLD_SOURCE_BLACK_BACKGROUND_NOT_ALPHA_REPAIRABLE",
                        "why":"Cannot safely replace opaque black pixels with fabricated white background"})
            return obs
        white=Image.new("RGBA",pix.size,(255,255,255,255))
        composited=Image.alpha_composite(white,pix).convert("RGB")
        composited.thumbnail((1020,1020),Image.Resampling.LANCZOS)
        final=Image.new("RGB",(1080,1080),"white")
        final.paste(composited,((1080-composited.width)//2,(1080-composited.height)//2))
        target=OUT/"pending-25-only-fifth-open-jar-transparent-PNG-composited-on-white-1080-QA.jpg"
        final.save(target,"JPEG",quality=93,optimize=True)
    corrected=target.read_bytes()
    with Image.open(io.BytesIO(corrected)) as im:
        im.load()
        if im.size!=(1080,1080) or im.format!="JPEG" or len(corrected)>=2_000_000:raise ValueError("new corrected JPG invalid")
    prior_manifest=json.loads((ROOT/"qa-review/v2934-bioheal-cream-four-real-source-scene-QA-only/manifest.json").read_text())
    zip_path=ROOT/prior_manifest["zip_path"]
    if h(zip_path.read_bytes())!=prior_manifest["zip_sha256"]:raise ValueError("prior source zip drift")
    files={}
    with zipfile.ZipFile(zip_path) as z:
        for name in z.namelist():
            if name.lower().endswith((".jpg",".jpeg",".png")):
                b=z.read(name);files[h(b)]=b
    photos=[]
    for row in prior_manifest["source_records"]:
        if row["sha256"] not in files:raise ValueError("baseline source absent: "+row["sha256"])
        photos.append(files[row["sha256"]])
    photos.append(corrected)
    zippath=OUT/"pending-25-4-old-1-alpha-corrected-fifth-candidate-INTERNAL-NOT-RETAIL.zip"
    with zipfile.ZipFile(zippath,"w") as z:
        for i,b in enumerate(photos):
            zi=zipfile.ZipInfo(f"{i+1:02d}-{'NEW-alpha-corrected' if i==4 else 'original'}-BiohealCream50-QA.jpg")
            zi.compress_type=zipfile.ZIP_STORED;zi.external_attr=0o644<<16;z.writestr(zi,b)
    with zipfile.ZipFile(zippath) as z:
        if not all(h(z.read(zi))==h(b) for zi,b in zip(z.namelist(),photos)):raise ValueError("zip byte digest changed")
    cp=OUT/"pending-25-only-fifth-alpha-repaired-five-source-CONTACT-INTERNAL.jpg"
    contact=Image.new("RGB",(1380,1050),"#f5f6f7");d=ImageDraw.Draw(contact)
    d.text((20,15),"BIOHEAL NAD PRIZCELL CREAM 50mL | 4 preserved + alpha-repaired 5th",fill="#243238")
    d.text((20,40),"INTERNAL QA ONLY. Front-view 1/2 near duplicates; 3/5 open-jar composition overlap; do not approve retail.",fill="#a2423a")
    for i,b in enumerate(photos):
        xx=20+(i%3)*455;yy=82+(i//3)*462
        d.rounded_rectangle((xx,yy,xx+440,yy+432),radius=10,fill="white",outline="#d1d2d3",width=2)
        with Image.open(io.BytesIO(b)) as im:
            im=im.convert("RGB");im.thumbnail((395,380),Image.Resampling.LANCZOS)
            contact.paste(im,(xx+(440-im.width)//2,yy+8+(380-im.height)//2))
        d.text((xx+10,yy+405),f"FRAME {i+1} {'new alpha repair' if i==4 else 'original unmodified'}",fill="#46545b")
    contact.save(cp,"JPEG",quality=91,optimize=True)
    obs.update({"status":"ONE_FAILED_FRAME_ALPHA_BACKGROUND_CORRECTED_QA_ONLY",
                "new_JPG":str(target.relative_to(ROOT)),"new_JPG_sha256":h(corrected),"new_JPG_bytes":len(corrected),
                "new_qa_zip":str(zippath.relative_to(ROOT)),"new_zip_sha256":h(zippath.read_bytes()),
                "contact":str(cp.relative_to(ROOT)),
                "commercial_rights":False,"exact_stock_edition":False,
                "semantically_distinct_5_scenes":False,
                "reason_not_retail":"Underlying product photos #1/#2 and #3/#5 may be semantically similar; photo rights and original MK still missing"})
    return obs
def main():
    if OUT.exists():raise RuntimeError("v2965 exists; refuse rerun")
    family={}
    for k,path in INPUT.items():
        family[k]=json.loads((ROOT/path).read_text())
        if family[k]["version"] not in ["v2963","v2961","v2958","v2964"]:raise ValueError("wrong manifest")
    OUT.mkdir(parents=True)
    bio=bioheal_alpha_repair(family["pending-25"])
    ledger={}
    for fam,m in family.items():
        if fam=="pending-25":
            ledger[fam]={"technical_result":bio["status"],
              "original_4_zip_preserved":True,"candidate_new_JPG":bio.get("new_JPG"),
              "fifth_photo_file_exists":bool(bio.get("new_JPG")),
              "independent_scene_count_verified":False,
              "retail_release":"HOLD","reason":"Photo 1/2 duplicate-like; 3/5 possibly common open-jar product source; exact MK/stock/license absent"}
            continue
        path=m.get("new_JPG",m.get("new_reference_JPG"))
        digest=m.get("new_JPG_sha256",m.get("new_reference_SHA256"))
        if not path or not digest:raise ValueError("Missing candidate fifth for "+fam)
        blob=verified(path,digest)
        with Image.open(io.BytesIO(blob)) as im:
            im.load();passed=im.size==(1080,1080) and im.format=="JPEG" and len(blob)<2_000_000
        zip_name=m.get("five_photo_zip",m.get("new_internally_staged_five_source_zip",m.get("candidate_zip")))
        zip_hash=m.get("five_photo_zip_sha256",m.get("new_zip_sha256",m.get("candidate_zip_sha256")))
        if not zip_name or not zip_hash:raise ValueError("Missing zip link for "+fam)
        verified(zip_name,zip_hash)
        ledger[fam]={"new_fifth_JPG":path,"new_JPG_sha256":digest,
           "native_px":m.get("native_dimensions",m.get("native_px")),
           "QA_zip":zip_name,"QA_zip_sha256":zip_hash,
           "existing_4_hashes_preserved":True,"technical_pass":passed,
           "visual_status":"PASS_DISTINCT_COMPOSITION_REFERENCE_ONLY",
           "retail_release":"HOLD_MK_RIGHTS_STOCK_INDEPENDENT_FINAL_QA"}
    result={"version":"v2965","date_kst":"2026-11-06",
      "prev_checkpoint":"v2964","project":"Shopee Thumbnail Creator PRO 82 SKU / 41 families",
      "photo_imports_this_sequence":"v2958, v2961, v2963, v2964",
      "family_evidence":ledger,"pending25_alpha":{"details":bio},
      "public_approved_prior_families":11,"public_verified_prior_URLs":55,
      "previous_public_files_modified":0,"previous_source_files_modified":0,
      "new_retail_approved":0,"new_public_url_verified":0,"new_public_assets":0,
      "new_customer_source_authorizations":0,
      "verified_MK_original_binary_accessible":False,
      "publishing_route":"UNCHANGED_NOT_ATTEMPTED_NOT_AUTHORIZED_BY_QA",
      "prevent_false_5photo_count":"Source file count != independent scene count or commercial rights.",
      "next_source_work":[
        "pending-25 obtain distinctly composed independent 50mL native source matching stock, avoid near-repeat current #3/5",
        "pending-20 keep two front label groups separate until owned exact 25AD unit confirmed",
        "all candidate complete families require stock version/photo reuse permission/original MK binary before customer JPGs and Render deployment"
      ],"spreadsheet_exported":False}
    (OUT/"manifest.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"version":"v2965","bioheal_status":bio["status"],
        "confirmed_fifth_reference_sets":["pending-27","pending-29","pending-30"],
        "sale_approvals":0,"public_verified_URLs_new":0},ensure_ascii=False))
if __name__=="__main__":main()
