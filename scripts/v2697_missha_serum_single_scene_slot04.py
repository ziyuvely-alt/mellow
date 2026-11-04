#!/usr/bin/env python3
"""v2697 MISSHA PDRN 30 mL actual scene QA repair, no hallucinated objects.
Use official product-page gallery media06 showing one serum held by a model.
Never copy gallery media05: unrelated Vita C gift, and avoid duplicate media01/02.
Retain previous QA frames 01/02/03/05 exactly; replace only frame04.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import hashlib,json,shutil,base64
SRC=Path('qa-review/v2696-missha-serum-official-gallery-proof')
BASE=Path('qa-review/v2676-missha-pdrn-serum-fiveframe-qa')
OUT=Path('qa-review/v2697-missha-serum-one-product-lifestyle-photo-repair')
assert SRC.exists() and BASE.exists() and not OUT.exists()
OUT.mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
src=SRC/'source-06-REVIEW-ONLY.jpg'
assert src.is_file()
with Image.open(src) as im:
 im.load()
 assert im.format=='JPEG' and im.size==(1080,1080)
base=sorted(BASE.glob('[0-9][0-9]-*.jpg'))
assert len(base)==5
frames=[]
for file in base:
 slot=int(file.name[:2])
 if slot==4:continue
 dest=OUT/file.name
 shutil.copy2(file,dest)
 assert sha(dest)==sha(file)
 frames.append({'slot':slot,'file':dest.name,'sha256':sha(dest),'preserved':True})
dest=OUT/'04-official-30mL-serum-model-holding-single-product-QA.jpg'
shutil.copy2(src,dest)
assert sha(dest)==sha(src)
frames.append({'slot':4,'file':dest.name,'sha256':sha(dest),'preserved':False,
               'official_source':"https://static.ableshop.kr/ext/images/goods/editor/26/5/12/14/0000389036.jpg",
               'source_review':'v2696 media06, model applies/holds only same serum; no gift or variant bottles'})
frames=sorted(frames,key=lambda x:x['slot'])
assert [x['slot'] for x in frames]==[1,2,3,4,5]
for x in frames:
 p=OUT/x['file']
 with Image.open(p) as im:
  im.load();assert im.format=='JPEG' and im.size==(1080,1080)
 assert p.stat().st_size<2000000
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',24)
board=Image.new('RGB',(1870,490),'#f0eeee')
d=ImageDraw.Draw(board)
d.text((18,15),'v2697 MISSHA 30mL SINGLE SERUM 5-FRAME QA / NOT RETAIL APPROVED',font=font,fill='#222222')
for x in frames:
 with Image.open(OUT/x['file']) as im:thumb=im.convert('RGB').resize((340,340),Image.Resampling.LANCZOS)
 px=20+(x['slot']-1)*369
 board.paste(thumb,(px,70))
 d.text((px,421),f"FRAME {x['slot']:02d} / "+('PRESERVED' if x['preserved'] else 'NEW SCENE'),fill='#222',font=font)
proof=OUT/'v2697-five-jpg-visual-qa.jpg'
board.save(proof,'JPEG',quality=83,optimize=True)
(OUT/'v2697-visual-qa.b64.txt').write_text(base64.b64encode(proof.read_bytes()).decode())
report={'version':'v2697','family':'pending-13','product':'MISSHA PDRN NAD+ Firming Repair Serum 30mL',
'actual_product_jpgs':5,'prior_JPG_files_preserved_sha_identical':4,
'frame04_old_multiple_products_removed':True,'frame04_replaced_with_official_same_serum_model_scene':True,
'unrelated_Vitamin_C_gift_photo_explicitly_rejected':True,'old_29_other_QA_product_sets_untouched':True,
'final_retail_approved':False,'photo_publication_permission_verified':False,
'owned_stock_generation_verified':False,'v2647_full_archive_compared':False,
'previous_approved_11_families_untouched':True,'published_55_urls_untouched':True,
'final_excel_shared':False,'frames':frames}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'version':'v2697','new_qa_fiveframe_set':True,'changed_frames':[4],
'preserved_originals':4,'commercially_approved':False}))
