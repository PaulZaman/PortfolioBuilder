import pandas as pd
import numpy as np

def filter_for_dates(performances, start_date, end_date):
	"""Filter the portfolio data for the given date range.

	Args:
		performances (df): DataFrame containing portfolio performance data. ("ptf" and "date)
		start_date (str): Start date for filtering.
		end_date (str): End date for filtering.

	Returns:
		df: Filtered DataFrame.
	"""
	return performances[performances['date'].between(start_date, end_date)].reset_index(drop=True)

def adjust_time_frame(performances, time_frame):
	"""Adjust the portfolio data to the specified time frame using compounded returns
	and format the date accordingly.

	Args:
		performances (df): DataFrame with 'date' and 'ptf' (as return) columns.
		time_frame (str): One of "daily", "weekly", "monthly", "quarterly", "yearly".

	Returns:
		df: DataFrame with aggregated compounded returns and formatted date labels.
	"""
	if time_frame == "daily":
		return performances

	# Define the resample rule and formatting function
	rule_format = {
		"weekly": ("W", lambda d: d.strftime("%Y-%m-%d")),
		"monthly": ("M", lambda d: d.strftime("%Y-%m")),
		"quarterly": ("QE", lambda d: f"Q{((d.month - 1) // 3) + 1}-{d.year}"),
		"yearly": ("Y", lambda d: str(d.year)),
	}

	if time_frame not in rule_format:
		return performances

	rule, format_fn = rule_format[time_frame]

	# Resample and compute compounded return
	agg_df = performances.set_index("date").resample(rule)["ptf"].apply(lambda x: (1 + x).prod() - 1).reset_index()

	# Format the date column accordingly
	agg_df["date"] = agg_df["date"].apply(format_fn)

	return agg_df

def get_max_drawdown(returns):
	"""Calculate the maximum drawdown of a portfolio.

	Args:
		returns (pd.Series): Daily returns of the portfolio.

	Returns:
		float: Maximum drawdown as a percentage.
	"""
	cumulative_returns = (1 + returns).cumprod()
	drawdowns = cumulative_returns / cumulative_returns.cummax() - 1
	max_drawdown = drawdowns.min()
	return max_drawdown

def adjust_portfolio(portfolio, start_date=None, end_date=None, time_frame=None):
	"""Adjust portfolio based on the given time frame.

	Args:
		portfolio (dict): Portfolio data.
		start_date (str): Start date for the portfolio.
		end_date (str): End date for the portfolio.
		time_frame (str): Time frame for aggregation. One of "daily", "weekly", "quarterly", "monthly".

	Returns:
		portfolio (dict): Adjusted portfolio data.
	"""
	# If no start date is provided, use the first date in the portfolio
	if start_date is None:
		start_date = pd.to_datetime(portfolio['dates'][0]).strftime("%Y-%m-%d")
	# If no end date is provided, use today's date
	if end_date is None:
		end_date = pd.to_datetime("today").strftime("%Y-%m-%d")
	# If no time frame is provided, use daily
	if time_frame is None:
		time_frame = "daily"

	# Create a dataframe for the portfolio
	performances = pd.DataFrame(columns=["date", "ptf"])
	performances["date"] = pd.to_datetime(portfolio['dates'])
	performances['ptf'] = portfolio['performance']

	# Calculate the mean daily return before adjusting the portfolio
	daily_performance = performances['ptf'].copy()
	mean_daily_return = daily_performance.mean()
	max_dd = get_max_drawdown(daily_performance)

	# Filter for dates
	performances = filter_for_dates(performances, start_date, end_date)

	# Adjust time frame
	performances = adjust_time_frame(performances, time_frame)

	# Calculate cumulative returns
	performances["ptf_cum"] = (1 + performances["ptf"]).cumprod() - 1


		# === RISK & RETURN METRICS ===
	mean_daily_return = daily_performance.mean()
	std_daily_return = daily_performance.std()
	volatility = std_daily_return * np.sqrt(252)  # Annualized
	sharpe_ratio = (mean_daily_return / std_daily_return) * np.sqrt(252)
	sortino_ratio = (mean_daily_return / daily_performance[daily_performance < 0].std()) * np.sqrt(252)

	# === RETURN CONSISTENCY ===
	hit_ratio = (daily_performance > 0).mean()
	best_return = daily_performance.max()
	worst_return = daily_performance.min()

	# === DRAWDOWN METRICS ===
	max_dd = get_max_drawdown(daily_performance)
	calmar_ratio = ((1 + mean_daily_return) ** 252 - 1) / abs(max_dd)

	# === FINAL METRICS DICT ===
	metrics = {
		# Basic performance metrics
		"total_cum_return": performances["ptf_cum"].iloc[-1],
		"mean_yearly_return": (mean_daily_return + 1) ** 252 - 1,
		"mean_daily_return": mean_daily_return,

		# Risk and return ratios
		"volatility": volatility,		# Annualized volatility
		"sharpe_ratio": sharpe_ratio,	# Annualized Sharpe ratio
		"sortino_ratio": sortino_ratio, # Annualized Sortino ratio
		"calmar_ratio": calmar_ratio,	# Annualized Calmar ratio

		# Drawdown
		"max_drawdown": max_dd,


		# Performance consistency
		"hit_ratio": hit_ratio,
		"best_daily_return": best_return,
		"worst_daily_return": worst_return,
	}
	
	# Add the metrics to the portfolio dictionary
	portfolio["metrics"] = metrics
	portfolio["performance"] = performances["ptf"].tolist()
	portfolio["dates"] = performances["date"].tolist()
	portfolio['performance_cum'] = performances["ptf_cum"]

	return portfolio
