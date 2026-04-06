"""Domain model representing a single stock summary.

The class also acts as an in-memory registry so that any module can look up
a :class:`StockSummary` by its stock code.
"""

from __future__ import annotations


class StockSummary:
    """Holds metadata and computed scores for one stock ticker."""

    _code_summary_map: dict[str, StockSummary] = {}

    # ------------------------------------------------------------------
    # Registry (class-level)
    # ------------------------------------------------------------------

    @classmethod
    def add_summary(cls, summary: StockSummary) -> None:
        """Register *summary* so it can be retrieved by code later."""
        cls._code_summary_map[summary.code] = summary

    @classmethod
    def get_codes(cls) -> list[str]:
        """Return all registered stock codes."""
        return list(cls._code_summary_map.keys())

    @classmethod
    def get_summary(cls, code: str) -> StockSummary:
        """Return the :class:`StockSummary` for *code*.

        Raises:
            KeyError: If *code* has not been registered.
        """
        return cls._code_summary_map[code]

    # ------------------------------------------------------------------
    # Instance
    # ------------------------------------------------------------------

    def __init__(self, name: str, raw_code: str) -> None:
        self._name: str = name
        self._raw_code: str = raw_code
        self._code: str = str(raw_code).rjust(6, "0")
        self._trend_score: int = 0

        # Price fields – initialised to 0 until the analyser sets them.
        self._price: int = 0
        self._price_7: int = 0
        self._price_30: int = 0
        self._price_60: int = 0

    def __repr__(self) -> str:
        return f"StockSummary(name={self._name!r}, code={self._code!r})"

    # ------------------------------------------------------------------
    # Read-only properties
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Company name."""
        return self._name

    @property
    def raw_code(self) -> str:
        """Original (unpadded) code from the Excel source."""
        return self._raw_code

    @property
    def code(self) -> str:
        """Zero-padded 6-digit stock code."""
        return self._code

    # ------------------------------------------------------------------
    # Price properties (read/write)
    # ------------------------------------------------------------------

    @property
    def price(self) -> int:
        """Current closing price."""
        return self._price

    @price.setter
    def price(self, value: int) -> None:
        self._price = value

    @property
    def price_7(self) -> int:
        """Closing price 7 trading days ago."""
        return self._price_7

    @price_7.setter
    def price_7(self, value: int) -> None:
        self._price_7 = value

    @property
    def price_30(self) -> int:
        """Closing price 30 trading days ago."""
        return self._price_30

    @price_30.setter
    def price_30(self, value: int) -> None:
        self._price_30 = value

    @property
    def price_60(self) -> int:
        """Closing price 60 trading days ago."""
        return self._price_60

    @price_60.setter
    def price_60(self, value: int) -> None:
        self._price_60 = value

    # ------------------------------------------------------------------
    # Trend score
    # ------------------------------------------------------------------

    @property
    def trend_score(self) -> int:
        """Computed trend score assigned by :class:`StockAnalyser`."""
        return self._trend_score

    def update_trend_score(self, score: int) -> None:
        """Set a new *score* for this stock."""
        self._trend_score = score
