#!/usr/bin/env python3
"""v2561: identify exactly two remaining tight dHash candidate pairs from
v2560 isolated draft corpus and produce real JPG proof boards.
Read-only: never update reviewed JPEGs or publish.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageStat,ImageChops,ImageDraw,ImageFont
import json,hashlib
B=Path("v2561-v2560-input")
M=json.loads((B/"manifest.json").read_text())
D=B/"review-JPG-by-family"
O=Path("v2561-two-remaining-pair-proof");O.mkdir(parents=True,exist_ok=True)
assert len(list(D.glob("pending-*/*.jpg")))==156
assert M["images_changed_in_SEPARATE_QA_COPY"]==6 and M["other_images_preserved_sha_identical"]==150
p=M["perceptual_candidates"]
assert len(p)==2,len(p)
cross=json.loads(Path("evidence/inventory-30-family-crosswalk-20261104.json").read_text())
names={x["family_id"]:x["family_name"] for x in cross["pending_families"]}
rows=[]
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",22)
for item in p:
 fam=item["family"];fa=D/fam/item["a"];fb=D/fam/item["b"]
 assert fa.is_file() and fb.is_file()
 ia=Image.open(fa).convert("RGB");ib=Image.open(fb).convert("RGB")
 assert ia.size==ib.size==(1080,1080)
 diff=ImageChops.difference(ia.resize((256,256)),ib.resize((256,256)))
 mae=round(sum(ImageStat.Stat(diff).mean)/3,3)
 changed=sum(any(t>=24 for t in px) for px in diff.getdata())/(256**2)
 board=Image.new("RGB",(1150,700),"#f9f9f9")
 for col,im in enumerate((ia,ib)):
  thumb=ImageOps.contain(im,(550,550))
  x=col*575+(575-thumb.width)//2;y=14+(550-thumb.height)//2
  board.paste(thumb,(x,y))
 d=ImageDraw.Draw(board)
 d.text((24,577),f"{fam}: {names.get(fam,'unknown')}  |  dHash {item['distance']}",font=font,fill="#222")
 d.text((24,614),f"RGB MAE {mae}/255 | Changed pixel fraction (>24): {changed:.1%}",font=font,fill="#333")
 d.text((24,650),"QA HOLD | NO AUTO-DELETE | NO COMMERCIAL PERMISSION",font=font,fill="#444")
 jpg=O/(fam+"-"+fa.name[:2]+"-"+fb.name[:2]+"-REAL-pair-proof.jpg")
 board.save(jpg,"JPEG",quality=87,optimize=True)
 touched=[{"family":a["family"],"slot":a["slot"]} for a in M["merge_changes"]]
 hit=any(x["family"]==fam and x["slot"] in (int(fa.name[:2]),int(fb.name[:2])) for x in touched)
 rows.append({"family":fam,"product":names.get(fam),"slot_a":int(fa.name[:2]),"slot_b":int(fb.name[:2]),
 "dhash_distance":item["distance"],"pixel_mae_0_255":mae,
 "changed_pixel_fraction":round(changed,4),"source_sha_a":hashlib.sha256(fa.read_bytes()).hexdigest(),
 "source_sha_b":hashlib.sha256(fb.read_bytes()).hexdigest(),"was_part_of_six_replacements":hit,
 "visual_evidence":jpg.name,"status":"MANUAL_SCENE_REVIEW_HOLD"})
report={"version":"v2561","base_run":41753618979,"total_original_jpgs":156,"source_originals_edited":0,
"candidate_count":2,"pairs":rows,
"no_auto_deletion":True,"photo_rights_verified":False,"commercial_release_approved":False,
"original_55_public_urls_modified":0,"excel_created":False,
"note":"Review actual two-page visual evidence; dHash alone not grounds to remove or replace photography."}
(O/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"remaining_pairs":len(rows),"families":{r["family"]:r["product"] for r in rows},
"pair_slots":{r["family"]:[r["slot_a"],r["slot_b"]] for r in rows},
"touch_new_candidate":sum(r["was_part_of_six_replacements"] for r in rows),
"pixel_MAE":[r["pixel_mae_0_255"] for r in rows]},ensure_ascii=False))
