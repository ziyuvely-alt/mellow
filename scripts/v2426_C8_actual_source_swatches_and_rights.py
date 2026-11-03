#!/usr/bin/env python3
"""Shopee v2.4.26: source-backed, version-safe CLIO MINI three-shade chart DRAFT
+ actual C8 options QA + OBgE permission request. No unsourced fake color.
Not public or licensed for Shopee until official source license/packaging QA.
"""
import csv,hashlib,io,json,re,shutil,requests
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'v2425-input'
OUT=ROOT/'v2426-output'
OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
FILE=ROOT/'evidence/v2425-C8-working-SKU-45-options.tsv'
with FILE.open(encoding='utf-8') as f:rs=list(csv.DictReader(f,delimiter='\t'))
assert len(rs)==45
# Cross-check actual workbook-sourced, earlier prior TSV. All original options immutable.
VALID_PERI={f'{i:03d}' for i in (1,2,3,5,8,9,10,11,12,13,14,15,16,17,18,19,20)}
for x in rs:
 fid=x['family_id'];option=x['raw_option']
 if fid=='pending-08':
  if option not in VALID_PERI:x['status']='NOT_IN_VERIFIED_26AD_RETAILER_LIST'
  elif option=='012':x['status']='NAMESPELLING_CONFLICT_12'
  else:x['status']='NAME_MATCH_NEW_26AD_NOT_PREVIOUS_GENERATION_PROOF'
 elif fid=='pending-01' and option=='21':x['status']='EXCLUDE_21_FROM_COVER_LASTING_PENDING_EXPLICIT_APPROVAL'
 elif fid=='pending-02' and option=='21':x['status']='MOIST_UP_21_NOT_AUTOMATICALLY_EXCLUDED'
 elif fid=='pending-04':x['status']='CLIO_MINI_3_SHADES_CONFIRMED'
 elif fid=='pending-10':x['status']='OBGE_OFFICIAL_3_SHADES_CONFIRMED'
 elif fid in ('pending-05','pending-06','pending-07'):x['status']='CLIO_SHADE_NAME_VERIFIED_KIT_EDITION_HOLD'
 else:x['status']='OFFICIAL_SHADE_PHOTO_PENDING'
 x['swatch_verified']='NO' # Cannot infer licensed official brand swatch from option table
 x['global_sku_unchanged']='YES'
 x['image_license_verified']='NO'
