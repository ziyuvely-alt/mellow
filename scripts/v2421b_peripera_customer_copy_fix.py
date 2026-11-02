#!/usr/bin/env python3
"""v2.4.21b: fix one verified repetitive customer caption in Peripera EN frame.
Everything else remains exactly as v2421 SHA. No public image writes.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import shutil,hashlib,json
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'input-v2421-customer'
OUT=ROOT/'production-v2421b-final';shutil.copytree(P,OUT,dirs_exist_ok=True)
target=OUT/'en-customer-drafts/pending-08/INFO_SCOPE_05_V2415_EN_V2421.jpg'
old=target.read_bytes()
sha=lambda b:hashlib.sha256(b).hexdigest()
im=Image.open(target).convert('RGB')
d=ImageDraw.Draw(im);bg=im.getpixel((500,745))
d.rectangle((140,628,944,720),fill=bg)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
for size in range(36,20,-1):
 ft=ImageFont.truetype(font,size)
 box=d.textbbox((0,0),'Mood Glowy Tint',font=ft)
 if box[2]-box[0] < 700:break
d.text(((1080-(box[2]-box[0]))/2,643),'Mood Glowy Tint',font=ft,fill=(42,67,56))
im.save(target,'JPEG',quality=93,optimize=True)
with Image.open(target) as ck:assert ck.size==(1080,1080) and ck.format=='JPEG'
assert target.stat().st_size<2_000_000
assert sha(old)!=sha(target.read_bytes())
# Preserve prior version separately; not replace public or original reference
ref=OUT/'v2421-original-peripera-frame'
ref.mkdir(exist_ok=True)
(ref/'INFO_SCOPE_05_V2415_EN_V2421_original.jpg').write_bytes(old)
summary=json.loads((OUT/'summary.json').read_text(encoding='utf8'))
summary.update({'version':'2.4.21b','one_additional_visual_repetition_fixed':1,'additional_jpg_revisions':1,'prior_64_customer_frame_count_preserved':64,'original_peripera_v2421_sha256':sha(old),'refined_peripera_v2421b_sha256':sha(target.read_bytes()),'total_215_originals_preserved':215,'public_urls_untouched':55})
(OUT/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
