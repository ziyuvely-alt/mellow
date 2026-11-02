#!/usr/bin/env python3
"""Check BBIA brand-shop original product-photo URLs; evidence only, not release approval."""
import concurrent.futures as cf
import json
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

PATH=Path('evidence/official-photos.json')
IMAGES=json.loads(PATH.read_text(encoding='utf8'))['hero_sources']

def check(p):
    url=p['url']; err=''
    for attempt in range(2):
        try:
            req=Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; BBIA-OriginalPhotoEvidence/1.0)','Accept':'image/avif,image/webp,image/jpeg,image/png,image/*'})
            with urlopen(req,timeout=22) as r:
                content=r.read(8_000_001)
                status=r.status
                ctype=r.headers.get('content-type','').split(';')[0]
            actual=(content[:3]==b'\xff\xd8\xff' or content[:8]==b'\x89PNG\r\n\x1a\n' or content[:4]==b'RIFF')
            result={'family':p['family'],'goodsNo':p['goodsNo'],'url':url,'status':'PASS' if status==200 and actual and len(content)>1500 else 'FAIL','http':status,'content_type':ctype,'byte_count':len(content),'real_image_header':actual}
            if not actual:result['error']='No recognized image signature'
            if len(content)>8_000_000:result['error']='Image too large to validate'
            return result
        except Exception as e:
            err=f'{type(e).__name__}: {e}'
            if attempt==0:time.sleep(1)
    return {'family':p['family'],'goodsNo':p['goodsNo'],'url':url,'status':'FAIL','error':err}

def main():
    with cf.ThreadPoolExecutor(max_workers=9) as ex:
        results=list(ex.map(check,IMAGES))
    good=sum(x['status']=='PASS' for x in results)
    report={'checked_at':'GitHub Actions runner timestamp','expected':len(results),'pass':good,'fail':len(results)-good,'results':results}
    Path('bbia-official-photos-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    for x in results:print(x['status'],x['goodsNo'],x['family'],x.get('http','?'),x.get('error',''),flush=True)
    print('OFFICIAL_PHOTOS_VERIFIED',good,'/',len(results))
    print('NOTE: Valid file response does not prove full shade swatches, exact current option roster, or selling-image approval.')

if __name__=='__main__':main()