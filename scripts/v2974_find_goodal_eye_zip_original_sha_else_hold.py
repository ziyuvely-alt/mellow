#!/usr/bin/env python3
"""v2974: one-pass exact-match recovery search of existing GOODAL eye cream frames.
This is an alternative to repeatedly downloading ZIPs. Output JSON only.
"""
from pathlib import Path
import hashlib,io,json,zipfile
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa-review/v2974-goodal-eyecream-same-SHA-original-candidate-search-20261106"
V2973=ROOT/"qa-review/v2973-goodal-eyecream-duplicate-false-alarm-resolution-20261106/manifest.json"
V2970=ROOT/"qa-review/v2970-remaining-stock-archive-audit-no-new-binary-20261106/manifest.json"

def sha(b):return hashlib.sha256(b).hexdigest()
def ah(im):
    p=list(im.convert("L").resize((9,8),Image.Resampling.LANCZOS).getdata())
    return "".join("1" if p[y*9+x]>p[y*9+x+1] else "0" for y in range(8) for x in range(8))
def hd(a,b):return sum(x!=y for x,y in zip(a,b))
def main():
    if OUT.exists():raise RuntimeError("v2974 exists, never redo")
    old=json.loads(V2973.read_text(encoding="utf8"))
    v2970=json.loads(V2970.read_text(encoding="utf8"))
    src=v2970["results"]["pending-21"]
    archive=ROOT/src["archive"]
    if sha(archive.read_bytes())!=src["archive_SHA256"]:raise RuntimeError("source ZIP changed")
    with zipfile.ZipFile(archive) as z:
        names=[x.filename for x in z.infolist() if x.filename.lower().endswith(".jpg")]
        if len(names)!=5:raise RuntimeError("expected five source entries")
        target={slot:z.read(names[slot-1]) for slot in (3,4)}
    target_hash={s:sha(b) for s,b in target.items()}
    reference_hash={int(k):v["reference_sha256"] for k,v in old["source_mapping"].items()}
    if any(target_hash[s]!=old["source_mapping"][str(s)]["archived_sha256"] for s in (3,4)):
        raise RuntimeError("v2973 target byte hash changed")
    target_d={}
    for s,b in target.items():
        with Image.open(io.BytesIO(b)) as im:im.load();target_d[s]=ah(im)
    candidates=[]
    for path in (ROOT/"qa-review").rglob("*"):
        if path.suffix.lower() not in (".jpg",".jpeg",".png",".webp"):continue
        name=path.as_posix().lower()
        if ("pending-21" not in name and "goodal" not in name and "eyecream" not in name):continue
        data=path.read_bytes()
        digest=sha(data)
        if digest in target_hash.values() or digest in reference_hash.values():
            candidates.append({"path":str(path.relative_to(ROOT)),
                "sha256":digest,"direct_target_slots":[s for s,k in target_hash.items() if k==digest],
                "already_reviewed_legacy_reference":[s for s,k in reference_hash.items() if k==digest]})
    exact={s:[x["path"] for x in candidates if s in x["direct_target_slots"]] for s in (3,4)}
    # If exact hits do not exist as standalone JPGs, only report metric.
    # Do NOT infer duplicate photos from near-identical dHash or trust a different reference image.
    unresolved=[s for s in (3,4) if not exact[s]]
    state="BOTH_MATCHING_STANDALONE_FOUND" if not unresolved else "ONE_OR_MORE_ARCHIVED_FRAME_HAS_NO_STANDALONE_MATCH"
    out={
      "version":"v2974","prior":"v2973","project":"Shopee Thumbnail Creator PRO / 82 SKU, 41 families",
      "family":"pending-21","product":"GOODAL 25AD eye cream 30mL",
      "method":"One offline-pass SHA256 search across only already-committed relevant JPG/PNG paths; no web re-fetch or new photo creation.",
      "archived_sha256":target_hash,"matching_existing_standalone_paths":exact,
      "standalone_matches_recorded":candidates,"unresolved_slots":unresolved,
      "outcome":state,
      "aHash_distance_archived_3_vs_4":hd(target_d[3],target_d[4]),
      "not_proven":"Distinctness of exact archived frames until directly visually inspected; actual stock single/two pack, commercial rights, original MK",
      "replacement_action":"Do not delete/replace either candidate merely for hash similarity. Verify true archived frames or hold only that specific issue, not all other products.",
      "new_image_bytes_created":0,"new_public_urls":0,"new_retail_approved":0,
      "legacy_published_product_families_preserved":11,"legacy_verified_URLs_preserved":55,
      "audit_v2970_result":"19 other archive ZIPs, 130 JPG/PNG files inspected",
      "audit_v2971_result":"16 loose JPG refs inspected, Peripera JPG/PNG 01-20 structurally verified",
      "latest_rollup":"v2972 30-family release hold remains authoritative for all other families",
      "public_repo_rule":"Do not store new unlicensed binary images on public GitHub",
      "final_spreadsheet_shared":False
    }
    OUT.mkdir(parents=True)
    (OUT/"manifest.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"version":"v2974","outcome":state,"matches":{str(s):len(exact[s]) for s in (3,4)},
                      "new_images":0,"new_public_urls":0}))
if __name__=="__main__":main()
