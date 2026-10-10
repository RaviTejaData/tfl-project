import json
from pathlib import Path

import pandas as pd

pd.set_option("display.width", 200)
rows = []

for file_path in sorted(Path("data/raw/line_status").glob("*.jsonl")):
    with open(file_path) as f:
        for raw_line in f:
            record = json.loads(raw_line)
            for line in record["lines"]:
                for status in line["lineStatuses"]:
                    rows.append({
                        "fetched_at": record["fetched_at"],
                        "line": line["name"],
                        "status": status["statusSeverityDescription"],
                    })

df = pd.DataFrame(rows)

print(df.tail(12))
print()
print(df.groupby(["line", "status"]).size())
