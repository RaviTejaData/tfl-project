import os
import psycopg
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


rows = []

for line in response.json():
    for index, status in enumerate(line["lineStatuses"]):
        rows.append((
            fetched_at,
            line["id"],
            index,
            line["name"],
            status["statusSeverity"],
            status["statusSeverityDescription"],
            status.get("reason"),
        ))

insert_sql = """
INSERT INTO line_status
    (fetched_at, line_id, status_index, line_name, severity, status, reason)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT DO NOTHING
"""

with psycopg.connect(os.getenv("DATABASE_URL")) as conn:
    with conn.cursor() as cur:
        cur.executemany(insert_sql, rows)

print(f"Inserted {len(rows)} rows into Supabase")
