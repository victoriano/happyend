import json,glob,os,re,sys
bad=[];ok=0
for fn in sorted(glob.glob('/home/claude/finales-cine/i18n/in/*.json')):
    out=fn.replace('/in/','/out/')
    if not os.path.exists(out): bad.append((os.path.basename(fn),'missing'));continue
    try: o=json.load(open(out))
    except Exception as e: bad.append((os.path.basename(fn),'json '+str(e)[:60]));continue
    i=json.load(open(fn));miss=0;es=0
    for k,v in i.items():
        for kk in v['texts']:
            t=o.get(k,{}).get(kk) if isinstance(o.get(k),dict) else None
            if not t or not isinstance(t,str): miss+=1
            elif re.search(r'[ñ¿¡]|\b(una|los|las|que|pero|sociedad|serie)\b',t): es+=1
    if miss or es>2: bad.append((os.path.basename(fn),f'miss={miss} es={es}'))
    else: ok+=1
print('ok',ok,'bad',len(bad));[print(b) for b in bad[:200] if '-q' not in sys.argv]
