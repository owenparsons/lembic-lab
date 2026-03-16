"""Domain exceptions for Lembic."""


class LembicError(Exception):
    """Base exception for all Lembic errors."""


class CellNotFoundError(LembicError):
    """Raised when a cell ID is not found in the manifest."""

    def __init__(self, cell_id: str) -> None:
        self.cell_id = cell_id
        super().__init__(f"Cell not found: {cell_id}")


class SectionNotFoundError(LembicError):
    """Raised when a section ID/name is not found in the manifest."""

    def __init__(self, section_ref: str) -> None:
        self.section_ref = section_ref
        super().__init__(f"Section not found: {section_ref}")


class CellFileError(LembicError):
    """Raised when a cell's source file cannot be read or written."""


class ManifestError(LembicError):
    """Raised when the manifest is invalid or cannot be loaded."""


class KernelError(LembicError):
    """Raised when a kernel operation fails."""


class KernelNotStartedError(KernelError):
    """Raised when trying to use a kernel that hasn't been started."""


class ExecutionError(LembicError):
    """Raised when cell execution fails."""


class ProjectError(LembicError):
    """Raised when project initialization or configuration fails."""


class ExportError(LembicError):
    """Raised when export operations fail."""


class EnvironmentError(LembicError):
    """Raised when environment/venv operations fail."""
