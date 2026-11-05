#!/usr/bin/env python3
"""v2878 | 26AD, 4g, peripera Mood Glowy Tint inventory 001..020 exact-edition
online photo discovery. NEVER reuse older "INK Mood Glowy Tint" photos.

One bounded pass over retailer Hwahae's known 26AD product records
76650..76669, validate title vs *official user's stock options*, extract
real source image with original source SHA, and keep all originals in a
NEW internal QA folder. 04/06/07 are OliveYoung exclusives per peripera's
own account, do not delete these even when not listed at this merchant.
No 021..030 or -01/-02 options; no fabricated RGB swatches.

All unlicensed external images are QA references only. If merchant source
low-resolution, does not visibly show a unique shade, or title mismatches,
report HOLD. No commercial use, public URL writes, spreadsheet, or
changes to already approved source PNGs.
"""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urljoin
from hashlib import sha256
from html import unescape as htmlunescape
from PIL import Image,ImageOps,ImageDraw,ImageFont
from io import BytesIO
import re,json,os,time

from bs4 import BeautifulSoup

R=Path("qa-review")
OLD=R/"v2853-peripera-26AD-vs-legacy-20-option-block"/"manifest.json"
STATE=R/"v2877-mini-21N-alternate-original-and-30family-delta-QA"/"stock30-delta-next-queue.json"
OUT=R/"v2878-peripera-26AD-20-shade-exact-edition-original-photo-QA"
assert OLD.exists() and STATE.exists() and not OUT.exists()
prior=json.loads(OLD.read_text());previous=json.loads(STATE.read_text())
assert prior["version"]=="v2853" and len(prior["rows"])==20
assert previous["version"]=="v2877" and previous["family_count"]==30
expected={r["shade"]:r for r in prior["rows"]}
assert list(sorted(expected))==[f"{i:02d}" for i in range(1,21)]
exclusive={"04","06","07"}
assert set(prior["absent_from_checked_official_store_numbers"])==exclusive

