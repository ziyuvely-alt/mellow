#!/usr/bin/env python3
"""v2835: Check whether the two high native-resolution 21N image references
are *actually variant-exclusive* rather than Shopify shared/all-shade images.
No duplicate photo production and no item publishing.
"""
from pathlib import Path
from urllib.parse import urlparse,unquote
from collections import defaultdict
import requests,json,hashlib
ROOT=Path("qa-review")
OLD=ROOT/"v2834-clio-meshglow-mini-21N-high-native-resolution-source-probe"
OUT=ROOT/"v2835-clio-mini-21N-merchant-variant-image-assignment-audit"
assert OLD.is_dir() and not OUT.exists()
OUT.mkdir()
base=json.loads((OLD/"manifest.json").read_text())
assert base["higher_native_source_count"]==2
target_url_by_merchant={x["merchant"]:x["url"] for x in base["qualified_higher_native_reference_photos"]}
SOURCES=[
 ("W Cosmetics Australia","https://wcosmetics.com.au/products/clio-kill-cover-mesh-glow-essential-cushion-mini.js"),
 ("La Cosmetique Australia","https://lacosmetique.com.au/products/kill-cover-mesh-glow-essential-cushion-mini-3-shades.js")
]
records=[]
for merchant,url in SOURCES:
 entry={"merchant":merchant,"catalog_url":url,"family":"pending-04",
   "product":"CLIO Mesh Glow Essential MINI 5g","status":"HOLD_CATALOG_ACCESS"}
 try:
  r=requests.get(url,headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"},timeout=17)
  r.raise_for_status();j=r.json()
  title=str(j.get("title",""))
  assert "mesh glow" in title.lower() and "mini" in title.lower(),title
  rows=[]
  for v in j.get("variants",[]):
   image=v.get("featured_image") or v.get("image")
   image_url=image.get("src","") if isinstance(image,dict) else (image if isinstance(image,str) else "")
   if image_url.startswith("//"):image_url="https:"+image_url
   rows.append({"shade_title":v.get("title"),"variant_id":v.get("id"),"sku":v.get("sku"),"linked_photo_url":image_url})
  matching=[x for x in rows if "21n" in str(x["shade_title"]).lower() or "linen" in str(x["shade_title"]).lower()]
  other=[x for x in rows if x not in matching]
  seen=target_url_by_merchant.get(merchant,"")
  # URLs are compared exactly as fetched and retained in v2834 manifest.
  matches=[x for x in matching if x["linked_photo_url"]==seen]
  other_matches=[x for x in other if x["linked_photo_url"]==seen]
  no_link_others=[x for x in other if not x["linked_photo_url"]]
  entry.update({"status":"SHADE_LINK_AUDIT_COMPLETE",
    "catalog_product_title":title,"all_variant_rows":rows,
    "total_variants":len(rows),"21N_variant_rows":len(matching),
    "21N_exact_saved_photo_link_matches":len(matches),
    "other_variant_rows_sharing_same_photo":len(other_matches),
    "other_variant_rows_without_image_link":len(no_link_others),
    "photo_uniquely_mapped_to_21N_in_available_catalog":bool(matches) and not other_matches,
    "strong_standalone_21N_image_evidence":bool(matches) and not other_matches and not no_link_others,
    "warning":"Shopify featured_image is a merchant catalog pointer; even an exclusive link does not prove 5g stock packaging or photo use rights."})
 except Exception as exc:
  entry.update({"status":"HOLD_CATALOG_ACCESS_OR_WRONG_PRODUCT",
                "error_type":type(exc).__name__,"error":str(exc)[:200]})
 records.append(entry)
lines=["# v2835 CLIO Mesh Glow Essential Mini 5g 21N source mapping","",
"**Internal QA only**. Source image rights and actual owned-stock edition remain unverified.",
"",
"| Merchant | 21N link | Same image reused by other shades | Missing links in other variants | Evidence |",
"|---|---|---:|---:|---|"]
for x in records:
 lines.append(f"| {x['merchant']} | {x.get('21N_exact_saved_photo_link_matches','?')} | {x.get('other_variant_rows_sharing_same_photo','?')} | {x.get('other_variant_rows_without_image_link','?')} | {x['status']} |")
lines.extend(["","Do not substitute 21N low-res hero with a generic shared photo or a Founwear Original Mini 5g image.",
"Retain the higher native media only as photo references until the physical stock and rights conditions are met."])
(OUT/"audit.md").write_text("\n".join(lines)+"\n")
report={
 "version":"v2835","baseline":"v2834","family":"pending-04",
 "task":"21N Linen 5g high native source shade-scoped Shopify variant-link audit",
 "merchant_results":records,
 "photo_JPGs_reencoded_or_regenerated":0,
 "source_21N_480px_retained_as_previous_reference":True,
 "v2834_two_higher_native_photo_references_untouched":True,
 "new_retail_approved":0,
 "actual_owned_stock_edition_confirmed":False,
 "photo_reuse_rights_verified":False,
 "authentic_original_MK_logo_confirmed":False,
 "11_approved_families_unchanged":True,
 "55_published_urls_unchanged":True,
 "final_xlsx_shared":False
}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2835","merchants_checked":len(records),
 "reports":[{"merchant":x["merchant"],"status":x["status"],"exclusive":x.get("photo_uniquely_mapped_to_21N_in_available_catalog"),"strong":x.get("strong_standalone_21N_image_evidence")} for x in records],
 "retail_approved":0}))
