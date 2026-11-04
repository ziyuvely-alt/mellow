#!/usr/bin/env python3
"""v219: source-only audit; do not publish, restyle, replace or upscale product JPGs."""
import argparse, hashlib, io, json
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image, ImageDraw, ImageFont

BASE="https://images002.sabangnet.co.kr/v1/AUTH_c55e59a8ec2149e7ad5e61ca73645bd9/mw169402/image/"
SOURCES=[
("refill_hero","https://cdn-pro-web-250-115.cdn-nhncommerce.com/sky007com_godomall_com/data/goods/24/02/06/1000000124/1000000124_magnify_061.jpg","REFILL_EXCLUSIVE_PHOTO"),
("detail_02",BASE+"1781219858555.jpg","SHARED_CAMPAIGN_NOT_REFILL_ONLY"),
("detail_03",BASE+"1781219858561.jpg","SHARED_BENEFIT_AND_TEXTURE"),
("detail_04",BASE+"1781219858580.jpg","SHARED_BEFORE_AFTER"),
("detail_06",BASE+"1781219858586.jpg","FULL_COMPACT_NOT_REFILL_ONLY"),
("detail_07",BASE+"1781219858599.jpg","SHARED_MATERIAL_TEXTURE"),
("detail_09",BASE+"1781219858605.jpg","SHADE_CHART_AND_FULL_COMPACT"),
("detail_10",BASE+"1781219858611.jpg","SHARED_APPLICATION_AND_CASE"),
]
def fetch(url):
    with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=22) as r:
        return r.status, r.read(15_000_000)

def main(folder):
    folder.mkdir(parents=True,exist_ok=True)
    records=[]
    tiles=[]
    for name,url,role in SOURCES:
        entry={"key":name,"official_page_source":"https://www.bbia.co.kr/goods/goods_view.php?goodsNo=1000000124","source_url":url,"role_gate":role,"sales_approved":False}
        try:
            status,data=fetch(url)
            im=Image.open(io.BytesIO(data)); im.load()
            entry.update(status="DOWNLOADED",http_status=status,format=im.format,size=list(im.size),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
            entry["has_at_least_1080px_source_width"]=im.width>=1080
            entry["reuse_gate"]="REFILL_HERO_REFERENCE" if name=="refill_hero" else "DETAIL_REFERENCE_ONLY_NEVER_REFILL_PACK_PROOF"
            # Native source unchanged; only a small preview sheet is composed.
            preview=im.convert("RGB");preview.thumbnail((280,275),Image.Resampling.LANCZOS)
            tiles.append((name,preview.copy(),entry["size"],role))
        except Exception as e:
            entry.update(status="HOLD_FETCH_FAILED",error=f"{type(e).__name__}: {str(e)[:140]}")
        records.append(entry)
    board=Image.new("RGB",(1280,940),"#f5f5f5")
    draw=ImageDraw.Draw(board)
    draw.text((20,12),"BBIA v219 | OFFICIAL SOURCE QUALITY (not sales images)",fill="#202020")
    for i,(name,img,sz,role) in enumerate(tiles):
        x=20+(i%4)*315;y=56+(i//4)*420
        board.paste(img,(x,y))
        draw.text((x,y+287),name+" "+str(sz),fill="#222222")
        draw.text((x,y+313),role[:34],fill="#555555")
    board.save(folder/"BBIA_v219_OFFICIAL_SOURCE_CONTACT.jpg",quality=87)
    passed=[x for x in records if x["status"]=="DOWNLOADED"]
    (folder/"BBIA_v219_OFFICIAL_SOURCE_AUDIT.json").write_text(json.dumps({
       "checkpoint":"v219","scope":"source quality / product identity; no new sale image",
       "downloads_ok":len(passed),"downloads_failed":len(records)-len(passed),
       "distinct_source_hashes":len(set(x["sha256"] for x in passed)),
       "high_resolution_photos":[x["key"] for x in passed if x["has_at_least_1080px_source_width"]],
       "refill_hero_high_res":any(x["key"]=="refill_hero" and x["has_at_least_1080px_source_width"] for x in passed),
       "records":records,
       "policy":["Shared full-size compact image cannot prove refill contents","Never create fake shade swatches","Do not regenerate v217","No approved public file touched"]
    },ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("V219_SOURCE_QA",json.dumps({"downloaded":len(passed),"failed":len(records)-len(passed),"sizes":{x["key"]:x["size"] for x in passed},"refill_hero_high_res":any(x["key"]=="refill_hero" and x["has_at_least_1080px_source_width"] for x in passed)}))

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--out",default="/tmp/bbia-v219")
    main(Path(parser.parse_args().out))
