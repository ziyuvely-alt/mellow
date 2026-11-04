#!/usr/bin/env python3
"""v2608: source exactly two authentic mesh-blur cushion product photography
scenes, not the generic Founwear/Glow variants. Reuse original v2597 156
review corpus, compare six images in pending-07. No public/Excel changes.
Commercial photograph usage rights and owned-stock generation are not certified.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from io import BytesIO
from PIL import Image,ImageOps,ImageChops,ImageStat
import json,hashlib
BASE=Path("input/review-JPG-by-family/pending-07")
OUT=Path("v2608-CLIO-meshblur-two-authentic-photo-QA")
OUT.mkdir(exist_ok=True)
originals=sorted(BASE.glob("*.jpg"))
assert len(originals)==6,len(originals)
sources=[
 {"scene":"open-purple-cushion-and-puff",
 "source_page":"https://global.oliveyoung.com/product/detail?prdtNo=GA250531088",
 "url":"https://cdn-image.oliveyoung.com/prdtImg/1466/df6e7370-6e57-4b6b-b9c6-6957f4fc015c.jpg?AR=0&QT=80&RS=1500x1500&SF=webp",
 "fallback":"https://down-th.img.susercontent.com/file/sg-11134202-825b3-mexpkkx6jfnlc0"},
 {"scene":"mesh-foundation-structure-closeup",
 "source_page":"https://kosmetics.com.hk/products/clio-killcover-mesh-blur-cushion",
 "url":"https://kosmetics.com.hk/cdn/shop/files/Kill_Cover_Mesh_Blur_Cushion_T_6.jpg?v=1765941648&width=2000",
 "fallback":"https://medias.watsons.com.sg/publishing/WTCSG-92779-extra6-zoom.jpg?version=1763669429"}
]
def h(x):return hashlib.sha256(x).hexdigest()
def dhash(image):
 pix=list(ImageOps.grayscale(image).resize((9,8),Image.Resampling.LANCZOS).getdata());v=0
 for y in range(8):
  for x in range(8):v=(v<<1)|(pix[y*9+x]>pix[y*9+x+1])
 return v
def mae(a,b):
 x=a.convert("RGB").resize((128,128));y=b.convert("RGB").resize((128,128))
 return round(sum(ImageStat.Stat(ImageChops.difference(x,y)).mean)/3,2)
previous=[(p,Image.open(p).convert("RGB")) for p in originals]
accepted=[];results=[]
for source in sources:
 row={"scene":source["scene"],"source_page":source["source_page"],
 "commercial_rights_verified":False,"stock_edition_verified":False}
 for idx,url in enumerate((source["url"],source["fallback"]),1):
  try:
   req=Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"image/webp,image/png,image/jpeg,image/*"})
   with urlopen(req,timeout=17) as resp:raw=resp.read(7000001)
   assert 13000<len(raw)<7000000
   orig=Image.open(BytesIO(raw));orig.load()
   assert orig.format in ("JPEG","PNG","WEBP") and min(orig.size)>=400
   scaled=ImageOps.contain(orig.convert("RGB"),(1080,1080),Image.Resampling.LANCZOS)
   scene=Image.new("RGB",(1080,1080),"#f9f9fc")
   scene.paste(scaled,((1080-scaled.width)//2,(1080-scaled.height)//2))
   candidate=OUT/(source["scene"]+"-QA.jpg")
   scene.save(candidate,"JPEG",quality=91,optimize=True,subsampling=0)
   assert candidate.stat().st_size<2000000
   checks=[{"against":p.name[:2],"dhash_distance":(dhash(scene)^dhash(prev)).bit_count(),"mean_pixel_difference":mae(scene,prev)} for p,prev in previous]
   checks += [{"against":"new-"+s,"dhash_distance":(dhash(scene)^dhash(img)).bit_count(),"mean_pixel_difference":mae(scene,img)} for s,img in accepted]
   duplicate=[x for x in checks if x["dhash_distance"]<=6 or x["mean_pixel_difference"]<8]
   row.update({"status":"DUPLICATE_HOLD" if duplicate else "DISTINCT_PRODUCT_PHOTO_REVIEW_ONLY",
      "candidate_file":candidate.name,
      "sha256":h(candidate.read_bytes()),
      "source_sha256":h(raw),"source_image_size":list(orig.size),
      "source_format":orig.format,"downloaded_source":url,"similarity_alerts":duplicate,"all_compared":checks})
   if not duplicate:accepted.append((source["scene"],scene))
   break
  except Exception as exc:
   row[f"attempt_{idx}_failure"]=type(exc).__name__
 else:row["status"]="SOURCE_UNAVAILABLE_HOLD"
 results.append(row)
manifest={"version":"v2608","family":"pending-07",
 "product":"CLIO Kill Cover Mesh Blur Cushion 15g with refill",
 "original_six_images_unchanged":True,
 "source_urls_attempted":2,
 "source_photos_downloaded":sum(bool(x.get("candidate_file")) for x in results),
 "genuinely_distinct_photos":len(accepted),
 "photos_held":len(results)-len(accepted),
 "existing_156_sources_modified":0,
 "published_55_urls_unchanged":True,"new_public_urls":0,
 "product_rights_or_stock_match_authorized":False,
 "original_MK_logo_verified":False,
 "commercial_release_approved":False,
 "xlsx_created_or_shared":False,
 "results":results}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"photos_downloaded":manifest["source_photos_downloaded"],"distinct":len(accepted),"held":manifest["photos_held"],"published":0,"xlsx":False}))
