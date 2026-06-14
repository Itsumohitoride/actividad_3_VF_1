import json
import sys
from graphify.detect import detect
from pathlib import Path

result = detect(Path("."))
json.dump(result, open("graphify-out/.graphify_detect.json", "w", encoding="utf-8"), ensure_ascii=False)

total = result.get("total_files", 0)
print(f"Total files: {total}")
ft = result.get("files", {})
for k, v in ft.items():
    print(f"  {k}: {len(v)} files")
if total == 0:
    print("WARNING: No files detected")
