#!/usr/bin/env python3
"""v2572: remove false collision between inventory 26AD edition marker and
shade #026 while preserving source stock and the exact selected #001-#020 scope.
Crosscheck all 20 authored English names with PERIPERA-sponsored Minsco 2026
review lineup; do NOT make a color swatch or claim owned stock physically matched.
"""
import ast,json,re
from pathlib import Path
SRC=Path("scripts/v2539_peripera_exact_20_english_shade_names.py")
INV=Path("evidence/inventory-30-family-crosswalk-20261104.json")
PREV=Path("evidence/v2569-peripera-004-006-007-014-naming-verified-20261104.json")
OUT=Path("v2572-peripera-edition-semantic-preflight")
OUT.mkdir(exist_ok=True)
tree=ast.parse(SRC.read_text())
shade_assignments=[x for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="shades" for t in x.targets)]
assert len(shade_assignments)==1
names=ast.literal_eval(shade_assignments[0].value)
assert len(names)==20
video_names=["Tiny strawberry","Coral chemistry","Juicy peach","Anyway, peach","Baby fairy","Pink youth","Plum fizz","Joking pink","Rose in mind","Bare pink","Visual pink","Campus queen","Mood queen","Rosy wish","My pick rose","Rose-pick","Blush fig","Coral influencer","Cherry so what","Brown yakgwa"]
def normalized(s):return re.sub(r"[^a-z0-9]","",s.casefold())
matched=[normalized(x)==normalized(y) for x,y in zip(names,video_names)]
assert all(matched),[(i+1,x,y) for i,(x,y) in enumerate(zip(names,video_names)) if normalized(x)!=normalized(y)]
stock=json.loads(INV.read_text())
item=next(x for x in stock["pending_families"] if x["family_id"]=="pending-08")
assert len(item["option_values"])==20
assert all(re.match(fr"^{i:03d} ",s) for i,s in enumerate(item["option_values"],1))
assert all("(26AD)" in r["product"] for r in item["inventory_rows"])
assert not any(re.match(r"^0?(?:21|22|23|24|25|26)\b",s) for s in item["option_values"])
old=json.loads(PREV.read_text())
assert old["inventory_product_generation"]=="26AD"
assert old["inventory_scope"]=="001-020 only"
assert "Rosy Wish"==names[13]
status={"version":"v2572","family":"pending-08",
 "product":"PERIPERA Mood Glowy Tint 4g","stock_edition_marker":"26AD",
 "shade_code_number_026":"EXCLUDED_NOT_THE_SAME_AS_26AD",
 "selected_shades":[f"{i:03d}" for i in range(1,21)],
 "published_2026_sponsored_review":"https://www.youtube.com/watch?v=2M3eJESkSac",
 "published_retailer_26AD":"https://m.gsshop.com/prd/prd.gs?prdid=1106843033",
 "20_image_english_names_match_video":True,
 "20_names_verified_count":20,
 "historical_26AD_vs_26_shade_false_equivalence":"RESOLVED_SEMANTIC_DISTINCTION",
 "v2539_existing_option_name_candidate_reused":True,
 "seller_stock_edition_photo_matched":False,
 "source_licensing_confirmed":False,
 "actual_photo_colors_swatch_verified":False,
 "original_mk_logo_recovered":False,
 "public_release_approved":False,
 "existing_156_image_bytes_modified":0,
 "old_55_public_urls_changed":0,
 "xlsx_created_or_shared":False,
 "next":"Do not exclude genuine 26AD inventory solely because 026 shade is excluded. Preserve all 001-020 selected shades, require actual packaging and swatch rights before final image."}
(OUT/"peripera-26AD-vs-026-semantic-resolution.json").write_text(json.dumps(status,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"actual_inventory_edition":"26AD","excluded_shade":"026","english_names_source_match":20,"false_semantic_block_resolved":True,"still_sales_hold":True,"photo_changes":0}))
