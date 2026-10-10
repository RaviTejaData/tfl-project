import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone
from pathlib import Path


load_dotenv()
app_key = os.getenv("TFL_APP_KEY")

url = "https://api.tfl.gov.uk/Line/Mode/tube/Status"
response = requests.get(url, params={"app_key": app_key}, timeout=10)
response.raise_for_status()

for line in response.json():
    status = line["lineStatuses"][0]["statusSeverityDescription"]
    print(f"{line['name']}: {status}")


fetched_at = datetime.now(timezone.utc)

folder = Path("data/raw/line_status")
folder.mkdir(parents=True, exist_ok=True)
file_path = folder / f"{fetched_at:%Y-%m-%d}.jsonl"

record = {"fetched_at": fetched_at.isoformat(), "lines": response.json()}

with open(file_path, "a") as f:
    f.write(json.dumps(record) + "\n")

print(f"Saved to {file_path}")
