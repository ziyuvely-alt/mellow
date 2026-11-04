from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
from rembg import remove,new_session
import json
r=Path("qa-review")
src=r/"v2816-clio-original-mini-5g-23N-real-single-unit-source"
dst=r/"v2817-clio-mini-23N-one-alpha-QA"
assert src.is_dir() and not dst.exists()
dst.mkdir()
p=src/"02-original-sasa-23N-5g-photo-1080-QA.jpg"
with Image.open(p) as im:
    im.load()
    assert im.size==(1080,1080)
    original=im.convert("RGBA")
cut=remove(original,session=new_session("isnet-general-use"))
assert cut.mode=="RGBA"
mask=cut.getchannel("A")
bbox=mask.getbbox()
if not bbox:
    raise ValueError("No foreground found")
coverage=sum(v>=128 for v in mask.getdata())/(cut.width*cut.height)
assert 0.035<coverage<0.8 and bbox[2]-bbox[0]>175 and bbox[3]-bbox[1]>175
cut=cut.crop(bbox)
cut.save(dst/"01-23N-5g-true-alpha-QA.png")
hero=Image.new("RGB",(1080,1080),"white")
thumb=ImageOps.contain(cut,(900,900),Image.Resampling.LANCZOS)
hero.paste(thumb,((1080-thumb.width)//2,(1080-thumb.height)//2),thumb)
jpg=dst/"01-23N-5g-true-alpha-1080-QA.jpg"
hero.save(jpg,"JPEG",quality=91,optimize=True)
assert jpg.stat().st_size<2000000
contact=Image.new("RGB",(1100,555),"white")
contact.paste(original.convert("RGB").resize((520,520)),(15,15))
contact.paste(hero.resize((520,520)),(565,15))
contact.save(dst/"before-after-QA.jpg","JPEG",quality=85)
(dst/"manifest.json").write_text(json.dumps({"version":"v2817","family":"pending-05","product":"CLIO The Original Mini 5g 23N","alpha_coverage":coverage,"qa_only":True,"retail_approval":False,"stock_edition_verified":False,"photo_rights_verified":False,"prior_originals_unchanged":True,"verified_55_urls_unchanged":True,"new_png":"01-23N-5g-true-alpha-QA.png","new_jpg":jpg.name},indent=2))
print("v2817 true alpha saved, QA only",round(coverage,3))
