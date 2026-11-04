import json,io,hashlib,concurrent.futures
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw
IDS={'1000000125':[4,5,6],'1000000216':[4,5,6],'1000000187':[4,5,6]}
OUT=Path('/tmp/bbia-v302');OUT.mkdir(parents=True,exist_ok=True)
m={str(p['product_id']):p for p in json.loads(Path('evidence/bbia-image-review-input.json').read_text())['families']}
jobs=[(sku,i,m[sku]['detail_references'][i]) for sku,idx in IDS.items() for i in idx]
def fetch(t):
 sku,i,url=t;d={'sku':sku,'index':i,'url':url}
 try:
  with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=18) as r:b=r.read(12_000_000)
  im=Image.open(io.BytesIO(b));im.load()
  fn=f'BBIA_{sku}_SOURCE_{i}_v302.jpg';(OUT/fn).write_bytes(b)
  d.update(status='SAVED',filename=fn,dimensions=[im.width,im.height],sha256=hashlib.sha256(b).hexdigest())
  return d,im.convert('RGB')
 except Exception as e:d.update(status='HOLD',reason=str(e)[:130]);return d,None
with concurrent.futures.ThreadPoolExecutor(max_workers=9) as e:rs=list(e.map(fetch,jobs))
board=Image.new('RGB',(1830,1710),'#f7f6f4');p=ImageDraw.Draw(board)
p.text((12,12),'BBIA v302 / 9 UNUSED DETAIL SOURCES / NO AUTO APPROVAL',fill='#222')
for row,sku in enumerate(IDS):
 y=50+row*555;p.text((12,y),sku+' '+m[sku]['family'],fill='#222')
 for col,(d,im) in enumerate([a for a in rs if a[0]['sku']==sku]):
  x=col*610
  if im is None:continue
  full=im.copy();full.thumbnail((230,430));board.paste(full,(x+5,y+35))
  top=im.crop((0,0,im.width,min(im.height,980)));top.thumbnail((310,410))
  board.paste(top,(x+260,y+42))
  p.text((x+10,y+470),f'INDEX {d["index"]} / {im.width}x{im.height}',fill='#555')
board.save(OUT/'BBIA_v302_NINE_SOURCES_CONTACT.jpg',quality=88)
report={'checkpoint':'v302','parent':'v301','attempted':len(jobs),'downloaded':sum(d['status']=='SAVED' for d,i in rs),'records':[d for d,i in rs],'public_unchanged':True,'sales_approved':0}
(OUT/'BBIA_v302_MANIFEST.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('V302_RESULT',json.dumps({'attempted':len(jobs),'saved':report['downloaded']}))
