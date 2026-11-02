#!/usr/bin/env python3
"""v2.4.20 global English master from verified original metadata.
Only redraw original text-only INFO cards (no product photographs retouched).
Check every overlay before saving. Do not touch published 55 live images.
"""
import csv,hashlib,json,re,shutil,zipfile,io
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=Path(__file__).resolve().parents[1]
PRIOR=ROOT/'input-v2416c'
PUB=ROOT/'input-v2420-public'
OUT=ROOT/'production-v2420-en-master';OUT.mkdir(exist_ok=True)
MASTER_LANGUAGE='EN'
COUNTRIES={'EN':'Global master','TW':'Traditional Chinese','TH':'Thai','VN':'Vietnamese','BR':'Portuguese'}
EXCLUDED=['MX']
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SOURCE_TSV=ROOT/'evidence/v2420-en-frame-content.tsv'
HANGUL=re.compile(r'[\uac00-\ud7a3\u1100-\u11ff\u3130-\u318f]')
if MASTER_LANGUAGE!='EN':raise RuntimeError('EN master required')
with SOURCE_TSV.open(encoding='utf-8') as f:
 dict_rows=list(csv.DictReader(f,delimiter='\t'))
MAP={(r['family'],r['file']):r for r in dict_rows}
assert len(MAP)==64,('Expected 64 explicit English source mappings',len(MAP))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ft(n,bold=False):
 try:return ImageFont.truetype(BOLD if bold else FONT,n)
 except:return ImageFont.load_default()
def assure_english(*texts):
 for s in texts:
  if HANGUL.search(s):raise ValueError('LANGUAGE_QA_HOLD Korean in rendered copy '+s[:60])
def draw_centered(draw,text,y,box=(90,990),size=40,bold=False,color=(46,64,56)):
 # Strict fit; never leave cropped letters
 for n in range(size,19,-1):
  face=ft(n,bold)
  rect=draw.textbbox((0,0),text,font=face)
  if rect[2]-rect[0]<=box[1]-box[0]:
   x=(box[0]+box[1]-(rect[2]-rect[0]))//2
   draw.text((x,y),text,font=face,fill=color);return
 raise ValueError('TEXT_OVERFLOW '+text)
def paint(r,previous,target):
 texts=[r[k] for k in ('role','headline','line_1','line_2')]
 assure_english(*texts)
 # Existing originals are graphic-only editorial info cards, with no package photo.
 with Image.open(previous) as old:
  original=old.convert('RGB')
  corner=original.getpixel((8,8))
  # Use the actual original upper margin background to maintain its aesthetic.
  bg=tuple(int(v*.92+246*.08) for v in corner)
 fid=r['family']
 variant=(int(fid.split('-')[-1])+sum(r['file'].encode('utf8')))%3
 accent=[(222,235,226),(247,224,212),(235,235,229)][variant]
 ink=(42,67,56)
 canvas=Image.new('RGB',(1080,1080),bg);d=ImageDraw.Draw(canvas)
 d.text((70,72),'MELLOWKR  /  PRODUCT GUIDE',font=ft(29,True),fill=ink)
 d.line((72,139,1012,139),fill=(149,172,153),width=3)
 draw_centered(d,texts[0],197,(68,1012),size=39,bold=True)
 d.rounded_rectangle((72,303,1008,762),radius=35,fill=accent)
 if variant==0:
  d.rounded_rectangle((120,344,958,718),radius=24,outline=(181,197,179),width=3)
 elif variant==1:
  d.rectangle((120,347,134,716),fill=(137,159,142))
 else:
  d.ellipse((836,340,1025,529),outline=(185,187,171),width=3)
 draw_centered(d,texts[1],386,(160,924),size=72,bold=True)
 d.line((187,506,892,506),fill=(150,167,147),width=2)
 draw_centered(d,texts[2],565,(135,945),size=42,bold=False)
 draw_centered(d,texts[3],643,(135,945),size=36,bold=False)
 d.line((70,839,1008,839),fill=(172,188,171),width=2)
 draw_centered(d,'AUTHENTIC PRODUCT INFORMATION',878,(90,990),size=28,bold=True)
 draw_centered(d,'GLOBAL ENGLISH MASTER',948,(90,990),size=25)
 canvas.save(target,'JPEG',quality=92,optimize=True)
 with Image.open(target) as ck:
  assert ck.format=='JPEG' and ck.size==(1080,1080)
 assert target.stat().st_size<2_000_000
def compare(old,new,path):
 with Image.open(old) as a,Image.open(new) as b:
  ia=a.convert('RGB').resize((540,540),Image.Resampling.LANCZOS)
  ib=b.convert('RGB').resize((540,540),Image.Resampling.LANCZOS)
 out=Image.new('RGB',(1080,590),(255,255,255));out.paste(ia,(0,44));out.paste(ib,(540,44))
 d=ImageDraw.Draw(out);d.text((15,12),'ORIGINAL',font=ft(22,True),fill=(40,55,50))
 d.text((554,12),'EN MASTER (DRAFT)',font=ft(22,True),fill=(40,55,50))
 path.parent.mkdir(parents=True,exist_ok=True);out.save(path,'JPEG',quality=84,optimize=True)
