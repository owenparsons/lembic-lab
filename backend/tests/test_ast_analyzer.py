"""Tests for the AST analyzer service."""

from lembic.services.ast_analyzer import analyze_cell


def test_simple_assignment():
    deps = analyze_cell("x = 1")
    assert "x" in deps.variables_defined
    assert len(deps.variables_read) == 0


def test_reads_variable():
    deps = analyze_cell("y = x + 1")
    assert "y" in deps.variables_defined
    assert "x" in deps.variables_read


def test_function_definition():
    deps = analyze_cell("def foo(x):\n    return x + 1")
    assert "foo" in deps.variables_defined


def test_import():
    deps = analyze_cell("import pandas as pd")
    assert "pd" in deps.variables_defined
    assert any("pandas" in i for i in deps.imports)


def test_from_import():
    deps = analyze_cell("from pathlib import Path")
    assert "Path" in deps.variables_defined
    assert any("Path" in i for i in deps.imports)


def test_complex_cell():
    code = """
import numpy as np
x = np.array([1, 2, 3])
y = x.mean()
print(y)
"""
    deps = analyze_cell(code)
    assert "np" in deps.variables_defined
    assert "x" in deps.variables_defined
    assert "y" in deps.variables_defined
    assert "print" in deps.variables_read


def test_syntax_error():
    deps = analyze_cell("def broken(")
    assert len(deps.variables_defined) == 0
    assert len(deps.variables_read) == 0


def test_for_loop_target():
    deps = analyze_cell("for i in range(10):\n    pass")
    assert "i" in deps.variables_defined
    assert "range" in deps.variables_read


def test_tuple_unpacking():
    deps = analyze_cell("a, b = 1, 2")
    assert "a" in deps.variables_defined
    assert "b" in deps.variables_defined
