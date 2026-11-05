#!/usr/bin/env python3
"""Immutable release-preflight for all 30 remaining stock families.
Checks actual QA ZIP bytes for current six nearest-ready families, maintains
product generation, photo rights, physical stock and true MK gates separately.
Never modifies customer public images, does not deploy to Render.
"""
import io,json,zipfile,hashlib
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa-review/v2968-30-family-real-zip-integrity-and-no-repeat-gate-20261106"
M={
 "v2966":"qa-review/v2966-30-family-post-production-evidence-and-restart-ledger-20261106/manifest.json",
 "v2967":"qa-review/v2967-bioheal-cream50-two-distinct-alternative-scenes-20261106/manifest.json",
 "v2954":"qa-review/v2954-three-family-five-original-JPG-byteexact-ZIPs-20261106/manifest.json",
 "v2957":"qa-review/v2957-goodal-25AD-label-generation-split-and-hard-publish-gate-20261106/manifest.json",
 "v2965":"qa-review/v2965-bioheal-alpha-repair-and-four-family-gate-20261106/manifest.json"
}
def sha(data):return hashlib.sha256(data).hexdigest()
def fetch(path):return json.loads((ROOT/path).read_text(encoding="utf8"))
def audit_zip(path,expected):
    p=ROOT/path
    raw=p.read_bytes()
    if sha(raw)!=expected:raise ValueError("Immutable ZIP SHA256 no longer matches manifest: "+path)
    frames=[]
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        invalid=z.testzip()
        if invalid:raise ValueError("ZIP CRC failure "+path+" "+invalid)
        files=[x for x in z.infolist() if not x.is_dir() and x.filename.lower().endswith((".jpg",".jpeg"))]
        for entry in files:
            blob=z.read(entry.filename)
            with Image.open(io.BytesIO(blob)) as im:
                im.load()
                info={"name":entry.filename,"sha256":sha(blob),"bytes":len(blob),
                      "dimensions":list(im.size),"format":im.format,
                      "meets_1080_2MB_JPEG":im.format=="JPEG" and im.size==(1080,1080) and len(blob)<2_000_000}
            frames.append(info)
    return {"zip":path,"zip_sha256":expected,"zip_bytes":len(raw),"JPG_count":len(frames),
            "all_JPG_1080_under2MB":all(x["meets_1080_2MB_JPEG"] for x in frames),
            "exact_duplicate_JPG_hashes":len({x["sha256"] for x in frames})!=len(frames),
            "frames":frames,"CRC_pass":True}
