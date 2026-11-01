#!/usr/bin/env python3
"""Plugin 6: XLSX inventory and verified photographic-source ingest.
No fabricated images. No release claim for unmatched photographs.
"""
import argparse,csv,hashlib,io,json,re,sys,urllib.request,zipfile
from collections import OrderedDict
from pathlib import Path
from xml.etree import ElementTree as ET
from PIL import Image, UnidentifiedImageError
N='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
LOCALES=['EN','TW','TH','VN','BR']

def read_sku_rows(path):
    out=[]
    with zipfile.ZipFile(path) as z:
        ss=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            ss=[''.join(t.text or '' for t in si.iter(N+'t')) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall(N+'si')]
        # Shopee mass upload's real data tab. Check for canonical columns and skip explanation rows.
        for xmlname in sorted(x for x in z.namelist() if re.fullmatch(r'xl/worksheets/sheet\d+\.xml',x)):
            tree=ET.fromstring(z.read(xmlname)); rows=tree.findall('.//'+N+'sheetData/'+N+'row')
            decoded=[]
            for row in rows:
                data={}
                for c in row.findall(N+'c'):
                    col=re.match(r'[A-Z]+',c.attrib['r']).group()
                    v=c.find(N+'v'); val=v.text if v is not None else ''
                    if c.get('t')=='s' and val: val=ss[int(val)]
                    elif c.get('t')=='inlineStr':val=''.join(t.text or '' for t in c.iter(N+'t'))
                    data[col]=val or ''
                decoded.append((int(row.get('r')),data))
            if not any(d.get('B')=='Product Name' and d.get('D')=='Parent SKU' for _,d in decoded):continue
            for rowno,d in decoded:
                if rowno<7 or not d.get('D') or not (d.get('M') or d.get('B')):continue
                if d.get('D').startswith('Please input'):continue
                out.append({'source_file':path.name,'source_sheet':xmlname,'row':rowno,
                 'parent_sku':d['D'],'product':d.get('B',''),'option':d.get('G',''),'option_sku':d.get('M',''),
                 'images':[{'column':col,'url':d.get(col,'')} for col in ['H','N','O','P','Q','R','S'] if d.get(col,'').startswith(('https://','http://'))]})
            break
    return out

def inventory(paths):
    rows=sum((read_sku_rows(Path(p)) for p in paths),[])
    groups=OrderedDict()
    for r in rows:
        key=r['parent_sku'].strip()
        fam=groups.setdefault(key,{'key':key,'sku_count':0,'product_name':r['product'], 'options':[], 'sources':[],'source_files':set()})
        fam['sku_count']+=1
        if r['product'] and not fam['product_name']:fam['product_name']=r['product']
        if r['option']:fam['options'].append(r['option'])
        fam['source_files'].add(r['source_file'])
        for img in r['images']:
            if img['url'] not in [i['url'] for i in fam['sources']]:fam['sources'].append(img)
    for fam in groups.values():fam['source_files']=sorted(fam['source_files'])
    return rows,list(groups.values())

def fetch_jpg(url, timeout=15):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; ShopeeZIPStudio/0.1)'})
    with urllib.request.urlopen(req,timeout=timeout) as res:
        data=res.read(12_000_000+1)
    if len(data)>12_000_000:raise ValueError('too large')
    im=Image.open(io.BytesIO(data));im.verify()
    im=Image.open(io.BytesIO(data));w,h=im.size
    if w<500 or h<500:raise ValueError(f'low-resolution source {w}x{h}')
    if im.format not in ('JPEG','PNG','WEBP'):raise ValueError(f'unsupported format {im.format}')
    return data,im.format,(w,h)

def run(args):
    target=Path(args.output);target.mkdir(parents=True,exist_ok=True)
    rows,fams=inventory(args.xlsx)
    (target/'inventory.json').write_text(json.dumps({'sku_rows':len(rows),'families':fams,'locales':LOCALES},ensure_ascii=False,indent=2),encoding='utf-8')
    with (target/'family_manifest.csv').open('w',newline='',encoding='utf-8-sig') as f:
        wr=csv.writer(f);wr.writerow(['Product family','SKU rows','Option count','URL candidates','Status'])
        for fam in fams:wr.writerow([fam['key'],fam['sku_count'],len(fam['options']),len(fam['sources']),'AWAITING_VERIFIED_SOURCE'])
    records=[];downloaded=0
    if args.download:
        srcdir=target/'source_candidates';srcdir.mkdir(exist_ok=True)
        for n,fam in enumerate(fams,1):
            for i,entry in enumerate(fam['sources'],1):
                if downloaded>=args.max_downloads:break
                url=entry['url'];name=f'{n:03d}_{i:02d}'
                try:
                    data,fmt,sz=fetch_jpg(url);ext={'JPEG':'jpg','PNG':'png','WEBP':'webp'}[fmt]
                    path=srcdir/(name+'.'+ext);path.write_bytes(data);downloaded+=1
                    records.append({'family':fam['key'],'url':url,'file':str(path.relative_to(target)),
                      'size':len(data),'dimensions':sz,'sha256':hashlib.sha256(data).hexdigest(),'status':'CANDIDATE_NEEDS_PRODUCT_MATCH'})
                except Exception as e:records.append({'family':fam['key'],'url':url,'status':'FETCH_FAILED','error':str(e)[:300]})
            if downloaded>=args.max_downloads:break
    (target/'source_ledger.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    report={'total_sku_rows':len(rows),'total_families':len(fams),'downloaded_source_candidates':downloaded,
       'complete_sale_ready_jpg':0,'complete_family_zips':0,'status':'SOURCE_INGEST_ONLY_NOT_SALE_READY',
       'warning':'Downloaded candidate images have not been matched to exact package and shade. No fabricated sale-ready images.'}
    (target/'run_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    out=Path(args.zip);out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for f in target.rglob('*'):
            if f.is_file():z.write(f,f.relative_to(target))
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('xlsx',nargs='+');p.add_argument('--output',default='build');p.add_argument('--zip',default='BBIA_SOURCE_INGEST.zip');p.add_argument('--download',action='store_true');p.add_argument('--max-downloads',type=int,default=20);run(p.parse_args())
