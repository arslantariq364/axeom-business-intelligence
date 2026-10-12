"""
Automated Submission Packaging Script for Axeom Challenge.
Bundles all required deliverables into a clean ZIP archive while strictly
excluding secrets, bytecode caches, virtual environments, and temporary files.
"""

import os
import sys
import zipfile
from pathlib import Path

WORKSPACE = Path("/home/arslan-tariq/Downloads/Axeom Challenge - Pack 01")
OUTPUT_ZIP = WORKSPACE / "Axeom_Challenge_Pack_01_Submission.zip"

# Strict exclusion rules per challenge guidelines
EXCLUDE_DIRS = {
    "__pycache__", ".pytest_cache", ".git", ".gemini", "venv", ".venv",
    "env", "scratch", ".system_generated", "uploads"
}
EXCLUDE_EXTENSIONS = {".pyc", ".pyo", ".log", ".DS_Store", ".tmp"}
EXCLUDE_FILES = {
    ".env", "axeom_synthetic_test.db", "Axeom_Challenge_Pack_01_Submission.zip",
    ".gitignore", ".gitkeep"
}

def build_package():
    print(f"[Package] Assembling submission bundle at {OUTPUT_ZIP.name}...")
    
    file_count = 0
    total_bytes = 0
    
    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(WORKSPACE):
            # Prune excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
            
            for f in files:
                if f in EXCLUDE_FILES or f.startswith(".env") or f.endswith(".tmp"):
                    continue
                if any(f.endswith(ext) for ext in EXCLUDE_EXTENSIONS):
                    continue
                
                full_path = Path(root) / f
                rel_path = full_path.relative_to(WORKSPACE)
                
                zf.write(full_path, arcname=rel_path)
                file_count += 1
                total_bytes += full_path.stat().st_size
                
    zip_size_mb = OUTPUT_ZIP.stat().st_size / (1024 * 1024)
    print(f"[Package] Packaged {file_count} files ({total_bytes / (1024 * 1024):.2f} MB uncompressed).")
    print(f"[Package] Created archive: {OUTPUT_ZIP} ({zip_size_mb:.2f} MB compressed).")
    return OUTPUT_ZIP

if __name__ == "__main__":
    build_package()
