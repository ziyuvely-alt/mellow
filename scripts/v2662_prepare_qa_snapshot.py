#!/usr/bin/env python3
"""Stage exactly 14 previously created JPGs for immutable GitHub QA-only branch."""
from pathlib import Path
import hashlib,json,shutil
SOURCE=Path("source/v2656")
OUTPUT=Path("qa-review/v2662-14-candidate-snapshot")
record=json.loads((SOURCE/"manifest.json").read_text())
assert record["version"]=="v2656" and len(record["files"])==14
assert not OUTPUT.exists(),"QA snapshot already exists: never overwrite"
(OUTPUT/"images").mkdir(parents=True)
rows=[]
for row in record["files"]:
 p=SOURCE/row["file"]
 assert p.exists()
 h=hashlib.sha256(p.read_bytes()).hexdigest()
 assert h==row["sha256"]
 dest=OUTPUT/"images"/p.name
 shutil.copy2(p,dest)
 assert hashlib.sha256(dest.read_bytes()).hexdigest()==h
 rows.append({"filename":dest.name,"family":row["family"],"sha256":h,"bytes":dest.stat().st_size})
assert len(rows)==14
data={"version":"v2662","purpose":"persistent 14 prior QA candidate JPG snapshot",
"original_source_artifact":"v2656","source_is_historical":True,"latest_v2647":False,
"images":rows,"retail_approved":0,"copyright_licensing_verified":False,
"physical_stock_edition_verified":False,"no_public_paths_affected":True,
"no_xlsx_shared":True}
(OUTPUT/"manifest.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"staged":len(rows),"hash_verified":len(rows),"for_public_sale":0}))
