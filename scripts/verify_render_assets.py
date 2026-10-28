#!/usr/bin/env python3
"""Verify anonymous public Shopee thumbnail URLs against source asset hashes."""
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import urllib.request

BASE = os.environ.get("IMAGE_BASE_URL", "https://mellow-bbia-images.onrender.com").rstrip("/")
MANIFEST = Path(__file__).resolve().parents[1] / "public" / "asset-manifest.json"

def verify(asset):
    url = f"{BASE}/{asset['file']}"
    error = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ShopeeAssetQA/1.0", "Accept": "image/jpeg,image/*"})
            with urllib.request.urlopen(req, timeout=25) as response:
                code = response.status
                kind = response.headers.get("Content-Type", "").split(";")[0].strip().lower()
                blob = response.read()
            checksum = hashlib.sha256(blob).hexdigest()
            assert code == 200, f"HTTP {code}"
            assert kind in ("image/jpeg", "image/jpg"), f"Content type {kind}"
            assert blob.startswith(bytes.fromhex("ffd8ff")), "Not JPEG data"
            assert len(blob) == asset["bytes"], "Byte size differs"
            assert checksum == asset["sha256"], "SHA256 differs"
            return {"url": url, "status": "pass", "http_status": code, "bytes": len(blob), "sha256": checksum}
        except Exception as exc:
            error = str(exc)
            if attempt < 2:
                time.sleep(5)
    return {"url": url, "status": "fail", "reason": error}

def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    items = manifest["assets"]
    assert len(items) == manifest["asset_count"] == 30
    results = []
    for idx, asset in enumerate(items, 1):
        result = verify(asset)
        results.append(result)
        print(f"[{idx}/30] {result['status'].upper()} {asset['file']} {result.get('reason', '')}", flush=True)
    passed = sum(item["status"] == "pass" for item in results)
    report = {"base_url": BASE, "expected_count": 30, "verified_count": passed,
              "failed_count": 30-passed, "all_verified": passed == 30, "results": results}
    Path("render-url-verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"VALIDATED {passed}/30", flush=True)
    return 0 if passed == 30 else 1

if __name__ == "__main__":
    sys.exit(main())
