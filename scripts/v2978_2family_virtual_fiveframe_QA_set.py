#!/usr/bin/env python3
"""v2978: validate two new ORIGINAL QA image bytes and reference only old unchanged
photo bytes. Build 5-frame virtual replacement plans, no ZIP duplication/public sales.
"""
from pathlib import Path
import hashlib,io,json,zipfile
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa-review/v2978-two-five-frame-virtual-sets-reuse-existing-binaries-20261106"
PATHS={
 "stock_v2970":"qa-review/v2970-remaining-stock-archive-audit-no-new-binary-20261106/manifest.json",
 "obge_v2905":"qa-review/v2905-obge-finisher5g-five-official-no-unverified-MK-internal-QA/manifest.json",
 "goodal_new":"qa-review/v2976-goodal-eyecream-one-original-howto-frame-no-photo-20261106/manifest.json",
 "obge_new":"qa-review/v2977-obge-finisher5g-one-original-directions-frame-20261106/manifest.json",
}
def sha(b):return hashlib.sha256(b).hexdigest()
def load(rel):return json.loads((ROOT/rel).read_text(encoding="utf8"))
def check_jpg(data,path):
    with Image.open(io.BytesIO(data)) as im:
        im.load();fmt=im.format;dims=list(im.size)
    if fmt!="JPEG" or dims!=[1080,1080] or len(data)>=2_000_000:
        raise ValueError("Frame is not approved technical JPG 1080 <2 MB: "+path)
    return {"path":path,"bytes":len(data),"sha256":sha(data),"dimensions":dims,"technical_pass":True}
