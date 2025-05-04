import argparse
import logging
import webbrowser
from pathlib import Path

import pandas as pd

from app.services.yfinance_service import fetch_prices
from metrics import (
    calculate_returns,
    optimise_weights,
    compute_portfolio_series,
    sharpe_ratio,
    sortino_ratio,
    total_return,
    periodic_avg_return,
)
from charts import cumulative_return_chart

# ----------------------------------------------------------------------------
#  CLI
# ----------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Portfolio optimiser (Yahoo Finance)")
    p.add_argument("--tickers", nargs="+", required=True, help="List of tickers")
    p.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    p.add_argument("--end", help="End date (default: today)")
    p.add_argument("--interval", default="1d", help="Yahoo interval, e.g. 1m, 5m, 1d…")
    p.add_argument("--metric", default="sharpe", help="Optimisation metric")
    p.add_argument("--outfile", default="portfolio.html", help="HTML output path")
    return p


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


def main():
    parser = _build_parser()
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    # 1) Fetch price data -----------------------------------------------------
    prices = fetch_prices(
        tickers=args.tickers,
        start_date=args.start,
        end_date=args.end,
        interval=args.interval,
    )

    # 2) Compute returns & optimise weights ----------------------------------
    returns = calculate_returns(prices, args.interval)
    weights = optimise_weights(returns, args.metric)
    weights_dict = {c: round(w, 4) for c, w in zip(returns.columns, weights)}

    # 3) Build portfolio performance series ----------------------------------
    cum_pct = compute_portfolio_series(returns, weights)

    # 4) Compute metric value ------------------------------------------------
    score = _evaluate_metric(args.metric, weights, returns)

    # 5) Create figure & export ----------------------------------------------
    fig = cumulative_return_chart(cum_pct, f"Optimised Portfolio – {args.metric.capitalize()}")
    out = Path(args.outfile).resolve()
    fig.write_html(out, include_plotlyjs="inline")

    # 6) Report ---------------------------------------------------------------
    print("Optimised weights:")
    for tk, w in weights_dict.items():
        print(f"  {tk:<6} : {w:.4f}")
    print(f"{args.metric.capitalize()} score: {score:.4f}")
    print(f"Figure saved to {out}")

    # auto‑open
    try:
        webbrowser.open(out.as_uri())
    except Exception as exc:  # pragma: no cover – safety
        logging.warning("Cannot open browser: %s", exc)


if __name__ == "__main__":
    main()
