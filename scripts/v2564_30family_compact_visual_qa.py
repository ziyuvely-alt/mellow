#!/usr/bin/env python3
"""v2564 one-pass 30-family compact visual QA boards from immutable v2560 corpus,
overlay ONLY two latest v2563 deltas. No regenerated sales frames or spreadsheets.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import hashlib,json
BASE=Path("v2564-base/review-JPG-by-family")
DELTA=Path("v2564-delta")
OUT=Path("v2564-thirty-family-visual-gallery");OUT.mkdir(exist_ok=True)
CROSS=json.loads(Path("evidence/inventory-30-family-crosswalk-20261104.json").read_text())
inventory={v["family_id"]:v for v in CROSS["pending_families"]}
assert len(inventory)==30
report=json.loads((DELTA/"manifest.json").read_text())
assert report["changed_in_virtual_QA_overlay"]==2 and report["source_image_count"]==156
expected_deltas={(v["family"],v["slot"]):DELTA/(v["family"]+f"-slot{v['slot']:02d}-QA.jpg") for v in report["changes"]}
assert all(p.is_file() for p in expected_deltas.values())
assert len(expected_deltas)==2
fnt=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",23)
fsmall=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",17)
status=[]
seen_deltas=set()
for n in range(1,31):
    family=f"pending-{n:02d}"
    data=inventory[family]
    original=sorted((BASE/family).glob("*.jpg"))
    assert len(original)==(6 if n in (1,2,4,5,6,7) else 5),(family,len(original))
    # Actual JPEGs are shown in their complete content, no invented product pixels.
    board=Image.new("RGB",(1710,1310),"#f5f6f5")
    d=ImageDraw.Draw(board)
    d.text((42,24),family+" /  Product image scene QA  /  "+str(len(original))+" frames",font=fnt,fill="#203c30")
    d.text((42,67),"REVIEW ONLY: not approved for public sales or copied into final URL paths",font=fsmall,fill="#5c6460")
    hashes=[];files=[];applied=[]
    for i,p in enumerate(original):
        slot=int(p.name[:2]);key=(family,slot)
        selected=expected_deltas.get(key,p)
        if key in expected_deltas:
            seen_deltas.add(key);applied.append(slot)
        im=Image.open(selected);im.load()
        assert im.format=="JPEG" and im.size==(1080,1080) and selected.stat().st_size<2_000_000
        h=hashlib.sha256(selected.read_bytes()).hexdigest()
        hashes.append(h);files.append({"slot":slot,"sha256":h,"is_latest_delta":key in expected_deltas})
        thumb=ImageOps.contain(im.convert("RGB"),(510,495),Image.Resampling.LANCZOS)
        col=i%3;row=i//3;x=col*570+30+(510-thumb.width)//2
        y=105+row*576+(495-thumb.height)//2
        board.paste(thumb,(x,y))
        d.text((col*570+42,610+row*576),f"{family} / SLOT {slot:02d}",font=fsmall,fill="#2e3c35")
        if key in expected_deltas:
            d.text((col*570+315,610+row*576),"NEW QA DELTA",font=fsmall,fill="#497662")
    assert len(hashes)==len(set(hashes))
    d.text((43,1270),"Blocked: product edition / photo rights / original MK logo / human content validation",font=fsmall,fill="#6c665b")
    output=OUT/(family+"-all-actual-scenes-QA.jpg")
    board.save(output,"JPEG",quality=82,optimize=True)
    assert output.stat().st_size<2_000_000
    status.append({"family":family,"product":data["family_name"],"frame_count":len(original),"latest_delta_slots":applied,
       "contact_sheet":output.name,"source_files":files,
       "exact_duplicate_hash_count":0,"final_release":"BLOCKED_UNVERIFIED_EDITION_RIGHTS_LOGO_VISUAL"})
assert len(status)==30 and seen_deltas==set(expected_deltas)
manifest={"version":"v2564","source_base_run":41753618979,"source_delta_run":41754796166,
"review_jpgs":156,"families":30,"contact_sheets":30,
"latest_delta_images":len(seen_deltas),"old_originals_recreated":0,
"old_55_verified_public_urls_changed":0,"new_urls_published":0,
"spreadsheet_created_or_shared":False,"technical_all_JPG_pass":True,
"copyright_permissions_verified":False,"physical_edition_verified":False,
"original_mk_logo_verified":False,"sales_ready_groups":0,
"release_status":"VISUAL_REVIEW_GALLERY_ONLY","groups":status}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
(OUT/"review-index.md").write_text("# 30-group full-frame QA gallery (156 real JPGs)\n\n"
+"Every family includes all its actual saved pictures. The two newest deltas appear marked. No public publishing, spreadsheets or final commercial approval.\n\n"
+"| Family | Product | Images | Delta slots |\n|---|---|---:|---|\n"
+"\n".join(f"| {r['family']} | {r['product']} | {r['frame_count']} | {', '.join(map(str,r['latest_delta_slots'])) or '-'} |" for r in status)+"\n")
print(json.dumps({"families":30,"images_referenced":156,"QA_boards_created":30,"new_deltas_applied":len(seen_deltas),"source_public_URL_changed":0}))
