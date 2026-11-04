#!/usr/bin/env python3
"""v2565 release-gate batch ledger grounded in 30-family product inventory crosswalk
and physically stored 156 JPEG visual QA contact manifests.
Does not pretend commercial photo rights or stock edition were checked. No XLSX.
"""
import json
from pathlib import Path
X=json.loads(Path("evidence/inventory-30-family-crosswalk-20261104.json").read_text())
R=json.loads(Path("v2565-v2564-gallery/manifest.json").read_text())
assert R["families"]==30 and R["review_jpgs"]==156 and R["sales_ready_groups"]==0
inv={p["family_id"]:p for p in X["pending_families"]}
g={p["family"]:p for p in R["groups"]}
assert len(inv)==len(g)==30 and set(inv)==set(g)
O=Path("v2565-30family-release-hold-and-batch-queue");O.mkdir(exist_ok=True)
specific={
"pending-01":["CUSHION_21_23_25_27_EXACT_EDITION_SHADE_CONFIRMATION"],
"pending-02":["MOIST_UP_21_23_EXACT_STOCK_SHADE_ISSUE","EXTERNAL_WATERMARKED_SWATCH_NOT_LICENSED"],
"pending-03":["MISSHA_BB_OLD_VS_PRO_GENERATION"],
"pending-04":["CLIO_MESH_GLOW_MINI_21N_21C_23N_REAL_SWATCH_REQUIREMENT"],
"pending-05":["CLIO_FOUNWEAR_BUNDLE_EXACT_STOCK_AND_FIVE_SHADES"],
"pending-06":["CLIO_MESH_GLOW_SET_VS_SEPARATE_PUFF_GIFT","CLIO_FIVE_SHADE_STOCK_CHECK"],
"pending-07":["CLIO_MESH_BLUR_NOT_MESH_GLOW","CLIO_THREE_SHADE_STOCK_CHECK"],
"pending-08":["PERIPERA_01_TO_20_ONLY","26AD_EDITION_AND_OFFICIAL_SWATCH_NOT_FINAL"],
"pending-10":["OBGE_HOMME_CUSHION_15G_NOT_WRONG_13G_GENERATION"],
"pending-15":["DRG_GREEN_MILD_OLD_STOCK_EDITION"],
"pending-16":["DRG_2022_RED_BLEMISH_NOT_MODERN_EX"],
"pending-18":["DRG_BRIGHTENING_UP_SUN_PLUS_NOT_MOISTURE_SUN","SPF50_PA_3PLUSES_OLD_EDITION"],
"pending-19":["GOODAL_25AD_ALPHA_GLOBALSELL_EDITION"],
"pending-20":["GOODAL_SERUM_MIST_25AD_NOT_NEW_E_TXA"],
"pending-21":["GOODAL_EYE_25AD_ACTUAL_TUBE_PACK"],
"pending-22":["OBGE_MAX_WATERFUL_300ML_PUMP_NOT_UNRELATED"],
"pending-23":["OBGE_POREZERO_50ML_NOT_150ML"],
"pending-26":["PIXELPURE_145ML_ONLY","REJECT_OFFICIAL_GALLERY_150ML_PHOTOS_02_TO_04","REJECT_SHOPPING_BAG_IMAGE_05"],
}
hard={"CUSHION_21_23_25_27_EXACT_EDITION_SHADE_CONFIRMATION","MOIST_UP_21_23_EXACT_STOCK_SHADE_ISSUE",
"PERIPERA_01_TO_20_ONLY","26AD_EDITION_AND_OFFICIAL_SWATCH_NOT_FINAL",
"OBGE_HOMME_CUSHION_15G_NOT_WRONG_13G_GENERATION",
"PIXELPURE_145ML_ONLY","REJECT_OFFICIAL_GALLERY_150ML_PHOTOS_02_TO_04"}
rows=[]
for family in sorted(g):
    product=inv[family];visual=g[family]
    count=visual["frame_count"]
    options=[v for v in product.get("option_values",[]) if str(v).strip()]
    needs_options=bool(product.get("requires_option_chart",False))
    blocks=["UNVERIFIED_COMMERCIAL_PHOTO_REUSE_RIGHTS",
     "EXACT_OWNED_STOCK_EDITION_NOT_VISUALLY_SIGNED_OFF",
     "ORIGINAL_MELLOWKR_MK_LOGO_UNAVAILABLE",
     "FULL_HUMAN_VISUAL_COPY_CLAIM_REVIEW_PENDING"]+specific.get(family,[])
    priority="P0_EXACT_PRODUCT_OR_SHADE_BLOCK" if any(v in hard for v in specific.get(family,[])) else ("P1_OPTION_CROSSCHECK" if needs_options else "P2_GENERAL_VISUAL_AND_RIGHTS")
    rows.append({"family":family,"product":product["family_name"],"frames":count,
       "option_values":options,"requires_real_source_option_chart":needs_options,
       "approved":False,"priority":priority,"hold_reasons":blocks,
       "latest_delta_slots":visual["latest_delta_slots"],
       "provenance":"catalog+inventory+real-image-QA-manifest; human review not asserted"})
assert sum(x["frames"] for x in rows)==156
assert len(rows)==30 and all(not x["approved"] for x in rows)
q=sorted(rows,key=lambda x:({"P0_EXACT_PRODUCT_OR_SHADE_BLOCK":0,"P1_OPTION_CROSSCHECK":1,"P2_GENERAL_VISUAL_AND_RIGHTS":2}[x["priority"]],x["family"]))
summary={"version":"v2565","baseline_run":41755010679,"scope":30,"JPGs_audited_by_prior_run":156,
 "release_approved_groups":0,"priority_counts":{p:sum(x["priority"]==p for x in rows) for p in ("P0_EXACT_PRODUCT_OR_SHADE_BLOCK","P1_OPTION_CROSSCHECK","P2_GENERAL_VISUAL_AND_RIGHTS")},
 "approved_public_URLs_changed":0,"previous_55_URLs_preserved":True,
 "source_image_bytes_edited":0,"XLSX_created":False,"XLSX_shared":False,
 "readiness_boundary":"Technical JPG checks and visual proof boards are prepared; commercial license, actual stock, original logo and manual QA not complete.",
 "next_work_batch":[x["family"] for x in q[:8]],"products":q}
(O/"release-gates.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
(O/"next-batch.md").write_text("# 30-product release gate and issue-specific work queue\n\n"
+"Technical rendering is NOT commercial release approval. Previously completed 11 public families / 55 URLs remain unchanged.\n\n"
+"| Priority | Product family | Frames | Exact-variant blockers |\n|---|---|---:|---|\n"
+"\n".join(f"| {x['priority']} | {x['family']} {x['product']} | {x['frames']} | {', '.join(specific.get(x['family'],[])) or 'General stock, rights, logo, visual sign-off'} |" for x in q)
+"\n\nNo Excel was produced. Approval must be evidenced separately for each product.\n")
print(json.dumps({"families":len(rows),"images":156,"priority_counts":summary["priority_counts"],"release_approved":0,
"first_batch":summary["next_work_batch"],"published":0},ensure_ascii=False))
