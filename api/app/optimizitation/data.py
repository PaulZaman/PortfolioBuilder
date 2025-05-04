"""data.py – Data retrieval layer for Yahoo Finance
-------------------------------------------------
Centralizes all functions that access Yahoo Finance (via yfinance).
Other modules should NOT import yfinance directly, but use the helpers exposed here.
"""

import logging
import re
import warnings
from datetime import datetime
from typing import Iterable, Dict

import pandas as pd
import yfinance as yf

__all__ = [
    "INTRADAY_LIMIT_DAYS",
    "RESAMPLE_RULE",
    "fetch_prices",
]

# ─────────────────────────────────────────────────────────────────────────────
#  INTERNAL CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
# Maximum intraday lookback supported by Yahoo Finance.
INTRADAY_LIMIT_DAYS: Dict[str, int] = {
    "1m": 7,
    "2m": 60,
    "5m": 60,
    "15m": 60,
    "30m": 60,
    "60m": 730,
    "90m": 60,
    "1h": 730,
    "4h": 730,
}

# Mapping yfinance intervals to pandas resample rules (shared with metrics)
RESAMPLE_RULE: Dict[str, str] = {
    "1m": "1T", "2m": "2T", "5m": "5T", "15m": "15T",
    "30m": "30T", "60m": "60T", "90m": "90T",
    "1h": "1H", "4h": "4H", "1d": "1D", "5d": "5D",
    "1wk": "1W", "1mo": "1M", "3mo": "3M",
}

_logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def _extract_close(df: pd.DataFrame) -> pd.Series | None:
    """Extract the closing price series (Adjusted Close if available, otherwise Close)."""
    if df.empty:
        return None
    if isinstance(df.columns, pd.MultiIndex):
        lvl0 = df.columns.get_level_values(0)
        col = "Adj Close" if "Adj Close" in lvl0 else "Close"
        return df.xs(col, level=0, axis=1).iloc[:, 0].dropna()
    col = "Adj Close" if "Adj Close" in df.columns else "Close"
    return df[col].dropna()


def _download_single(ticker: str, start: pd.Timestamp, end: pd.Timestamp, interval: str) -> pd.Series | None:
    """Download a single ticker with one retry attempt and a period fallback."""
    tried_retry = False
    while True:
        try:
            df = yf.download(
                ticker,
                start=start.strftime("%Y-%m-%d"),
                end=end.strftime("%Y-%m-%d"),
                interval=interval,
                progress=False,
                auto_adjust=False,
                timeout=30,
            )
            ser = _extract_close(df)
            if ser is not None and not ser.empty:
                return ser
            raise ValueError("empty dataframe")
        except Exception as exc:
            msg = str(exc)
            match = re.search(r"(?:Only|last|within the last)\s+(\d+)\s+days", msg, re.IGNORECASE)
            if match and not tried_retry:
                limit = int(match.group(1))
                start = end - pd.Timedelta(days=limit - 1)
                _logger.info("%s: Yahoo limit %s d – retrying with start=%s", ticker, limit, start.date())
                tried_retry = True
                continue
            warnings.warn(f"{ticker}: download failed – {msg}")
            break

    # Fallback method using period="Xd"
    limit = INTRADAY_LIMIT_DAYS.get(interval, 30)
    try:
        _logger.info("%s: fallback using period=%sd", ticker, limit)
        df = yf.download(
            ticker,
            period=f"{limit}d",
            interval=interval,
            progress=False,
            auto_adjust=False,
            timeout=30,
        )
        return _extract_close(df)
    except Exception as exc:
        warnings.warn(f"{ticker}: fallback failed – {exc}")
        return None

# ─────────────────────────────────────────────────────────────────────────────
#  PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────

def fetch_prices(
    tickers: Iterable[str],
    start_date: str | pd.Timestamp,
    end_date: str | pd.Timestamp | None = None,
    interval: str = "1d",
) -> pd.DataFrame:
    """Download and align close price series for given tickers and interval.

    - If the intraday interval exceeds the Yahoo limit, start_date is trimmed.
    - Tickers that fail to download are skipped with warnings.
    - Raises ValueError if no usable data is retrieved.
    """
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date) if end_date else pd.Timestamp.today().normalize()

    # Adjust start date if interval is intraday and too long
    max_hist = INTRADAY_LIMIT_DAYS.get(interval)
    if max_hist and (end - start).days + 1 > max_hist:
        warnings.warn(
            f"Interval '{interval}' is limited to {max_hist} days – start_date was adjusted automatically.")
        start = end - pd.Timedelta(days=max_hist - 1)

    data: dict[str, pd.Series] = {}
    for tk in tickers:
        _logger.info("%s: downloading %s %s → %s", tk, interval, start.date(), end.date())
        ser = _download_single(tk, start, end, interval)
        if ser is None or ser.empty:
            warnings.warn(f"{tk}: no data retrieved – skipped")
            continue
        data[tk] = ser

    if not data:
        raise ValueError("No usable price data fetched.")

    df = pd.DataFrame(data).dropna(how="all")
    if df.empty:
        raise ValueError("Price DataFrame is empty after alignment.")
    return df
