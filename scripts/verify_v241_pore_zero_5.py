import json,hashlib,urllib.request,time
from io import BytesIO
from PIL import Image
from pathlib import Path
assets=json.loads(Path('evidence/v241-pore-zero-5.json').read_text())
results=[]
for a in assets:
 url='https://mellow-bbia-images.onrender.com/'+a['file']
 record={'url':url,'expected_sha256':a['sha256'],'expected_bytes':a['bytes']}
 for attempt in range(3):
  try:
   request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; MellowKRValidation/1.0)','Accept':'image/jpeg,image/*'})
   with urllib.request.urlopen(request,timeout=30) as response:
    data=response.read(2000001)
    record['http']=response.status
    record['mime']=response.headers.get('Content-Type','')
   image=Image.open(BytesIO(data));image.load()
   record['dimensions']=list(image.size)
   record['image_format']=image.format
   record['bytes']=len(data)
   record['actual_sha256']=hashlib.sha256(data).hexdigest()
   record['pass']=record['http']==200 and record['mime'].lower().startswith('image/jpeg') and image.format=='JPEG' and image.size==(1080,1080) and len(data)<2000000 and len(data)==a['bytes'] and record['actual_sha256']==a['sha256']
   if record['pass']:break
  except Exception as ex:record.update({'pass':False,'error':str(ex)})
  time.sleep(8)
 results.append(record)
 print(record,flush=True)
Path('v241-pore-zero-public-5.json').write_text(json.dumps({'total':len(results),'passed':sum(r['pass'] for r in results),'results':results},ensure_ascii=False,indent=2))
