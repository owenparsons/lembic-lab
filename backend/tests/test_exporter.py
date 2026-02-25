"""Tests for export service."""

import json

import pytest

from lembic.models.export import ExportFormat
from lembic.services.exporter import Exporter
from lembic.services.file_manager import FileManager


@pytest.fixture
def fm(tmp_project):
    return FileManager(tmp_project)


@pytest.fixture
def exporter(fm):
    # Create a few cells first
    fm.create_cell(content="import pandas as pd\ndf = pd.DataFrame({'a': [1,2,3]})")
    fm.create_cell(content="# Analysis\nThis is a markdown cell", cell_type="markdown")
    fm.create_cell(content="print(df.describe())")
    return Exporter(fm)


def test_export_ipynb(exporter, tmp_project):
    result = exporter.export(ExportFormat.IPYNB)
    assert result.format == ExportFormat.IPYNB
    assert result.path.endswith(".ipynb")

    # Verify the file was created and is valid JSON
    path = tmp_project / result.path
    assert path.exists()

    nb = json.loads(path.read_text())
    assert nb["nbformat"] == 4
    assert len(nb["cells"]) == 3
    assert nb["cells"][0]["cell_type"] == "code"
    assert nb["cells"][1]["cell_type"] == "markdown"
    assert nb["cells"][2]["cell_type"] == "code"


def test_export_python(exporter, tmp_project):
    result = exporter.export(ExportFormat.PYTHON)
    assert result.format == ExportFormat.PYTHON
    assert result.path.endswith(".py")

    path = tmp_project / result.path
    assert path.exists()

    content = path.read_text()
    assert "# %%" in content
    assert "# %% [markdown]" in content
    assert "import pandas" in content


def test_export_package(exporter, tmp_project):
    result = exporter.export(ExportFormat.PACKAGE)
    assert result.format == ExportFormat.PACKAGE

    pkg_dir = tmp_project / result.path
    assert pkg_dir.exists()
    assert (pkg_dir / "pyproject.toml").exists()

    # Find the src dir
    src_dirs = list((pkg_dir / "src").iterdir())
    assert len(src_dirs) == 1
    pkg_src = src_dirs[0]
    assert (pkg_src / "__init__.py").exists()
