#!/usr/bin/env python3
"""v2910 10-frame immutable historical Dr.G image QA.
Do NOT restore or edit old assets. This is contact-sheet and issue classification only.
"""
from pathlib import Path
from io import BytesIO
from hashlib import sha256
from PIL import Image, ImageDraw, ImageOps, ImageFont
import subprocess, json, time

ROOT=Path("qa-review")
PRE=ROOT/"v2909-missha-pdrn-v2908-four-photo-visual-and-duplicate-QA"/"stock30-incremental-state-v2909.json"
OUT=ROOT/"v2910-drg-2022-red-and-2023-moisture-sun-10-existing-image-qa"
state=json.loads(PRE.read_text())
assert state["version"]=="v2909" and len(state["families"])==30 and not OUT.exists()
DATA={
 "pending-16":{
 "name":"Dr.G R.E.D Blemish Clear Soothing Cream 70mL, 2022 old edition",
 "sha":"0d261a616cacb756108936ff05e520ec22e5f5fe",
 "folder":"public/owned86/20261029/drg-red-blemish-clear-soothing-cream-70ml",
 "files":["a68f9b0956a1_01.jpg","17c12aad66a7_02.jpg","3ff07100b8f5_03.jpg","3f4aa0b81985_04.jpg","0a62a56a4b28_05.jpg"],
 "inspection":[
  ("OLD_JAR_FRONT","Old label R.E.D BLEMISH green-band 70mL jar appears; exact owned 2022 label not confirmed",[]),
  ("MODEL_HOLD","Model holding visibly green-band Dr.G jar, third-party portrait/model release needed",["MODEL_PHOTO_RIGHTS"]),
  ("HANDS_HOLD","Open jar with finger in cream, old green-band visible, rights/edition hold",["HAND_PHOTO_RIGHTS"]),
  ("OLD_JAR_CLOSEUP","Close-up front jar marked R.E.D BLEMISH, green-band, no visible EX word",[]),
  ("OPEN_OLD_JAR","Open cream jar label and texture, 70mL text visible",[])
 ]},
 "pending-17":{
 "name":"Dr.G Brightening Up Moisture Sun 50mL, 2023 edition",
 "sha":"1eff81ba41fe71740e18ac1793efaa7f26f90430",
 "folder":"public/owned86/20261029/drg-brightening-up-moisture-sun-50ml",
 "files":["1901d1e8f6d5_01.jpg","a7f643fda435_02.jpg","2ca0483b69b3_03.jpg","942c208e9bfe_04.jpg","22c81ed5d01a_05.jpg"],
 "inspection":[
  ("TUBE_HERO","Beige 50mL tube, orange sun logo; confirms visual Moisture Sun edition only, not actual stock",["SPF_CLAIM_NEEDS_LABEL_CHECK"]),
  ("MODEL_HANDS_HOLD","Tube applied over arms and held in hands; image usage/model rights not verified",["MODEL_HANDS_RIGHTS"]),
  ("TUBE_USAGE","Tube dispenses cream onto fingertip; package partially cropped",["HANDS_RIGHTS","SUNSCREEN_USE_CLAIMS_VERIFY"]),
  ("TUBE_DETAIL","Beige tube with cap off and cream line; 'Vegan' in footer must be supported or removed before sale",["VEGAN_CLAIM_UNVERIFIED","SPF_CLAIM_NEEDS_LABEL_CHECK"]),
  ("TEXTURE_ONLY","Beige cream strokes show texture, cannot independently prove exact product edition",["TEXTURE_NOT_STOCK_PROOF"])
 ]}
}
def git_bytes(commit,path):
 p=subprocess.run(["git","show",f"{commit}:{path}"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 if p.returncode:raise RuntimeError(f"immutable source missing {commit[:9]}:{path}: "+p.stderr.decode(errors="replace")[:130])
 return p.stdout
def on_current_main(path):
 p=subprocess.run(["git","cat-file","-e",f"origin/main:{path}"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 return p.returncode==0
def font(sz):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",sz)
 except:return ImageFont.load_default()
def panel(family, photos, records):
 w,h=1080,1080
 canvas=Image.new("RGB",(w,h),"#f5f6f5");dr=ImageDraw.Draw(canvas)
 dr.text((25,17),family.upper()+" | LEGACY PHOTO/CLAIM QC | v2910",font=font(29),fill="#242424")
 dr.text((25,64),"Reference-only, NO stock edition / MK logo / photo rights approval",font=font(18),fill="#a13636")
 for i,(im,rr) in enumerate(zip(photos,records)):
  row,col=divmod(i,3);x=20+col*353;y=111+row*452
  dr.rounded_rectangle((x,y,x+340,y+425),radius=8,fill="white",outline="#cccccc",width=2)
  small=ImageOps.contain(im,(320,330),Image.Resampling.LANCZOS)
  canvas.paste(small,(x+170-small.width//2,y+8+(330-small.height)//2))
  dr.text((x+10,y+350),f"{i+1:02} {rr['role']}",font=font(15),fill="#292929")
  status="CURRENT MAIN" if rr["present_in_current_main"] else "HISTORY ONLY"
  dr.text((x+10,y+382),status+"  |  NOT RETAIL APPROVED",font=font(13),fill="#9c2626")
 dr.text((25,1030),"Old source files unchanged. This QA image is NOT a customer-facing image.",font=font(17),fill="#565656")
 return canvas

OUT.mkdir(parents=True)
results=[]
for family,s in DATA.items():
 ims=[];records=[]
 for i,name in enumerate(s["files"]):
  path=s["folder"]+"/"+name
  b=git_bytes(s["sha"],path)
  with Image.open(BytesIO(b)) as raw:
   raw.load()
   assert raw.format=="JPEG" and raw.size==(1080,1080) and len(b)<2_000_000,(path,raw.size,len(b))
   im=ImageOps.exif_transpose(raw).convert("RGB")
  role,note,flags=s["inspection"][i]
  row={"slot":i+1,"role":role,"existing_immutable_history_source":f"{s['sha']}:{path}",
   "source_bytes_sha256":sha256(b).hexdigest(),
   "image_format":"JPEG","image_pixels":[1080,1080],"image_bytes":len(b),
   "present_in_current_main":on_current_main(path),
   "visual_observation":note,"blocking_flags":flags+["UNAUTHENTICATED_MK_LOGO_IN_ARTWORK","EXACT_OWNED_STOCK_EDITION_UNCONFIRMED","PHOTO_COMMERCIAL_USE_RIGHTS_UNCONFIRMED"],
   "photo_rights_verified":False,"retail_approved":False}
  ims.append(im);records.append(row)
 out=OUT/(family+"-five-existing-frames-1080-INTERNAL-QA.jpg")
 panel(family,ims,records).save(out,"JPEG",quality=90,optimize=True,subsampling=0)
 with Image.open(out) as ch:assert ch.format=="JPEG" and ch.size==(1080,1080)
 assert out.stat().st_size<2_000_000
 any_missing=sum(not r["present_in_current_main"] for r in records)
 results.append({"family":family,"name":s["name"],"original_commit":s["sha"],
    "existing_history_photos_validated":5,"missing_from_current_main":any_missing,
    "old_files_recovered_in_history_without_restoring_public_assets":True,
    "comparison_path":str(out),"frames":records,
    "retail_status":"UNAPPROVED_EXACT_STOCK_MK_LOGO_RIGHTS_HOLD"})
 st=state["families"][family]
 st.update({"last_delta_version":"v2910",
  "release_status":"HISTORICAL_FIVE_EXISTING_JPG_QA_CHECKED_EDITION_RIGHTS_MK_HOLD",
  "v2910_existing_5frames_historical_commit":s["sha"],
  "v2910_5frame_current_main_missing_count":any_missing,
  "v2910_contact_QA_path":str(out),
  "latest_photo_QA_checkpoint":f"v2910: 5 immutable original 1080 JPG inspected; {any_missing} absent on current main. Old edition visual and model/marketing text flagged. No release; actual stock edition, genuine MK logo and commercial rights HOLD.",
  "sale_approved":False})
report={"version":"v2910","baseline":"v2909","generated_at_UTC":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "old_10_JPGs_inspected":10,"new_internal_visual_QA_contact_JPGs":2,
 "old_image_bytes_rewritten":0,"previous_public_image_URLs_changed":0,"existing_commercial_11_families_modified":0,
 "old_55_verified_public_URLs_protected":True,"sales_release_approvals":0,"new_retail_images_published":0,
 "original_MK_logo_verified":False,"stock_batch_reconciled":False,"photo_commercial_rights_verified":False,
 "cases":results,"final_spreadsheet_shared":False}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
state["version"]="v2910";state["baseline"]="v2909";state["new_sales_approvals"]=0;state["new_public_URLs"]=0;state["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2910.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2910","historical_images_inspected":10,"new_QA_contact_JPGs":2,
 "missing_on_current_main":{x["family"]:x["missing_from_current_main"] for x in results},
 "new_sales_approvals":0},ensure_ascii=False))
