#!/usr/bin/env python3
import subprocess
import sys
import shutil
from pathlib import Path

def main():
    project_root = Path(__file__).parent
    target_dir = Path.home() / "Documents" / "SimCity 4" / "PythonScripts"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy Python source files
    src_python = project_root / "src" / "python"
    for item in src_python.rglob("*"):
        if item.is_file():
            relative_path = item.relative_to(src_python)
            target_file = target_dir / relative_path
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target_file)
    
    # Install dependencies directly without building project
    subprocess.run([
        "uv", "pip", "install", 
        "--target", str(target_dir),
        "pydantic>=2.0.0,<3.0.0"
    ], check=True)
    
    print(f"Setup complete: {target_dir}")

if __name__ == "__main__":
    main()