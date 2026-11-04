#!/usr/bin/env python3
"""Read-only BBIA product-image audit; never modifies published JPGs."""
import argparse
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

SOF = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
TARGET_IDS = ("206", "1000000122")  # existing public groups, never rewrite
HOLD_IDS = {"200": "variant photo pending", "1000000124": "refill-only hero pending"}
MAX_BYTES = 2_000_000
EXPECTED = 1080

def jpeg_dimensions(data):
    if not data.startswith(b"\xff\xd8"):
        return None
    p = 2
    while p + 4 < len(data):
        if data[p] != 0xFF:
            return None
        while p < len(data) and data[p] == 0xFF:
            p += 1
        if p >= len(data):
            break
        marker = data[p]; p += 1
        if marker in (0xD8, 0xD9, 0x01) or 0xD0 <= marker <= 0xD7:
            continue
        if marker == 0xDA:
            break
        if p + 2 > len(data):
            return None
        length = int.from_bytes(data[p:p+2], "big")
        if length < 2 or p + length > len(data):
            return None
        if marker in SOF and length >= 7:
            h = int.from_bytes(data[p+3:p+5], "big")
            w = int.from_bytes(data[p+5:p+7], "big")
            return [w, h]
        p += length
    return None

def inspect(path, root):
    data = path.read_bytes()
    dims = jpeg_dimensions(data)
    issues = []
    if dims is None or not data.endswith(b"\xff\xd9"):
        issues.append("JPEG_STRUCTURE_REVIEW")
    if len(data) >= MAX_BYTES:
        issues.append("OVER_2MB")
    if dims != [EXPECTED, EXPECTED]:
        issues.append("NOT_1080_SQUARE")
    return {
        "path": str(path.relative_to(root)),
        "bytes": len(data),
        "dimensions": dims,
        "sha256": hashlib.sha256(data).hexdigest(),
        "issues": issues,
    }

def run(root):
    base = root / "public" / "images"
    by_family = defaultdict(list)
    by_sha = defaultdict(list)
    for jpg in sorted(base.rglob("*.jpg")) if base.exists() else []:
        item = inspect(jpg, root)
        family = jpg.relative_to(base).parts[0]
        by_family[family].append(item)
        by_sha[item["sha256"]].append(item["path"])
    duplicate_sha = [p for p in by_sha.values() if len(p) > 1]
    findings = {}
    for key in TARGET_IDS:
        files = by_family.get(key, [])
        findings[key] = {
            "published_jpg_count": len(files),
            "files": files,
            "exact_six_files": sorted(Path(x["path"]).name for x in files) == [
                "01.jpg", "02.jpg", "03.jpg", "04.jpg", "05.jpg", "06.jpg"
            ],
            "technical_issues": sum(bool(x["issues"]) for x in files),
            "sales_approved_by_this_audit": False
        }
    for key, why in HOLD_IDS.items():
        findings[key] = {
            "published_jpg_count": len(by_family.get(key, [])),
            "status": "DO_NOT_PROMOTE_CANDIDATE",
            "hold_reason": why,
            "sales_approved_by_this_audit": False,
        }
    return {
        "checkpoint": "v216",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "READ_ONLY_ACTUAL_JPG_BYTES",
        "published_total_jpg_checked": sum(map(len, by_family.values())),
        "family_directories": len(by_family),
        "sha256_duplicate_groups": duplicate_sha,
        "targets": findings,
        "policy": {
            "does_not_modify_public_images": True,
            "does_not_certify_package_or_shade_authenticity": True,
            "do_not_infer_sales_approval_from_file_count": True,
        },
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--out")
    args = parser.parse_args()
    result = run(Path(args.repo).resolve())
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(rendered + "\n", encoding="utf-8")
    print(json.dumps({
        "checkpoint": "v216",
        "jpg_checked": result["published_total_jpg_checked"],
        "families": result["family_directories"],
        "duplicate_groups": len(result["sha256_duplicate_groups"]),
        "targets": {k: {"count": v["published_jpg_count"], "technical_issues": v.get("technical_issues", "held")} for k, v in result["targets"].items()}
    }))

if __name__ == "__main__":
    main()
