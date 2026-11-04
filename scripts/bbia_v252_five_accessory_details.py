import io,json,hashlib,concurrent.futures
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw,ImageFont
items=[
('1000000185','EAU MATTE CUSHION PUFF','BLACK PUFF DETAIL',0,740),
('1000000126','EAU CUSHION PUFF','WHITE PUFF DETAIL',0,740),
('1000000200','EAU POWDER PACT PUFF','POWDER PUFF DETAIL',0,740),
('1000000127','EAU FINGER PUFF','FINGER PUFF DETAIL',0,740),
('1000000142','EAU PERFECT BRUSH','BRUSH HEAD DETAIL',0,740)]
m={str(x['product_id']):x for x in json.loads(Path('evidence/bbia-image-review-input.json').read_text())['families']}
out=Path('/tmp/bbia-v252');out.mkdir(parents=True,exist_ok=True)
def fetch(t):
    sku,name,role,top,bottom=t
    url=m[sku]['detail_references'][0]
    with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=22) as f:b=f.read(12000000)
    im=Image.open(io.BytesIO(b)).convert('RGB')
    return t,im,hashlib.sha256(b).hexdigest(),url
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:rows=list(pool.map(fetch,items))
board=Image.new('RGB',(1660,1150),'#f7f7f7')
pen=ImageDraw.Draw(board)
pen.text((12,10),'BBIA v252 FIVE ACCESSORY DETAIL PHOTOS | QA PENDING',fill='#222222')
font=lambda n,b:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-'+('Bold' if b else '')+'.ttf' if b else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
manifest=[]
for k,(t,source,digest,url) in enumerate(rows):
    sku,name,role,top,bottom=t
    pic=source.crop((0,top,source.width,min(source.height,bottom)))
    pic.thumbnail((950,790),Image.Resampling.LANCZOS)
    can=Image.new('RGB',(1080,1080),'#fbfaf9');d=ImageDraw.Draw(can)
    d.text((60,43),'BBIA',font=font(49,True),fill='#292526')
    d.text((60,120),name,font=font(30,True),fill='#3d3838')
    d.line((60,177,1020,177),fill='#d9cdcb',width=2)
    can.paste(pic,((1080-pic.width)//2,197+(792-pic.height)//2))
    d.text((60,1001),role,font=font(24,False),fill='#675b59')
    filename='BBIA_'+sku+'_DETAIL_v252_QA_PENDING.jpg'
    dest=out/filename;can.save(dest,'JPEG',quality=91,optimize=True,subsampling=0)
    if dest.stat().st_size>=2000000:raise RuntimeError('File over size for '+sku)
    thumb=can.copy();thumb.thumbnail((530,520))
    board.paste(thumb,((k%3)*550+10,48+(k//3)*555))
    manifest.append(dict(goodsNo=sku,output=filename,bytes=dest.stat().st_size,
      sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),size=[1080,1080],
      source_url=url,source_sha256=digest,source_crop=[0,top,source.width,min(source.height,bottom)],
      role=role,status='QA_PENDING_NOT_PUBLISHED'))
board.save(out/'BBIA_v252_FIVE_NEW_CONTACT.jpg',quality=89)
(out/'BBIA_v252_MANIFEST.json').write_text(json.dumps(dict(checkpoint='v252',parent='v251',created=len(manifest),
   files=manifest,published_changed=False,sales_approved=0),indent=2))
print('V252_CREATED',json.dumps({'created':len(manifest),'ids':[x['goodsNo'] for x in manifest]}))
