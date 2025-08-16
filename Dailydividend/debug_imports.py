#!/usr/bin/env python
import sys
import os
import importlib

print("Python Path:")
for p in sys.path:
    print(f"  - {p}")

print("\nDirectory Structure:")
for root, dirs, files in os.walk("/app", topdown=True):
    level = root.replace("/app", "").count(os.sep)
    indent = " " * 4 * level
    print(f"{indent}{os.path.basename(root)}/")
    sub_indent = " " * 4 * (level + 1)
    for f in files:
        if f.endswith(".py"):
            print(f"{sub_indent}{f}")

print("\nTrying imports:")
try:
    from app.backend.scheduler.news import DAILY_NEWS
    print("✅ Successfully imported from app.backend.scheduler.news")
except Exception as e:
    print(f"❌ Failed to import from app.backend.scheduler.news: {e}")

try:
    sys.path.insert(0, "/app")
    from app.backend.scheduler.news import DAILY_NEWS
    print("✅ Successfully imported from app.backend.scheduler.news after path adjustment")
except Exception as e:
    print(f"❌ Failed to import from app.backend.scheduler.news after path adjustment: {e}")
