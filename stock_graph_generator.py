"""Generate interactive candlestick charts with technical overlays.

Charts are rendered as self-contained HTML files using Plotly.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pandas as pd
import plotly.graph_objs as graph_obj
import plotly.offline as offline
from plotly.subplots import make_subplots

from config import EXPORT_GRAPH_PATH_TEMPLATE
from logger import get_logger
from stock_data_frame_generator import StockDataFrameGenerator

if TYPE_CHECKING:
    from stock_summary import StockSummary

_logger = get_logger(__name__)


class StockGraphGenerator:
    """Create and save candlestick + volume charts for a single stock."""

    @classmethod
    def generate_graph(
        cls, summary: StockSummary, data_frame: pd.DataFrame
    ) -> None:
        """Build a Plotly figure for *summary* and persist it as HTML."""
        start = time.time()

        if data_frame.empty:
            _logger.warning("Empty DataFrame for %s – skipping graph.", summary.name)
            return

        # Identify non-trading dates for gap removal
        date_all = pd.date_range(
            start=data_frame["date"].iloc[0],
            end=data_frame["date"].iloc[-1],
        )
        date_obs = {d.strftime("%Y-%m-%d") for d in data_frame["date"]}
        date_breaks = [
            d for d in date_all.strftime("%Y-%m-%d").tolist() if d not in date_obs
        ]

        # Layout: rows 1-2 = candlestick, row 3 = volume
        fig = make_subplots(
            rows=3,
            cols=1,
            shared_xaxes=True,
            specs=[[{"rowspan": 2}], [None], [{}]],
        )

        fig.add_trace(
            graph_obj.Candlestick(
                x=data_frame.date,
                open=data_frame.open,
                high=data_frame.high,
                low=data_frame.low,
                close=data_frame.close,
                increasing_line_color="red",
                decreasing_line_color="blue",
                name="일봉",
            ),
            row=1,
            col=1,
        )

        for column_name in StockDataFrameGenerator.get_ma_column_names():
            fig.add_trace(
                graph_obj.Scatter(
                    x=data_frame.date,
                    y=data_frame[column_name],
                    name=column_name,
                ),
                row=1,
                col=1,
            )

        fig.add_trace(
            graph_obj.Bar(
                x=data_frame.date,
                y=data_frame.volume,
                name="거래량",
            ),
            row=3,
            col=1,
        )

        fig.update_layout(
            title=f"{summary.name} - {summary.trend_score}"
        )
        fig.update_xaxes(rangeslider_visible=False)
        fig.update_xaxes(rangebreaks=[dict(values=date_breaks)])

        cls._save_graph(summary, fig)

        elapsed = round(time.time() - start, 4)
        _logger.info(
            "StockGraphGenerator.generate_graph(%s): %s s", summary.name, elapsed
        )

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    @classmethod
    def _save_graph(cls, summary: StockSummary, fig: graph_obj.Figure) -> None:
        """Write *fig* to an HTML file named after the stock."""
        path = EXPORT_GRAPH_PATH_TEMPLATE.format(filename=summary.name)
        offline.plot(fig, auto_open=False, filename=path)

    @classmethod
    def show_graph(cls, fig: graph_obj.Figure) -> None:  # pragma: no cover
        """Open *fig* in the default browser (for local debugging)."""
        fig.show()
