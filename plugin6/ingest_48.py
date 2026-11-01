#!/usr/bin/env python3
"""BBIA candidate photo ingest. Evidence only, never marks sale-ready."""
import base64, concurrent.futures, csv, gzip, hashlib, io, json, os, re, time, urllib.parse, urllib.request, zipfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent
TARGET=ROOT/"out"
DOMAIN_ALLOW={"cdn-pro-web-250-115.cdn-nhncommerce.com","sky007.com","www.bbia.co.kr","bbia.co.kr"}
def get_entry(args):
    index,family,number,url=args
    family_id=f"{index:03d}"
    try:
        parsed=urllib.parse.urlparse(url)
        if parsed.scheme!="https" or parsed.hostname not in DOMAIN_ALLOW:
            raise ValueError("unapproved URL host")
        req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0", "Accept":"image/avif,image/webp,image/jpeg,image/png,*/*"})
        with urllib.request.urlopen(req,timeout=24) as response:
            data=response.read(10_000_001)
        if len(data)>10_000_000:raise ValueError("source too large")
        im=Image.open(io.BytesIO(data)); im.load()
        if im.format not in ("JPEG","PNG","WEBP"):raise ValueError(f"invalid format {im.format}")
        if min(im.size)<500:raise ValueError(f"small image {im.size}")
        ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[im.format]
        p=TARGET/"candidates"/family_id/f"{number:02d}.{ext}"
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(data)
        return {"family_id":family_id,"product":family["name"],"url":url,"file":p.relative_to(TARGET).as_posix(),"width":im.width,"height":im.height,"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest(),"status":"CANDIDATE_NEEDS_PRODUCT_SHADE_QA"}
    except Exception as e:
        return {"family_id":family_id,"product":family["name"],"url":url,"status":"FETCH_FAILED","error":str(e)[:200]}
def main():
    TARGET.mkdir(exist_ok=True)
    raw=(ROOT/"bbia_inventory_48.json.gz.b64").read_text().strip()
    families=json.loads(gzip.decompress(base64.b64decode(raw)))
    assert len(families)==48, "unexpected inventory size"
    assert sum(f["count"] for f in families)==314, "unexpected SKU count"
    roster=[{"id":f"{idx:03d}","name":f["name"],"parent_sku":f["key"],"sku_count":f["count"],"candidate_count":len(f["urls"])} for idx,f in enumerate(families,1)]
    (TARGET/"roster.json").write_text(json.dumps(roster,ensure_ascii=False,indent=2))
    jobs=[(idx,f,n,u) for idx,f in enumerate(families,1) for n,u in enumerate(f["urls"],1)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        rows=list(pool.map(get_entry,jobs))
    with (TARGET/"source_ledger.csv").open("w",encoding="utf-8-sig",newline="") as fo:
        fields=["family_id","product","status","url","file","width","height","bytes","sha256","error"]
        w=csv.DictWriter(fo,fieldnames=fields);w.writeheader();w.writerows(rows)
    successes=sum(x["status"].startswith("CANDIDATE") for x in rows)
    report={"sku_rows":314,"families":48,"source_url_attempts":len(rows),"candidate_images_saved":successes,"failed_downloads":len(rows)-successes,"verified_sale_ready_images":0,"localized_zips":0,"note":"Source candidates require product/option visual verification before any sale-ready production."}
    (TARGET/"run_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False))
if __name__=="__main__": main()
