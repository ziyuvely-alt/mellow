#!/usr/bin/env python3
"""v2663: Create one compact visual proof JPEG and a textual base64 view bridge.
Only existing immutable QA photos are read. No sales approval or existing file edits.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import json,base64,hashlib
root=Path('qa-review/v2662-14-candidate-snapshot')
manifest=json.loads((root/'manifest.json').read_text())
assert len(manifest['images'])==14
out=Path('qa-review/v2663-visual-proof');out.mkdir(parents=True,exist_ok=True)
board=Image.new('RGB',(1200,1280),'#eeeeee');d=ImageDraw.Draw(board)
d.text((12,10),'v2663 ORIGINAL QA IMAGES | NEVER PUBLISH',fill='black')
for k,row in enumerate(manifest['images']):
 p=root/'images'/row['filename']
 assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
 with Image.open(p) as im:
  im.load(); assert im.size==(1080,1080)
  thumb=im.convert('RGB').resize((280,280),Image.Resampling.LANCZOS)
 x=10+(k%4)*298;y=40+(k//4)*310
 board.paste(thumb,(x,y))
 d.text((x,y+282),row['family']+' | '+row['filename'][:20],fill='black')
proof=out/'v2663-all14-contact-sheet.jpg'
board.save(proof,'JPEG',quality=56,optimize=True)
(out/'v2663-all14-contact-sheet.b64.txt').write_text(base64.b64encode(proof.read_bytes()).decode('ascii'))
(out/'manifest.json').write_text(json.dumps({'version':'v2663','source':'v2662 immutable 14 JPEG branch',
 'jpg_image_count':14,'proof_sha256':hashlib.sha256(proof.read_bytes()).hexdigest(),
 'proof_bytes':proof.stat().st_size,'no_originals_modified':True,
 'approval_status':'VISUAL_REVIEW_REQUIRED'},indent=2)+'\n')
print(json.dumps({'source_images':14,'proof_bytes':proof.stat().st_size,'preview_exists':True}))
