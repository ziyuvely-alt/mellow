import hashlib,json,urllib.request,time
from io import BytesIO
from PIL import Image
from pathlib import Path
entries=json.loads(Path('evidence/v242-missha5.json').read_text())
rows=[]
for a in entries:
 u='https://mellow-bbia-images.onrender.com/'+a['path']
 result={'url':u,'expected_sha256':a['sha256'],'expected_bytes':a['bytes']}
 for _ in range(3):
  try:
   req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0 (MellowKR Authenticated product verifier)','Accept':'image/jpeg'})
   with urllib.request.urlopen(req,timeout=28) as r:
    result['http_status']=r.status
    result['mime']=r.headers.get('Content-Type','')
    blob=r.read(2000001)
   im=Image.open(BytesIO(blob));im.load()
   result['format']=im.format;result['dimensions']=list(im.size)
   result['bytes']=len(blob);result['sha256']=hashlib.sha256(blob).hexdigest()
   result['passed']=result['http_status']==200 and result['mime'].lower().startswith('image/jpeg') and im.format=='JPEG' and im.size==(1080,1080) and len(blob)<2000000 and len(blob)==a['bytes'] and result['sha256']==a['sha256']
   if result['passed']:break
  except Exception as exc:result.update({'passed':False,'error':str(exc)[:200]})
  time.sleep(5)
 rows.append(result)
 print('PASS' if result['passed'] else 'FAIL',u,flush=True)
Path('v242-missha5-public-verification.json').write_text(json.dumps({'total':len(rows),'passed':sum(r['passed'] for r in rows),'results':rows},indent=2))
