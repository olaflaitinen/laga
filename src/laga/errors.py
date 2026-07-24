from __future__ import annotations


class LagaError(ValueError):
    """Raised when JSON repair cannot produce a valid result.

    Args:
        message: Human-readable explanation of the failure.
        position: Character offset where the problem was detected, if known.
    """

    def __init__(
        self,
        message: str,
        position: int | None = None,
        line: int | None = None,
        column: int | None = None,
        context: str | None = None,
    ) -> None:
        self.message = message
        self.position = position
        self.line = line
        self.column = column
        self.context = context
        if line is not None and column is not None:
            formatted = f"{message} at line {line}, column {column}"
        elif position is None:
            formatted = message
        else:
            formatted = f"{message} at position {position}"
        if context:
            formatted = f"{formatted} near {context!r}"
        super().__init__(formatted)
