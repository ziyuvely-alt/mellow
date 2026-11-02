import json,hashlib,urllib.request,time
from io import BytesIO
from PIL import Image
from pathlib import Path
assets=json.loads(Path('evidence/v241-obge-4.json').read_text())
out=[]
for a in assets:
 url='https://mellow-bbia-images.onrender.com/'+a['file']
 r={'url':url,'expected_sha256':a['sha256']}
 for attempt in range(3):
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; MellowKRValidation/1.0)'})
   with urllib.request.urlopen(req,timeout=30) as response:
    data=response.read(2000001);r['http']=response.status;r['mime']=response.headers.get('Content-Type','')
   im=Image.open(BytesIO(data));im.load()
   r.update({'bytes':len(data),'actual_sha256':hashlib.sha256(data).hexdigest(),'dimensions':list(im.size)})
   r['pass']=(r['http']==200 and r['mime'].lower().startswith('image/jpeg') and im.format=='JPEG' and im.size==(1080,1080) and len(data)==a['bytes'] and r['actual_sha256']==a['sha256'])
   if r['pass']:break
  except Exception as e:r.update({'pass':False,'error':str(e)})
  time.sleep(8)
 out.append(r);print(r,flush=True)
Path('v241-obge-public-check.json').write_text(json.dumps({'passed':sum(x['pass'] for x in out),'total':len(out),'results':out},indent=2))
