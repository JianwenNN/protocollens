import requests, json
from pathlib import Path

out_dir = Path("samples")
out_dir.mkdir(exist_ok=True)

r = requests.get("https://clinicaltrials.gov/api/v2/studies", params={
    "query.cond": "lung cancer",
    "filter.overallStatus": "RECRUITING",
    "pageSize": 5,
})
r.raise_for_status()

for s in r.json()["studies"]:
    nct_id = s["protocolSection"]["identificationModule"]["nctId"]
    path = out_dir / f"{nct_id}.json"
    path.write_text(json.dumps(s, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"saved {path}")