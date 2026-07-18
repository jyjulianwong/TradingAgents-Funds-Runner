"""
Entry point executed inside the Docker container.

Reads /app/config.py (mounted at runtime), runs TradingAgentsGraph for every
symbol sequentially, converts the Markdown report to PDF, then uploads the PDF
to the configured storage backend.
"""

import importlib.util
import logging
import os
import sys
from datetime import date
from pathlib import Path
from types import ModuleType

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph

from runner.convert import md_to_pdf
from runner.uploaders.base import BaseUploader
from runner.uploaders.s3 import S3Uploader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

_CONFIG_PATH = Path("/app/config.py")
_REPORTS_ROOT = Path("/app/reports")


def _load_run_config() -> ModuleType:
    if not _CONFIG_PATH.exists():
        logger.error("config.py not found at %s — mount it with -v $(pwd)/config.py:/app/config.py:ro", _CONFIG_PATH)
        sys.exit(1)
    spec = importlib.util.spec_from_file_location("config", _CONFIG_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _signal_to_folder(signal: str) -> str:
    """Map the 5-tier PM rating to one of three upload folder names."""
    return {"Buy": "buy", "Overweight": "buy", "Hold": "hold", "Underweight": "sell", "Sell": "sell"}.get(
        signal, "hold"
    )


def _build_uploader() -> BaseUploader:
    bucket = os.environ.get("AWS_S3_REPORTS_BUCKET_NAME")
    if not bucket:
        logger.error("AWS_S3_REPORTS_BUCKET_NAME is not set — cannot upload reports")
        sys.exit(1)
    region = os.environ.get("AWS_DEFAULT_REGION", "eu-west-2")
    return S3Uploader(bucket=bucket, region=region)


def _run_symbol(
    symbol: str,
    analysis_date: str,
    analysts: list[str],
    uploader: BaseUploader,
) -> bool:
    """Run TradingAgents for one symbol, convert to PDF, upload. Returns True on success."""
    report_dir = _REPORTS_ROOT / analysis_date / symbol

    logger.info("=== %s | %s ===", symbol, analysis_date)
    try:
        ta_config = {
            **DEFAULT_CONFIG,
            "results_dir": str(_REPORTS_ROOT),
            "data_cache_dir": str(_REPORTS_ROOT / ".cache"),
            "enable_visualizer": False,
        }
        ta = TradingAgentsGraph(selected_analysts=tuple(analysts), config=ta_config)

        final_state, signal = ta.propagate(symbol, analysis_date)
        logger.info("%s signal: %s", symbol, signal)

        complete_report_path = ta.save_reports(final_state, symbol, save_path=report_dir)
        logger.info("Markdown report saved to %s", complete_report_path)

        pdf_path = report_dir / "final_report.pdf"
        md_to_pdf(complete_report_path, pdf_path)
        logger.info("PDF rendered at %s", pdf_path)

        remote_key = f"reports/{analysis_date}/{_signal_to_folder(signal)}/{symbol}/final_report.pdf"
        url = uploader.upload(pdf_path, remote_key)
        logger.info("Uploaded to %s", url)
        return True

    except Exception:
        logger.exception("Failed to process %s", symbol)
        return False


def main() -> None:
    cfg = _load_run_config()

    symbols: list[str] = cfg.SYMBOLS
    analysis_date: str = cfg.ANALYSIS_DATE or date.today().isoformat()
    analysts: list[str] = getattr(cfg, "ANALYSTS", ["market", "social", "news", "fundamentals"])

    if not symbols:
        logger.error("SYMBOLS list in config.py is empty — nothing to do")
        sys.exit(1)

    logger.info("Run config: date=%s, analysts=%s, symbols=%s", analysis_date, analysts, symbols)

    uploader = _build_uploader()

    results: dict[str, bool] = {}
    for symbol in symbols:
        results[symbol] = _run_symbol(symbol, analysis_date, analysts, uploader)

    passed = [s for s, ok in results.items() if ok]
    failed = [s for s, ok in results.items() if not ok]

    logger.info("Done — %d succeeded, %d failed", len(passed), len(failed))
    if passed:
        logger.info("  OK : %s", ", ".join(passed))
    if failed:
        logger.warning("  ERR: %s", ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()
