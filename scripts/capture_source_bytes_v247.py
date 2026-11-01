"""Collect actual public image bytes for documented Shopee candidate sources.

Staging only. Retrieved images are NOT automatically official, approved,
seller-ready, or authorized for republication.
"""
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
from urllib.parse import urlparse
import requests
from PIL import Image, ImageFile

Image.MAX_IMAGE_PIXELS = 50_000_000
ImageFile.LOAD_TRUNCATED_IMAGES = False
BASE = Path("source-first-output-v247")
BASE.mkdir(exist_ok=True)
items = json.loads(Path("evidence/source-first-16.json").read_text(encoding="utf-8"))
rows = []
columns = ["id","name","candidate_url","source_page","status","filename","bytes","width","height","sha256","error"]
headers = {"User-Agent":"Mozilla/5.0 (compatible; Shopee-Source-QA/1.0)", "Accept":"image/avif,image/webp,image/png,image/jpeg,image/*;q=0.8"}
def http_candidate(url):
    parsed = urlparse(url)
    return parsed.scheme == "https" and bool(parsed.netloc) and not parsed.username and not parsed.password
def collect(item):
    url = item.get("url","")
    rec = {k:"" for k in columns}
    rec.update({"id":str(item.get("id","")),"name":item.get("name",""),"candidate_url":url,"source_page":item.get("page",""),"status":"NOT_STARTED"})
    if not http_candidate(url):
        rec.update(status="INVALID_HTTPS_SOURCE",error="Only absolute HTTPS sources permitted")
        return rec
    try:
        response = requests.get(url,headers=headers,timeout=(10,20),stream=True,allow_redirects=True)
        response.raise_for_status()
        if not http_candidate(response.url):
            raise ValueError("Redirected outside HTTPS")
        buf = io.BytesIO()
        for chunk in response.iter_content(chunk_size=65536):
            buf.write(chunk)
            if buf.tell() > 16_000_000:
                raise ValueError("candidate image exceeds 16MB")
        raw = buf.getvalue()
        with Image.open(io.BytesIO(raw)) as im:
            im.load()
            width,height = im.size
            if width < 200 or height < 200:
                raise ValueError("candidate resolution too small")
            if im.format not in ("JPEG","PNG","WEBP"):
                raise ValueError("unsupported source image format")
            suffix = {"JPEG":".jpg","PNG":".png","WEBP":".webp"}[im.format]
        target = BASE / str(item["id"])
        target.mkdir(exist_ok=True)
        filename = target / ("source_photo" + suffix)
        filename.write_bytes(raw)
        rec.update(status="DOWNLOADED_UNAPPROVED",filename=str(filename),bytes=len(raw),width=width,height=height,sha256=hashlib.sha256(raw).hexdigest())
    except Exception as exc:
        rec.update(status="DOWNLOAD_FAILED",error=f"{type(exc).__name__}: {str(exc)[:230]}")
    return rec
for item in items:
    result = collect(item)
    rows.append(result)
    print(result["id"],result["name"],result["status"],result["error"],flush=True)
with (BASE/"candidate_manifest.csv").open("w",newline="",encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f,fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)
(BASE/"README.txt").write_text(
    "SOURCE CANDIDATES ONLY. Validate product edition, packaging, options, source authenticity, "
    "publication rights and official swatches before any seller image release. "
    "This artifact does not update public/images or verified URL mapping.\n",encoding="utf-8")
count=sum(r["status"]=="DOWNLOADED_UNAPPROVED" for r in rows)
print(f"Downloaded {count}/{len(rows)} candidate images. None approved for publication.")