def main():
    if OUT.exists():raise SystemExit("v2968 exists, no repeat")
    j={k:fetch(v) for k,v in M.items()}
    roster=j["v2966"]["family_lanes"]
    if len(roster)!=30 or len(set(r["family_id"] for r in roster))!=30:
        raise ValueError("30-family roster changed unexpectedly")
    zips={}
    v2954=j["v2954"]
    byfam={q["family"]:q for q in v2954["results"]} if "results" in v2954 else v2954["families"]
    for family in ("pending-23","pending-28"):
        r=byfam[family]
        zips[family]=audit_zip(r.get("byte_exact_zip"),r.get("zip_sha256"))
    q=j["v2965"]["family_evidence"]
    for family in ("pending-27","pending-29","pending-30"):
        zips[family]=audit_zip(q[family]["QA_zip"],q[family]["QA_zip_sha256"])
    b=j["v2967"]
    if not b.get("new_five_photo_QA_ZIP"): raise ValueError("v2967 actual fifth candidate missing")
    zips["pending-25"]=audit_zip(b["new_five_photo_QA_ZIP"],b["new_ZIP_SHA256"])
    if any(v["JPG_count"]!=5 or not v["all_JPG_1080_under2MB"] for v in zips.values()):
        raise ValueError("One family is technically incomplete; keep archive and report error rather than publishing")
    goodal={name:audit_zip(info["zip"],info["zip_sha256"]) for name,info in j["v2957"]["groups"].items()}
    if [goodal[k]["JPG_count"] for k in ("LABEL_A","LABEL_B")]!=[3,2]:
        raise ValueError("Goodal A/B label groups were inadvertently mixed")
    if len({f["sha256"] for row in goodal.values() for f in row["frames"]})!=5:
        raise ValueError("Goodal original-frame hash collision detected")
    priority=[]
    for row in roster:
        family=row["family_id"]
        technical=zips.get(family)
        if family=="pending-20":
            stage="HOLD_FRONT_LABEL_GENERATION_CONFLICT"; archived=5; independent=False
        elif family=="pending-25":
            stage="QA_5_FILE_BYTE_VALID_FOUR_SCENE_CANDIDATE_RIGHTS_HOLD"
            archived=5;independent=False
        elif technical:
            stage="QA_5_FILE_BYTE_VALID_RETAIL_PROVENANCE_HOLD"; archived=5;independent=None
        else:
            stage=row["production_stage"]; archived=None;independent=None
        blocked=["PHYSICAL_STOCK_EDITION_UNVERIFIED","COMMERCIAL_PHOTO_REUSE_PERMISSION_UNVERIFIED","AUTHENTIC_MELLOWKR_MK_ORIGINAL_BINARY_NOT_ACCESSIBLE","CUSTOMER_CLEAN_FINAL_FRAME_NOT_APPROVED"]
        if family=="pending-20":blocked.insert(0,"MIXED_FRONT_LABELS_A_VS_B")
        if family=="pending-25":blocked.insert(0,"NEAR_DUPLICATE_OR_RELATED_PRODUCT_VIEW_1_2_AND_3_5")
        priority.append({
          "family_id":family,"product":row["product"],"production_stage":stage,
          "source_photo_count":archived,
          "verified_five_independent_scenes":independent,
          "technical_zip_audited_this_run":bool(technical),
          "publication":"HOLD_NOT_APPROVED",
          "release_gate_missing":blocked,
          "next_action":row.get("next_action"),
          "skip_more_source_search_if_stock_and_rights_blocked":family in ["pending-23","pending-27","pending-28","pending-29","pending-30"]
        })
    label_evidence={
       "source_name":"YesStyle product listing '2025 Version - 100ml'",
       "source_page":"https://www.yesstyle.com/en/goodal-green-tangerine-vita-c-serum-mist-100ml/info.html/pid.1136600635",
       "source_bundle":"https://www.yesstyle.com/en/goodal-green-tangerine-vita-c-serum-mist-2pcs-bundle-set-2025-version/info.html/pid.1137843407",
       "seller_photo_link":"https://d1flfk77wl2xk4.cloudfront.net/Assets/goodal-green-tangerine-vita-c-serum-mist-2pcs-bundle-set-100ml-x-2-pcs/01/055/XXL_p0225005501.jpg",
       "observed_label":"LABEL_A: SERUM MIST / NIACINAMIDE / HYALURONIC ACID",
       "evidence_strength":"EXTERNAL_RETAIL_2025_VERSION_PHOTO_SUPPORTS_LABEL_A_CANDIDACY",
       "does_not_prove":"actual user's owned 25AD stock bottle or exclusion of different packaging batches",
       "current_brand_official_product":"https://clubclio.co.kr/shop/goodsView/0000003795",
       "official_brand_text_says_100ml":True,
       "official_product_page_visible_label_cross_verified":False,
       "do_not_use_mixed_A_B_images":True
    }
    result={"version":"v2968","checkpoint_base":"v2967","project":"Shopee Thumbnail Creator PRO, 82 SKUs/41 groups, 30 pending",
      "audit_scope":"6 independently staged 5-JPG internal QA ZIPs plus 2 separate Goodal label group ZIPs",
      "source_JPGs_examined_in_zip":sum(x["JPG_count"] for x in zips.values())+sum(x["JPG_count"] for x in goodal.values()),
      "tech_pass_five_JPG_families":list(zips.keys()),
      "byte_exact_preserved":True,"retail_source_authentication_checked":False,
      "zip_audits":zips,"goodal_split_integrity":goodal,
      "goodal_2025_version_label_evidence":label_evidence,
      "family_release_roster":priority,
      "remaining_families_count":30,
      "existing_11_published_preserved":True,"existing_55_verified_URLs_preserved":True,
      "new_sales_approved":0,"new_anonymous_render_URLs_verified":0,
      "previous_QA_ZIPs_overwritten":0,"new_customer_JPGs":0,
      "critical_blocker":"Commercial source-photo rights and physical stock/variant plus authenticated original MK binary. No public deployment attempted.",
      "do_not_repeat":["v2957 A-B product label split","v2967 Bioheal candidate image lookup","v2954/v2958/v2961/v2963/v2965 old successful ZIP creation","historical 55 previously verified URLs"],
      "next_exec":["Prioritize usable assets from pending23/28/27/29/30; do not source more photos until rights and true MK accessible","Resolve actual Goodal A/B 25AD stock identity; external 2025 listing supports A only tentatively","Bioheal pending25 scene 1/2 similar, replacement needed only with rights-cleared source","Once seller assets legally approved and MellowKR original MK available, generate retail JPGs in a new version path and verify anonymous SHA256"],
      "final_excel_shared":False
    }
    OUT.mkdir(parents=True)
    (OUT/"manifest.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    (OUT/"release-blocker-matrix.json").write_text(json.dumps(priority,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"version":"v2968","verified_5photo_families":len(zips),
                      "zip_JPGs_inspected":result["source_JPGs_examined_in_zip"],
                      "Goodal_A_B":[goodal["LABEL_A"]["JPG_count"],goodal["LABEL_B"]["JPG_count"]],
                      "frozen_legacy_URLs":55,"new_public":0}))
if __name__=="__main__":main()
