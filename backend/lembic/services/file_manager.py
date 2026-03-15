"""File manager: manifest CRUD, cell file operations, project scaffolding."""

from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

import yaml

from lembic.errors import CellNotFoundError, ManifestError
from lembic.models.cells import CellEntry, CellType
from lembic.models.notebook import NotebookManifest
from lembic.services.name_generator import generate_name


class FileManager:
    """Manages the on-disk notebook structure: manifest + cell files."""

    def __init__(self, project_dir: Path) -> None:
        self.project_dir = project_dir
        self.manifest_path = project_dir / "notebook.yaml"
        self.cells_dir = project_dir / "cells"
        self._manifest: NotebookManifest | None = None

    def load_manifest(self) -> NotebookManifest:
        """Load the manifest from disk, caching in memory."""
        if self._manifest is not None:
            return self._manifest

        if not self.manifest_path.exists():
            self._manifest = NotebookManifest()
            return self._manifest

        try:
            raw = yaml.safe_load(self.manifest_path.read_text()) or {}
            self._manifest = NotebookManifest(**raw)
        except Exception as e:
            raise ManifestError(f"Failed to load manifest: {e}") from e

        return self._manifest

    def save_manifest(self) -> None:
        """Write the current manifest to disk."""
        manifest = self.load_manifest()
        cells = []
        for entry in manifest.cells:
            cell_dict: dict = {
                "id": entry.id,
                "name": entry.name,
                "type": entry.cell_type.value,
                "file": entry.file,
            }
            if entry.annotation is not None:
                cell_dict["annotation"] = entry.annotation.model_dump()
            cells.append(cell_dict)
        data: dict = {}
        if manifest.name:
            data["name"] = manifest.name
        data["settings"] = manifest.settings.model_dump()
        data["cells"] = cells
        if manifest.sections:
            data["sections"] = [s.model_dump() for s in manifest.sections]
        self.manifest_path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))

    def invalidate_manifest(self) -> None:
        """Force reload on next access."""
        self._manifest = None

    def get_cell_entry(self, cell_id: str) -> CellEntry:
        """Get a cell entry by full ID, 4-char prefix, or name.

        Resolution order: exact ID match, then prefix match, then name match.
        Raises CellNotFoundError if no match, or if the match is ambiguous.
        """
        manifest = self.load_manifest()

        # 1. Exact ID match
        for entry in manifest.cells:
            if entry.id == cell_id:
                return entry

        # 2. Prefix match (4-char short ID from the UI)
        prefix_matches = [e for e in manifest.cells if e.id.startswith(cell_id)]
        if len(prefix_matches) == 1:
            return prefix_matches[0]
        if len(prefix_matches) > 1:
            names = ", ".join(f"{e.id} ({e.name})" for e in prefix_matches)
            raise CellNotFoundError(
                f"Ambiguous prefix '{cell_id}' matches multiple cells: {names}"
            )

        # 3. Name match
        name_matches = [e for e in manifest.cells if e.name == cell_id]
        if len(name_matches) == 1:
            return name_matches[0]

        raise CellNotFoundError(cell_id)

    def _cell_path(self, entry: CellEntry) -> Path:
        """Resolve the file path for a cell entry."""
        return self.project_dir / entry.file

    def read_cell(self, cell_id: str) -> str:
        """Read the content of a cell file."""
        entry = self.get_cell_entry(cell_id)
        path = self._cell_path(entry)
        if not path.exists():
            return ""
        return path.read_text()

    def write_cell(self, cell_id: str, content: str) -> None:
        """Write content to a cell file."""
        entry = self.get_cell_entry(cell_id)
        path = self._cell_path(entry)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def cell_content_hash(self, cell_id: str) -> str:
        """Get the SHA-256 hash of a cell's content."""
        content = self.read_cell(cell_id)
        return hashlib.sha256(content.encode()).hexdigest()

    def _generate_unique_id(self, existing_ids: set[str]) -> str:
        """Generate an 8-char hex ID whose 4-char prefix is unique."""
        existing_prefixes = {eid[:4] for eid in existing_ids}
        for _ in range(100):
            new_id = uuid.uuid4().hex[:8]
            if new_id[:4] not in existing_prefixes:
                return new_id
        raise RuntimeError("Could not generate ID with unique 4-char prefix")

    def _generate_unique_cell_id(self) -> str:
        """Generate an 8-char hex ID whose 4-char prefix is unique among existing cells."""
        manifest = self.load_manifest()
        return self._generate_unique_id({e.id for e in manifest.cells})

    def _generate_unique_section_id(self) -> str:
        """Generate an 8-char hex ID whose 4-char prefix is unique among existing sections."""
        manifest = self.load_manifest()
        return self._generate_unique_id({s.id for s in manifest.sections})

    def create_cell(
        self,
        cell_type: CellType = CellType.CODE,
        name: str | None = None,
        content: str = "",
        after_id: str | None = None,
    ) -> CellEntry:
        """Create a new cell, add to manifest, write file."""
        manifest = self.load_manifest()
        existing_names = {e.name for e in manifest.cells}

        cell_id = self._generate_unique_cell_id()
        if name is None:
            name = generate_name(existing_names)

        ext = ".md" if cell_type == CellType.MARKDOWN else ".py"
        filename = f"cells/{cell_id}_{name}{ext}"

        entry = CellEntry(id=cell_id, name=name, type=cell_type, file=filename)

        # Insert at position
        if after_id is None:
            manifest.cells.append(entry)
        else:
            idx = self._find_index(after_id)
            manifest.cells.insert(idx + 1, entry)

        # Write file
        path = self.project_dir / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

        self.save_manifest()
        return entry

    def delete_cell(self, cell_id: str) -> None:
        """Delete a cell from manifest and remove its file."""
        manifest = self.load_manifest()
        entry = self.get_cell_entry(cell_id)

        # Remove file
        path = self._cell_path(entry)
        if path.exists():
            path.unlink()

        # Remove from manifest
        manifest.cells = [e for e in manifest.cells if e.id != cell_id]
        self.save_manifest()

    def rename_cell(self, cell_id: str, new_name: str) -> None:
        """Rename a cell (updates manifest and renames file)."""
        manifest = self.load_manifest()
        entry = self.get_cell_entry(cell_id)
        old_path = self._cell_path(entry)

        ext = ".md" if entry.cell_type == CellType.MARKDOWN else ".py"
        new_filename = f"cells/{cell_id}_{new_name}{ext}"
        new_path = self.project_dir / new_filename

        # Rename file
        if old_path.exists():
            old_path.rename(new_path)

        # Update manifest entry
        for e in manifest.cells:
            if e.id == cell_id:
                e.name = new_name
                e.file = new_filename
                break

        self.save_manifest()

    def move_cell(self, cell_id: str, after_id: str | None) -> None:
        """Move a cell to after the specified cell (or to start if after_id is None)."""
        manifest = self.load_manifest()
        entry = self.get_cell_entry(cell_id)

        # Remove from current position
        manifest.cells = [e for e in manifest.cells if e.id != cell_id]

        # Insert at new position
        if after_id is None:
            manifest.cells.insert(0, entry)
        else:
            idx = self._find_index(after_id)
            manifest.cells.insert(idx + 1, entry)

        self.save_manifest()

    def reorder_cells(self, cell_ids: list[str]) -> None:
        """Reorder all cells to match the given ID order."""
        manifest = self.load_manifest()
        entries_by_id = {e.id: e for e in manifest.cells}

        new_cells = []
        for cid in cell_ids:
            if cid not in entries_by_id:
                raise CellNotFoundError(cid)
            new_cells.append(entries_by_id[cid])

        manifest.cells = new_cells
        self.save_manifest()

    def _find_index(self, cell_id: str) -> int:
        """Find the index of a cell in the manifest."""
        manifest = self.load_manifest()
        for i, entry in enumerate(manifest.cells):
            if entry.id == cell_id:
                return i
        raise CellNotFoundError(cell_id)
