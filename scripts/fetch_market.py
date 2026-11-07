#!/usr/bin/env python3
"""Fetch daily market closes from Yahoo Finance's unofficial chart endpoint."""
import datetime as dt, json, pathlib, time, urllib.parse, urllib.request
from zoneinfo import ZoneInfo

ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/"data"; ARCHIVE=ROOT/"markets"
DATA.mkdir(exist_ok=True); ARCHIVE.mkdir(exist_ok=True)
ASSETS=[
 ("SPX","S&P 500","^GSPC","index",""),("NASDAQ","NASDAQ Composite","^IXIC","index",""),
 ("DOW","Dow Jones","^DJI","index",""),("RUT","Russell 2000","^RUT","index",""),
 ("VIX","CBOE VIX","^VIX","index",""),("GOLD","Gold futures","GC=F","commodity","USD/oz"),
 ("DXY","US Dollar Index","DX-Y.NYB","index",""),("US10Y","US 10Y Treasury yield","^TNX","yield","%"),
]
def nydate(ts): return dt.datetime.fromtimestamp(ts,dt.timezone.utc).astimezone(ZoneInfo("America/New_York")).date()
def fetch(symbol):
 url=f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol,safe='')}?range=1mo&interval=1d"
 req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; ZYQMarkets/1.0)","Accept":"application/json"})
 err=None
 for attempt in range(3):
  try:
   with urllib.request.urlopen(req,timeout=25) as r: payload=json.loads(r.read())
   result=payload["chart"]["result"][0]; q=result["indicators"]["quote"][0]
   pts=[(t,v) for t,v in zip(result["timestamp"],q["close"]) if v is not None]
   if len(pts)<2: raise ValueError("Not enough closes")
   return pts,result.get("meta",{}).get("currency")
  except Exception as e: err=e; time.sleep(2**attempt)
 raise RuntimeError(f"{symbol}: {err}")
def main():
 now=dt.datetime.now(dt.timezone.utc); today=now.astimezone(ZoneInfo("America/New_York")).date()
 items=[]; dates=[]; errors=[]
 for key,name,ticker,kind,unit in ASSETS:
  try:
   pts,currency=fetch(ticker)
   done=[p for p in pts if nydate(p[0])<today]
   if len(done)<2: done=pts[-2:]
   ts,val=done[-1]; prev=done[-2][1]
   change=(val/prev-1)*100 if prev else None
   dates.append(nydate(ts))
   items.append({"key":key,"name":name,"symbol":ticker,"value":round(float(val),4),
    "change_pct":round(change,4) if change is not None else None,
    "history":[round(float(v),4) for _,v in done[-12:]],"unit":unit,"kind":kind,"currency":currency})
   print(f"OK {key}: {val}")
  except Exception as e: errors.append(f"{key}: {e}"); print(f"ERROR {key}: {e}")
 if len(items)<5: raise SystemExit("Fewer than five symbols fetched; keeping previous published data. "+"; ".join(errors))
 session=min(dates).isoformat(); slug=session
 data={"site":"ZYQ / MARKETS","session_date":session,"generated_at_utc":now.strftime("%Y-%m-%d %H:%M UTC"),
       "source":"Yahoo Finance chart data (unofficial; delayed data may apply)","items":items,"warnings":errors}
 (DATA/"market-latest.json").write_text(json.dumps(data,indent=2),encoding="utf-8")
 day=ARCHIVE/slug; day.mkdir(parents=True,exist_ok=True)
 (day/"market.json").write_text(json.dumps(data,indent=2),encoding="utf-8")
 # Standalone archive page renders from its local snapshot.
 html="""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SESSION — ZYQ / MARKETS</title><link rel="stylesheet" href="/assets/styles.css"></head><body><div class="shell"><header class="topbar"><a class="brand" href="/"><span class="brand-mark">Z</span><span>ZYQ <i>/</i> MARKETS</span></a><div class="top-meta">DAILY ARCHIVE</div></header><main><section class="page-head"><div class="eyebrow">HISTORICAL EDITION</div><h1>SESSION</h1><p>Market snapshot · Historical daily close</p></section><section class="section"><div class="market-grid" id="grid"></div><p class="data-note">Source: Yahoo Finance chart data (unofficial; delayed data may apply). Not investment advice.</p></section><section class="section"><a class="text-link" href="/">← BACK TO LATEST EDITION</a></section></main><footer>ZYQ / MARKETS · INFORMATIONAL ONLY</footer></div><script>fetch("./market.json").then(r=>r.json()).then(d=>{document.querySelector("h1").textContent=d.session_date;document.getElementById("grid").innerHTML=d.items.map(x=>{let c=x.change_pct,cl=c>0?"positive":c<0?"negative":"neutral",v=Number(x.value).toLocaleString("en-US",{maximumFractionDigits:2,minimumFractionDigits:2});return `<article class="market-card"><div class="card-top"><span class="card-name">${x.name}</span><span class="card-symbol">${x.symbol}</span></div><div class="card-value">${v}${x.unit==="%"?"%":""}</div><div class="change ${cl}">${c>0?"+":""}${c.toFixed(2)}% day</div></article>`}).join("")});</script></body></html>"""
 html=html.replace("SESSION",session)
 (day/"index.html").write_text(html,encoding="utf-8")
 archive_file=DATA/"archive.json"
 try: old=json.loads(archive_file.read_text()).get("entries",[])
 except Exception: old=[]
 bydate={e["date"]:e for e in old if "date" in e}; bydate[session]={"date":session,"slug":slug}
 entries=sorted(bydate.values(),key=lambda x:x["date"],reverse=True)
 (archive_file).write_text(json.dumps({"entries":entries},indent=2),encoding="utf-8")
 rows="".join(f'<tr><td>{e["date"]}</td><td><a href="/markets/{e["slug"]}/">Open edition ↗</a></td></tr>' for e in entries)
 index=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Daily Archive — ZYQ / MARKETS</title><link rel="stylesheet" href="/assets/styles.css"></head><body><div class="shell"><header class="topbar"><a class="brand" href="/"><span class="brand-mark">Z</span><span>ZYQ <i>/</i> MARKETS</span></a><div class="top-meta">DAILY ARCHIVE</div></header><main><section class="page-head"><div class="eyebrow">THE RECORD</div><h1>Daily archive.</h1><p>Previous market editions, organized by session date.</p></section><section class="section"><table class="archive-table"><thead><tr><th>SESSION</th><th>EDITION</th></tr></thead><tbody>{rows}</tbody></table></section></main><footer>ZYQ / MARKETS · INFORMATIONAL ONLY</footer></div></body></html>"""
 (ARCHIVE/"index.html").write_text(index,encoding="utf-8")
 print(f"Published {session}; {len(items)} instruments; {len(entries)} archived sessions.")
 if errors: print("Warnings: "+"; ".join(errors))
if __name__=="__main__": main()
