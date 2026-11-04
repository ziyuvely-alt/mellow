#!/usr/bin/env python3
"""v230: finish only three v229 source-ready products. Never rerun the first 12."""
import argparse,sys,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw
sys.path.insert(0,"scripts")
from bbia_v229_bulk_photo_production import inspect,produce
IDS=("172","1000000056","1000000251")
def main(out):
    out.mkdir(parents=True,exist_ok=True)
    master=json.loads(Path("evidence/bbia-image-review-input.json").read_text(encoding="utf-8"))
    found={str(x["product_id"]):x for x in master["families"]}
    report={"checkpoint":"v230","parent":"v229","selected_only":list(IDS),"records":[],"new_jpgs":0,
            "prior_12_v229_jpg_modified":False,"public_files_modified":False,"sales_approved":0}
    board=Image.new("RGB",(1080,440),"#f7f7f6")
    d=ImageDraw.Draw(board)
    d.text((15,10),"BBIA v230 | THREE QUEUED SOURCE PHOTO CANDIDATES",fill="black")
    for i,key in enumerate(IDS):
        data=found.get(key)
        if not data:
            report["records"].append({"goodsNo":key,"status":"SOURCE_MASTER_NOT_FOUND"});continue
        info,photo=inspect(data)
        if photo is not None and min(photo.size)>=800 and info["status"]=="PHOTO_DOWNLOADED":
            info=produce(out,info,photo)
            if info["status"]=="NEW_QA_CANDIDATE_CREATED":
                report["new_jpgs"]+=1
                thumbnail=Image.open(out/info["new_jpg"]).convert("RGB")
                thumbnail.thumbnail((340,340))
                board.paste(thumbnail,(10+i*358,42))
        else:
            info["status"]="SOURCE_QUALITY_HOLD" if photo is not None else info["status"]
        report["records"].append(info)
    if report["new_jpgs"]:
        board.save(out/"BBIA_v230_THREE_CONTACT.jpg",quality=89)
    (out/"BBIA_v230_MANIFEST.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("V230_RESULT",json.dumps({"new_jpgs":report["new_jpgs"],"records":[{"id":x["goodsNo"],"status":x["status"]} for x in report["records"]]}))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True)
    main(Path(p.parse_args().out))
