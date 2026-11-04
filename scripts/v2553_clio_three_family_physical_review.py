#!/usr/bin/env python3
"""v2553 inspect three CLIO product groups and enumerate exact SKU-safe frame repairs.
No JPG source changes, no synthetic shades, no public release, no spreadsheet.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont,ImageStat,ImageChops
import hashlib,json,itertools
ROOT=Path("v2553-input/review-JPG-by-family")
OUT=Path("v2553-clio-three-family-proof");OUT.mkdir(exist_ok=True)
PRODUCTS={
 "pending-06":{"product":"CLIO Kill Cover Mesh Glow Essential Cushion Set","option_count":5,
 "exact_options":["19N","19C","21N","21C","23N"],"suspect":[1,5],
 "guard":"Mesh Glow only; do not substitute Mesh Blur or Founwear"},
 "pending-07":{"product":"CLIO Kill Cover Mesh Blur Cushion Set 15g x2","option_count":3,
 "exact_options":["19C","19N","21N"],"suspect":[1,4],
 "guard":"Mesh Blur only; prior six unrelated marketing sources explicitly rejected"},
 "pending-05":{"product":"CLIO Kill Cover Founwear Cushion Set","option_count":5,
 "exact_options":["19N","19C","21N","21C","23N"],"suspect":[1,5],
 "guard":"Founwear only; set/refill edition must match inventory"}
}
def dhash(im):
 g=list(ImageOps.grayscale(im).resize((9,8),Image.Resampling.LANCZOS).getdata())
 h=0
 for y in range(8):
  for x in range(8): h=(h<<1)|(g[y*9+x]>g[y*9+x+1])
 return h
reports=[]
for fam,meta in PRODUCTS.items():
 paths=sorted((ROOT/fam).glob("*.jpg"))
 assert len(paths)==6,(fam,len(paths))
 slots={int(p.name[:2]):p for p in paths}
 assert set(slots)==set(range(1,7)),(fam,list(slots))
 metrics={}; thumbnails={}
 for slot,p in slots.items():
  im=Image.open(p);im.load()
  assert im.format=="JPEG" and im.size==(1080,1080) and p.stat().st_size<2_000_000
  metrics[slot]={"filename":p.name,"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
   "dhash":dhash(im),"mean_rgb":[round(v,1) for v in ImageStat.Stat(im.convert("RGB").resize((128,128))).mean]}
  thumbnails[slot]=im.convert("RGB")
 pairs=[]
 for a,b in itertools.combinations(range(1,7),2):
  d=(metrics[a]["dhash"]^metrics[b]["dhash"]).bit_count()
  if d<=10:
   im1=thumbnails[a].resize((128,128));im2=thumbnails[b].resize((128,128))
   diff=ImageStat.Stat(ImageChops.difference(im1,im2)).mean
   mae=sum(diff)/3
   pairs.append({"slots":[a,b],"dhash":d,"mae_0_255":round(mae,2),
    "priority":"HIGH" if mae<8 else "REVIEW",
    "decision":"NEEDS_HUMAN_SCENE_CONFIRMATION_NOT_AUTO_DELETE"})
 sheet=Image.new("RGB",(1650,1230),"#fafafa")
 draw=ImageDraw.Draw(sheet)
 font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",22)
 for slot in range(1,7):
  im=ImageOps.contain(thumbnails[slot],(520,520))
  col=(slot-1)%3;row=(slot-1)//3
  x=col*550+(550-im.width)//2;y=row*615+20+(520-im.height)//2
  sheet.paste(im,(x,y))
  draw.text((col*550+30,row*615+554),f"{fam} | SLOT {slot:02d}",font=font,fill="#242424")
 sheet.save(OUT/(fam+"-six-actual-JPG-proof.jpg"),"JPEG",quality=87,optimize=True)
 # New image publication is prohibited absent evidence of exact edition, rights and manual scene QA.
 reports.append({"family":fam,**meta,"jpg_count":6,"all_actual_jpg_1080_square_under_2mb":True,
  "all_sha_distinct":len({m["sha256"] for m in metrics.values()})==6,
  "similar_pairs":pairs,"suspect_pair_previous":meta["suspect"],
  "sha_by_slot":{str(s):v["sha256"] for s,v in metrics.items()},
  "product_specific_rights_and_edition_hold":True,
  "visual_correction_status":"EVIDENCE_READY_REPLACEMENT_NOT_AUTHORIZED"})
report={"version":"v2553","families_examined":3,"images_examined":18,"technical_files_modified":0,
 "previous_156_original_jpg_preserved":True,"existing_public_55_url_changes":0,"xlsx_created":False,
 "new_marketing_images":0,"new_sales_approval":False,"product_evidence":reports,
 "independent_prior_goodal_slot05_candidate_retained_in_v2552":True,
 "next_action":"Only source-backed distinct scene with verified edition and rights may be used to replace near-identical frame; move on to next product on missing source."}
(OUT/"report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"families":3,"images":18,"suspect_similarity_pairs":sum(len(x["similar_pairs"]) for x in reports),
 "by_family":{x["family"]:len(x["similar_pairs"]) for x in reports},"approved":False}))
