"""AST-based analysis: variable dependencies, import cycle detection."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import NamedTuple


class CellDependencies(NamedTuple):
    """Variables read and defined by a cell."""

    variables_read: set[str]
    variables_defined: set[str]
    imports: set[str]


def analyze_cell(source: str) -> CellDependencies:
    """Extract variable dependencies from a cell's source code via AST."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return CellDependencies(set(), set(), set())

    defined: set[str] = set()
    read: set[str] = set()
    imports: set[str] = set()

    for node in ast.walk(tree):
        # Definitions
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            defined.add(node.name)
        elif isinstance(node, ast.ClassDef):
            defined.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                _collect_names(target, defined)
        elif isinstance(node, ast.AugAssign):
            _collect_names(node.target, defined)
        elif isinstance(node, ast.AnnAssign) and node.target:
            _collect_names(node.target, defined)
        elif isinstance(node, ast.For):
            _collect_names(node.target, defined)

        # Imports
        elif isinstance(node, ast.Import):
            for alias in node.names:
                local_name = alias.asname or alias.name.split(".")[0]
                imports.add(alias.name)  # Store full module name
                defined.add(local_name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                name = alias.asname or alias.name
                imports.add(f"{module}.{name}" if module else name)
                defined.add(name)

        # Reads (Name nodes that aren't in a store context)
        elif isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Load):
                read.add(node.id)

    # Variables read but not defined locally are true dependencies
    external_reads = read - defined
    return CellDependencies(external_reads, defined, imports)


def _collect_names(node: ast.AST, names: set[str]) -> None:
    """Collect variable names from assignment targets."""
    if isinstance(node, ast.Name):
        names.add(node.id)
    elif isinstance(node, ast.Tuple | ast.List):
        for elt in node.elts:
            _collect_names(elt, names)
    elif isinstance(node, ast.Starred):
        _collect_names(node.value, names)


def detect_import_cycles(lib_dir: Path) -> list[list[str]]:
    """Detect circular imports in the lib/ directory.

    Returns a list of cycles, where each cycle is a list of module names.
    """
    # Build adjacency list
    graph: dict[str, set[str]] = {}

    for py_file in lib_dir.rglob("*.py"):
        if py_file.name.startswith("_"):
            continue
        module = py_file.stem
        try:
            source = py_file.read_text()
            tree = ast.parse(source)
        except (SyntaxError, OSError):
            continue

        deps: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module.startswith("lib.") or node.module == "lib":
                    parts = node.module.split(".")
                    if len(parts) >= 2:
                        deps.add(parts[1])
        graph[module] = deps

    # DFS cycle detection
    cycles: list[list[str]] = []
    visited: set[str] = set()
    path: list[str] = []
    on_path: set[str] = set()

    def dfs(node: str) -> None:
        if node in on_path:
            cycle_start = path.index(node)
            cycles.append(path[cycle_start:] + [node])
            return
        if node in visited:
            return
        visited.add(node)
        on_path.add(node)
        path.append(node)
        for neighbor in graph.get(node, set()):
            dfs(neighbor)
        path.pop()
        on_path.remove(node)

    for module in graph:
        dfs(module)

    return cycles
