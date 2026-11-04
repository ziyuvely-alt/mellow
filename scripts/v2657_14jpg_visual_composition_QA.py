#!/usr/bin/env python3
"""v2657: selective cropping risk and framed-image QA of v2656 consolidated
14 original candidates. Immutable inputs. No OCR or claims of human visual review.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageStat,ImageFilter
import json,hashlib,statistics
IN=Path("source/v2656");OUT=Path("v2657-visual-composition-QA");OUT.mkdir(exist_ok=True)
manifest=json.loads((IN/"manifest.json").read_text())
assert manifest["version"]=="v2656" and len(manifest["files"])==14
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
results=[];thumbs=[]
for r in manifest["files"]:
 p=IN/r["file"]
 assert p.exists() and digest(p)==r["sha256"]
 with Image.open(p) as im:
  im.load(); assert im.format=="JPEG" and im.size==(1080,1080)
  image=im.convert("RGB")
 gray=ImageOps.grayscale(image)
 # Frame-risk heuristic: unusually sharp horizontal/vertical internal rectangle lines.
 # Thresholds produce REVIEW flags, not confident conclusions.
 edges=gray.filter(ImageFilter.FIND_EDGES)
 bands={}
 for side,rect in {"top":(40,65,1040,85),"bottom":(40,995,1040,1015),
                   "left":(65,40,85,1040),"right":(995,40,1015,1040)}.items():
  bands[side]=round(ImageStat.Stat(edges.crop(rect)).mean[0],2)
 overall=ImageStat.Stat(gray).stddev[0]
 high_bands=[k for k,v in bands.items() if v>=28]
 # Clipping risk is only a visual proxy: candidates are enlarged source regions.
 flag="REVIEW_BORDER_OR_CUT_LABEL_RISK" if high_bands or overall<18 else "COMPOSITION_REVIEW_REQUIRED"
 result={"family":r["family"],"file":p.name,"sha256":r["sha256"],"bytes":p.stat().st_size,
         "edge_strength_by_border_region":bands,"image_grayscale_stddev":round(overall,2),
         "elevated_edge_regions":high_bands,"heuristic":flag,
         "real_product_visibility_confirmed":False,
         "text_not_clipped_confirmed":False,
         "commercial_rights_verified":False,"latest_v2647_crosscheck":False}
 results.append(result)
 # Read-only contact-sheet with labels outside the original images
 thumbs.append((r["family"],p.name,image.resize((380,380),Image.Resampling.LANCZOS),flag))
for offset in (0,8):
 batch=thumbs[offset:offset+8]
 if not batch:continue
 board=Image.new("RGB",(1640,1000),"#f2f3f5")
 d=ImageDraw.Draw(board)
 d.text((20,12),"v2657 QA CONTACT SHEET | ORIGINAL HISTORICAL CROPS, NOT RETAIL APPROVED",fill="#111111")
 for k,(family,name,thumb,flag) in enumerate(batch):
  col=k%4;row=k//4;x=10+col*410;y=50+row*470
  board.paste(thumb,(x,y))
  d.text((x,y+385),family+" | "+name[:31],fill="#111111")
  d.text((x,y+410),flag[:36],fill="#a02222" if flag.startswith("REVIEW_BORDER") else "#333333")
 board.save(OUT/f"v2657-contact-sheet-{offset//8+1}.jpg",quality=90,optimize=True)
data={"version":"v2657","source":"v2656 immutable 14 candidate QA JPEG package",
 "sha256_preserved":14,"review_candidates":len(results),
 "elevated_border_edge_heuristic":sum(bool(x["elevated_edge_regions"]) for x in results),
 "low_contrast_images":sum(x["image_grayscale_stddev"]<18 for x in results),
 "human_visual_review_done":False,
 "image_content_or_product_identity_verified":False,
 "known_defects_confirmed":0,
 "candidates_replaced":0,"retail_approved":0,
 "limitations":["Edge heuristic may flag real product lines and miss incorrect text",
                "Contact sheets are QA previews of historic v2593 crops only",
                "No claim of packaging, photo rights or current v2647 match"],
 "results":results,"comparison_sheets":["v2657-contact-sheet-1.jpg","v2657-contact-sheet-2.jpg"],
 "prior_approved_11_unchanged":True,"verified_55_urls_unchanged":True,"xlsx_shared":False}
(OUT/"v2657-review.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"reviewed":len(results),
 "edge_risk_flags":data["elevated_border_edge_heuristic"],
 "low_contrast_flags":data["low_contrast_images"],"contact_sheets":2,
 "approved":0,"public_mutations":0},ensure_ascii=False))
