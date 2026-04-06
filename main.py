"""Entry-point for the stock-graph-analyser pipeline.

Orchestrates: parsing → data-frame generation → analysis → graph export.
"""

from __future__ import annotations

import glob
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import RESTRICT_STOCK_COUNT, TEST_MODE, THREAD_COUNT
from logger import get_logger, setup_logging
from stock_analyser import StockAnalyser
from stock_data_frame_generator import StockDataFrameGenerator
from stock_graph_generator import StockGraphGenerator
from stock_summary import StockSummary
from stock_summary_parser import StockSummaryParser

_logger = get_logger(__name__)


def initialize() -> None:
    """Bootstrap all subsystems."""
    StockSummaryParser.initialize(RESTRICT_STOCK_COUNT)
    StockDataFrameGenerator.initialize()
    StockAnalyser.initialize()


def process(stock_code: str) -> None:
    """Run the full pipeline for a single *stock_code*."""
    try:
        summary = StockSummary.get_summary(stock_code)
        data_frame = StockDataFrameGenerator.generate_data_frame(summary)
        StockAnalyser.analyze(summary, data_frame)
        StockGraphGenerator.generate_graph(summary, data_frame)
    except Exception:
        _logger.exception("Failed to process stock %s", stock_code)


def pre_run() -> None:
    """Clean up stale score files from the previous run."""
    for file_path in glob.glob(os.path.join(StockAnalyser.export_path, "*")):
        if not file_path.endswith("Temp.txt"):
            try:
                os.remove(file_path)
            except OSError as exc:
                _logger.warning("Could not remove %s: %s", file_path, exc)


def run() -> None:
    """Dispatch to test or production mode."""
    if TEST_MODE:
        _run_test()
    else:
        _run_production()


def _run_test() -> None:
    """Process a single stock for quick debugging."""
    process("005930")  # 삼성전자


def _run_production() -> None:
    """Process all registered stocks in parallel."""
    futures = []
    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        for code in StockSummary.get_codes():
            futures.append(executor.submit(process, code))
        for future in as_completed(futures):
            future.result()


if __name__ == "__main__":
    setup_logging()

    start = time.time()

    initialize()
    pre_run()
    run()

    StockAnalyser.save_score_list()
    StockAnalyser.save_score_html()
    _logger.info("main.py: %s s", round(time.time() - start, 4))
