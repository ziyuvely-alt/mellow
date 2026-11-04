#!/usr/bin/env python3
"""v231 preserve 14 already-generated source-photo drafts, excluding 1000000166 promo banner."""
import argparse,hashlib,json,shutil,zipfile
from pathlib import Path
from PIL import Image
EXCLUDE={"1000000166":"PRIMARY_SOURCE_IS_PROMOTIONAL_KOREAN_BANNER"}
def main(a,b,out):
    out.mkdir(parents=True,exist_ok=True)
    srcs=[p for d in (a,b) for p in d.glob("BBIA_*_OFFICIAL_PHOTO_EN_v229_QA_PENDING.jpg")]
    items=[]; hashes=set()
    folder=out/"QA_PENDING_JPG"
    folder.mkdir(exist_ok=True)
    for p in srcs:
        parts=p.name.split("_")
        sku=parts[1]
        if sku in EXCLUDE:
            items.append({"goodsNo":sku,"source":p.name,"status":"EXCLUDED_PROMOTIONAL_SOURCE"});continue
        data=p.read_bytes();digest=hashlib.sha256(data).hexdigest()
        if digest in hashes:items.append({"goodsNo":sku,"status":"DUPLICATE_BYTE_HASH_SKIPPED"});continue
        with Image.open(p) as im:
            im.verify()
        with Image.open(p) as im:
            dims=list(im.size)
        if dims != [1080,1080] or len(data)>=2_000_000:
            items.append({"goodsNo":sku,"status":"TECHNICAL_REJECT","dimensions":dims});continue
        target=folder/p.name
        shutil.copyfile(p,target)
        hashes.add(digest)
        items.append({"goodsNo":sku,"file":p.name,"sha256":digest,"bytes":len(data),"dimensions":dims,
                      "status":"PHOTO_DRAFT_RETAINED_PENDING_VISUAL_AND_SHADE_APPROVAL"})
    accepted=[x for x in items if x["status"]=="PHOTO_DRAFT_RETAINED_PENDING_VISUAL_AND_SHADE_APPROVAL"]
    manifest={"checkpoint":"v231","source_versions":["v229","v230"],"accepted_jpg":len(accepted),
       "excluded_promo":sum(x["status"]=="EXCLUDED_PROMOTIONAL_SOURCE" for x in items),
       "existing_public_images_modified":False,"approved_55_urls_modified":False,"sales_approved":0,
       "scope_note":"Image files copied byte-for-byte; no edits, no duplicate renders, no automatic brand or shade approval",
       "records":items}
    (out/"BBIA_v231_14_CANDIDATE_MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    with zipfile.ZipFile(out/"BBIA_v231_FOURTEEN_QA_PENDING_JPG.zip","w",zipfile.ZIP_DEFLATED) as z:
        for p in folder.glob("*.jpg"):z.write(p,arcname=p.name)
        z.write(out/"BBIA_v231_14_CANDIDATE_MANIFEST.json",arcname="QA_MANIFEST.json")
    with zipfile.ZipFile(out/"BBIA_v231_FOURTEEN_QA_PENDING_JPG.zip") as z:
        assert z.testzip() is None
    print("V231_CURATED",json.dumps({"accepted":len(accepted),"rejected_promo":manifest["excluded_promo"],"zip_valid":True,"reused_unchanged":True}))
    if len(accepted)!=14: raise RuntimeError(f"Expected fourteen, got {len(accepted)}")
if __name__=="__main__":
    p=argparse.ArgumentParser()
    for arg in ("a","b","out"):p.add_argument("--"+arg,required=True)
    s=p.parse_args();main(Path(s.a),Path(s.b),Path(s.out))
