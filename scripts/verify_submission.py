"""
Independent Submission Verification Script.
Audits answers.json, answers_working.json, and the submission ZIP archive
strictly by JSON field name (not line numbers) and inspects bundle contents.
"""

import json
import zipfile
from pathlib import Path

WORKSPACE = Path("/home/arslan-tariq/Downloads/Axeom Challenge - Pack 01")

REQUIRED_JSON_KEYS = [
    "pack_id", "your_name", "your_email", "live_link", "video_link", "code_or_files_link",
    "client_count", "clients", "payers_who_are_not_clients", "overdue", "overdue_total",
    "we_owe", "never_billed", "never_billed_total", "billing_tool_is_wrong",
    "lost_requests", "lost_requests_root_causes", "lost_requests_started_getting_worse_in",
    "never_replied_leads", "most_likely_to_leave", "best_marketing_channel",
    "what_this_data_cannot_tell_us", "monday_top_3"
]

SYNTHETIC_TEST_IDS = [
    "INV-9001", "INV-9100", "INV-9888", "INV-9777", "INV-9999", "P9001", "P9010", "P9011",
    "Torres Tire & Auto", "Cedar Ridge Properties", "Patel Risk Associates", "test_owner_action"
]

def verify_json(file_path):
    print(f"\n[Verify] Checking {file_path.name} by JSON field names...")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    missing_keys = [k for k in REQUIRED_JSON_KEYS if k not in data]
    if missing_keys:
        print(f"  ❌ Missing keys: {missing_keys}")
    else:
        print(f"  ✅ All {len(REQUIRED_JSON_KEYS)} required top-level JSON keys present.")
    
    raw_content = json.dumps(data)
    found_synthetic = [s for s in SYNTHETIC_TEST_IDS if s in raw_content]
    if found_synthetic:
        print(f"  ❌ Contaminated with synthetic test IDs: {found_synthetic}")
    else:
        print(f"  ✅ 100% clean: 0 synthetic test IDs present.")
        
    return data

def verify_zip(zip_path):
    print(f"\n[Verify] Inspecting {zip_path.name} bundle contents...")
    if not zip_path.exists():
        print(f"  ❌ Archive not found: {zip_path}")
        return False
        
    with zipfile.ZipFile(zip_path, "r") as zf:
        namelist = zf.namelist()
        print(f"  Total files in archive: {len(namelist)}")
        
        # Check required files
        for req in ["answers.json", "answers_working.json", "writeup.pdf", "assumptions.md", "daily_log.md", "app.py"]:
            if req in namelist:
                print(f"  ✅ Required deliverable present: {req}")
            else:
                print(f"  ❌ Missing deliverable: {req}")
                
        # Check forbidden items
        forbidden = [n for n in namelist if ".env" in n or "__pycache__" in n or ".pyc" in n or "venv" in n or ".git" in n or "synthetic" in n]
        if forbidden:
            print(f"  ❌ Forbidden files found in archive: {forbidden[:5]}")
        else:
            print(f"  ✅ Archive is clean: zero secrets, virtualenvs, bytecodes, or test artifacts.")

if __name__ == "__main__":
    verify_json(WORKSPACE / "answers.json")
    verify_json(WORKSPACE / "answers_working.json")
    verify_zip(WORKSPACE / "Axeom_Challenge_Pack_01_Submission.zip")
