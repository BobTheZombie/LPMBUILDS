#!/usr/bin/env python3
import collections, json, pathlib, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parent.parent
obj=json.loads((ROOT/'package-chain.json').read_text())
packs=obj['packages']; issue=[];count=0
for n,p in packs.items():
    f=ROOT/n/(n+'.lpmbuild')
    if not f.is_file():issue.append('missing: '+str(f));continue
    s=f.read_text();count+=1
    if subprocess.run(['bash','-n',str(f)]).returncode: issue.append('invalid shell: '+n)
    if p['family']!='Meta' and 'SHA256SUMS=(' not in s:issue.append('missing digest: '+n)
    if p['family']!='Meta' and '"SKIP"' in s:issue.append('UNLOCKED SHA256: '+n)
print('Recipes:',count,'/ expected',len(packs))
for e in issue:print(e)
returncode=1 if issue else 0
sys.exit(returncode)
