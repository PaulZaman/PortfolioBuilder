"""metrics.py – Return series & portfolio statistics
===================================================
Contains all numerical computations: returns, portfolio metrics,
and weight optimisation.
No I/O, no charts.
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from app.services.yfinance_service import RESAMPLE_RULE 

__all__ = [
    "calculate_returns",
    "sharpe_ratio",
    "sortino_ratio",
    "total_return",
    "periodic_avg_return",
    "optimise_weights",
    "compute_portfolio_series",
]

# ─────────────────────────────────────────────────────────────────────
#  RETURNS
# ─────────────────────────────────────────────────────────────────────

def calculate_returns(prices: pd.DataFrame, interval: str) -> pd.DataFrame:
    """Resample *prices* according to interval, then return pct‑change."""
    if interval not in RESAMPLE_RULE:
        raise ValueError(f"Unsupported interval '{interval}'")

    if not isinstance(prices.index, pd.DatetimeIndex):
        prices.index = pd.to_datetime(prices.index)

    rs = prices.resample(RESAMPLE_RULE[interval]).last().dropna()
    ret = rs.pct_change().dropna()
    if ret.empty:
        raise ValueError("No returns – insufficient data")
    return ret

# ─────────────────────────────────────────────────────────────────────
#  METRICS
# ─────────────────────────────────────────────────────────────────────

def _annualise(mu: float, ppy: int) -> float:
    """Linear annualisation (simple returns)."""
    return mu * ppy


def sharpe_ratio(weights: np.ndarray, returns: pd.DataFrame, rf: float = 0.0, ppy: int = 252) -> float:
    mu = np.dot(weights, returns.mean())
    sigma = np.sqrt(np.dot(weights.T, returns.cov() @ weights))
    return (_annualise(mu, ppy) - rf) / (sigma * np.sqrt(ppy))


def sortino_ratio(weights: np.ndarray, returns: pd.DataFrame, rf: float = 0.0, ppy: int = 252) -> float:
    mu = np.dot(weights, returns.mean())
    downside = returns.clip(upper=0)
    sigma_d = np.sqrt(np.dot(weights.T, downside.cov() @ weights))
    return (_annualise(mu, ppy) - rf) / (sigma_d * np.sqrt(ppy))


def total_return(weights: np.ndarray, returns: pd.DataFrame) -> float:
    cum = (1 + returns).cumprod().iloc[-1] - 1
    return np.dot(weights, cum)


def periodic_avg_return(weights: np.ndarray, returns: pd.DataFrame, period: str = "weekly") -> float:
    freq = {"weekly": 52, "daily": 252}[period]
    return np.dot(weights, returns.mean()) * freq

# ─────────────────────────────────────────────────────────────────────
#  OPTIMISATION
# ─────────────────────────────────────────────────────────────────────

def optimise_weights(
    returns: pd.DataFrame,
    metric: str = "sharpe",
    *,
    allow_short: bool = False,
    max_long: float = 1.0,
    max_short: float = 1.0,
) -> np.ndarray:
    """Optimise portfolio weights based on *metric*.

    Parameters
    ----------
    returns : DataFrame
        Return matrix (index = dates, columns = assets).
    metric : str
        One of "sharpe", "sortino", "total return", "weekly return", "daily return".
    allow_short : bool, optional
        If True, allows negative weights (short positions).
    max_long : float, optional
        Upper bound per asset for long positions.
    max_short : float, optional
        Lower bound (negative) per asset for short positions. Ignored if allow_short == False.
    """
    n = returns.shape[1]
    x0 = np.full(n, 1 / n)

    # Define bounds -----------------------------------------------------------
    if allow_short:
        bounds = [(-max_short, max_long) for _ in range(n)]
    else:
        bounds = [(0.0, max_long) for _ in range(n)]

    cons = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]

    def obj(w: np.ndarray) -> float:
        m = metric.lower()
        if m == "sharpe":
            return -sharpe_ratio(w, returns)
        if m == "sortino":
            return -sortino_ratio(w, returns)
        if m == "total return":
            return -total_return(w, returns)
        if m == "weekly return":
            return -periodic_avg_return(w, returns, "weekly")
        if m == "daily return":
            return -periodic_avg_return(w, returns, "daily")
        raise ValueError(f"Unsupported metric '{metric}'")

    res = minimize(obj, x0, bounds=bounds, constraints=cons, method="SLSQP")
    if not res.success:
        raise RuntimeError(res.message)
    return res.x

# ─────────────────────────────────────────────────────────────────────
#  CONVENIENCE
# ─────────────────────────────────────────────────────────────────────

def compute_portfolio_series(returns: pd.DataFrame, weights: np.ndarray) -> pd.Series:
    """Cumulative performance in percentage."""
    port = (returns * weights).sum(axis=1)
    cum_pct = ((1 + port).cumprod() - 1) * 100
    return cum_pct
