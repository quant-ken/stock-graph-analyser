"""Parse the stock-list Excel file and populate the StockSummary registry."""

from __future__ import annotations

import time

import pandas as pd

from config import RESOURCE_EXCEL_PATH
from logger import get_logger
from stock_summary import StockSummary

_logger = get_logger(__name__)


class StockSummaryParser:
    """Read the master stock list and create :class:`StockSummary` instances."""

    @classmethod
    def initialize(cls, restrict_stock_count: int) -> None:
        """Load the Excel file and register up to *restrict_stock_count* stocks."""
        start = time.time()

        try:
            data_frame = pd.read_excel(RESOURCE_EXCEL_PATH)
        except FileNotFoundError:
            _logger.error("Stock list not found: %s", RESOURCE_EXCEL_PATH)
            raise

        for idx, row in enumerate(data_frame.itertuples(index=True)):
            if idx >= restrict_stock_count:
                break
            cls._process_row(row)

        elapsed = round(time.time() - start, 4)
        _logger.info("StockSummaryParser.initialize(): %s s", elapsed)

    @classmethod
    def _process_row(cls, row: object) -> None:
        """Create a :class:`StockSummary` from a single Excel row."""
        summary = StockSummary(
            name=getattr(row, "종목명"),
            raw_code=getattr(row, "종목코드"),
        )
        StockSummary.add_summary(summary)
