#!/usr/bin/env python3
"""Review-only visual similarity comparison for 5 held BBIA variant scenes.

Requires local v144 125-image ZIP. Does not edit product images.
"""
import io, json, zipfile, hashlib
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

GROUPS = {
    "ESSENTIAL_EYE_LOOKS": {
        "needles": ["03_SMOKY_EYE_LOOK", "03_LOVELY_EYE_LOOK"],
        "roi": [.07, .33, .93, .79],
    },
    "LAST_PEN_EYE_LOOKS": {
        "needles": [
            "03_BLACK_FIT_EYE_LOOK", "05_BROWN_EYE_LOOK",
            "06_CHOCO_BROWN_EYE_LOOK"
        ],
        "roi": [.07, .34, .93, .77],
    },
}


def audit(archive: Path):
    records = []
    with zipfile.ZipFile(archive) as z:
        for group, spec in GROUPS.items():
            samples = []
            for needle in spec["needles"]:
                name = next(
                    n for n in z.namelist()
                    if n.startswith("HOLD_DO_NOT_PUBLISH/") and needle in n
                )
                raw = z.read(name)
                img = Image.open(io.BytesIO(raw)).convert("RGB")
                w, h = img.size
                l, t, r, b = spec["roi"]
                crop = np.asarray(img.crop((int(l*w), int(t*h), int(r*w), int(b*h))))
                samples.append((name, crop, hashlib.sha256(raw).hexdigest()))
            for i in range(len(samples)):
                for j in range(i + 1, len(samples)):
                    a, b = samples[i], samples[j]
                    x = cv2.cvtColor(cv2.resize(a[1], (200, 100)), cv2.COLOR_RGB2GRAY)
                    y = cv2.cvtColor(cv2.resize(b[1], (200, 100)), cv2.COLOR_RGB2GRAY)
                    ex, ey = cv2.Canny(x, 60, 150) > 0, cv2.Canny(y, 60, 150) > 0
                    records.append({
                        "group": group, "file_a": a[0], "file_b": b[0],
                        "crop_mean_absolute_gray_difference": round(float(np.abs(x.astype(float)-y.astype(float)).mean()), 2),
                        "edge_jaccard": round(float(np.logical_and(ex, ey).sum()/max(1, np.logical_or(ex, ey).sum())), 4),
                        "sha256_a": a[2], "sha256_b": b[2],
                        "status": "HOLD_SHADE_PROOF_MISSING"
                    })
    return {
        "source": archive.name, "compared_pairs": len(records),
        "note": "Numbers are triage signals, NOT shade accuracy proof or sales approval.",
        "pairs": records, "sales_approved": 0
    }


if __name__ == "__main__":
    archive = Path("BBIA_v144_125JPG_RECOVERED_QA_ONLY.zip")
    print(json.dumps(audit(archive), ensure_ascii=False, indent=2))
