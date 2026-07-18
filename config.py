"""
Run configuration — edit this file to control which symbols are analysed and
how TradingAgents is configured for each run.

All TRADINGAGENTS_* environment variables documented in .env.example still apply
and take precedence over any matching DEFAULT_CONFIG values; this file only
exposes the settings that are specific to the runner (symbols, date, analysts).
"""

# Tickers / ISINs to analyse. Processed sequentially in the order listed.
SYMBOLS: list[str] = [
    "GB00BJS8SF95",  # Fidelity Index UK P Acc (FTSE All-Share proxy)
    "GB00BJS8SH10",  # Fidelity Index US P Acc (S&P 500)
    "GB00B8HPRW47",  # FP WHEB Sustainability Impact C Acc (top 3 holdings)
    "GB00B80QG615",  # HSBC American Index Acc C (S&P 500)
    "GB00BN08ZN29",  # iShares Corporate Bond Index S Acc (iBoxx GBP Non-Gilts proxy)
    "GB00BN091933",  # iShares Enviro & Low Carbon Tilt Real Estate S Acc (FTSE EPRA Nareit proxy)
    "GB00BN08ZG51",  # iShares Japan Equity Index S Acc (FTSE Japan)
    "GB00BN08ZQ59",  # iShares Pacific ex Japan Equity Index S Acc
    "GB00BG0QP042",  # L&G European Index C Acc (FTSE World Europe ex UK)
    "GB00BL6C2119",  # L&G Future World ESG Tilted & Opt Emerging Markets C Acc
    "GB00BMFXWS95",  # L&G Future World ESG Tilted & Opt Developed C Acc
    "GB00BJLP1W53",  # L&G Global Technology Index Trust C Acc (FTSE World Technology)
    "GB00BK5HLJ16",  # abrdn Global REIT Tracker N Acc (FTSE EPRA Nareit Developed)
    "GB00B784NS11",  # AXA Framlington Biotech Z Acc (top 3 holdings)
    "GB00B6WZJX05",  # AXA Framlington Health Z Acc (top 3 holdings)
    "GB00B3B9VD63",  # Barings Global Agriculture I Acc (top 3 holdings)
    "GB00B6865B79",  # BlackRock Natural Resources D Acc (top 3 holdings)
    "GB00B88MP089",  # JPMorgan Natural Resources C Acc (top 3 holdings)
    "GB00BVLL5586",  # Ninety One Global Gold B Inc (top 3 holdings)
    "GB00B76V7Q08",  # Schroder Global Healthcare Z Acc (top 3 holdings)
    "GB00B56FW078",  # WS Guinness Global Energy I Acc (largest weights, proxy via sister strategy)
]

# Analysis date as "YYYY-MM-DD", or None to default to today.
ANALYSIS_DATE: str | None = None

# Analyst team to include. Valid keys: "market", "social", "news", "fundamentals".
ANALYSTS: list[str] = ["market", "social", "news", "fundamentals"]
