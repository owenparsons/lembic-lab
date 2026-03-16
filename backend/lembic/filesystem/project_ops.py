"""Project initialization and scaffolding."""

import subprocess
from pathlib import Path

import yaml


def initialize_project(project_dir: Path, name: str | None = None, *, init_git: bool = True) -> None:
    """Create a new Lembic project with full directory structure."""
    project_dir.mkdir(parents=True, exist_ok=True)

    if name is None:
        name = project_dir.name

    # Create directories
    (project_dir / "cells").mkdir(exist_ok=True)
    (project_dir / "lib").mkdir(exist_ok=True)
    (project_dir / "outputs" / "plots").mkdir(parents=True, exist_ok=True)
    (project_dir / "outputs" / "tables").mkdir(parents=True, exist_ok=True)
    (project_dir / ".notebook" / "history").mkdir(parents=True, exist_ok=True)

    # Create manifest
    manifest_path = project_dir / "notebook.yaml"
    if not manifest_path.exists():
        manifest = {
            "name": name,
            "settings": {
                "close_terminal_on_exit": True,
                "shell": "/bin/zsh",
            },
            "cells": [],
        }
        manifest_path.write_text(yaml.dump(manifest, default_flow_style=False, sort_keys=False))

    # Create .gitignore for Lembic artifacts
    gitignore_path = project_dir / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text(
            "# Lembic\n"
            ".notebook/\n"
            ".claude/\n"
            "execution_log.jsonl\n"
            "outputs/\n"
            "__pycache__/\n"
            "*.pyc\n"
            ".venv/\n"
        )

    # Create lib/__init__.py
    lib_init = project_dir / "lib" / "__init__.py"
    if not lib_init.exists():
        lib_init.write_text('"""Project function library."""\n')

    # Create CLAUDE.md for CC context
    claude_md = project_dir / "CLAUDE.md"
    if not claude_md.exists():
        template_path = Path(__file__).resolve().parent.parent / "templates" / "CLAUDE.md.template"
        template = template_path.read_text()
        claude_md.write_text(template.replace("{name}", name))

    # Create .claude/settings.local.json — pre-allow editing notebook files
    claude_settings_dir = project_dir / ".claude"
    claude_settings_dir.mkdir(exist_ok=True)
    claude_settings = claude_settings_dir / "settings.local.json"
    if not claude_settings.exists():
        import json

        settings = {
            "permissions": {
                "allow": [
                    "Read",
                    "Edit(/notebook.yaml)",
                    "Edit(/cells/**)",
                    "Write(/cells/**)",
                    "Edit(/lib/**)",
                    "Write(/lib/**)",
                    "Bash(lembic add-cell *)",
                    "Bash(lembic delete-cell *)",
                    "Bash(lembic move-cell *)",
                    "Bash(lembic status)",
                    "Bash(lembic variables)",
                    "Bash(lembic run-cell *)",
                    "Bash(lembic annotate *)",
                ]
            }
        }
        claude_settings.write_text(json.dumps(settings, indent=2) + "\n")

    # Initialize git repo for auto-checkpoints
    if init_git:
        git_dir = project_dir / ".git"
        if not git_dir.exists():
            subprocess.run(["git", "init"], cwd=project_dir, capture_output=True)
            subprocess.run(["git", "add", "-A"], cwd=project_dir, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "lembic: auto-checkpoint init"],
                cwd=project_dir, capture_output=True,
            )
