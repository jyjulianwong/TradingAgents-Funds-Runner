"""
Run configuration — edit this file to control which symbols are analysed and
how TradingAgents is configured for each run.

All TRADINGAGENTS_* environment variables documented in .env.example still apply
and take precedence over any matching DEFAULT_CONFIG values; this file only
exposes the settings that are specific to the runner (symbols, date, analysts).
"""

# Tickers / ISINs to analyse. Processed sequentially in the order listed.
SYMBOLS: list[str] = [
    "AAPL",
    "MSFT",
]

# Analysis date as "YYYY-MM-DD", or None to default to today.
ANALYSIS_DATE: str | None = None

# Analyst team to include. Valid keys: "market", "social", "news", "fundamentals".
ANALYSTS: list[str] = ["market", "social", "news", "fundamentals"]
