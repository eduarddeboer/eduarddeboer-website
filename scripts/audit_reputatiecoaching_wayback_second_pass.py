#!/usr/bin/env python3
from __future__ import annotations

import argparse, html, json, re, time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REPORT_ROOT = ROOT / "data" / "archive" / "link-repair"
PODCAST_ROOT = ROOT / "content" / "nl" / "archief" / "reputatiecoaching"
USER_AGENT = "eduarddeboer.com-wayback-second-pass/1.0 (+https://eduarddeboer.com/)"
RC_HOSTS = {"reputatiecoaching.nl", "www.reputatiecoaching.nl", "dev.reputatiecoaching.nl"}

def norm_text(v: str) -> str:
    v = html.unescape(v).lower()
    v = re.sub(r"[^a-z0-9]+", " ", v)
    return " ".join(v.split())

def normalize_url(v: str) -> str:
    v = html.unescape(v.strip())
    p = urlsplit(v)
    host = (p.hostname or "").lower()
    port = p.port
    netloc = host
    if port and not ((p.scheme == "http" and port == 80) or (p.scheme == "https" and port == 443)):
        netloc = f"{host}:{port}"
    return urlunsplit((p.scheme.lower(), netloc, p.path or "/", p.query, ""))

def episode_date(number: int) -> str:
    path = PODCAST_ROOT / f"{number:03d}" / "index.md"
    if not path.exists():
        return ""
    m = re.search(r"(?m)^date:\s*['\"]?([^'\"\n]+)", path.read_text(encoding="utf-8"))
    return re.sub(r"[^0-9]", "", m.group(1))[:8] if m else ""

