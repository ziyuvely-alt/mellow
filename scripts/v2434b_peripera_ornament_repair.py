#!/usr/bin/env python3
"""v2434b: repair only the damaged ornamental circle on previously revised Peripera info JPG.
No generated product imagery, unchanged copy and sales restrictions.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
P=Path("baseline-v2434")/"sales-image-drafts"/"pending-08"/"INFO_FORMULA_01_V2414_EN_V2421_V2434.jpg"
O=Path("v2434b-output");O.mkdir(exist_ok=True)
assert P.exists()
with Image.open(P) as img:
 img=img.convert("RGB");d=ImageDraw.Draw(img)
 # The damaged arc occupies the 835..1026 horizontal region around y341..530.
 # Redraw the original complete circle within the existing uniform information panel.
 color=img.getpixel((775,350))
 d.rectangle((832,332,1038,539),fill=color)
 d.ellipse((835,341,1026,528),outline=(171,177,158),width=3)
 # Restore horizontal decorative divider, extending beneath circle exactly as in original.
 d.line((187,506,892,506),fill=(164,175,158),width=2)
 # Reopen text-area if the line crosses type? text sits y585+, no.
 dst=O/"sales-image-drafts"/"pending-08"/"INFO_FORMULA_01_ornament_repaired_V2434b.jpg"
 dst.parent.mkdir(parents=True,exist_ok=True)
 img.save(dst,"JPEG",quality=95,optimize=True)
 with Image.open(dst) as test:
  test.load();assert test.size==(1080,1080) and test.format=="JPEG" and dst.stat().st_size<2000000
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
result={"version":"2.4.34b","actual_visual_error_corrected":1,"original_v2434_modified":False,
"source_sha":sha(P),"output":str(dst.relative_to(O)),"output_sha":sha(dst),
"new_unique_active_JPG":1,"supersedes":"production-assets-v2434-obge-peripera-drafts/sales-image-drafts/pending-08/INFO_FORMULA_01_V2414_EN_V2421_V2434.jpg",
"status":"SALES_IMAGE_DRAFT","rights_verified":False,"final_qa_approved":False,
"public_URL_changes":0,"note":"Ornamental circle restored on original flat-colored panel; no source photograph edited."}
(O/"v2434b_checkpoint.json").write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result),flush=True)
