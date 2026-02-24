"""Domain exceptions for DataFlow."""


class DataFlowError(Exception):
    """Base exception for all DataFlow errors."""


class CellNotFoundError(DataFlowError):
    """Raised when a cell ID is not found in the manifest."""

    def __init__(self, cell_id: str) -> None:
        self.cell_id = cell_id
        super().__init__(f"Cell not found: {cell_id}")


class CellFileError(DataFlowError):
    """Raised when a cell's source file cannot be read or written."""


class ManifestError(DataFlowError):
    """Raised when the manifest is invalid or cannot be loaded."""


class KernelError(DataFlowError):
    """Raised when a kernel operation fails."""


class KernelNotStartedError(KernelError):
    """Raised when trying to use a kernel that hasn't been started."""


class ExecutionError(DataFlowError):
    """Raised when cell execution fails."""


class ProjectError(DataFlowError):
    """Raised when project initialization or configuration fails."""


class ExportError(DataFlowError):
    """Raised when export operations fail."""
