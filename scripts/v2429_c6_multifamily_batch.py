#!/usr/bin/env python3
"""Shopee v2.4.29: independent C6 image-source QA, 30-family queue and immutable source check.
No fictional colors, no new public product imagery, no unverified commercial release.
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
import csv, hashlib, json, re, shutil, traceback
from datetime import datetime,timezone

SRC=Path("v2427b-source")
OLD=Path("v2428-source")
OUT=Path("v2429-output")
OUT.mkdir(exist_ok=True)
ROOT=SRC/"immutable-v2426b"/"originals-v2425-unchanged"/"prior-immutable"/"immutable-prev"/"preserved-v2422"
assert SRC.exists() and OLD.exists() and ROOT.exists()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def qa(p):
    with Image.open(p) as im:
        im.load()
        return {"path":str(p),"sha256":sha(p),"format":im.format,"pixels":[im.width,im.height],"bytes":p.stat().st_size,"jpg_spec_ok":im.format=="JPEG" and im.size==(1080,1080) and p.stat().st_size<2_000_000}
def font(size,bold=False):
    dirs=["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    return ImageFont.truetype(dirs[0],size)
def contact_sheet(paths,dest,title,sub):
    # Not a swatch: real existing source image contact sheet for operator QA.
    im=Image.new("RGB",(1080,1080),(247,245,241)); d=ImageDraw.Draw(im)
    d.text((42,33),title,font=font(29,True),fill=(40,48,45))
    d.text((42,80),sub,font=font(19),fill=(85,89,83))
    d.line((42,125,1038,125),fill=(190,187,177),width=2)
    for i,p in enumerate(paths[:4]):
        x=42+(i%2)*506; y=154+(i//2)*427
        with Image.open(p) as a:
            a=ImageOps.contain(a.convert("RGB"),(478,350),Image.Resampling.LANCZOS)
            im.paste(a,(x+(478-a.width)//2,y+(350-a.height)//2))
        d.text((x,y+355),p.name[:43],font=font(15),fill=(75,76,75))
    d.text((42,1020),"Existing photographed JPGs only | internal source review",font=font(16),fill=(85,89,83))
    im.save(dest,"JPEG",quality=90,optimize=True)
    return qa(dest)
C6=[
 ("pending-01","MISSHA Magic Cushion Cover Lasting",4,"21 excluded from swatch; keep original SKU"),
 ("pending-02","MISSHA Magic Cushion Moist Up",2,"21 separately review"),
 ("pending-05","CLIO Kill Cover Founwear Special Set",5,"kit and edition check needed"),
 ("pending-06","CLIO Mesh Glow Essential Special Set",5,"kit and edition check needed"),
 ("pending-07","CLIO Mesh Blur Special Set",3,"kit and edition check needed"),
 ("pending-08","Peripera Mood Glowy Tint",20,"26AD vs original 01-20 unresolved; 04/06/07,12 conflict")
]
C8=[x[0] for x in C6]+["pending-04","pending-10"]
pre=sorted(p for p in SRC.rglob("*.jpg") if p.is_file())
prehash={str(p.relative_to(SRC)):sha(p) for p in pre}
assert len(prehash)>=531, "source lost existing JPG"
original_status=SRC/"immutable-v2426b"/"C8_45_options_v2426_verified_status.csv"
assert original_status.is_file()
with original_status.open(encoding="utf-8-sig",newline="") as f: records=list(csv.DictReader(f))
assert len(records)==45
from collections import Counter
counts=Counter(row["family_id"] for row in records)
assert sum(counts.values())==45
baseline=OLD/"v2428_checkpoint.json"
assert baseline.exists() and json.loads(baseline.read_text())["version"]=="2.4.28"
official={
 "pending-01":[],
 "pending-02":[],
 "pending-05":[{"url":"https://clubclio.co.kr/shop/goodsView/0000006670","evidence":"Official page lists 19C/19N/21C/21N/23N and newer options; kit-generation correspondence not established"}],
 "pending-06":[{"url":"https://clubclio.co.kr/shop/goodsView/6182","evidence":"Official mesh glow essential kit listed; 15g*2 combinations; precise shade photo not established"}],
 "pending-07":[{"url":"https://clubclio.co.kr/shop/goodsList/120701000000000","evidence":"Official mesh blur kit listed; color-photo option evidence unresolved"}],
 "pending-08":[],
}
# Each family gets an actual 1080x1080 source-photo contact QA JPG, never a fake shade chart.
family_results=[]
created=[]
for fid,name,expected,issue in C6:
    step={"group_id":fid,"name":name,"expected_skus":expected,"actual_skus":counts.get(fid,0),"initial_state":"QUEUED","current_state":"SOURCE_SEARCH","official_evidence":official[fid],"blockers":[],"qa_jpg":[],"next_action":None}
    try:
        assert counts[fid]==expected
        candidates=[]
        for segment in ["en-photo-captions","en-hero-fixed","en-customer-drafts","originals-immutable/preserved-pending-originals"]:
            folder=ROOT/segment/fid
            if folder.is_dir(): candidates += sorted(folder.glob("*.jpg"))
        chosen=[]; seen=set()
        for x in candidates:
            if sha(x) not in seen:
                chosen.append(x);seen.add(sha(x))
        step["existing_jpg_found"]=len(chosen)
        if chosen:
            op=OUT/(fid+"_real_source_contact_QA_V2429.jpg")
            q=contact_sheet(chosen,op,name[:46],"Existing photos / NO shade match or resale approval")
            assert q["jpg_spec_ok"]
            created.append(q)
            step["qa_jpg"].append(q)
            step["current_state"]="SOURCE_QA_HOLD"
        else:step["current_state"]="SOURCE_QA_HOLD"
        step["blockers"]=["SHADE_EVIDENCE_REQUIRED","COMMERCIAL_REUSE_PERMISSION_REQUIRED",issue]
        step["next_action"]="Verify exact official swatch photograph and generation/edition; do not make customer 6th shade JPG from approximations"
    except Exception as e:
        step["current_state"]="SOURCE_QA_HOLD"; step["blockers"].append("EXECUTION_ERROR:"+type(e).__name__);step["next_action"]=str(e)[:180]
    family_results.append(step)
# Additional B/D photo QA: choose actual stored existing non-C8 source frames, without guessing grade.
all_families=sorted({m.group(1) for p in pre if (m:=re.search(r"(pending-\d+)",str(p)))})
non_c8=[x for x in all_families if x not in C8]
extra=[]
for fid in non_c8[:8]:
    candidates=sorted(p for p in pre if "/"+fid+"/" in "/"+str(p.relative_to(SRC)) and "/originals-immutable/" in str(p))
    if not candidates: candidates=sorted(p for p in pre if "/"+fid+"/" in "/"+str(p.relative_to(SRC)))
    if candidates:
        extra.append({"id":fid,"sources":[{"path":str(p.relative_to(SRC)),"sha256":sha(p)} for p in candidates[:2]],"state":"VISUAL_QA","grade":"UNKNOWN_FROM_AVAILABLE_EVIDENCE"})
# Expand queue exclusively from real pending ids, if fewer than 30 do not fabricate IDs.
queue=[]
for fid in all_families:
    known=next((x for x in family_results if x["group_id"]==fid),None)
    queue.append({"group_id":fid,"state":known["current_state"] if known else "QUEUED","known_grade":"C" if fid in C8 else "UNKNOWN","source":"existing GitHub pending-id path"})
no_reconstruction=30-len(queue)
with (OUT/"work_queue.json").open("w",encoding="utf-8") as f: json.dump({"expected_incomplete":30,"recovered_unique_ids":len(queue),"unresolved_ids_count":max(0,no_reconstruction),"queue":queue},f,indent=2,ensure_ascii=False)
for x in family_results:
    (OUT/(x["group_id"]+"_checkpoint.json")).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding="utf-8")
with (OUT/"C6_execution.json").open("w",encoding="utf-8") as f:json.dump(family_results,f,indent=2,ensure_ascii=False)
with (OUT/"BD_photo_audit_queue.json").open("w",encoding="utf-8") as f:json.dump(extra,f,indent=2,ensure_ascii=False)
shutil.copy2(original_status,OUT/"C8_45_options_UNMODIFIED.csv")
assert sha(original_status)==sha(OUT/"C8_45_options_UNMODIFIED.csv")
assert {str(p.relative_to(SRC)):sha(p) for p in pre}==prehash
report={"version":"2.4.29","timestamp_utc":datetime.now(timezone.utc).isoformat(),
 "source_v2428":"production-assets-v2428-multifamily-qa","source_v2427b":"production-assets-v2427b-obge-shade-clean",
 "C6_groups_attempted":6,"C6_groups_source_photo_QA_completed":sum(bool(x["qa_jpg"]) for x in family_results),
 "new_shade_JPG":0,"new_JPG_total":len(created),"new_customer_ready_JPG":0,
 "grade_BD_photo_groups_queued":len(extra),"30_group_ids_recovered":len(queue),"30_group_ids_not_found":max(0,no_reconstruction),
 "global_sku_records_preserved":len(records),"source_JPG_preserved":len(prehash),
 "source_JPG_sha_unchanged":True,"live_urls_mutated":0,"live_urls_network_verified":False,
 "peripera_generation_resolved":False,"missha_cover_21_excluded_from_chart":True,
 "commercial_image_license_verified":0,"MK_original_binary_recovered":False,
 "FINAL_QA_APPROVED":0,"READY_EXCEPT_LOGO":0,
 "created_QA_files":created,"next_restart":"pending-01 official color photo evidence, then pending-02, pending-05/06/07, pending-08; source-verified options only; next unknown grade photo queue"
}
(OUT/"v2429_checkpoint.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps({k:v for k,v in report.items() if k!="created_QA_files"},ensure_ascii=False),flush=True)
