#!/usr/bin/env python3
"""v2418d alpha-preserving final correction for authentic transparent OBgE 300ml.
This specifically removes the black background caused by RGB-converting a transparent
official PNG. No new product or logo content is synthesized.
"""
from pathlib import Path
import shutil,json,hashlib
from PIL import Image,ImageOps,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
PRE=ROOT/'input-v2418c';OUT=ROOT/'production-v2418d';OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def font(n,b=False):
 try:return ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-'+('Bold' if b else 'Regular')+'.ttc',n)
 except:return ImageFont.load_default()
def render(source,target):
 with Image.open(source) as im:
  im.load()
  if im.format!='PNG':raise RuntimeError('Expected exact official PNG original')
  original=ImageOps.exif_transpose(im).convert('RGBA')
 if original.getchannel('A').getextrema()!=(0,255):raise RuntimeError('Expected non-opaque source with alpha')
 bg=Image.new('RGBA',(1080,1080),(242,247,241,255))
 original.thumbnail((910,890),Image.Resampling.LANCZOS)
 x=(1080-original.width)//2;y=20+(885-original.height)//2
 bg.alpha_composite(original,(x,y))
 out=bg.convert('RGB')
 d=ImageDraw.Draw(out)
 d.rectangle((0,938,1080,1080),fill=(225,235,226))
 d.text((65,955),'OBgE  /  MAX WATERFUL SUN CREAM',font=font(31,True),fill=(45,64,52))
 d.text((66,1011),'300 mL  |  Original official transparent PNG',font=font(24),fill=(57,79,65))
 out.save(target,'JPEG',quality=93,optimize=True)
 with Image.open(target) as im:assert im.format=='JPEG' and im.size==(1080,1080)
 assert target.stat().st_size<2_000_000
count=0
for p in sorted(PRE.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(PRE);dest=OUT/rel;dest.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(p,dest)
 if sha(p)!=sha(dest):raise RuntimeError('Original changed')
 count+=1
source=list((PRE/'new-source-original').glob('obge_300_*.png'))
if len(source)!=1:raise RuntimeError('Official original PNG missing')
new=OUT/'new-alpha-corrected-product-photo'/'pending-22'/'CLEAN_PRODUCT_ALPHA_VERIFIED_V2418D.jpg'
new.parent.mkdir(parents=True,exist_ok=True)
render(source[0],new)
review=OUT/'review-five-frame-sets'/'pending-22'
old=list(review.glob('01_*.jpg'))
if len(old)!=1:raise RuntimeError('Expected exact one prior review image')
old[0].unlink()
shutil.copy2(new,review/'01_CLEAN_PRODUCT_ALPHA_VERIFIED_V2418D.jpg')
group=list((OUT/'review-five-frame-sets').glob('pending-*'))
if len(group)!=12 or any(len(list(d.glob('*.jpg')))!=5 for d in group):raise RuntimeError('Review set cardinality changed')
summary={'version':'2.4.18d','source_previous_files_preserved':count,'new_alpha_corrected_jpg':1,'final_b12_five_frame_sets':len(group),'original_png_has_alpha':True,'source_sha256':sha(source[0]),'corrected_jpg_sha256':sha(new),'black_background_issue_fixed':True,'actual_source_photography_unchanged':True,'logo_binary_restored':False,'production_complete_qa_pending':0,'ready_except_logo':0,'official_swatch_chart_completed':0,'public_urls_preserved':55}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
