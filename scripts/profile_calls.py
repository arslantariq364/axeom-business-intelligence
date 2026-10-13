import sys
import os
import time
import traceback
from pathlib import Path
from collections import Counter

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import services.db as db_mod

call_counts = Counter()
call_times = []

orig_get_db = db_mod.get_db

def profile_get_db():
    t0 = time.perf_counter()
    stack = traceback.extract_stack()
    # Find the caller outside profile_get_db and services/db.py
    caller = "unknown"
    for frame in reversed(stack[:-1]):
        filename = os.path.basename(frame.filename)
        if filename != "db.py" and "profile_calls.py" not in filename:
            caller = f"{filename}:{frame.name}:{frame.lineno}"
            break
    conn = orig_get_db()
    dt = time.perf_counter() - t0
    call_counts[caller] += 1
    call_times.append((caller, dt))
    print(f"[{len(call_times)}] get_db called from {caller} in {dt:.3f}s", flush=True)
    return conn

db_mod.get_db = profile_get_db

# Also patch is_dataset_cleared to trace how often it is called
orig_is_cleared = db_mod.is_dataset_cleared
is_cleared_counts = Counter()

def profile_is_cleared():
    stack = traceback.extract_stack()
    caller = "unknown"
    for frame in reversed(stack[:-1]):
        filename = os.path.basename(frame.filename)
        if filename != "db.py" and "profile_calls.py" not in filename:
            caller = f"{filename}:{frame.name}:{frame.lineno}"
            break
    is_cleared_counts[caller] += 1
    return orig_is_cleared()

db_mod.is_dataset_cleared = profile_is_cleared

# Now import app and call /api/state
from app import app

print("Invoking get_state() with tracing...")
t_start = time.perf_counter()
with app.test_request_context():
    from app import get_state
    resp = get_state()
total = time.perf_counter() - t_start

print("\n" + "="*60)
print(f"TOTAL TIME FOR get_state(): {total:.3f}s")
print(f"TOTAL get_db() CALLS: {len(call_times)} (Total DB connect time: {sum(t for _, t in call_times):.3f}s)")
print("\nTOP get_db() CALLERS:")
for caller, count in call_counts.most_common(20):
    total_caller_time = sum(t for c, t in call_times if c == caller)
    print(f"  {count:4d}x | {total_caller_time:6.2f}s | {caller}")

print(f"\nTOTAL is_dataset_cleared() CALLS: {sum(is_cleared_counts.values())}")
for caller, count in is_cleared_counts.most_common(20):
    print(f"  {count:4d}x | {caller}")
print("="*60)
