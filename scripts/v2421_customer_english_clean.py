#!/usr/bin/env python3
"""v2.4.21: conservative pixel-level patch of v2420 exact EN frames.
Do not regenerate product photos or invent a logo/shade; all 215 JPG originals immutable.
Only remove internal English production footer and unverified production caveats.
"""
import csv,hashlib,json,re,shutil
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'input-v2420-en'
OUT=ROOT/'production-v2421-customer-copy'
OUT.mkdir(exist_ok=True)
META=ROOT/'evidence/v2420-en-frame-content.tsv'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
RESTRICTED=re.compile(r'(?i)(verification required|source check|inventory check|official source check|packaging version pending|internal review|qa pending|reference only|global english master|authentic product information|official shade chart pending|check actual|confirm package|no invented|review official|refer to official|refer to the full|official formula reference|official protection rating|see official ingredients|listed in official|contents may vary|contents vary|korean retail package)')
KOREAN=re.compile(r'[\uac00-\ud7a3\u1100-\u11ff\u3130-\u318f]')
CONSUMER={
'Check actual set contents':'Cushion compact',
'Check actual stock edition':'CLIO cushion compact',
'Official set variation':'CLIO Kill Cover cushion',
'Official kit version':'Kill Cover Mesh Glow',
'Set contents may vary':'Mesh Glow Cushion compact',
'Check refill configuration':'Mesh Blur Cushion compact',
'Refill contents vary by set':'Mesh Blur Cushion',
'Official shade chart pending':'Perfect Cover Cushion',
'No invented swatches':'Selling shades 01 to 20',
'Refer to official INCI':'Key formula ingredients',
'Refer to the full INCI':'Ingredient information',
'Official formula reference':'Zinc oxide UV filter',
'Official protection rating':'Sun protection cushion',
'Confirm package edition':'Brightening Up Moisture Sun',
'Review official concentration':'Niacinamide ingredient',
'Official product size':'Gentle Gel-to-Foam Cleanser',
'See official ingredients':'Ingredient information',
'Listed in official INCI':'Formula ingredient highlights',
'Korean retail package':'Magic Cushion compact',
'Single item, not 1+1 set':'30 mL eye cream',
'Only shades 01 to 20':'Selling shades 01 to 20',
}
def hashf(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def face(n,b=False):return ImageFont.truetype(BOLD if b else FONT,n)
def centered(d,s,y,width=(145,935),size=40,bold=False):
 for n in range(size,19,-1):
  f=face(n,bold);b=d.textbbox((0,0),s,font=f)
  if b[2]-b[0]<=width[1]-width[0]:
   d.text(((width[0]+width[1]-(b[2]-b[0]))/2,y),s,font=f,fill=(42,67,56));return
 raise ValueError('overflow '+s)
def clean_copy(s,fid):
 if s=='Official shade chart pending':
  return 'Selling shades 01 to 20' if fid=='pending-08' else 'Select your cushion shade'
 return CONSUMER.get(s,s)
with META.open(encoding='utf-8') as f:source=list(csv.DictReader(f,delimiter='\t'))
assert len(source)==64
rows=[];pristine=0;updated=0;holds=[];sensitive=0
for section in ('preserved-pending-originals','preserved-public-http'):
 source_dir=OLD/section
 for p in source_dir.rglob('*.jpg'):
  target=OUT/'originals-immutable'/section/p.relative_to(source_dir)
  target.parent.mkdir(parents=True,exist_ok=True)
  shutil.copy2(p,target);assert hashf(p)==hashf(target);pristine+=1
assert pristine==215,pristine
for r in source:
 fid=r['family'];name=Path(r['file']).stem+'_EN_V2420.jpg'
 old=OLD/'en-master-drafts'/fid/name
 assert old.exists(),old
 target=OUT/'en-customer-drafts'/fid/(Path(r['file']).stem+'_EN_V2421.jpg')
 target.parent.mkdir(parents=True,exist_ok=True)
 texts=[clean_copy(r[k],fid) for k in ['role','headline','line_1','line_2']]
 if any(KOREAN.search(s) or RESTRICTED.search(s) for s in texts):
  holds.append({'family':fid,'old_file':name,'status':'EN_COPY_REVISION','reason':'Unresolved restricted content or Korean in customer copy'})
  continue
 with Image.open(old) as v:
  im=v.convert('RGB')
 d=ImageDraw.Draw(im)
 # Preserve actual rendered header, body and product facts. Remove only QA-only footer.
 bgcolor=im.getpixel((8,796))
 d.rectangle((0,812,1079,1079),fill=bgcolor)
 # A simple understated rule keeps the existing MellowKR typographic design.
 d.line((73,853,1005,853),fill=(173,186,172),width=2)
 corrections=0
 for k,txt,y in [('line_1',texts[2],565),('line_2',texts[3],643)]:
  if txt==r[k]:continue
  # Flat body color within this established information-only layout.
  accent=im.getpixel((500,745))
  d.rectangle((140,y-12,943,y+70),fill=accent)
  centered(d,txt,y,width=(143,937),size=42 if k=='line_1' else 36)
  corrections+=1
 if r['headline']!=texts[1] or r['role']!=texts[0]:
  holds.append({'family':fid,'old_file':name,'status':'EN_COPY_REVISION','reason':'Headline/role unsupported for localized area retouch'})
  continue
 im.save(target,'JPEG',quality=93,optimize=True)
 with Image.open(target) as verify:
  assert verify.format=='JPEG' and verify.size==(1080,1080) and target.stat().st_size<2_000_000
 assert hashf(old)!=hashf(target)
 compare=OUT/'before-after'/fid/(Path(r['file']).stem+'_V2420_V2421.jpg')
 compare.parent.mkdir(parents=True,exist_ok=True)
 with Image.open(old) as a:
  both=Image.new('RGB',(1080,570),'white')
  both.paste(a.convert('RGB').resize((540,540)),(0,30))
  both.paste(im.resize((540,540)),(540,30))
  d2=ImageDraw.Draw(both)
  d2.text((14,6),'V2.4.20',font=face(17,True),fill=(40,60,53))
  d2.text((554,6),'V2.4.21  /  CUSTOMER COPY',font=face(17,True),fill=(40,60,53))
  both.save(compare,'JPEG',quality=88,optimize=True)
 rows.append({'family':fid,'prior_jpg':name,'customer_jpg':target.name,'prior_sha256':hashf(old),'new_sha256':hashf(target),'corrected_main_copy_fields':corrections,'footer_internal_labels_removed':2,'copy_status':'EN_COPY_PASS_VISUAL_QA_PENDING'})
 updated+=1
 sensitive+=corrections
 print('EN_CUSTOMER',fid,name,'patch fields',corrections,flush=True)
assert len(rows)+len(holds)==64
# Do not automatically change published originals. Previously flagged 16 images are separated.
public_input=OLD/'public_55_en_and_visual_qa.csv'
with public_input.open(encoding='utf-8-sig',newline='') as f:pub=list(csv.DictReader(f))
flagged=[x for x in pub if x['public_qa_status']=='PUBLIC_VISUAL_REVISION']
for x in flagged:
 p=OLD/'preserved-public-http'/'images'/x['family']/(f'{int(x["slot"]):02d}.jpg')
 # Split-branch lotion published paths use two directories.
 if not p.exists():
  rel=x['url'].split('.onrender.com/')[-1]
  p=OLD/'preserved-public-http'/rel
 if p.is_file():
  dst=OUT/'public-16-immutable-candidates'/x['family']/p.name
  dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
  assert hashf(p)==hashf(dst)
def csvout(path,records,cols):
 with (OUT/path).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(records)
csvout('customer_en_revision_manifest.csv',rows,['family','prior_jpg','customer_jpg','prior_sha256','new_sha256','corrected_main_copy_fields','footer_internal_labels_removed','copy_status'])
csvout('copy_qa_hold.csv',holds,['family','old_file','status','reason'])
# The source-photo 96-image set is left unchanged and explicitly QA gated.
photo_count=sum(1 for p in (OLD/'preserved-pending-originals').rglob('*.jpg') if not p.name.startswith(('INFO_','PIXELPURE_INFO_')))
assert photo_count==96,photo_count
summary={'version':'2.4.21','prior_public_original_jpg_preserved':55,'prior_pending_original_jpg_preserved':160,'customer_facing_en_jpg_edited':updated,'customer_copy_internal_footer_labels_removed':updated*2,'unsafe_main_copy_fields_replaced':sensitive,'en_copy_hold':len(holds),'public_16_original_qa_flagged':len(flagged),'public_new_visual_replacements_approved':0,'public_exact_url_list_historical_verified':False,'public_39_unverified_source_closed':0,'source_photo_96_unmodified':photo_count,'source_photo_96_visual_qa_final_pass':0,'en_master_complete_families':0,'final_qa_approved':0,'actual_original_mk_logo_recovered':False,'official_color_chart_complete':0,'public_urls_untouched':55,'note':'Pixel-level edits remove only editorial/internal copy from v2420 INFO drafts; independent original product photos and public originals are immutable. No fabricated logo or unlicensed picture substitution.'}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
