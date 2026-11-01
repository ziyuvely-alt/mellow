from pathlib import Path
from PIL import Image,ImageDraw
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from io import BytesIO
import requests,re,json,hashlib,zipfile,concurrent.futures
FAMILIES={
 "06_over_glaze_stick":"1000000128",
 "07_glow_tint_mini":"1000000163",
 "08_last_velvet_mini":"1000000186",
 "09_leau_tint_mini":"1000000187",
 "10_over_glaze_mini":"1000000208",
 "11_glow_tint":"1000000136",
 "13_ready_water_lipstick":"1000000074",
 "14_leau_tint":"1000000113",
}
root=Path("plugin6-official-multiview-08");root.mkdir(exist_ok=True)
session=requests.Session();session.headers.update({"User-Agent":"Mozilla/5.0","Accept":"text/html,image/*"})
def one(item):
 name,gid=item; page="https://www.bbia.co.kr/goods/goods_view.php?goodsNo="+gid
 out=root/name;out.mkdir(exist_ok=True)
 rec={"key":name,"goods_id":gid,"page":page,"images":[],"page_status":"ERROR"}
 try:
  response=session.get(page,timeout=16);response.raise_for_status();rec["page_status"]="HTTP_200"
  soup=BeautifulSoup(response.text,"html.parser")
  links=[]
  for tag in soup.find_all(["img","source"]):
   for attr in ("src","data-src","data-original","data-lazy-src"):
    val=tag.get(attr)
    if val:links.append(urljoin(response.url,val))
  links+=["https:"+v if v.startswith("//") else v for v in re.findall(r"(?:https?:)?//[^\s\"\'<>]+?\.(?:png|jpg|jpeg|webp)",response.text,re.I)]
  uniq=list(dict.fromkeys(u for u in links if ("1000000"+gid[-3:]) in u and ("cdn" in u or "goods" in u)))
  # fallback for images loaded from detail CDN product picture path
  if len(uniq)<2:uniq=list(dict.fromkeys(u for u in links if "cdn" in u and (gid in u or "/goods/" in u)))
  for i,u in enumerate(uniq[:45]):
   try:
    r=session.get(u,timeout=8,headers={"Referer":page});r.raise_for_status()
    if len(r.content)>8_000_000:continue
    im=Image.open(BytesIO(r.content));im.load()
    w,h=im.size
    if min(w,h)<550 or im.format not in ("JPEG","PNG","WEBP"):continue
    target=out/f"asset_{i:03d}.jpg"
    im.convert("RGB").save(target,quality=90,optimize=True)
    rec["images"].append({"name":target.name,"url":u,"width":w,"height":h,"sha256":hashlib.sha256(r.content).hexdigest()})
    if len(rec["images"])>=10:break
   except Exception:continue
 except Exception as e:rec["error"]=str(e)[:250]
 return rec
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 result=list(pool.map(one,FAMILIES.items()))
for rec in result:
 print(rec["key"],rec["page_status"],len(rec["images"]),flush=True)
 if not rec["images"]:continue
 thumbs=[]
 for a in rec["images"]:
  im=Image.open(root/rec["key"]/a["name"]);im.thumbnail((190,180))
  tile=Image.new("RGB",(210,215),"white");tile.paste(im,((210-im.width)//2,5))
  ImageDraw.Draw(tile).text((5,190),a["name"],fill="black");thumbs.append(tile)
 ncols=5;nrows=(len(thumbs)+4)//5;sheet=Image.new("RGB",(ncols*210,nrows*215),"#ddd")
 for i,tile in enumerate(thumbs):sheet.paste(tile,((i%ncols)*210,(i//ncols)*215))
 sheet.save(root/rec["key"]/"CONTACT.jpg",quality=82)
(root/"sources_manifest.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
with zipfile.ZipFile(root/"MULTIVIEW_SOURCE_CANDIDATES_QA_PENDING.zip","w",zipfile.ZIP_DEFLATED) as z:
 for p in root.rglob("*"):
  if p.is_file() and p.suffix.lower() in (".jpg",".json"):z.write(p,p.relative_to(root).as_posix())
