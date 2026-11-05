"""v2940 release gate reconciliation after v2939. No source images rewritten."""
from pathlib import Path
from zipfile import ZipFile
from hashlib import sha256
from io import BytesIO
from PIL import Image
import json,time
Q=Path('qa-review')
def load(p):return json.loads((Q/p/'manifest.json').read_text(encoding='utf-8'))
def state(p,file):return json.loads((Q/p/file).read_text(encoding='utf-8'))
BASE=state('v2939-goodal-100ml-live-citrus-source-QA','stock30-incremental-state-v2939.json')
M26=load('v2926-30family-26sourcezip-qa-state-and-next-action-ledger')
M29=load('v2929-pixelpure-three-four-photo-pack-source-integrity-QA')
M34=load('v2934-bioheal-cream-four-real-source-scene-QA-only')
M36=load('v2936-bioheal-serum-five-source-original-byte-QA-not-retail')
M39=load('v2939-goodal-100ml-live-citrus-source-QA')
OUT=Q/'v2940-four-final-source-gaps-photo-archive-integrity-and-approval-gate'
assert not OUT.exists()
assert BASE['version']=='v2939' and len(BASE['families'])==30
assert M26['five_source_archived_family_count']==19 and M26['sha256_and_ZIP_CRC_verified_archives']==26
assert M39['new_source_photos']==2 and M39['five_source_target_gap']==0
def check(path,digest,num):
 p=Path(path);assert p.exists() and sha256(p.read_bytes()).hexdigest()==digest
 with ZipFile(p) as z:
  assert z.testzip() is None and len(z.namelist())==num
  for name in z.namelist():
   b=z.read(name)
   with Image.open(BytesIO(b)) as im:
    im.load();assert im.format=='JPEG' and im.size==(1080,1080) and len(b)<2000000
 return {'path':str(p),'sha256':digest,'verified_photos':num,'ZIP_CRC':'PASS','photo_dimension':'1080x1080 reference only'}
data={}
for row in M29['results']:
 data[row['family']]=check(row['archive_ZIP'],row['archive_ZIP_sha256'],4)
data['pending-25']=check(M34['zip_path'],M34['zip_sha256'],4)
data['pending-20']=check(M39['qa_zip'],M39['qa_zip_sha256'],5)
data['pending-24']=check(M36['source_ZIP'],M36['source_ZIP_sha256'],5)
assert sorted(data)==sorted(['pending-20','pending-24','pending-25','pending-27','pending-29','pending-30'])
blocked={
 'pending-25':'NAD PRIZCELL Glow Boost Cream 50mL: a fifth authentic independently distinct, rights-cleared product source photo remains missing',
 'pending-27':'Pixelpure Soothing Ampoule Toner 200mL: fifth distinct manufacturer scene not found (gallery/detail scanned)',
 'pending-29':'Pixelpure Radiance Aqua Soothing Cream 50mL: fifth distinct manufacturer scene not found (gallery/detail scanned)',
 'pending-30':'Pixelpure Aura Radiance Serum 50mL: fifth distinct manufacturer scene not found (gallery/detail scanned)'
}
assert all(data[k]['verified_photos']==4 for k in blocked)
for k in blocked:
 BASE['families'][k].update({
   'last_delta_version':'v2940',
   'v2940_verified_existing_reference_images':4,
   'v2940_remaining_distinct_original_scene_slots':1,
   'v2940_source_archive_integrity':'SHA256_AND_ZIP_CRC_PASS',
   'v2940_release_gate':'HOLD_MISSING_FIFTH_AND_LICENSE_STOCK',
   'sale_approved':False})
for k in ('pending-20','pending-24'):
 BASE['families'][k].update({'v2940_verified_existing_reference_images':5,
    'v2940_remaining_distinct_original_scene_slots':0,
    'v2940_release_gate':'HOLD_RIGHTS_STOCK_MK',
    'sale_approved':False})
approved_by_count=19+2
assert approved_by_count==21 and sum(data[k]['verified_photos'] for k in blocked)==16
assert 30-approved_by_count-len(blocked)==5
report={
 'version':'v2940','baseline':'v2939','date_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
 'pending_total':30,'source_set_5of5_families':21,'source_set_4of5_families':4,
 'mixed_options_and_edition_hold_families':5,
 'remaining_distinct_source_photo_slots':4,
 'verified_current_family_ZIPs':6,
 'source_set_does_not_mean_retail_release':True,
 'new_public_URLs':0,'new_retail_approvals':0,
 'approved_prior_families_preserved':11,'existing_public_urls_preserved':55,
 'old_photo_bytes_modified':0,'final_spreadsheet_shared':False,
 'next_immediate_work':['Obtain manufacturer-licensed, edition-verified fifth sources for four listed products','Reconcile physical owned stock exact variants and source rights before retail use','Do not repeat unsuccessful official product detail/gallery scans without new source'],
 'four_missing_source_families':[{'family':k,'product':BASE['families'][k]['product'],'missing':1,'reason':v,'verified_archive':data[k]} for k,v in blocked.items()],
 'other_verified_families':[{'family':k,'images':5,'verified_archive':data[k],'sale_approved':False} for k in ('pending-20','pending-24')],
 'rights_and_stock_gate':'HOLD_FOR_ALL_30'
}
OUT.mkdir(parents=True)
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
BASE.update({'version':'v2940','baseline':'v2939','new_sales_approvals':0,'new_public_URLs':0,'final_spreadsheet_shared':False})
(OUT/'stock30-incremental-state-v2940.json').write_text(json.dumps(BASE,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'version':'v2940','five_photo_sets':21,'four_photo_sets':4,'still_missing_scenes':4,'CRC_SHA_archives':6,'sales_release':0},ensure_ascii=False))
