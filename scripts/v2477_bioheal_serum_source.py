from urllib.request import Request,urlopen
from PIL import Image,ImageOps,ImageDraw
from pathlib import Path
import json,hashlib,io
out=Path('v2477-bioheal-serum-source');out.mkdir(exist_ok=True)
urls=[f'https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0023/A000000233882{num}ko.{ext}?l=ko' for num,ext in [('35','jpg'),('02','jpg'),('25','jpg'),('24','jpg'),('16','jpg'),('34','jpeg')]]
results=[];seen=set();thumbs=[]
for i,url in enumerate(urls):
 item={'url':url,'status':'UNAVAILABLE'}
 try:
  with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'image/*'}),timeout=18) as r: b=r.read(6_000_001)
  if len(b)>6_000_000:raise ValueError('size too large')
  img=Image.open(io.BytesIO(b));img.load()
  if img.format not in ('JPEG','PNG','WEBP') or min(img.size)<240:raise ValueError('bad photo resolution or format')
  h=hashlib.sha256(b).hexdigest()
  if h in seen: item['status']='EXACT_DUPLICATE';results.append(item);continue
  seen.add(h);name=f'photo-{i+1:02d}.jpg';img.convert('RGB').save(out/name,'JPEG',quality=94)
  item.update(status='PHOTO_BYTES_DOWNLOADED_QA_HOLD',file=name,sha256=h,original_dimensions=img.size,original_bytes=len(b))
  z=ImageOps.contain(img.convert('RGB'),(290,280));tile=Image.new('RGB',(310,325),'white');tile.paste(z,((310-z.width)//2,5));ImageDraw.Draw(tile).text((10,290),name,fill='black');thumbs.append(tile)
 except Exception as e:item['error']=str(e)[:140]
 results.append(item)
if thumbs:
 sheet=Image.new('RGB',(310*len(thumbs),325),'white')
 for i,t in enumerate(thumbs):sheet.paste(t,(310*i,0))
 sheet.save(out/'review.jpg',quality=88)
(out/'manifest.json').write_text(json.dumps({'product':'BIOHEAL BOH NAD PRIZCELL Glow Power Serum 30mL','family':'pending-24','source':'Olive Young product no A000000233882','photos':results,'rights_verified':False,'exact_stock_edition_verified':False,'published':False},ensure_ascii=False,indent=2))
print(json.dumps({'downloaded':len(thumbs),'attempted':len(urls)}))
