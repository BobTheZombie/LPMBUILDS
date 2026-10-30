#!/usr/bin/env python3
"""Fetch a recipe's single HTTPS source, hash the source bytes, and lock SHA256SUMS.

Run this from the bundle root. By default lock all recipes in parallel.
Use --select plasma-workspace kwin to lock specific sources. No SKIP remains
in selected recipes on successful completion.
"""
import argparse, concurrent.futures, hashlib, json, pathlib, re, sys, urllib.request
ROOT=pathlib.Path(__file__).resolve().parent.parent
def lock(name, remove_invalid=False):
    recipe=ROOT/name/(name+'.lpmbuild')
    if not recipe.exists():raise ValueError('Missing recipe '+name)
    data=recipe.read_text()
    m=re.search(r'^SOURCE=\(\n\s*"(https://[^"\n]+)"\n\)',data,re.M)
    if not m:return name,'skipped (source-free meta)'
    source=m.group(1)
    req=urllib.request.Request(source,headers={'User-Agent':'LPM-SHA256-Locker/1.0'})
    h=hashlib.sha256()
    with urllib.request.urlopen(req,timeout=180) as s:
        for block in iter(lambda:s.read(1024*1024),b''):h.update(block)
    digest=h.hexdigest()
    data,number=re.subn(r'^SHA256SUMS=\(\n\s*"(?:SKIP|[0-9a-f]{64})"\n\)',
       'SHA256SUMS=(\n    "'+digest+'"\n)',data,count=1,flags=re.M)
    if number!=1:raise RuntimeError(name+': unsupported SHA256SUMS format')
    tmp=recipe.with_suffix('.lpmbuild.tmp');tmp.write_text(data);tmp.replace(recipe)
    return name,digest
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--select',nargs='+')
    ap.add_argument('--jobs',type=int,default=3)
    args=ap.parse_args()
    names=args.select or sorted(p.name for p in ROOT.iterdir() if p.is_dir() and (p/(p.name+'.lpmbuild')).exists())
    errors=0
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,args.jobs)) as pool:
        futs={pool.submit(lock,n):n for n in names}
        for f in concurrent.futures.as_completed(futs):
            name=futs[f]
            try: n,d=f.result();print(n,d,flush=True)
            except Exception as e:print(name,'ERROR',e,file=sys.stderr,flush=True);errors+=1
    return bool(errors)
if __name__=='__main__':sys.exit(main())
