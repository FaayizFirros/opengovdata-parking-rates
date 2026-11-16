#!/usr/bin/env python3
"""Fetch URA parking rate bands server-side once a month. No keys in output."""
import json
import os
import re
from pathlib import Path
from urllib.request import Request, urlopen
from datetime import datetime, timezone

BASE="https://eservice.ura.gov.sg/uraDataService"
OUTPUT=Path("ura-carpark-rates.json")
CODE=re.compile(r"^[A-Z0-9_-]{2,12}$")
def fetch(url, headers):
    req=Request(url,headers={"Accept":"application/json","User-Agent":"OpenGovData1.0-Monthly-URA/1.0",**headers})
    with urlopen(req,timeout=25) as response:
        if response.status!=200:
            raise RuntimeError("URA returned non-success HTTP code")
        raw=response.read(3_000_001)
        if len(raw)>3_000_000:
            raise RuntimeError("Response size limit exceeded")
        return json.loads(raw)
def safe(value, limit=90):
    return "".join(c for c in str(value or "").strip() if c.isprintable())[:limit]
def normalise(item):
    if not isinstance(item,dict): return None
    code=safe(item.get("ppCode"),12).upper()
    if not CODE.fullmatch(code) or safe(item.get("vehCat"),30).upper() not in ("CAR","C"):
        return None
    row={"code":code,"name":safe(item.get("ppName")),"vehicle":"Car",
         "start":safe(item.get("startTime"),25),"end":safe(item.get("endTime"),25),
         "weekday_rate":safe(item.get("weekdayRate"),70),"weekday_min":safe(item.get("weekdayMin"),50),
         "saturday_rate":safe(item.get("satdayRate"),70),"saturday_min":safe(item.get("satdayMin"),50),
         "sunday_ph_rate":safe(item.get("sunPHRate"),70),"sunday_ph_min":safe(item.get("sunPHMin"),50),
         "remarks":safe(item.get("remarks"),180)}
    if not any(row[k] for k in ("weekday_rate","saturday_rate","sunday_ph_rate")):
        return None
    return row
def generate(key, request=fetch):
    auth={"AccessKey":key}
    token_json=request(BASE+"/insertNewToken/v1",auth)
    if token_json.get("Status")!="Success" or not isinstance(token_json.get("Result"),str):
        raise RuntimeError("URA token response invalid")
    token=token_json["Result"]
    if len(token)<10: raise RuntimeError("URA token missing")
    response=request(BASE+"/invokeUraDS/v1?service=Car_Park_Details",{**auth,"Token":token})
    if response.get("Status")!="Success" or not isinstance(response.get("Result"),list):
        raise RuntimeError("URA Car_Park_Details response invalid")
    rows=[r for x in response["Result"] if (r:=normalise(x))]
    if not rows: raise RuntimeError("No valid car tariff rows; previous data retained")
    rates=sorted({json.dumps(row,sort_keys=True):row for row in rows}.values(),
                 key=lambda x:(x["code"],x["start"],x["end"]))
    return {"schema":1,"source":"URA Data Service: Car_Park_Details",
            "licence":"Singapore Open Data Licence",
            "licence_url":"https://www.ura.gov.sg/eservices-info/maps/acceptance-grant-licence/",
            "source_url":"https://eservice.ura.gov.sg/maps/api/",
            "updated_utc":datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z"),
            "note":"Indicative monthly rates; check carpark signs for actual charges.",
            "rates":rates}
if __name__=="__main__":
    key=os.getenv("URA_ACCESS_KEY","").strip()
    if not key: raise SystemExit("URA_ACCESS_KEY Actions secret is missing")
    output=generate(key)
    data=json.dumps(output,separators=(",",":"),ensure_ascii=False)+"\n"
    if len(data.encode("utf-8"))>2_000_000: raise RuntimeError("Output exceeds app size limit")
    temp=OUTPUT.with_suffix(".tmp")
    temp.write_text(data,encoding="utf-8")
    temp.replace(OUTPUT)
    print("Monthly URA rate bands:",len(output["rates"]))
    print("Distinct carpark codes:",len({r["code"] for r in output["rates"]}))
    print("No access credentials or session tokens exported.")