def collect_unlinked():
    occurrences = []
    for path in sorted(REPORT_ROOT.glob("batch-???-???.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for ep in data.get("episodes", []):
            number = int(ep["episode"])
            d = episode_date(number)
            for link in ep.get("links", []):
                if link.get("action") != "unlinked":
                    continue
                occurrences.append({
                    "episode": number,
                    "date": d,
                    "label": link.get("label") or "",
                    "url": normalize_url(link.get("original_url") or ""),
                    "kind": link.get("kind") or "",
                })
    return occurrences

def parse_old_repo(old_repo: Path):
    by_path = {}
    by_slug = defaultdict(list)
    by_title = defaultdict(list)
    for path in old_repo.glob("content/**/*.md"):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        fm = re.match(r"^---\n([\s\S]*?)\n---", text)
        if not fm:
            continue
        front = fm.group(1)
        um = re.search(r"(?m)^url:\s*['\"]?([^'\"\n]+)", front)
        if not um:
            continue
        u = um.group(1).strip()
        if not u.startswith("/"):
            continue
        if not u.endswith("/") and "." not in u.rsplit("/",1)[-1]:
            u += "/"
        by_path[u] = {"url":u, "source":str(path.relative_to(old_repo))}
        slug = u.strip("/").split("/")[-1]
        if slug:
            by_slug[slug].append(u)
        tm = re.search(r"(?m)^title:\s*['\"]?([^'\n]+?)['\"]?\s*$", front)
        if tm:
            by_title[norm_text(tm.group(1))].append(u)
    return by_path, by_slug, by_title

def variants(url: str, extra_paths=()):
    p = urlsplit(normalize_url(url))
    host = (p.hostname or "").lower()
    hosts = [host]
    if host in RC_HOSTS:
        hosts += ["reputatiecoaching.nl", "www.reputatiecoaching.nl", "dev.reputatiecoaching.nl"]
    else:
        if host.startswith("www."):
            hosts.append(host[4:])
        elif host:
            hosts.append("www." + host)
    hosts = list(dict.fromkeys(h for h in hosts if h))
    paths = [p.path or "/"]
    paths.extend(extra_paths)
    expanded = []
    for path in paths:
        if not path.startswith("/"): path = "/" + path
        expanded.append(path)
        if path != "/":
            expanded.append(path.rstrip("/") if path.endswith("/") else path + "/")
    paths = list(dict.fromkeys(expanded))
    queries = [p.query]
    if p.query:
        queries.append("")
    out=[]
    for h in hosts:
        for scheme in ["http","https"]:
            for path in paths:
                for q in queries:
                    candidate=urlunsplit((scheme,h,path,q,""))
                    if candidate not in out:
                        out.append(candidate)
    return out[:24]

def get_json(url: str, timeout=12.0):
    req=Request(url,headers={"User-Agent":USER_AGENT,"Accept":"application/json"})
    with urlopen(req,timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8","replace"))

def available(candidate: str, stamp: str):
    params={"url":candidate}
    if stamp: params["timestamp"]=stamp
    url="https://archive.org/wayback/available?"+urlencode(params)
    try:
        data=get_json(url)
    except Exception:
        return None
    c=(data.get("archived_snapshots") or {}).get("closest")
    if not isinstance(c,dict) or not c.get("available"):
        return None
    status=str(c.get("status") or "")
    if status not in {"","200"}: return None
    u=str(c.get("url") or "")
    ts=str(c.get("timestamp") or "")
    if u.startswith("http://web.archive.org/"):
        u="https://"+u[len("http://"):]
    return {"capture_url":u,"timestamp":ts,"candidate":candidate,"method":"available"}

def cdx(candidate: str, stamp: str):
    params=[
        ("url",candidate),("output","json"),
        ("fl","timestamp,original,statuscode,mimetype"),
        ("filter","statuscode:200"),("collapse","digest"),("limit","80"),
        ("from","2009"),("to","2022")
    ]
    url="https://web.archive.org/cdx/search/cdx?"+urlencode(params)
    try:
        data=get_json(url,15.0)
    except Exception:
        return None
    if not isinstance(data,list) or len(data)<2:
        return None
    rows=data[1:]
    target=int(stamp or "20150101")
    valid=[]
    for row in rows:
        if not isinstance(row,list) or len(row)<2: continue
        ts=str(row[0]); orig=str(row[1])
        if not ts.isdigit(): continue
        valid.append((abs(int(ts[:8])-target),ts,orig))
    if not valid: return None
    _,ts,orig=min(valid)
    return {
        "capture_url":f"https://web.archive.org/web/{ts}/{orig}",
        "timestamp":ts,"candidate":orig,"method":"cdx"
    }

def find_capture(url: str, stamp: str, extra_paths=()):
    vs=variants(url,extra_paths)
    # Broad availability API pass first.
    for candidate in vs:
        hit=available(candidate,stamp)
        if hit: return hit
        time.sleep(0.06)
    # CDX is more complete than the availability API. Keep this pass bounded.
    for candidate in vs[:10]:
        hit=cdx(candidate,stamp)
        if hit: return hit
        time.sleep(0.10)
    return None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--old-repo",required=True)
    ap.add_argument("--output",default="data/archive/link-repair/second-pass-wayback-audit.json")
    args=ap.parse_args()

    occurrences=collect_unlinked()
    by_url=defaultdict(list)
    for item in occurrences:
        by_url[item["url"]].append(item)

    old_path, old_slug, old_title=parse_old_repo(Path(args.old_repo))
    results=[]
    for idx,(url,items) in enumerate(sorted(by_url.items()),1):
        p=urlsplit(url)
        extra=[]
        evidence=[]
        if (p.hostname or "").lower() in RC_HOSTS:
            path=p.path or "/"
            if path in old_path:
                extra.append(path); evidence.append("old_repo_exact_path")
            slug=path.strip("/").split("/")[-1]
            matches=old_slug.get(slug,[])
            if len(matches)==1 and matches[0] != path:
                extra.append(matches[0]); evidence.append("old_repo_unique_slug")
            labels={norm_text(i["label"]) for i in items if norm_text(i["label"])}
            title_matches=set()
            for label in labels:
                for u in old_title.get(label,[]): title_matches.add(u)
            if len(title_matches)==1:
                cand=next(iter(title_matches))
                if cand not in extra:
                    extra.append(cand); evidence.append("old_repo_exact_title")
        stamps=[i["date"] for i in items if i["date"]]
        stamp=sorted(stamps)[len(stamps)//2] if stamps else ""
        hit=find_capture(url,stamp,extra)
        confidence="none"
        if hit:
            hp=urlsplit(hit["candidate"])
            op=urlsplit(url)
            same_path=(hp.path.rstrip("/") or "/") == (op.path.rstrip("/") or "/")
            same_family=((hp.hostname or "").replace("www.","") == (op.hostname or "").replace("www.",""))
            if same_path and same_family:
                confidence="high_exact"
            elif evidence:
                confidence="high_repo_supported"
            else:
                confidence="medium_variant"
        results.append({
            "original_url":url,
            "kind":items[0]["kind"],
            "occurrences":len(items),
            "episodes":sorted({i["episode"] for i in items}),
            "labels":sorted({i["label"] for i in items if i["label"]}),
            "old_repo_evidence":evidence,
            "result":hit,
            "confidence":confidence,
        })
        print(f"{idx}/{len(by_url)} {confidence} {url}",flush=True)

    high=[r for r in results if r["confidence"].startswith("high_")]
    medium=[r for r in results if r["confidence"]=="medium_variant"]
    no=[r for r in results if r["result"] is None]
    payload={
        "generated_at":datetime.now(timezone.utc).isoformat(),
        "scope":{
            "unlinked_occurrences":len(occurrences),
            "unique_unlinked_urls":len(by_url),
        },
        "summary":{
            "unique_high_confidence_recoverable":len(high),
            "occurrences_high_confidence_recoverable":sum(r["occurrences"] for r in high),
            "unique_medium_confidence_recoverable":len(medium),
            "occurrences_medium_confidence_recoverable":sum(r["occurrences"] for r in medium),
            "unique_still_unresolved":len(no),
            "occurrences_still_unresolved":sum(r["occurrences"] for r in no),
        },
        "policy":{
            "high_exact":"Same normalized host family and path; scheme/www/slash/query variants allowed.",
            "high_repo_supported":"Alternative historical path is supported by the preserved reputatiecoaching.nl source repository.",
            "medium_variant":"Wayback capture found only through a broader URL variant; manual review recommended.",
            "none":"No usable 200 capture found in availability API or bounded CDX search.",
        },
        "results":results,
    }
    out=ROOT/args.output
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(payload["summary"],ensure_ascii=False),flush=True)

if __name__=="__main__":
    main()
