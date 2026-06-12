"""Discover tasks (eval/tasks/*/meta.yaml) and arms (eval/variants/*)."""

from __future__ import annotations

from pathlib import Path

import yaml

from .config import DEFAULT_MAX_TURNS, Arm, Task


def load_tasks(tasks_dir: Path, only: set[str] | None = None) -> list[Task]:
    tasks: list[Task] = []
    for meta_path in sorted(tasks_dir.glob("*/meta.yaml")):
        root = meta_path.parent
        meta = yaml.safe_load(meta_path.read_text()) or {}
        tid = meta.get("id", root.name)
        if only and tid not in only:
            continue
        tasks.append(Task(
            id=tid,
            root=root,
            source=meta.get("source", "self"),
            verify_image=meta["verify_image"],
            max_turns=int(meta.get("max_turns", DEFAULT_MAX_TURNS)),
            difficulty=meta.get("difficulty", "unknown"),
            tags=tuple(meta.get("tags", [])),
        ))
    return tasks


def load_arms(variants_dir: Path, only: set[str] | None = None) -> list[Arm]:
    """Always includes the native baseline `A`, plus one B_<comp> per variant
    directory that contains a .claude-plugin/plugin.json."""
    arms = [Arm(name="A")]  # native baseline
    for plugin_json in sorted(variants_dir.glob("*/.claude-plugin/plugin.json")):
        comp = plugin_json.parent.parent.name
        name = f"B_{comp}"
        if only and name not in only and comp not in only:
            continue
        arms.append(Arm(name=name, plugin_dir=plugin_json.parent.parent))
    return arms
