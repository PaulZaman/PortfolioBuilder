from pathlib import Path
from typing import Optional

import pandas as pd

from app.services.yfinance_service import fetch_prices

from app.optimizitation.metrics import (
    calculate_returns,
    optimise_weights,
    compute_portfolio_series,
    sharpe_ratio,
    sortino_ratio,
    total_return,
    periodic_avg_return,
)


def _evaluate_metric(metric: str, weights, returns) -> float:
    m = metric.lower()
    if m == "sharpe":
        return sharpe_ratio(weights, returns)
    if m == "sortino":
        return sortino_ratio(weights, returns)
    if m == "total return":
        return total_return(weights, returns)
    if m == "weekly return":
        return periodic_avg_return(weights, returns, "weekly")
    if m == "daily return":
        return periodic_avg_return(weights, returns, "daily")
    raise ValueError(f"Unsupported metric '{metric}'")


def optimize_portfolio(
    tickers: list[str],
    start_date: str,
    end_date: Optional[str] = None,
    interval: str = "1d",
    metric: str = "sharpe",
    allow_short: bool = False,
    max_long: float = 1.0,
    max_short: float = 1.0,
) -> dict:
    """
    Compute the optimal portfolio allocation based on a selected metric.

    Parameters
    ----------
    tickers : list of str
        List of Yahoo tickers.
    start : str
        Start date in YYYY-MM-DD format.
    end : str, optional
        End date (default: today).
    interval : str
        Data interval (e.g. '1d', '1m').
    metric : str
        Objective metric (e.g. 'sharpe', 'sortino', 'total return').
    allow_short : bool
        If True, allow short selling.
    max_long : float
        Max weight per asset.
    max_short : float
        Max short weight per asset (only if allow_short=True).

    Returns
    -------
    dict
        { 'weights': {ticker: weight, ...}, 'score': float, 'cum_returns': pd.Series }
    """
    prices = fetch_prices(
        tickers=tickers,
        start_date=start_date,
        end_date=end_date,
        interval=interval,
    )

    returns = calculate_returns(prices, interval)
    weights = optimise_weights(
        returns,
        metric=metric,
        allow_short=allow_short,
        max_long=max_long,
        max_short=max_short,
    )
    weights_dict = {tk: float(round(w, 6)) for tk, w in zip(returns.columns, weights)}
    score = _evaluate_metric(metric, weights, returns)
    cum_pct = compute_portfolio_series(returns, weights)

    return {
        "weights": weights_dict,
        "score": float(round(score, 6)),
        "cum_returns": cum_pct,
    }
