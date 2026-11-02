import requests, pathlib, json, hashlib, io
from PIL import Image
O=pathlib.Path('additional_real_photo_evidence');O.mkdir(exist_ok=True)
HEAD={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36'}
urls={
 'boh_jar_closed':'https://cdn-image.oliveyoung.com/prdtImg/1673/e7a6a36b-faee-4168-8137-5f1b1afa135a.jpg?AR=0&QT=80&RS=1500x1500&SF=webp',
 'boh_real_use':'https://cdn-image.oliveyoung.com/prdtImg/1699/fb33ae29-82da-4e95-8664-a1a83824edd3.jpg?AR=0&QT=80&RS=1500x1500',
 'cover_set_coupang':'https://image.coupangcdn.com/image/vendor_inventory/9f88/c0f91b86a95a4b4f1e04fe8d2efc1255ed007fa71718a8b2c13c8172c327.jpg',
 'cover_set_seller':'https://down-sg.img.susercontent.com/file/sg-11134207-7rdxu-mc1h4jshbjji0c',
}
rows=[]
for name,url in urls.items():
 r={'name':name,'url':url}
 try:
  v=requests.get(url,headers=HEAD,timeout=25);v.raise_for_status()
  im=Image.open(io.BytesIO(v.content)); im.load()
  assert im.width>=450 and im.height>=450
  p=O/(name+'.jpg');im.convert('RGB').save(p,'JPEG',quality=95,subsampling=0)
  r.update(status='downloaded',width=im.width,height=im.height,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),filename=str(p))
 except Exception as e:r.update(status='failed',error=str(e)[:240])
 rows.append(r);print(name,r['status'],flush=True)
(O/'report.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
