"""Compute trend scores for stocks and generate result reports.

The analyser inspects moving-average crossovers, RSI, MACD, and volume
signals to produce an overall score per stock.  Results are persisted as
empty marker files (for sorting) and later aggregated into a Markdown table.
"""

from __future__ import annotations

import glob
import os
from typing import TYPE_CHECKING

import pandas as pd

from config import (
    CROSS_OFFSET_PERCENT,
    EXPORT_SCORE_DIR,
    EXPORT_SCORE_RESULT_PATH,
    MACD_BULLISH_BONUS,
    MINIMUM_PRICE_COUNT,
    RSI_NEUTRAL_BONUS,
    RSI_OVERBOUGHT_PENALTY,
    RSI_PERIOD,
    SCORE_WEIGHT_MULTIPLIER,
    SEARCH_COUNT,
    TREND_COUNT,
    VOLUME_ABOVE_AVG_BONUS,
)
from logger import get_logger
from stock_data_frame_generator import StockDataFrameGenerator

if TYPE_CHECKING:
    from stock_summary import StockSummary

_logger = get_logger(__name__)


class StockAnalyser:
    """Score stocks based on technical indicators and persist the results."""

    export_path: str = EXPORT_SCORE_DIR

    _score_offset: float = 0.0

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    @classmethod
    def initialize(cls) -> None:
        """Pre-compute the per-step score offset."""
        cls._score_offset = 100 / SEARCH_COUNT * SCORE_WEIGHT_MULTIPLIER

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    @classmethod
    def analyze(cls, summary: StockSummary, data_frame: pd.DataFrame) -> None:
        """Run the full scoring pipeline for a single stock."""
        if data_frame.empty:
            _logger.warning("Empty DataFrame for %s – skipping analysis.", summary.name)
            return

        data_trend = data_frame.tail(SEARCH_COUNT + MINIMUM_PRICE_COUNT)
        total_count = len(data_trend)

        sma_names = StockDataFrameGenerator.get_sma_column_names()
        sma_short_middle_percents: list[float] = []
        sma_short_long_percents: list[float] = []

        price = price_7 = price_30 = price_60 = 0
        volumes: list[float] = []

        count = 0
        for row in data_trend.itertuples():
            if count < MINIMUM_PRICE_COUNT:
                count += 1
                continue

            day_offset = total_count - getattr(row, "Index")
            sma_short = getattr(row, sma_names[0])
            sma_middle = getattr(row, sma_names[1])
            sma_long = getattr(row, sma_names[2])
            close_price = getattr(row, "close")

            if day_offset <= TREND_COUNT:
                sma_short_middle_percents.append(
                    (sma_short - sma_middle) / sma_middle
                )
                sma_short_long_percents.append(
                    (sma_short - sma_long) / sma_long
                )

            if day_offset <= 1 and price == 0:
                price = close_price
            elif day_offset <= 7 and price_7 == 0:
                price_7 = close_price
            elif day_offset <= 30 and price_30 == 0:
                price_30 = close_price
            elif day_offset <= 60 and price_60 == 0:
                price_60 = close_price

            volumes.append(getattr(row, "volume", 0))

        # Base scores from MA trends
        score_short = cls._get_score(sma_short_middle_percents)
        score_long = cls._get_score(sma_short_long_percents)

        # Indicator bonus / penalty
        indicator_offset = cls._compute_indicator_offset(data_frame, volumes)

        # Persist summary data
        summary.update_trend_score(indicator_offset)
        summary.price = price
        summary.price_7 = price_7
        summary.price_30 = price_30
        summary.price_60 = price_60

        score_short -= indicator_offset
        score_long -= indicator_offset

        score_overall = cls._weighted_overall(score_short, score_long)

        _logger.info("%s 점수: %d", summary.name, indicator_offset)
        cls._save_result(summary, score_overall, score_short, score_long)

    # ------------------------------------------------------------------
    # Scoring helpers
    # ------------------------------------------------------------------

    @classmethod
    def _compute_indicator_offset(
        cls, data_frame: pd.DataFrame, volumes: list[float]
    ) -> int:
        """Return extra score points based on RSI, MACD, and volume."""
        offset = 0

        # RSI
        rsi_col = f"RSI{RSI_PERIOD}"
        if rsi_col in data_frame.columns:
            last_rsi = data_frame[rsi_col].iloc[-1]
            if last_rsi is not None:
                if 30 < last_rsi < 70:
                    offset += RSI_NEUTRAL_BONUS
                elif last_rsi > 70:
                    offset -= RSI_OVERBOUGHT_PENALTY

        # MACD
        if "MACD" in data_frame.columns and "MACDS" in data_frame.columns:
            if data_frame["MACD"].iloc[-1] > data_frame["MACDS"].iloc[-1]:
                offset += MACD_BULLISH_BONUS

        # Volume
        avg_volume = sum(volumes) / len(volumes) if volumes else 0
        if "volume" in data_frame.columns:
            current_volume = data_frame["volume"].iloc[-1]
            if current_volume > avg_volume:
                offset += VOLUME_ABOVE_AVG_BONUS

        return offset

    @classmethod
    def _get_score(cls, ma_percents: list[float]) -> int:
        """Score an MA-percent series by counting upward transitions."""
        if not ma_percents:
            return 0

        score: float = 0.0

        for i in range(len(ma_percents)):
            if i == 0:
                if ma_percents[i] < 0:
                    score += cls._score_offset
                continue
            if ma_percents[i] > ma_percents[i - 1]:
                score += cls._score_offset

        # Cross score – bonus when near the crossover zone
        score += cls._get_cross_score(ma_percents[-1])

        return int(score)

    @classmethod
    def _get_cross_score(cls, last_ma_percent: float) -> float:
        """Return a bonus if the last MA percent is near the crossover."""
        if -CROSS_OFFSET_PERCENT <= last_ma_percent <= CROSS_OFFSET_PERCENT:
            return cls._score_offset
        return 0.0

    @classmethod
    def _weighted_overall(cls, score_short: int, score_long: int) -> int:
        """Compute a weighted overall score from short / long components."""
        max_score = max(score_short, score_long, 1)

        short_ratio = score_short / max_score
        long_ratio = score_long / max_score

        short_weight = 0.3 + 0.7 * short_ratio
        long_weight = 0.3 + 0.7 * long_ratio

        total_weight = short_weight + long_weight
        return round(
            (score_short * short_weight + score_long * long_weight) / total_weight
        )

    # ------------------------------------------------------------------
    # File I/O
    # ------------------------------------------------------------------

    @classmethod
    def _save_result(
        cls,
        summary: StockSummary,
        score_overall: int,
        score_short: int,
        score_long: int,
    ) -> None:
        """Create an empty marker file whose name encodes the scores."""
        file_name = cls._build_file_name(
            summary, score_overall, score_short, score_long
        )
        try:
            with open(file_name, "w"):
                pass
        except OSError as exc:
            _logger.error("Failed to write result for %s: %s", summary.name, exc)

    @classmethod
    def _build_file_name(
        cls,
        summary: StockSummary,
        score_overall: int,
        score_short: int,
        score_long: int,
    ) -> str:
        """Return the full path for a score marker file."""
        template = (
            "{overall}_{short}_{long}_{name}_{code}"
            "_{price}_{price7}_{price30}_{price60}.txt"
        )
        name = template.format(
            overall=score_overall,
            short=score_short,
            long=score_long,
            name=summary.name,
            code=summary.code,
            price=summary.price,
            price7=summary.price_7,
            price30=summary.price_30,
            price60=summary.price_60,
        )
        return os.path.join(cls.export_path, name)

    # ------------------------------------------------------------------
    # Report generation
    # ------------------------------------------------------------------

    @classmethod
    def _natural_sort(cls, paths: list[str]) -> list[str]:
        """Sort file paths by the leading numeric score (descending)."""
        return sorted(
            paths,
            key=lambda p: int(os.path.basename(p).split("_")[0]),
            reverse=True,
        )

    @classmethod
    def _format_change(cls, value: float) -> str:
        """Format a percentage change with coloured emoji prefix."""
        arrow = "🟥+" if value > 0 else "🟦-"
        return f"{arrow}{abs(value):.2f}%"

    @classmethod
    def save_score_list(cls) -> None:
        """Aggregate all score marker files into a Markdown report."""
        file_paths = [
            p
            for p in glob.glob(os.path.join(EXPORT_SCORE_DIR, "*.txt"))
            if not p.endswith("Temp.txt")
        ]
        file_paths = cls._natural_sort(file_paths)

        header = "| 종합 점수 | 단기 점수 | 장기 점수 | 종목명 | 현재가 | 7D | 30D | 60D |"
        separator = "|-------|-------|-------|----------|----------|------------|------------|------------|"

        try:
            with open(EXPORT_SCORE_RESULT_PATH, "w") as fout:
                fout.write(header + "  \n")
                fout.write(separator + "  \n")

                for file_path in file_paths:
                    file_name = os.path.basename(file_path).replace(".txt", "")
                    if file_name == "Temp":
                        continue

                    elems = file_name.split("_")
                    score_overall = elems[0]
                    score_short = elems[1]
                    score_long = elems[2]
                    name = elems[3]
                    code = elems[4]
                    price = int(elems[5])
                    raw_price_7 = int(elems[6])
                    raw_price_30 = int(elems[7])
                    raw_price_60 = int(elems[8])

                    pct_7 = (
                        0.0
                        if raw_price_7 == 0
                        else (price - raw_price_7) / raw_price_7 * 100
                    )
                    pct_30 = (
                        0.0
                        if raw_price_30 == 0
                        else (price - raw_price_30) / raw_price_30 * 100
                    )
                    pct_60 = (
                        0.0
                        if raw_price_60 == 0
                        else (price - raw_price_60) / raw_price_60 * 100
                    )

                    url = f"https://finance.naver.com/item/fchart.naver?code={code}"
                    line = (
                        f"| {score_overall}점 | {score_short}점 | {score_long}점 "
                        f"| [{name}]({url}) | {price:,}원 "
                        f"| {cls._format_change(pct_7)} "
                        f"| {cls._format_change(pct_30)} "
                        f"| {cls._format_change(pct_60)} |"
                    )
                    fout.write(line + "  \n")

                fout.write("\nEOF \n")
        except OSError as exc:
            _logger.error("Failed to write score list: %s", exc)