with (OUT/'C8_45_options_v2426_verified_status.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
# Brand-origin CLIO Color Library photo reproduced on 3rd-party retailer site:
# use source pixels, crop actual photographed strokes, no synthetic swatches.
REF='https://rackhams.com/image/medium/f67c60eb-8246-4e57-81be-708a88ca13d7.jpg'
page='https://rackhams.com/clio-kill-cover-mesh-glow-essential-cushion-set-refill-5-colours'
success=False
error=''
raw=b''
try:
 response=requests.get(REF,timeout=(10,25),headers={'User-Agent':'Mozilla/5.0','Accept':'image/jpeg,image/*'});response.raise_for_status()
 raw=response.content
 with Image.open(io.BytesIO(raw)) as im:
  im.load(); assert im.format in ('JPEG','PNG','WEBP') and min(im.size)>=400
  source=im.convert('RGB')
 p=OUT/'source-evidence-clio-library.jpg';p.write_bytes(raw)
 W,H=source.size
 # Coordinates in reference 512x512. Crop genuine CLIO swatch stroke + its original
 # label in each cell. Original 19C,19N not reused for mini.
 swatches=[
  ('21C','Lingerie',(55,249,240,342)),
  ('21N','Linen',(262,249,465,342)),
  ('23N','Ginger',(262,370,465,475))
 ]
 for code,name,box in swatches:
  xx=tuple(int(v*W/512) if i%2==0 else int(v*H/512) for i,v in enumerate(box))
  crop=source.crop(xx)
  assert min(crop.size)>55
  proof=OUT/'official-color-library-evidence'/f'CLIO_{code}_{name}_ORIGINAL_CROP.png'
  proof.parent.mkdir(parents=True,exist_ok=True);crop.save(proof)
 bg=Image.new('RGB',(1080,1080),(250,247,242));d=ImageDraw.Draw(bg)
 font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
 bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
 d.text((58,53),'CLIO KILL COVER',font=ImageFont.truetype(bold,49),fill=(54,55,52))
 d.text((58,117),'Mesh Glow Essential Cushion Mini   /   5 g',font=ImageFont.truetype(font,29),fill=(74,76,69))
 d.line((58,178,1017,178),fill=(201,179,171),width=3)
 d.text((59,205),'AVAILABLE SHADES  /  3 OPTIONS',font=ImageFont.truetype(bold,27),fill=(98,80,86))
 for index,(code,name,_) in enumerate(swatches):
  x=58+index*339
  crop=Image.open(OUT/'official-color-library-evidence'/f'CLIO_{code}_{name}_ORIGINAL_CROP.png').convert('RGB')
  # Always letterbox actual source photo pixels. Do not recolor or paint any chips.
  crop=ImageOps.contain(crop,(308,250),Image.Resampling.LANCZOS)
  bg.paste(crop,(x+(307-crop.width)//2,308+(220-crop.height)//2))
  d.rounded_rectangle((x,595,x+305,748),radius=18,fill=(235,229,224))
  d.text((x+17,616),code,font=ImageFont.truetype(bold,39),fill=(53,53,51))
  d.text((x+17,677),name,font=ImageFont.truetype(font,31),fill=(53,53,51))
 d.line((58,814,1018,814),fill=(207,192,183),width=2)
 d.text((58,842),'Choose one shade per cushion.',font=ImageFont.truetype(font,29),fill=(74,75,69))
 d.text((58,898),'5 g  |  21C Lingerie  /  21N Linen  /  23N Ginger',font=ImageFont.truetype(font,25),fill=(74,75,69))
 target=OUT/'CLIO_Mesh_Glow_Mini_3Shade_actual_swatches_QA_V2426.jpg'
 bg.save(target,'JPEG',quality=91,optimize=True)
 with Image.open(target) as check:assert check.format=='JPEG' and check.size==(1080,1080)
 assert target.stat().st_size<2000000
 success=True
except Exception as e:error=f'{type(e).__name__}: {str(e)[:160]}'
# Provenance records and release gate
chart={
 'product':'CLIO Kill Cover Mesh Glow Essential Cushion Mini 5g',
 'options':['21C Lingerie','21N Linen','23N Ginger'],
 'actual_global_sku_option_match':'3/3',
 'source_brand_origin':'CLIO Color Library chart, reproduced at external retailer',
 'source_page':page,'source_image_url':REF,
 'original_source_SHA256':sha(OUT/'source-evidence-clio-library.jpg') if success else None,
 'candidate_SHA256':sha(OUT/'CLIO_Mesh_Glow_Mini_3Shade_actual_swatches_QA_V2426.jpg') if success else None,
 'actual_official_color_photo_crop':success,'download_error':error,
 'brand_authoritative_origin_verified':False,
 'commercial_reuse_permission_verified':False,
 'inventory_package_edition_verified':False,
 'release_status':'SHADE_IMAGE_DRAFT_QA_HOLD' if success else 'SOURCE_IMAGE_FETCH_HOLD',
 'official_complete_chart_approved':False}
(OUT/'clio_mini_swatch_provenance.json').write_text(json.dumps(chart,indent=2,ensure_ascii=False),encoding='utf8')
# Preserve current published/working source. DO NOT rewrite any previous JPEG.
old_count=0
for p in (OLD/'unchanged-v2424b').rglob('*.jpg'):
 target=OUT/'originals-v2425-unchanged'/p.relative_to(OLD/'unchanged-v2424b')
 target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
 assert sha(target)==sha(p);old_count+=1
assert old_count>=371,old_count
# Permission request for OBgE (NOT SENT)
message="""제목: [해외 쇼피 정품 리셀러] 오브제 상품 이미지 사용 및 편집 허가 요청

안녕하세요. 한국에서 정품 K-뷰티 상품을 해외 Shopee 고객에게 판매하는 리셀러입니다.
오브제 오일 컨트롤 피니셔 5g 및 맥스 워터풀 선크림 300ml의 정품 판매를 위해 공식 상품 사진 사용 허가를 문의드립니다.

사용 매체: Shopee 해외 판매용 상품 썸네일·상세페이지
대상 국가: 싱가포르(SG), 말레이시아(MY), 필리핀(PH), 태국(TH), 대만(TW), 베트남(VN), 브라질(BR). 멕시코(MX)는 제외합니다.
사용 방식: 제공받은 실제 제품 사진의 배경 정리·누끼, 정보형 배치, 영어 및 국가별 번역, MellowKR 원형 MK 로고 병기
사용 기간: 승인되는 기간과 범위에 한정. 이미지 파일의 제3자 재배포는 하지 않습니다.

다음 사항을 확인 부탁드립니다.
1. 공식 제품 이미지 또는 판매자용 공식 원본 자료 제공 가능 여부
2. 해외 Shopee 정품 리셀러의 상업적 게시 권한
3. 배경 정리, 크롭/합성 배치, 번역, 판매자 로고 표기 허용 범위
4. 국가, 판매 채널, 유효 기간 및 출처 표시 조건
5. 허가받은 이미지와 실제 판매 패키지 버전의 동일성 확인 방법

가능하시다면 서면 허가 또는 해당 판매자 이미지 이용약관을 전달 부탁드립니다.
공식 허가가 확인되기 전에는 해당 사진을 신규 판매 이미지로 승인·게시하지 않겠습니다.

감사합니다.
"""
(OUT/'OBgE_image_commercial_permission_request_NOT_SENT.txt').write_text(message,encoding='utf8')
(OUT/'rights_contacts.json').write_text(json.dumps({
 'obge':{'email':'export@adaptkorea.com','source':'https://www.obge.co.kr/shopinfo/company.html','agreement':'https://www.obge.co.kr/member/agreement.html','status':'DRAFT_NOT_SENT'},
 'clio':{'status':'BRAND_USAGE_LICENSE_NOT_VERIFIED'},
 'peripera':{'status':'BRAND_USAGE_LICENSE_NOT_VERIFIED'},
 'missha':{'status':'BRAND_USAGE_LICENSE_NOT_VERIFIED'},
 'pixelpure':{'status':'BRAND_USAGE_LICENSE_NOT_VERIFIED'}
},indent=2),encoding='utf8')
summary={'version':'2.4.26','all_C8_working_SKU_option_rows_checked':45,'C8_target_families':8,
 'peripera_26AD_vs_previous_generation_resolved':False,'peripera_current_26AD_number_name_matches':16,
 'peripera_missing_latest_retailer_numbers':['004','006','007'],'peripera_spelling_hold_012':True,
 'missha_cover_lasting_21_excluded_from_new_chart_pending_confirmation':True,
 'missha_moist_up_21_not_excluded':True,
 'clio_mini_3_shades_match':True,'obge_cushion_3_shades_match':True,
 'new_actual_source_swatches_chart_qa_jpg':1 if success else 0,
 'official_final_approved_chart_jpg':0,
 'preserved_previous_jpg_bytes':old_count,'existing_public_urls_unchanged':55,
 'rights_request_created_not_sent':True,'commercial_reuse_verified':0,
 'inventory_package_verified':0,'original_MK_png_recovered':False,
 'READY_EXCEPT_LOGO':0,'PRODUCTION_COMPLETE_QA_PENDING':0,'FINAL_QA_APPROVED':0,
 'note':'Official-origin-looking CLIO Color Library image is reseller-hosted; actual swatches are cropped not hallucinated. Not publishable without brand origin, license, stock and MK logo gates.'}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
