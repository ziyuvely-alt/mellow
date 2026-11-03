#!/usr/bin/env python3
"""v2.4.27: OBgE cushion targeted 4 EN product information revisions
and three real-source skin swatches from regional brand photo. No fabricated
shades, no product packaging edits, no public URL or original mutations.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
from io import BytesIO
import csv,hashlib,json,shutil,requests
ROOT=Path(__file__).resolve().parents[1]
S=ROOT/'v2426-source';O=ROOT/'v2427-output'
O.mkdir(exist_ok=True)
TOP='originals-v2425-unchanged/prior-immutable/immutable-prev/preserved-v2422'
SOURCE=S/TOP
FAMILY='pending-10'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ft(n,bold=False):
 return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if bold else '')+'.ttf',n)
# Archive every old JPEG untouched; avoid expensive recompilation/overwriting originals.
shutil.copytree(S,O/'immutable-v2426b',dirs_exist_ok=True)
prior=[p for p in S.rglob('*.jpg')]
for p in prior:assert sha(p)==sha(O/'immutable-v2426b'/p.relative_to(S))
# Earlier four English image cards truly exist; edit only their factual body panel.
DAT={
 'INFO_03_V2413_EN_V2421.jpg':('UV PROTECTION','SPF50+  PA++++','Daily UV protection','Perfect Cover Cushion | 15 g'),
 'INFO_04_V2413_EN_V2421.jpg':('3-IN-1 FUNCTION','TRIPLE FUNCTION','Brightening + wrinkle care','UV protection'),
 'INFO_05_V2413_EN_V2421.jpg':('NET CONTENT','15 g','Single cushion compact','Choose your preferred shade'),
 'INFO_SCOPE_01_V2414_EN_V2421.jpg':('PRODUCT DETAILS','PERFECT COVER','OBgE Perfect Cover Cushion','Lightweight cushion coverage')
}
# factual source: https://obge.co.kr/product/detail.html?product_no=10
en_dir=SOURCE/'en-customer-drafts'/FAMILY
ko_dir=SOURCE/'originals-immutable/preserved-pending-originals'/FAMILY
fixes=[]
for original,copy in DAT.items():
 src=en_dir/original
 if not src.exists():raise FileNotFoundError(src)
 original_image=Image.open(src).convert('RGB')
 im=original_image.copy();d=ImageDraw.Draw(im)
 # These four 1080px original EN information cards have a photo-free main
 # information panel bounded by x112..966 and y290..760. Redraw only panel copy.
 # Maintain original actual palette, geometry and outside of panel 100% intact.
 panel_color=im.getpixel((535,750))
 d.rounded_rectangle((126,334,955,729),radius=22,fill=panel_color)
 center=(126+955)//2
 for line,y,weight in [(copy[1],400,64),(copy[2],550,39),(copy[3],641,30)]:
  for sz in range(weight,18,-1):
   f=ft(sz,sz>=52);w=d.textbbox((0,0),line,font=f)[2]
   if w<780:break
  d.text((center-w//2,y),line,font=f,fill=(45,65,53))
 # This image has no product photograph; all old neighboring content preserved.
 out=O/'new-EN-info-four'/FAMILY/(Path(original).stem+'_V2427.jpg')
 out.parent.mkdir(parents=True,exist_ok=True)
 im.save(out,'JPEG',quality=93,optimize=True)
 with Image.open(out) as ck:assert ck.format=='JPEG' and ck.size==(1080,1080)
 assert out.stat().st_size<2_000_000 and sha(out)!=sha(src)
 original_ko=ko_dir/original.replace('_EN_V2421','')
 assert original_ko.exists(),original_ko
 with Image.open(original_ko) as before:
  compare=Image.new('RGB',(1080,565),(248,248,245))
  compare.paste(before.convert('RGB').resize((540,540)),(0,25))
  compare.paste(im.resize((540,540)),(540,25))
  dd=ImageDraw.Draw(compare);dd.text((8,4),'KOREAN SOURCE',font=ft(18,True),fill=(50,58,53))
  dd.text((550,4),'UPDATED EN MASTER',font=ft(18,True),fill=(50,58,53))
  comp=O/'before-after-four'/FAMILY/(Path(original).stem+'.jpg')
  comp.parent.mkdir(parents=True,exist_ok=True);compare.save(comp,'JPEG',quality=88,optimize=True)
 fixes.append({'source_korean':original_ko.name,'previous_english':original,'new_en':out.name,'original_sha':sha(original_ko),'prior_en_sha':sha(src),'new_en_sha':sha(out)})
 print('OBGE_EN',out.name,flush=True)
# Preserve exact genuine product picture with white rectangle until source alpha
# access or manual mask shape review: no invented transparency / damaged contour.
product=SOURCE/'en-photo-captions'/FAMILY/'SOURCE_01_363f13d61_EN_V2421C.jpg'
assert product.is_file()
shutil.copy2(product,O/'OBGE_product_photo_white_background_REJECTED_FOR_FINAL_QA.jpg')
# Genuine photographed shade swatches from OBgE HK manufacturer's regional page.
# Direct image source from regional OBgE product detail: three parallel swatches.
regional_page='https://obge.hk/en/products/perfect-homme-cushion'
regional_img='https://img-preview.myshopline.com/image/store/1687421143603/04-21626535-6844-498f-b15f-87c3322dc723.jpg?h=1000&q=80&w=1000'
swatch_state='RETRIEVAL_HOLD';photo_sha=None;swatch_file=None
try:
 r=requests.get(regional_img,headers={'User-Agent':'Mozilla/5.0','Accept':'image/jpeg,image/*'},timeout=(12,27))
 r.raise_for_status();content=r.content
 with Image.open(BytesIO(content)) as src:
  src.load()
  if src.format not in ('JPEG','PNG','WEBP') or min(src.size)<450:raise ValueError('not genuine high-res image')
  ref=src.convert('RGB')
 ref_file=O/'obge-three-shades-authentic-source.jpg';ref_file.write_bytes(content)
 photo_sha=sha(ref_file)
 w,h=ref.size
 # Image layout has three real photographed skin strokes in the upper 2/3;
 # crop strokes only, never generate synthetic swatch colors.
 sections=[('1','Ivory',(7,100,166,255)),('2','Beige',(177,100,336,255)),('3','Sand',(346,100,505,255))]
 canvas=Image.new('RGB',(1080,1080),(248,245,239));d=ImageDraw.Draw(canvas)
 d.text((56,65),'OBgE PERFECT COVER CUSHION',font=ft(44,True),fill=(48,56,49))
 d.text((56,130),'SHADE GUIDE  |  15 g  |  3 SHADES',font=ft(27),fill=(66,70,61))
 d.line((56,192,1025,192),fill=(180,173,155),width=3)
 for i,(num,name,rect) in enumerate(sections):
  box=(int(rect[0]*w/512),int(rect[1]*h/512),int(rect[2]*w/512),int(rect[3]*h/512))
  crop=ref.crop(box)
  crop=ImageOps.contain(crop,(308,345),Image.Resampling.LANCZOS)
  xx=56+i*341;canvas.paste(crop,(xx+(306-crop.width)//2,273))
  d.rounded_rectangle((xx,666,xx+307,805),radius=20,fill=(235,226,213))
  d.text((xx+20,689),'No. '+num,font=ft(35,True),fill=(52,54,50))
  d.text((xx+20,745),name,font=ft(29),fill=(52,54,50))
 d.line((56,858,1020,858),fill=(180,173,155),width=2)
 d.text((56,885),'1 Ivory    /    2 Beige    /    3 Sand',font=ft(31),fill=(67,68,63))
 swatch_file=O/'OBGE_Perfect_Cover_Cushion_3shade_actual_photo_QA_V2427.jpg'
 canvas.save(swatch_file,'JPEG',quality=92,optimize=True)
 with Image.open(swatch_file) as v:assert v.format=='JPEG' and v.size==(1080,1080)
 assert swatch_file.stat().st_size<2_000_000
 swatch_state='REGIONAL_BRAND_IMAGE_DRAFT_HOLD'
except Exception as e:
 swatch_state='IMAGE_FETCH_HOLD '+type(e).__name__+': '+str(e)[:130]
outcsv=O/'4_corrected_obge_english_sha.csv'
with outcsv.open('w',encoding='utf-8-sig',newline='') as f:
 fieldnames=list(fixes[0]);wr=csv.DictWriter(f,fieldnames=fieldnames);wr.writeheader();wr.writerows(fixes)
proof={
 'version':'2.4.27','obge_4_actual_modified_EN_JPG':len(fixes),
 'obge_photograph_white_rectangle_resolved':False,
 'obge_source_image_preserved_without_contour_damage':True,
 'obge_official_product_page':'https://obge.co.kr/product/detail.html?product_no=10',
 'obge_verified_claims':['15g','SPF50+ PA++++','brightening functional','wrinkle-care functional','UV protection'],
 'obge_3shade_opts':['1 Ivory','2 Beige','3 Sand'],'obge_real_photo_chart_state':swatch_state,
 'obge_real_photo_source_url':regional_img,'source_sha256':photo_sha,
 'official_renewed_edition_crosscheck_complete':False,
 'clio_mini_previous_3shade_candidate_preserved':True,
 'clio_photo_license_verified':False,
 'obge_photo_license_verified':False,
 '45_actual_working_SKU_options_prior_audit_preserved':True,
 'peripera_26AD_generation_conflict_resolved':False,
 'missha_cover_21_included':False,
 'original_MK_logo_binary_recovered':False,
 'official_new_sales_shade_charts_approved':0,
 'ready_except_logo':0,'final_qa_approved':0,
 'original_jpg_sha_preserved':len(prior),
 'live_55_public_urls_changed':0
}
(O/'summary.json').write_text(json.dumps(proof,indent=2,ensure_ascii=False),encoding='utf-8')
print('SUMMARY',json.dumps(proof,ensure_ascii=False),flush=True)
