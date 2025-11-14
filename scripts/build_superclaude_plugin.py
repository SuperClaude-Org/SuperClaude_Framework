#!/usr/bin/env python3
"""
Build SuperClaude plugin distribution artefacts from unified sources.

Usage:
    python scripts/build_superclaude_plugin.py
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_SRC = ROOT / "plugins" / "superclaude"
DIST_ROOT = ROOT / "dist" / "plugins" / "superclaude"
MANIFEST_DIR = PLUGIN_SRC / "manifest"


def load_metadata() -> dict:
    with (MANIFEST_DIR / "metadata.json").open() as f:
        metadata = json.load(f)

    version_file = ROOT / "VERSION"
    if version_file.exists():
        metadata["plugin_version"] = version_file.read_text().strip()
    else:
        # Fall back to metadata override or default version
        metadata["plugin_version"] = metadata.get("plugin_version", "0.0.0")

    metadata.setdefault("keywords", [])
    return metadata


def render_template(template_path: Path, placeholders: dict[str, str]) -> str:
    content = template_path.read_text()
    for key, value in placeholders.items():
        token = f"{{{{{key}}}}}"
        content = content.replace(token, value)
    return content


def copy_tree(src: Path, dest: Path) -> None:
    if not src.exists():
        return
    shutil.copytree(src, dest, dirs_exist_ok=True)


def main() -> None:
    if not PLUGIN_SRC.exists():
        raise SystemExit(f"Missing plugin sources: {PLUGIN_SRC}")

    metadata = load_metadata()

    placeholders = {
        "plugin_name": metadata["plugin_name"],
        "plugin_version": metadata["plugin_version"],
        "plugin_description": metadata["plugin_description"],
        "author_name": metadata["author_name"],
        "homepage_url": metadata["homepage_url"],
        "repository_url": metadata["repository_url"],
        "license": metadata["license"],
        "keywords_json": json.dumps(metadata["keywords"]),
        "marketplace_name": metadata["marketplace_name"],
        "marketplace_description": metadata["marketplace_description"],
    }

    # Clean dist directory
    if DIST_ROOT.exists():
        shutil.rmtree(DIST_ROOT)
    DIST_ROOT.mkdir(parents=True, exist_ok=True)

    # Copy top-level asset directories
    for folder in ["agents", "commands", "hooks", "scripts", "skills"]:
        copy_tree(PLUGIN_SRC / folder, DIST_ROOT / folder)

    # Render manifests
    claude_dir = DIST_ROOT / ".claude-plugin"
    claude_dir.mkdir(parents=True, exist_ok=True)

    plugin_manifest = render_template(MANIFEST_DIR / "plugin.template.json", placeholders)
    (claude_dir / "plugin.json").write_text(plugin_manifest + "\n")

    marketplace_manifest = render_template(MANIFEST_DIR / "marketplace.template.json", placeholders)
    (claude_dir / "marketplace.json").write_text(marketplace_manifest + "\n")

    # Copy tests into manifest directory
    tests_src = PLUGIN_SRC / "tests"
    if tests_src.exists():
        copy_tree(tests_src, claude_dir / "tests")

    print(f"✅ Built plugin artefacts at {DIST_ROOT}")


if __name__ == "__main__":
    main()
