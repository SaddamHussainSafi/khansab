#!/usr/bin/env python3
import json, sys, time, urllib.parse, urllib.request, urllib.error, datetime, os
BASE = os.path.dirname(os.path.abspath(__file__))
def load(n): return open(os.path.join(BASE,n)).read().strip()
def token(): return os.environ.get("IG_TOKEN","").strip() or load("token.txt")
CFG=json.loads(load("config.json")); TOK=token(); CAPS=json.loads(load("captions.json"))
GV=CFG["graph_version"]; IG=CFG["ig_user_id"]; POSTED=os.path.join(BASE,"posted.log")
def log(m):
    line=f"{datetime.datetime.utcnow().isoformat()}Z  {m}"; print(line,flush=True)
    open(os.path.join(BASE,"run.log"),"a").write(line+"\n")
def done(n):
    return os.path.exists(POSTED) and any(l.split("\t")[0]==str(n) for l in open(POSTED) if l.strip())
def mark(n,mid,perm): open(POSTED,"a").write(f"{n}\t{mid}\t{perm}\t{datetime.datetime.utcnow().isoformat()}Z\n")
def api(method,path,params):
    url=f"https://graph.facebook.com/{GV}/{path}"; data=urllib.parse.urlencode(params).encode()
    req=urllib.request.Request(url+"?"+data.decode()) if method=="GET" else urllib.request.Request(url,data=data,method="POST")
    try:
        with urllib.request.urlopen(req,timeout=60) as r: return json.loads(r.read())
    except urllib.error.HTTPError as e: log(f"API ERROR {e.code}: {e.read().decode()}"); raise
def due():
    try:
        from zoneinfo import ZoneInfo; today=datetime.datetime.now(ZoneInfo(CFG["timezone"])).date()
    except Exception: today=datetime.date.today()
    d=(today-datetime.date.fromisoformat(CFG["first_scheduled_date"])).days
    n=CFG["first_scheduled_poster"]+d
    return n if d>=0 and CFG["first_scheduled_poster"]<=n<=CFG["last_poster"] else None
def publish(n,dry=False,force=False):
    if done(n) and not force: return log(f"poster {n}: already posted - skip")
    e=CAPS.get(str(n))
    if not e: return log(f"poster {n}: NO CAPTION - abort")
    img=CFG["image_base_url"].format(n=f"{n:02d}")
    log(f"poster {n}: container  {img}")
    c=api("POST",f"{IG}/media",{"image_url":img,"caption":e["caption"],"access_token":TOK}); cid=c.get("id")
    if not cid: return log(f"poster {n}: container failed {c}")
    for _ in range(20):
        st=api("GET",cid,{"fields":"status_code","access_token":TOK})
        if st.get("status_code")=="FINISHED": break
        if st.get("status_code")=="ERROR": return log(f"poster {n}: ERROR {st}")
        time.sleep(5)
    else: return log(f"poster {n}: not FINISHED")
    if dry: return log(f"poster {n}: DRY ok (not published)")
    p=api("POST",f"{IG}/media_publish",{"creation_id":cid,"access_token":TOK}); mid=p.get("id")
    if not mid: return log(f"poster {n}: publish failed {p}")
    perm=api("GET",mid,{"fields":"permalink","access_token":TOK}).get("permalink","")
    mark(n,mid,perm); log(f"poster {n}: PUBLISHED {mid} {perm}")
if __name__=="__main__":
    flags={"--dry","--force"}; args=[a for a in sys.argv[1:] if a not in flags]
    dry="--dry" in sys.argv; force="--force" in sys.argv
    if args: publish(int(args[0]),dry=dry,force=force)
    else:
        n=due(); log("nothing scheduled today") if n is None else publish(n,dry=dry,force=force)
