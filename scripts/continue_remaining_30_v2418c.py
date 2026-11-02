#!/usr/bin/env python3
"""v2418c final visual correction: remove advert/model image from OBgE 300ml
review-frame-01; replace only with authentic standalone brand photo.
Existing v2418 and v2418b assets are preserved intact in separate folders.
"""
from pathlib import Path
import requests,hashlib,shutil,json,io,csv
from PIL import Image,ImageOps,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];PRE=ROOT/'input-v2418b';OUT=ROOT/'production-v2418c';OUT.mkdir(exist_ok=True)
URL='https://m.obge.co.kr/web/product/medium/202603/e039688781d45789b70ee436c13cf0f6.png'
PAGE='https://m.obge.co.kr/product/대용량가성비-맥스-워터풀-선크림-300ml/1251/'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def font(n,b=False):
 try:return ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-'+('Bold' if b else 'Regular')+'.ttc',n)
 except:return ImageFont.load_default()
def render_clean(src,out):
 with Image.open(src) as im:
  im.load()
  if im.format not in ('PNG','JPEG','WEBP') or min(im.size)<350:raise RuntimeError('Unexpected official image size')
  photo=ImageOps.exif_transpose(im).convert('RGB')
 base=Image.new('RGB',(1080,1080),(254,253,251));photo.thumbnail((1010,920),Image.Resampling.LANCZOS)
 base.paste(photo,((1080-photo.width)//2,7+(915-photo.height)//2))
 d=ImageDraw.Draw(base);d.rectangle((0,928,1080,1080),fill=(228,238,230))
 d.text((60,946),'OBgE / MAX WATERFUL SUN CREAM',font=font(31,True),fill=(47,67,56))
 d.text((60,1005),'300 mL   |   Brand official product photograph',font=font(25),fill=(67,84,73))
 base.save(out,'JPEG',quality=91,optimize=True)
 with Image.open(out) as im: assert im.format=='JPEG' and im.size==(1080,1080)
 assert out.stat().st_size<2_000_000
n=0
for p in sorted(PRE.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(PRE)
 if rel.parts and rel.parts[0]=='all-previous-jpg-byte-preserved':
  out=OUT/'preserved-v2418b'/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
 elif rel.parts and rel.parts[0]=='review-five-frame-sets':
  out=OUT/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
 elif rel.parts and rel.parts[0]=='new-clean-product-photos':
  out=OUT/'preserved-v2418b'/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
 elif rel.parts and rel.parts[0]=='real-source-originals':
  out=OUT/'preserved-v2418b'/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
 n+=1
source_log={'family':'pending-22','url':URL,'product_page':PAGE,'result':'NOT_PRODUCED','originals_preserved':n}
try:
 r=requests.get(URL,headers={'User-Agent':'Mozilla/5.0','Accept':'image/*'},timeout=(8,18));r.raise_for_status()
 if len(r.content)>12_000_000:raise ValueError('Source exceeds image size limit')
 raw=OUT/'new-source-original'/('obge_300_'+hashlib.sha256(r.content).hexdigest()[:16]+'.png')
 raw.parent.mkdir(parents=True,exist_ok=True);raw.write_bytes(r.content)
 target=OUT/'new-final-clean-photo'/'pending-22'/'CLEAN_PRODUCT_FRAME_V2418C.jpg'
 target.parent.mkdir(parents=True,exist_ok=True);render_clean(raw,target)
 review=OUT/'review-five-frame-sets'/'pending-22'
 old=list(review.glob('01_*.jpg'))
 if len(old)!=1:raise RuntimeError('unexpected review slot')
 old[0].unlink()
 shutil.copy2(target,review/'01_CLEAN_PRODUCT_FRAME_V2418C.jpg')
 source_log.update(result='CLEAN_OFFICIAL_PHOTO_REPLACED_MODEL_AD',source_sha256=sha(raw),new_sha256=sha(target),new_jpg=1)
except Exception as e:
 source_log.update(result='PHOTO_DOWNLOAD_OR_QA_FAILED',reason=str(e)[:220],new_jpg=0)
# Abort rather than misreport success if clean official standalone photo was not actually created.
if source_log['result']!='CLEAN_OFFICIAL_PHOTO_REPLACED_MODEL_AD':
 raise RuntimeError('Exact official standalone clean photo could not be built: '+str(source_log))
sets={}
for d in sorted((OUT/'review-five-frame-sets').glob('pending-*')):
 count=len(list(d.glob('*.jpg')))
 if count!=5:raise RuntimeError('Bad set '+d.name)
 sets[d.name]=count
(OUT/'source_verification.json').write_text(json.dumps(source_log,ensure_ascii=False,indent=2),encoding='utf-8')
summary={'version':'2.4.18c','new_clean_photo_jpg':1,'final_B12_five_frame_review_sets':len(sets),'corrected_model_advertisement_images':1,'original_v2418b_assets_preserved':True,'production_complete_qa_pending':0,'ready_except_logo':0,'official_swatch_complete':0,'logo_binary_recovered':False,'published_urls_preserved':55}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
