"""Tests for the cell name generator."""

from lembic.services.name_generator import generate_name


def test_generates_name():
    name = generate_name()
    parts = name.split("-")
    assert len(parts) == 2


def test_unique_names():
    names = set()
    for _ in range(1000):
        name = generate_name(names)
        assert name not in names
        names.add(name)
    assert len(names) == 1000


def test_avoids_collisions():
    existing = {"amber-arch", "azure-atlas"}
    name = generate_name(existing)
    assert name not in existing
