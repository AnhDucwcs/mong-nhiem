import json
from pathlib import Path

run_dir = Path("runs/calibration-run-0001")
raw_path = run_dir / "raw_responses.jsonl"

text = raw_path.read_text(encoding="utf-8")
lines = [l for l in text.split("\\n") if l.strip()]

# Overwrite properly
with open(raw_path, "w", encoding="utf-8") as f:
    for line in lines:
        f.write(line + "\n")

print(f"Fixed {len(lines)} records.")