src={};revisions=[];reused=0;holds=[];before_after=[]
for fid_dir in sorted(PRIOR.glob('pending-*')):
 if not fid_dir.is_dir():continue
 fid=fid_dir.name
 for old in sorted(fid_dir.glob('*.jpg')):
  original=OUT/'preserved-pending-originals'/fid/old.name;original.parent.mkdir(parents=True,exist_ok=True)
  shutil.copy2(old,original);assert sha(original)==sha(old);reused+=1
  key=(fid,old.name)
  if key in MAP:
   record=MAP[key]
   file=OUT/'en-master-drafts'/fid/(old.stem+'_EN_V2420.jpg')
   file.parent.mkdir(parents=True,exist_ok=True)
   try:
    paint(record,old,file)
    dst=OUT/'before-after'/fid/(old.stem+'_compare.jpg')
    compare(old,file,dst)
    revisions.append({'family':fid,'old_file':old.name,'new_file':file.name,'old_sha256':sha(old),'new_sha256':sha(file),'role':record['role'],'status':'EN_LANGUAGE_RENDERED_VISUAL_QA_PENDING'})
   except Exception as e:
    if file.exists():file.unlink()
    holds.append({'family':fid,'file':old.name,'reason':str(e)[:160]})
  else:
   src[old.name]=src.get(old.name,0)+1
missing=[k for k in MAP if not (PRIOR/k[0]/k[1]).is_file()]
assert reused==160,('Source archive changed',reused)
# Preserve all existing public JPEGs from HTTP audit branch, including original URLs.
from_root=PUB/'immutable-http-public'
public_count=0
for x in from_root.rglob('*.jpg'):
 target=OUT/'preserved-public-http'/x.relative_to(from_root)
 target.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(x,target);assert sha(target)==sha(x);public_count+=1
assert public_count==55,public_count
# Public image audit states are independent of language status.
pub_report=[]
with (PUB/'public_55_candidate_audit.csv').open(encoding='utf-8-sig',newline='') as f:
 pub_rows=list(csv.DictReader(f))
VISUAL_REPEAT_FAMILIES=(
 'clio-kill-cover-founwear-cushion-original-mini-sourcephoto-v245b-cutout-20261101',
 'lamelin-miracle-nmn-pdrn-biotox-cream-50ml-sourcephoto-v243-20261101',
 'lamelin-miracle-nmn-pdrn-biotox-mask-pack-v244-20261101',
 'lamelin-miracle-nmn-pdrn-needle-shot-hair-serum-22-v244-20261101'
)
for r in pub_rows:
 similar=r['family'] in VISUAL_REPEAT_FAMILIES and int(r['slot'])>1
 qa='PUBLIC_VISUAL_REVISION' if similar else 'PUBLIC_SOURCE_UNVERIFIED'
 pub_report.append({'family':r['family'],'slot':r['slot'],'url':r['url'],'repo_http_sha_match':r['same_as_repo'],'en_overlay':'EN_LANGUAGE_PASS_PROVISIONAL','public_qa_status':qa,'reason':'Repeated product scene; separate visual diversity QA' if similar else 'Existing English overlays visibly plausible, but edition/rights/logo/previous exact URL mapping not fully verified'})
def csv_write(path,records,columns):
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows(records)
csv_write(OUT/'en_revised_frame_manifest.csv',revisions,['family','old_file','new_file','old_sha256','new_sha256','role','status'])
csv_write(OUT/'language_qa_hold.csv',holds,[ 'family','file','reason'])
csv_write(OUT/'public_55_en_and_visual_qa.csv',pub_report,['family','slot','url','repo_http_sha_match','en_overlay','public_qa_status','reason'])
# Category-specific zipped deliverables. All 30 families preserved even if no revision.
for folder in sorted((OUT/'preserved-pending-originals').glob('pending-*')):
 dst=OUT/'family-EN-review-ZIPs'/f'{folder.name}.zip';dst.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(folder.glob('*.jpg')):
   en=OUT/'en-master-drafts'/folder.name/(p.stem+'_EN_V2420.jpg')
   use=en if en.is_file() else p
   z.write(use,arcname=use.name)
# Aggregate before-after contact sheet; strips only previews.
comparisons=list((OUT/'before-after').glob('pending-*/*.jpg'))
if comparisons:
 cols=4;w=540;h=295
 sheet=Image.new('RGB',(cols*w,((len(comparisons)+cols-1)//cols)*h),(249,249,249))
 for i,p in enumerate(sorted(comparisons)):
  with Image.open(p) as im:thumbnail=im.convert('RGB').resize((w,h),Image.Resampling.LANCZOS)
  sheet.paste(thumbnail,((i%cols)*w,(i//cols)*h))
 sheet.save(OUT/'EN_64_before_after_overview.jpg','JPEG',quality=82,optimize=True)
summary={'version':'2.4.20','public_55_http_originals_sha_preserved':public_count,'pending_source_jpg_preserved':reused,'original_info_frames_mapped':len(MAP),'original_info_frames_found':len(MAP)-len(missing),'english_rendered_jpg':len(revisions),'language_qa_hold_on_information_frames':len(holds),'unmapped_original_photography_or_hero':reused-len(revisions)-len(holds),'public_overlay_provisional_en':sum(x['en_overlay']=='EN_LANGUAGE_PASS_PROVISIONAL' for x in pub_report),'public_visual_revision_identified':sum(x['public_qa_status']=='PUBLIC_VISUAL_REVISION' for x in pub_report),'public_source_final_verification_pending':sum(x['public_qa_status']=='PUBLIC_SOURCE_UNVERIFIED' for x in pub_report),'public_product_mismatch_proven':0,'public_originals_modified':0,'new_public_urls':0,'en_master_complete_families_final_qa':0,'master_language':MASTER_LANGUAGE,'country_translations_deferred':['TW','TH','VN','BR'],'country_excluded':EXCLUDED,'note':'Source reconstruction: intentionally embedded Korean in 64 text-only INFO frames rewritten as English. Original photographic frames and 55 published images unchanged; accurate package and final English visual QA still gated.'}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
