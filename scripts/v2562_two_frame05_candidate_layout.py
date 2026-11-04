from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import hashlib,json
b=Path("input/review-JPG-by-family")
o=Path("v2562-review");o.mkdir(exist_ok=True)
items=[("pending-01",1,5,"MISSHA COVER LASTING","APPLICATION GUIDE"),("pending-06",2,5,"CLIO MESH GLOW","SET & APPLICATION")]
res=[]
for family,photo_slot,target,title,sub in items:
 folder=b/family
 src=list(folder.glob(f"{photo_slot:02d}*.jpg"))
 old=list(folder.glob(f"{target:02d}*.jpg"))
 assert len(src)==len(old)==1
 pic=Image.open(src[0]).convert("RGB")
 canvas=Image.new("RGB",(1080,1080),"#f7f7f5")
 d=ImageDraw.Draw(canvas)
 f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",34)
 d.text((46,46),title,fill="#333333",font=f)
 d.text((46,112),sub,fill="#555555",font=f)
 thumb=ImageOps.contain(pic,(580,680))
 canvas.paste(thumb,((620-thumb.width)//2,215+(680-thumb.height)//2))
 for i,s in enumerate(("01  TAKE","02  PAT","03  FOLLOW LABEL")):
  d.text((635,320+i*170),s,fill="#333333",font=f)
 d.text((52,973),"DRAFT | CHECK STOCK, RIGHTS AND LOGO",fill="#555555",font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",22))
 p=o/(family+"-slot05-CANDIDATE.jpg")
 canvas.save(p,"JPEG",quality=89,optimize=True)
 assert Image.open(p).size==(1080,1080) and p.stat().st_size<2000000
 res.append({"family":family,"file":p.name,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"originals_modified":0,"sales_approved":False})
(o/"manifest.json").write_text(json.dumps({"version":"v2562","candidates":res,"urls_changed":0,"excel_shared":False},indent=2))
print(json.dumps(res))