def main():
    if OUT.exists():raise RuntimeError("No repeat v2978, outputs already saved")
    inp={k:load(p) for k,p in PATHS.items()}
    if inp["goodal_new"]["version"]!="v2976" or inp["obge_new"]["version"]!="v2977":
        raise ValueError("Not a known original info frame checkpoint")
    a=inp["stock_v2970"]["results"]["pending-21"]
    zipped=ROOT/a["archive"]
    if sha(zipped.read_bytes())!=a["archive_SHA256"]:
        raise ValueError("Original goodal ZIP changed")
    goodal_rows=[]
    with zipfile.ZipFile(zipped) as z:
        files=[n for n in z.namelist() if n.lower().endswith(".jpg")]
        if len(files)!=5:raise ValueError("Goodal source ZIP isn't 5 frames")
        for i in [0,1,2,4]:
            dat=z.read(files[i])
            if sha(dat)!=a["JPG_files"][i]["SHA256"]:
                raise ValueError("Goodal archive source frame changed")
            r=check_jpg(dat,f"{a['archive']}!/{files[i]}")
            r.update({"slot":i+1,"kind":"EXISTING_UNCHANGED_PHOTO",
              "source_rights_confirmed":False,"stock_edition_confirmed":False})
            goodal_rows.append(r)
    g=inp["goodal_new"]
    new_goodal=(ROOT/g["created_original_JPG"]).read_bytes()
    if sha(new_goodal)!=g["image_SHA256"]:raise ValueError("Goodal new card hash mismatch")
    r=check_jpg(new_goodal,g["created_original_JPG"])
    r.update({"slot":4,"kind":"ORIGINAL_NONPHOTO_HOW_TO_QA","authentic_MK_logo_pending":True,
              "claimed_new_independent_photo":False})
    goodal_rows.append(r)
    goodal_rows=sorted(goodal_rows,key=lambda x:x["slot"])
    if [x["slot"] for x in goodal_rows]!=[1,2,3,4,5]:raise ValueError("Goodal storyboard slot collision")
    manifest=inp["obge_v2905"]
    obge_rows=[]
    if len(manifest["frames"])!=5:raise ValueError("OBgE frame count changed")
    for f in manifest["frames"][:4]:
        path=f["copy"];content=(ROOT/path).read_bytes()
        if sha(content)!=f["sha256"]:raise ValueError("OBgE legacy frame hash drift")
        r=check_jpg(content,path)
        r.update({"slot":f["slot"],"kind":"EXISTING_UNCHANGED_BRAND_SOURCE_PHOTO",
          "source_rights_confirmed":False,"stock_edition_confirmed":False,
          "marketing_copy_review":f.get("claim_review")})
        obge_rows.append(r)
    o=inp["obge_new"]
    new_obge=(ROOT/o["created_original_JPG"]).read_bytes()
    if sha(new_obge)!=o["JPG_SHA256"]:raise ValueError("OBgE new card hash mismatch")
    r=check_jpg(new_obge,o["created_original_JPG"])
    r.update({"slot":5,"kind":"ORIGINAL_NONPHOTO_HOW_TO_QA","authentic_MK_logo_pending":True,
        "claimed_new_independent_photo":False})
    obge_rows.append(r)
    if len({i["sha256"] for i in goodal_rows})!=5:raise ValueError("Goodal exact duplicate byte input")
    if len({i["sha256"] for i in obge_rows})!=5:raise ValueError("OBgE exact duplicate byte input")
    sets={
      "pending-21":{
       "product":"GOODAL Green Tangerine Vita-C Dark Spot Care Eye Cream, catalog 30 mL",
       "current_QA_5frame_set":goodal_rows,
       "legacy_duplicate_frame_04_excluded":a["JPG_files"][3]["SHA256"],
       "composition":"four archived product photo candidates + one original instruction graphic",
       "fully_distinct_product_photos_not_claimed":True,
       "ready_for_commercial_use":False,
       "blocking":["stocked 25AD single vs bundle proof","photo commercial reuse rights",
           "authentic original MellowKR MK PNG SHA verification","customer copy/crop and retail visual QA"]},
      "pending-09":{
       "product":"OBgE Oil Control Finisher, brand catalog 5g",
       "current_QA_5frame_set":obge_rows,
       "old_skin_portrait_candidate_05_excluded":manifest["frames"][4]["sha256"],
       "composition":"four archived OBgE source photo candidates + one original instruction graphic",
       "fully_distinct_product_photos_not_claimed":True,
       "ready_for_commercial_use":False,
       "blocking":["stocked exact 5g single pack proof","photo commercial reuse rights",
          "authentic original MellowKR MK PNG SHA verification","frame03 promotional copy and frame04 hand use commercial-rights check"]}
    }
    summary={
      "version":"v2978","parent":"v2977","project":"Shopee Thumbnail Creator PRO / 82SKU / 41 product families",
      "actual_JPGs_opened_decoded_and_SHA_verified":10,
      "new_original_text_frame_JPGs_saved_earlier":2,
      "new_scenes_from_unlicensed_external_photography":0,
      "new_jpg_created_in_this_run":0,"new_image_zip_created_in_this_run":0,
      "five_frame_storyboards":sets,"new_published_or_customer_approved":0,
      "existing_11_finished_families_preserved":True,
      "existing_55_verified_public_URLs_preserved":True,
      "customer_images_replaced_in_live_Render":0,
      "public_GitHub_upload_policy":"No unlicensed product photos reuploaded, only JSON references and wholly original instruction art",
      "do_not_repeat":["v2976 original GOODAL info frame", "v2977 original OBgE info frame",
         "v2978 unchanged-source SHA checks", "old 11 approved families and 55 URL checks"],
      "next_actions":[
        "pending-21: obtain actual owned SKU packaging 25AD 30mL single vs twin pack and commercial photo use permission, then add authenticated MK original to only the now-complete story",
        "pending-09: obtain actual owned 5g single pack, approve all four old source photo rights and logo, and review original information frame",
        "Other 28 pending families are unchanged; resume from v2975 and v2978 overlay"
      ],
      "final_xlsx_shared":False
    }
    OUT.mkdir(parents=True)
    (OUT/"manifest.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    (OUT/"five-frame-virtual-image-sets.json").write_text(json.dumps(sets,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"version":"v2978","audited_JPGs":10,"set_ids":list(sets),
      "replaced_virtual_slots":{"pending-21":4,"pending-09":5},
      "new_public":0,"legacy_urls_unchanged":55}))
if __name__=="__main__":main()
