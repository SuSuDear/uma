#!/usr/bin/env python3
import os
import re
import json
import shutil
from pathlib import Path

INPUT_DIR = Path("images")
OUTPUT_DIR = Path("GeneratedAssets.xcassets")

SUPPORTED_EXTS = {".png", ".jpg", ".jpeg", ".pdf"}

scale_pattern = re.compile(r"^(?P<name>.+?)(@(?P<scale>[23])x)?$")

def detect_scale(filename_stem):
    match = scale_pattern.match(filename_stem)
    if not match:
        return filename_stem, "1x"

    name = match.group("name")
    scale = match.group("scale")

    if scale == "2":
        return name, "2x"
    elif scale == "3":
        return name, "3x"
    else:
        return name, "1x"

def main():
    if not INPUT_DIR.exists():
        raise RuntimeError(f"Input dir not found: {INPUT_DIR}")

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    groups = {}

    for file in INPUT_DIR.iterdir():
        if not file.is_file():
            continue

        ext = file.suffix.lower()
        if ext not in SUPPORTED_EXTS:
            continue

        base_name, scale = detect_scale(file.stem)

        if base_name not in groups:
            groups[base_name] = []

        groups[base_name].append({
            "path": file,
            "filename": file.name,
            "scale": scale
        })

    for asset_name, files in groups.items():
        imageset_dir = OUTPUT_DIR / f"{asset_name}.imageset"
        imageset_dir.mkdir(parents=True, exist_ok=True)

        images = []

        for item in sorted(files, key=lambda x: x["scale"]):
            src = item["path"]
            dst = imageset_dir / item["filename"]
            shutil.copy2(src, dst)

            images.append({
                "idiom": "universal",
                "filename": item["filename"],
                "scale": item["scale"]
            })

        contents = {
            "images": images,
            "info": {
                "author": "xcode",
                "version": 1
            }
        }

        with open(imageset_dir / "Contents.json", "w", encoding="utf-8") as f:
            json.dump(contents, f, indent=2, ensure_ascii=False)

    root_contents = {
        "info": {
            "author": "xcode",
            "version": 1
        }
    }

    with open(OUTPUT_DIR / "Contents.json", "w", encoding="utf-8") as f:
        json.dump(root_contents, f, indent=2, ensure_ascii=False)

    print(f"Generated {OUTPUT_DIR}")
    print(f"Assets count: {len(groups)}")

if __name__ == "__main__":
    main()
