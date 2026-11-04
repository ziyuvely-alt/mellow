#!/usr/bin/env python3
"""v2729: new alpha-shape QA for 18 existing valid photo cutouts.

Read v2722's already-verified candidate file paths. Do NOT regenerate
or revalidate all 32 image pairs. Score foreground fragmentation,
large detached islands, source-like rectangular masks and edge-strip contact.
Produce 3 contact sheets showing the saved transparent PNGs on checkerboard.
Warnings are review prompts, not proof that retail use is licensed.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import numpy as np, cv2, json, hashlib, base64

ROOT=Path("qa-review")
BASE=ROOT/"v2722-thirty-family-file-backed-cutout-queue"/"manifest.json"
OUT=ROOT/"v2729-eighteen-accepted-masks-foreground-integrity-QA"
assert BASE.is_file() and not OUT.exists()
OUT.mkdir(parents=True)
m=json.loads(BASE.read_text())
selected=[r for r in m["source_status_by_family"] if r["review_status"]=="QA_CANDIDATE"]
assert len(selected)==18,len(selected)
font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
fn=lambda n,b=False:ImageFont.truetype(bold if b else font,n)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
scores=[]
for item in selected:
    fid=item["family"]
    spec=item["selected_QA_pair"]
    assert spec and spec["physical_pair_valid"],fid
    png=ROOT/spec["folder"]/spec["png_relative_path"]
    jpg=ROOT/spec["folder"]/spec["jpg_relative_path"]
    assert png.is_file() and jpg.is_file(),fid
    with Image.open(png) as x:
        x.load()
        assert x.mode=="RGBA",fid
        data=np.asarray(x.convert("RGBA")).copy()
    with Image.open(jpg) as x:
        x.load()
        assert x.format=="JPEG" and x.size==(1080,1080) and jpg.stat().st_size<2_000_000
    alpha=data[:,:,3]
    h,w=alpha.shape
    binary=np.uint8(alpha>=128)
    n,labels,stats,center=cv2.connectedComponentsWithStats(binary,8)
    regions=sorted([{"id":i,"area":int(stats[i,cv2.CC_STAT_AREA]),
        "bbox":[int(stats[i,0]),int(stats[i,1]),int(stats[i,2]),int(stats[i,3])]}
        for i in range(1,n) if stats[i,cv2.CC_STAT_AREA]>=40],
        key=lambda r:r["area"],reverse=True)
    assert regions,fid
    foreground=int(binary.sum())
    largest=regions[0]["area"]
    other=sum(x["area"] for x in regions[1:])
    detached_ratio=round(other/max(1,foreground),5)
    edge_contact={
        "top":round(float(binary[0,:].mean()),4),
        "bottom":round(float(binary[-1,:].mean()),4),
        "left":round(float(binary[:,0].mean()),4),
        "right":round(float(binary[:,-1].mean()),4),
    }
    opaque=float(np.mean(alpha>=248))
    soft=float(np.mean((alpha>10)&(alpha<248)))
    # A highly rectangular foreground mask with a large fraction of the
    # top/bottom/left/right edge covered can be a panel rather than a cutout.
    # Cropping exact alpha bbox naturally touches some sides; never flag
    # a small edge contact alone as clipping.
    warnings=[]
    if detached_ratio>.025:
        warnings.append("SIGNIFICANT_DETACHED_ALPHA_ISLANDS")
    elif detached_ratio>.007:
        warnings.append("MINOR_DETACHED_FRAGMENTS_CHECK")
    if any(v>.26 for v in edge_contact.values()):
        warnings.append("BROAD_MASK_TOUCHES_OUTPUT_EDGE_REVIEW")
    if foreground/(w*h)>.84:
        warnings.append("MASK_TOO_RECTANGULAR_OR_FILLING_FRAME")
    if max(edge_contact.values())>.7:
        warnings.append("LIKELY_BACKGROUND_PANEL_RETAINED")
    scores.append({
        "family":fid,
        "png_file":str(png),"png_sha256":sha(png),
        "jpg_file":str(jpg),"jpg_sha256":sha(jpg),
        "foreground_dimensions":[w,h],
        "foreground_fraction":round(foreground/(w*h),4),
        "opaque_fraction":round(opaque,4),
        "semi_transparent_fraction":round(soft,4),
        "component_count_area_ge_40":len(regions),
        "main_component_area":largest,
        "secondary_components_area":other,
        "secondary_components_ratio":detached_ratio,
        "top_three_components":regions[:3],
        "alpha_edge_contact":edge_contact,
        "warnings":warnings,
        "technical_category":"MASK_STRUCTURE_REVIEW_REQUIRED" if warnings else "MASK_STRUCTURE_NO_MAJOR_FLAG",
        "human_visual_qa_from_prior":item["visual_review_basis"],
        "retail_approved":False,
    })
assert len(scores)==18
# Preview alpha on checkerboard, not a false solid rectangle. No product
# photo pixel edits. Mark flagged candidates but do not modify their media.
for page in range(3):
    subset=scores[page*6:(page+1)*6]
    w=1490;h=1110
    contact=Image.new("RGB",(w,h),"#f3f1f1")
    draw=ImageDraw.Draw(contact)
    draw.text((19,14),f"v2729 ALPHA SOURCE-QA PAGE {page+1}/3 | 18 CANDIDATES | NO RETAIL RELEASE",
              font=fn(24,True),fill="#262426")
    for ix,rec in enumerate(subset):
        col=ix%3;row=ix//3
        tx=20+col*492;ty=68+row*525
        # Actual checkerboard displays mask quality and transparent edges.
        tile=Image.new("RGBA",(425,425),"white")
        td=ImageDraw.Draw(tile)
        for y in range(0,425,32):
            for x in range(0,425,32):
                if (x//32+y//32)%2:td.rectangle((x,y,x+31,y+31),fill="#e9e7e8")
        with Image.open(rec["png_file"]) as cut:
            foreground=ImageOps.contain(cut.convert("RGBA"),(390,390),Image.Resampling.LANCZOS)
        tile.alpha_composite(foreground,((425-foreground.width)//2,(425-foreground.height)//2))
        contact.paste(tile.convert("RGB"),(tx,ty))
        draw.text((tx+2,ty+428),rec["family"]+" | "+("FLAGGED" if rec["warnings"] else "MASK OK"),
                  font=fn(21,True),fill="#52353f")
        draw.text((tx+2,ty+460),"Detached "+str(round(rec["secondary_components_ratio"]*100,2))+"%  /  islands "+str(rec["component_count_area_ge_40"]),
                  font=fn(18),fill="#575057")
    proof=OUT/f"v2729-alpha-checkerboard-page-{page+1}.jpg"
    contact.save(proof,"JPEG",quality=85,optimize=True)
    (OUT/f"v2729-proof-page-{page+1}.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
report={
 "version":"v2729",
 "baseline":"v2728 latest completed workflow; v2723 stored 32 pair audit",
 "operation":"NEW_COMPONENT_AND_EDGE_ALPHA_ANALYSIS_FROM_18_EXISTING_PNGS",
 "distinct_product_families_analyzed":18,
 "original_PNG_or_JPG_files_modified":0,
 "new_product_images_generated":0,
 "checkerboard_QA_contact_sheets":3,
 "warning_families":[r["family"] for r in scores if r["warnings"]],
 "quiet_mask_families":[r["family"] for r in scores if not r["warnings"]],
 "visually_false_positive_possible":True,
 "manual_review_still_needed":True,
 "missing_original_authenticated_MK_logo_in_runtime":True,
 "commercial_licensing_and_real_stock_editions_still_unverified":True,
 "previous_approved_11_families_modified":False,
 "previous_55_public_URLs_modified":False,
 "new_retail_approved_count":0,
 "do_not_repeat":{
   "pending_13_older_source03_photo":"Already used in v2697 frame02; v2728 rembg clipped; DO NOT replicate original scene.",
   "preserve_older_photo_sets":True},
 "final_excel_or_sheets_shared":False,
 "results":scores
}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2729","scored":len(scores),
 "warning_families":report["warning_families"],
 "quiet_mask_families":report["quiet_mask_families"],
 "commercial_approvals":0}))
