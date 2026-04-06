"""Build a pandas DataFrame of historical price data with technical indicators.

Data is fetched from Naver Finance and enriched with SMA, EMA, RSI, and MACD
columns before being returned to the caller.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pandas as pd
import requests

from config import (
    EMA_COLUMN_FORMAT,
    EMA_PERIODS,
    HTTP_USER_AGENT,
    MACD_FAST,
    MACD_SLOW,
    MACD_SIGNAL,
    NAVER_FINANCE_BASE_URL,
    PAGE_COUNT,
    RSI_PERIOD,
    SMA_COLUMN_FORMAT,
    SMA_PERIODS,
)
from logger import get_logger

if TYPE_CHECKING:
    from stock_summary import StockSummary

_logger = get_logger(__name__)


class StockDataFrameGenerator:
    """Fetch historical stock data and produce a feature-rich DataFrame."""

    _sma_column_names: list[str] = []
    _ema_column_names: list[str] = []
    _ma_column_names: list[str] = []

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    @classmethod
    def initialize(cls) -> None:
        """Pre-compute column name lists from the configured periods."""
        start = time.time()

        cls._sma_column_names = [
            SMA_COLUMN_FORMAT.format(value=p) for p in SMA_PERIODS
        ]
        cls._ema_column_names = [
            EMA_COLUMN_FORMAT.format(value=p) for p in EMA_PERIODS
        ]
        cls._ma_column_names = cls._sma_column_names + cls._ema_column_names

        elapsed = round(time.time() - start, 4)
        _logger.info("StockDataFrameGenerator.initialize(): %s s", elapsed)

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    @classmethod
    def get_sma_column_names(cls) -> list[str]:
        """Return the list of SMA column names (e.g. ``['SMA10', …]``)."""
        return cls._sma_column_names

    @classmethod
    def get_ema_column_names(cls) -> list[str]:
        """Return the list of EMA column names."""
        return cls._ema_column_names

    @classmethod
    def get_ma_column_names(cls) -> list[str]:
        """Return all moving-average column names (SMA + EMA)."""
        return cls._ma_column_names

    # ------------------------------------------------------------------
    # Data frame generation
    # ------------------------------------------------------------------

    @classmethod
    def generate_data_frame(cls, summary: StockSummary) -> pd.DataFrame:
        """Fetch price history for *summary* and return an enriched DataFrame."""
        start = time.time()

        url = NAVER_FINANCE_BASE_URL.format(code=summary.code)
        frames: list[pd.DataFrame] = []

        for page in range(1, PAGE_COUNT):
            page_url = f"{url}&page={page}"
            try:
                response = requests.get(
                    page_url,
                    headers={"User-agent": HTTP_USER_AGENT},
                    timeout=30,
                )
                response.raise_for_status()
                page_tables = pd.read_html(response.text)
                frames.append(page_tables[0])
            except (requests.RequestException, ValueError) as exc:
                _logger.warning(
                    "Failed to fetch page %d for %s: %s", page, summary.name, exc
                )
                continue

        if not frames:
            _logger.error("No data fetched for %s", summary.name)
            return pd.DataFrame()

        data_frame = pd.concat(frames, ignore_index=True)

        # Rename Korean columns to English
        data_frame = data_frame.rename(
            columns={
                "날짜": "date",
                "종가": "close",
                "시가": "open",
                "고가": "high",
                "저가": "low",
                "거래량": "volume",
            }
        )

        data_frame = data_frame.dropna()

        # Convert data types
        data_frame["date"] = pd.to_datetime(data_frame["date"])
        numeric_cols = ["close", "open", "high", "low", "volume"]
        data_frame[numeric_cols] = data_frame[numeric_cols].astype(int)

        # Sort and re-index
        data_frame = data_frame.sort_values(by=["date"], ascending=True)
        data_frame = data_frame.reset_index(drop=True)

        # SMA
        for period in SMA_PERIODS:
            col = SMA_COLUMN_FORMAT.format(value=period)
            data_frame[col] = data_frame["close"].rolling(period).mean()

        # EMA
        for period in EMA_PERIODS:
            col = EMA_COLUMN_FORMAT.format(value=period)
            data_frame[col] = (
                data_frame["close"].ewm(span=period, adjust=False).mean()
            )

        # RSI
        delta = data_frame["close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(RSI_PERIOD).mean()
        avg_loss = loss.rolling(RSI_PERIOD).mean()
        rs = avg_gain / avg_loss
        data_frame[f"RSI{RSI_PERIOD}"] = 100 - (100 / (1 + rs))

        # MACD / Signal
        ema_fast = data_frame["close"].ewm(span=MACD_FAST, adjust=False).mean()
        ema_slow = data_frame["close"].ewm(span=MACD_SLOW, adjust=False).mean()
        data_frame["MACD"] = ema_fast - ema_slow
        data_frame["MACDS"] = (
            data_frame["MACD"].ewm(span=MACD_SIGNAL, adjust=False).mean()
        )

        elapsed = round(time.time() - start, 4)
        _logger.info(
            "StockDataFrameGenerator.generate_data_frame(%s): %s s",
            summary.name,
            elapsed,
        )

        return data_frame
