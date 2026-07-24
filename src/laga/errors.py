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
        context: str | None = None,
    ) -> None:
        self.message = message
        self.position = position
        self.context = context
        if position is None:
            formatted = message
        else:
            formatted = f"{message} at position {position}"
        if context:
            formatted = f"{formatted} near {context!r}"
        super().__init__(formatted)
