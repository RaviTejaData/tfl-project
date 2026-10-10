import json
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

load_dotenv()

rows = []

for file_path in sorted(Path("data/raw/line_status").glob("*.jsonl")):
    with open(file_path) as f:
        for raw_line in f:
            record = json.loads(raw_line)
            for line in record["lines"]:
                for index, status in enumerate(line["lineStatuses"]):
                    rows.append((
                        record["fetched_at"],
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
        inserted = cur.rowcount
    total = conn.execute("SELECT count(*) FROM line_status").fetchone()[0]

print(f"Read {len(rows)} rows from files, {inserted} new, {total} now in the table")