OUT.mkdir(parents=True)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
ft=lambda n,b=False:ImageFont.truetype(B if b else F,n)
sha=lambda p:sha256(p.read_bytes()).hexdigest()
client_header={
 "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
 "Accept":"text/html,application/xhtml+xml,image/avif,image/webp,image/png,image/jpeg,*/*",
 "Accept-Language":"ko-KR,ko;q=0.9,en-US;q=0.7",
}
html_parser=re.compile(r"(?:26\s*AD|26AD).*?\[\s*0?(\d{1,3})\s+([^\]\n]{1,32})\]",re.I|re.S)
source_rows={}
page_audit=[]
previews=[]
bad_net=0
for good_id in range(76650,76670):
 url=f"https://www.hwahae.co.kr/goods/{good_id}"
 log={"goods_id":good_id,"url":url,"status":"HOLD_PAGE_FETCH"}
 try:
  with urlopen(Request(url,headers=client_header),timeout=13) as res:
   body=res.read(2_300_000)
  if not body or len(body)<2000:raise ValueError("EMPTY_OR_SMALL_HTML")
  html=body.decode("utf-8","replace")
  soup=BeautifulSoup(html,"html.parser")
  t=soup.title.get_text(" ",strip=True) if soup.title else ""
  og_title=soup.find("meta",attrs={"property":"og:title"})
  if og_title:t=og_title.get("content") or t
  t=htmlunescape(t)
  log["page_title"]=t[:220]
  assert "페리페라" in t and "26AD" in t and "무드" in t,(t[:90],"UNRELATED_PAGE")
  match=html_parser.search(t)
  assert match is not None,("TITLE_SHADE_MISSING",t[:120])
  n=int(match.group(1))
  shade=f"{n:02d}"
  label=match.group(2).strip()
  log.update(shade=shade,product_shade_name=label)
  assert shade in expected,("NOT_01_TO_20",shade)
  should=expected[shade]
  correct=should["verified_clio_operated_retail_name"] or should["stock_name"]
  # Official v2853 stock 14 typo is an EXPLICIT isolated exception.
  if shade=="14":correct="로지위시"
  # 12 and 17 vary by spacing but official spelling is preserved via
  # the brand release, never edit original inventory.
  norm=lambda s:re.sub(r"\s+|[?？.,]","",s)
  assert norm(label)==norm(correct),("NAME_MISMATCH",label,correct)
  assert shade not in source_rows,("DUPLICATE_SHADE_PAGE",shade)
  meta=soup.find("meta",attrs={"property":"og:image"})
  candidates=[]
  if meta:
   val=htmlunescape(meta.get("content",""))
   if val:candidates.append(val)
  # HTML includes structured product image URLs; keep only same retailer
  # or the Hwahae CDN, and do not infer image from another shade.
  for src in re.findall(r'https?[^"\s<>]{15,420}',html):
   candidate=htmlunescape(src).replace("\\/","/").replace("&amp;","&")
   if "img.hwahae.co.kr/commerce/goods/" in candidate:
    candidates.append(candidate)
  candidates=list(dict.fromkeys(candidates))
  log["candidate_image_URLs"]=len(candidates)
  saved=False
  for pic_url in candidates[:6]:
   pic_url=pic_url.split("#",1)[0]
   if not pic_url.startswith("https://"):continue
   if not any(host in pic_url for host in ("img.hwahae.co.kr/","www.hwahae.co.kr/")):continue
   try:
    with urlopen(Request(pic_url,headers={"User-Agent":client_header["User-Agent"],"Accept":"image/*,*/*"}),timeout=12) as res:
     raw=res.read(6_000_001)
    if not 4000<len(raw)<6_000_000:continue
    with Image.open(BytesIO(raw)) as im:
     im.load();nat=im.size;fmt=im.format
     if fmt not in {"JPEG","PNG","WEBP"} or min(nat)<450:continue
     photo=im.convert("RGB")
    ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[fmt]
    root=OUT/f"26AD-{shade}-{label}-Hwahae-original.{ext}"
    root.write_bytes(raw)
    display=Image.new("RGB",(1080,1080),"#F9F9FB")
    d=ImageDraw.Draw(display)
    d.rounded_rectangle((38,39,1042,1042),radius=23,outline="#DED7E3",width=2)
    d.text((72,66),"peripera | MOOD GLOWY TINT 26AD",font=ft(30,True),fill="#403744")
    d.rounded_rectangle((72,132,1006,206),radius=13,fill="#F0E9F1")
    d.text((86,153),shade+"  "+label+"   |   4g   |   SOURCE QA",font=ft(21,True),fill="#544559")
    fit=ImageOps.contain(photo,(930,722),Image.Resampling.LANCZOS)
    display.paste(fit,((1080-fit.width)//2,220+(722-fit.height)//2))
    d.text((72,981),"NOT SALES  /  EXACT STOCK + LICENSE + VISUAL QA PENDING",font=ft(17,True),fill="#796B7C")
    out=OUT/f"26AD-{shade}-1080-real-retailer-image-QA.jpg"
    display.save(out,"JPEG",quality=92,subsampling=0,optimize=True)
    with Image.open(out) as z:assert z.format=="JPEG" and z.size==(1080,1080)
    assert out.stat().st_size<2_000_000
    rec={"shade":shade,"name":label,"page":url,
         "source_url":pic_url,"source_file":str(root),"source_sha256":sha(root),
         "source_native_pixels":list(nat),"source_format":fmt,
         "new_1080_JPG":str(out),"jpg_sha256":sha(out),"JPG_bytes":out.stat().st_size,
         "product_version_page":"26AD","retail_licensed":False,
         "source_specific_shade_photo":True,
         "visual_unique_product_version_authenticated":False,
         "original_RGB_swatches_recolored":False,"sale_approved":False}
    source_rows[shade]=rec
    previews.append((shade,display))
    log.update(status="26AD_NAMED_PAGE_AND_SOURCE_PHOTO_QA_SAVED",source_native_pixels=nat)
    saved=True
    break
   except Exception as im_err:
    log["image_last_error"]=type(im_err).__name__+":"+str(im_err)[:140]
  if not saved:log["status"]="26AD_NAMED_PAGE_FOUND_IMAGE_NOT_AVAILABLE"
  bad_net=0
 except Exception as exc:
  log.update(status="HOLD_NO_VALID_26AD_PRODUCT_PAGE",error=type(exc).__name__+": "+str(exc)[:180])
  if any(z in str(exc) for z in ("HTTP Error 403","HTTP Error 429","Forbidden")):
   bad_net+=1
  else:bad_net=0
 page_audit.append(log)
 if bad_net>=2:
  page_audit.append({"status":"STOP_SAME_ACCESS_FAILURE_TWICE_SWITCH_TO_OFFICIAL_NAME_EVIDENCE","at_goods_id":good_id})
  break
# Build source-only visual contact as paging, no extra photos and no
# incorrect cross-edition collage. For every image, keep its source title.
contact_files=[]
for offset in range(0,len(previews),8):
 group=previews[offset:offset+8]
 cols=4
 rows=(len(group)+cols-1)//cols
 board=Image.new("RGB",(2080,60+rows*560),"#F2EEF3")
 d=ImageDraw.Draw(board)
 d.text((14,10),"v2878 | ORIGINAL 26AD SOURCE PHOTO REFERENCES | LICENSE & STOCK HOLD",font=ft(22,True),fill="#4B4150")
 for idx,(shade,img) in enumerate(group):
  im=img.resize((505,505),Image.Resampling.LANCZOS)
  x=14+idx%cols*515;y=50+idx//cols*560
  board.paste(im,(x,y))
  d.text((x+5,y+515),f"26AD NO.{shade}  /  UNLICENSED QA",font=ft(17,True),fill="#625469")
 file=OUT/f"v2878-26AD-exact-edition-contact-{offset//8+1:02d}-QA.jpg"
 board.save(file,"JPEG",quality=88,optimize=True)
 contact_files.append({"path":str(file),"sha256":sha(file),"shade_numbers":[x[0] for x in group]})
# 26AD original 001..020 scope remains 20, no absent option deletion.
records=[]
for n in [f"{i:02d}" for i in range(1,21)]:
 p=expected[n]
 r={"shade":n,"inventory_option":p["inventory_option"],
    "legacy_mismatched_photo_quarantined":True,
    "peripera_oliveyoung_only":n in exclusive,
    "brand_official_name":("로지위시" if n=="14" else p["verified_clio_operated_retail_name"] or p["stock_name"]),
    "stock_name_mismatch":"로지워시/로지위시" if n=="14" else None,
    "owner_inventory_unchanged":True}
 if n in source_rows:r.update(status="26AD_REAL_PHOTO_CANDIDATE_AWAIT_VISUAL_LICENSE",candidate=source_rows[n])
 else:r.update(status="HOLD_NO_HIGH_RES_RETAIL_PRODUCT_PHOTO",candidate=None)
 records.append(r)
assert len(records)==20 and all(x["legacy_mismatched_photo_quarantined"] for x in records)
summary={"version":"v2878","baseline":"v2877","family":"pending-08",
 "product":"peripera Mood Glowy Tint 26AD 4g","current_scope_01_to_20":True,
 "n_inventory_options":20,
 "n_26AD_exact_edition_photo_candidates":len(source_rows),
 "retailer_page_requests":len([x for x in page_audit if "goods_id" in x]),
 "retailer_range":"Hwahae 76650..76669","photo_candidate_count":len(source_rows),
 "brand_channel_official_reference":"https://pf.kakao.com/_SZjzG",
 "brand_channel_oliveyoung_exclusive_shades":["04","06","07"],
 "brand_channel_14_name":"로지위시",
 "stock_014_typo_not_modified":True,
 "prior_old_ink_mood_glowy_photos_20_quarantined":True,
 "stock_04_06_07_never_deleted":True,
 "excluded_21_to_30_and_negative01_negative02":True,
 "no_fake_swatch_or_recolor":True,
 "per_shade":records,"page_attempt_log":page_audit,
 "contact_files":contact_files,
 "photo_original_rights_granted":False,
 "exact_owned_stock_packaging_matches_26AD_proved":False,
 "new_sales_approvals":0,"new_public_URLs":0,
 "old_11_finished_families_untouched":True,
 "old_55_public_URLs_unchanged":True,
 "original_inventory_spreadsheet_changed":False,
 "final_XLSX_shared":False,
 "next":"Visually inspect native source images for correct 26AD tube/artwork, reject near-duplicate cross-shade product photos; locate genuine correct 04/06/07 OliveYoung-only source, do not revive 20 legacy INK images. Then continue pending06 giftset duplicate-photo gap and pending12 unit mismatch."
}
(OUT/"manifest.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2878","new_exact_edition_photo_QA":len(source_rows),
 "missing_shades":[r["shade"] for r in records if r["candidate"] is None],
 "oliveyoung_exclusives":["04","06","07"],"sales_approved":0},ensure_ascii=False))
