"""Central configuration module for stock-graph-analyser.

All tunable parameters, file paths, and thresholds are defined here
so that every other module can import them from a single place.
"""

from __future__ import annotations

import os

# ---------------------------------------------------------------------------
# General
# ---------------------------------------------------------------------------
TEST_MODE: bool = os.getenv("TEST_MODE", "false").lower() == "true"
RESTRICT_STOCK_COUNT: int = int(os.getenv("RESTRICT_STOCK_COUNT", "1000"))
THREAD_COUNT: int = int(os.getenv("THREAD_COUNT", "64"))

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
RESOURCE_EXCEL_PATH: str = os.getenv(
    "RESOURCE_EXCEL_PATH", "./resource/stock_list.xlsm"
)
EXPORT_SCORE_DIR: str = os.getenv("EXPORT_SCORE_DIR", "./export/score/")
EXPORT_SCORE_RESULT_PATH: str = os.getenv(
    "EXPORT_SCORE_RESULT_PATH", "./export/score-result.md"
)
EXPORT_SCORE_HTML_PATH: str = os.getenv(
    "EXPORT_SCORE_HTML_PATH", "./export/score-result.html"
)
EXPORT_GRAPH_PATH_TEMPLATE: str = os.getenv(
    "EXPORT_GRAPH_PATH_TEMPLATE", "./export/graph/{filename}.html"
)

# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------
NAVER_FINANCE_BASE_URL: str = (
    "http://finance.naver.com/item/sise_day.nhn?code={code}"
)
HTTP_USER_AGENT: str = "Mozilla/5.0"
PAGE_COUNT: int = int(os.getenv("PAGE_COUNT", "12"))

# ---------------------------------------------------------------------------
# Moving averages
# ---------------------------------------------------------------------------
SMA_PERIODS: list[int] = [10, 20, 60, 120]
EMA_PERIODS: list[int] = [10, 20, 60, 120]
SMA_COLUMN_FORMAT: str = "SMA{value}"
EMA_COLUMN_FORMAT: str = "EMA{value}"

# ---------------------------------------------------------------------------
# Technical indicators
# ---------------------------------------------------------------------------
RSI_PERIOD: int = 14
MACD_FAST: int = 12
MACD_SLOW: int = 26
MACD_SIGNAL: int = 9

# ---------------------------------------------------------------------------
# Analyser scoring
# ---------------------------------------------------------------------------
TREND_COUNT: int = 280
SEARCH_COUNT: int = 72
CROSS_OFFSET_PERCENT: float = 4.25
SCORE_WEIGHT_MULTIPLIER: float = 1.5

RSI_NEUTRAL_BONUS: int = 5
RSI_OVERBOUGHT_PENALTY: int = 5
MACD_BULLISH_BONUS: int = 7
VOLUME_ABOVE_AVG_BONUS: int = 7
MINIMUM_PRICE_COUNT: int = 60
