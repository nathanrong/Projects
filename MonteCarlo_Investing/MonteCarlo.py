# Monte Carlo Simulation for Investment Portfolio Outcomes
#
# Objective:
# Estimate the distribution and probability of reaching an investment
# goal under uncertainty in historical market returns.
#
# Approach:
# - Use historical S&P 500 price returns from weekly or monthly data.
# - Generate simulated return paths using block bootstrap sampling.
# - Project portfolio balances using a salary-based contribution schedule.
# - Compare weekly and monthly contribution strategies.
#
# Key Inputs:
# - Starting portfolio balance
# - Salary, salary growth, and savings rate
# - Investment horizon and number of simulations
# - Historical return data and bootstrap block size
# - Investment expense ratio
# - Inflation rate
# - Simplified capital-gains tax rate
# - Target balance in today's dollars
#
# Key Outputs:
# - Distribution of final after-tax, inflation-adjusted balances
# - Mean, median, minimum, and maximum balances
# - 10th and 90th percentile outcomes
# - Probability of reaching the target
# - Comparison with a no-investment cash baseline
# - Comparison of weekly and monthly contributions
#
# Assumptions and Limitations:
# - The S&P 500 data is a price index and excludes dividends.
# - Returns are sampled from historical data and may not represent the future.
# - Inflation, salary growth, fees, and tax rates are currently fixed.
# - Contributions occur at the end of each simulation period.
# - Taxes are simplified and applied to gains at final liquidation.
# - Weekly and monthly models use separate historical return paths.

import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def load_historical_data(file_path):
    df = pd.read_csv(file_path)

    df["observation_date"] = pd.to_datetime(df["observation_date"])
    df["SP500"] = pd.to_numeric(df["SP500"], errors="coerce")
    df = df.dropna(subset="SP500").set_index("observation_date").sort_index()

    weekly_prices = df["SP500"].resample("W-FRI").last().dropna()
    weekly_returns = weekly_prices.pct_change().dropna()

    monthly_prices = df["SP500"].resample("ME").last().dropna()
    monthly_returns = monthly_prices.pct_change().dropna()

    if monthly_returns.empty or weekly_returns.empty:
        raise ValueError("No valid historical data was returned...")
    if not np.all(np.isfinite(monthly_returns)) or not np.all(np.isfinite(weekly_returns)):
        raise ValueError("Historical data returns non-finite values...")
    if np.any(monthly_returns <= -1) or np.any(weekly_returns <= -1):
        raise ValueError("Historical data consists of a drop of more than 100%...")
    return weekly_returns, monthly_returns

def block_bootstrap(data, block_size, num_periods, rng):
    # Validation
    if not 1 <= block_size <= len(data):
        raise ValueError("Block size must be between 1 and the data length...")

    num_blocks = len(data) - block_size + 1 # number of blocks of size block_size
    blocks_needed = int(np.ceil(num_periods / block_size))
    selected_indices = rng.integers(0, num_blocks, size=blocks_needed)
    blocks = [data[idx:idx+block_size] for idx in selected_indices]
    return np.concatenate(blocks)[:num_periods]

def project_balance(balance, contributions, returns, fee) -> tuple[float, np.ndarray]:
    # Validation
    if len(contributions) != len(returns):
        raise ValueError("Contribtuions and Returns must be equal lengths...")

    history = np.empty(len(returns)+1, dtype=float)
    history[0] = balance
    for period, (contribution, period_return) in enumerate(zip(contributions, returns), start=1):
        # End of period contribution, so contribution not included in stock expense ratio
        balance = balance * (1 + period_return) * (1 - fee) + contribution
        history[period] = balance
    return balance, history

def run_sim(balance, contributions, num_sims, train_returns, 
            fee, block_size, seed=None) -> np.ndarray:
    # Validation
    if balance < 0:
        raise ValueError("Balance must be zero or greater...")
    if num_sims <= 0:
        raise ValueError("Number of simulations must be greater than zero...")
    if not np.isfinite(fee) or not 0 <= fee < 1:
        raise ValueError("Expense ratio must be between 0 and 1...")

    train_returns = np.asarray(train_returns, dtype=float)
    num_periods = len(contributions)
    sim_paths = np.empty((num_sims, num_periods+1), dtype=float)
    rng = np.random.default_rng(seed)
    for sim in range(num_sims):
        returns = block_bootstrap(train_returns, block_size, num_periods, rng)

        _, history = project_balance(balance, contributions, returns, fee)
        sim_paths[sim, :] = history
    return sim_paths

def stats(final_bal, period, target_bal):
    # Statistics using NumPy
    min_val = np.min(final_bal)
    max_val = np.max(final_bal)
    mean_val = np.mean(final_bal)
    median_val = np.median(final_bal)
    p10, p90 = np.percentile(final_bal, [10, 90])
    target_mask = final_bal >= target_bal
    target_probability = np.mean(target_mask)

    # Print outputs
    title = f"{period} BALANCE STATISTICS"
    print(f"{title:^35}")
    print("=" * 35)
    print(f"Minimum Balance:    ${min_val:,.2f}")
    print(f"Maximum Balance:    ${max_val:,.2f}")
    print(f"Mean Balance:       ${mean_val:,.2f}")
    print(f"Median Balance:     ${median_val:,.2f}")
    print(f"10th Percentile:    ${p10:,.2f}")
    print(f"90th Percentile:    ${p90:,.2f}")
    print(f"Target Balance:     ${target_bal:,.2f}")
    print(f"Prob. of Reaching:  {target_probability * 100:.1f}%")

def comparison_plot(week_final_bal, month_final_bal, target_bal, principal):
    # Use the same bin boundaries for both distributions
    combined = np.concatenate((week_final_bal, month_final_bal))
    bins = np.histogram_bin_edges(combined, bins=50)

    week_mean = np.mean(week_final_bal)
    month_mean = np.mean(month_final_bal)

    plt.figure(figsize=(14, 7))

    plt.hist(week_final_bal, bins=bins, alpha=0.55, label="Weekly Contributions")
    plt.hist(month_final_bal, bins=bins, alpha=0.55, label="Monthly Contributions")

    plt.axvline(target_bal, color="crimson", linestyle="--",
        linewidth=3, label=f"Target (${target_bal:,.0f})")
    plt.axvline(week_mean, color="darkgreen", linestyle="-",
        linewidth=2, label=f"Weekly Mean (${week_mean:,.0f})")
    plt.axvline(month_mean, color="darkblue", linestyle="-",
        linewidth=2, label=f"Monthly Mean (${month_mean:,.0f})")
    plt.axvline(principal, color="black", linestyle="--",
        linewidth=3, label=f"No Investment (${principal:,.0f})")

    plt.title("After-Tax, Inflation-Adjusted Outcomes\nHistorical S&P 500 Bootstrap", fontsize=18, fontweight="bold")
    plt.xlabel("Final Balance ($)", fontsize=14)
    plt.ylabel("Frequency (Count)", fontsize=14)
    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))
    plt.legend(fontsize=12)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show(block=False)

def prediction_cone_plot(cases):
    fig, axes = plt.subplots(1, len(cases), figsize=(15, 6), squeeze=False)
    axes = axes[0]

    for ax, case in zip(axes, cases):
        paths, actuals = case["paths"], case["actuals"]
        label, color = case["label"], case["color"]
        p10, median, p90 = np.percentile(paths, [10, 50, 90], axis=0)
        sim_time = np.arange(paths.shape[1])

        ax.fill_between(sim_time, p10, p90, color=color, alpha=0.25, label="10th–90th percentile")
        ax.plot(sim_time, median, color=color, linewidth=2, label="Simulated median")

        all_inside = []

        for fold, actual in enumerate(actuals):
            actual = np.asarray(actual)
            inside = (actual[1:] >= p10[1:]) & (actual[1:] <= p90[1:])
            all_inside.extend(inside)

            actual_time = np.arange(len(actual))
            ax.plot(actual_time, actual, color="black", alpha=0.5, linewidth=1.5,
                    label="Actual test paths" if fold == 0 else None)

        coverage = np.mean(all_inside) * 100
        ax.set_title(f"{label}\nAverage coverage: {coverage:.1f}%", fontsize=16, fontweight="bold")
        ax.set_xlabel("Periods", fontsize=14)
        ax.set_ylabel("Balance ($)", fontsize=14)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=12)

    fig.suptitle("Aggregate Monte Carlo Prediction Cones vs. Actual Test Paths", fontsize=18, fontweight="bold")
    fig.tight_layout()
    plt.show(block=False)

def apply_inflation(current, inflation_rate, num_years):
    return np.asarray(current, dtype=float) / np.power(1 + inflation_rate, num_years)

def apply_taxes(final_bal, starting_bal, contributions, capital_gains_rate):
    final_bal = np.asarray(final_bal, dtype=float)
    contributions = np.asarray(contributions, dtype=float)

    cost_basis = starting_bal + np.sum(contributions)
    gains = np.maximum(final_bal - cost_basis, 0)
    taxes = gains * capital_gains_rate
    after_tax = final_bal - taxes
    return after_tax

def generate_contributions(salary, salary_growth, savings_rate, num_years, periods_per_year):
    # Validation
    if salary <= 0:
        raise ValueError("Salary must be greater than zero...")
    if not 0 <= salary_growth < 1:
        raise ValueError("Salary growth must be between zero and one...")
    if not 0 <= savings_rate < 1:
        raise ValueError("Savings rate must be between zero and one...")
    if not isinstance(periods_per_year, int) or not 1 <= periods_per_year <= 365:
        raise ValueError("Periods per year must be between one and 365... ")
    
    num_periods = num_years * periods_per_year
    contributions = np.empty(num_periods, dtype=float)

    for year in range(num_years):
        current_salary = salary * (1 + salary_growth) ** year
        contribution_per_period = current_salary * savings_rate / periods_per_year

        start = year * periods_per_year
        end = start + periods_per_year

        contributions[start:end] = contribution_per_period
    return contributions

def calc_principal(balance, contributions):
    contributions = np.asarray(contributions, dtype=float)
    history = np.empty(len(contributions) + 1, dtype=float)
    history[0] = balance
    history[1:] = balance + np.cumsum(contributions)
    return history[-1], history

def rolling_window(period_returns, train_periods, test_periods, step):
    splits = []

    for test_start in range(train_periods, len(period_returns) - test_periods + 1, step):
        train_start = test_start - train_periods
        test_end = test_start + test_periods

        train = period_returns.iloc[train_start:test_start]
        test = period_returns.iloc[test_start:test_end]

        splits.append((train, test))
    return splits

def main():
    # Constants
    balance = 10_000
    target_bal = 80_000
    salary = 100_000
    salary_growth = 0.03
    savings_rate = 0.10
    num_years = 5
    num_sims = 10_000
    annual_expense_ratio = 0.005
    monthly_expense_ratio = 1 - math.pow(1-annual_expense_ratio, 1/12)
    weekly_expense_ratio = 1 - math.pow(1 - annual_expense_ratio, 1 / 52)
    inflation_rate = 0.03
    capital_gains_rate = 0.15

    weekly_contribution = generate_contributions(salary, salary_growth, savings_rate, num_years, 52)
    monthly_contribution = generate_contributions(salary, salary_growth, savings_rate, num_years, 12)

    # Pull historical data - FRED dataset from St. Louis Federal Reserve
    weekly_returns, monthly_returns = load_historical_data("SP500.csv")

    # Five-year forward projection
    weekly_projection_paths = run_sim(balance, weekly_contribution, num_sims, 
                                      weekly_returns.to_numpy(), weekly_expense_ratio, block_size=26, seed=42)

    monthly_projection_paths = run_sim(balance, monthly_contribution, num_sims, monthly_returns.to_numpy(), 
                                       monthly_expense_ratio, block_size=6, seed=42)

    weekly_projection_final = weekly_projection_paths[:, -1]
    monthly_projection_final = monthly_projection_paths[:, -1]

    # Apply taxes using full five-year contribution schedules
    weekly_after_tax = apply_taxes(weekly_projection_final, balance, weekly_contribution, capital_gains_rate)

    monthly_after_tax = apply_taxes(monthly_projection_final, balance, monthly_contribution, capital_gains_rate)

    # Convert five-year outcomes to today's dollars
    real_week = apply_inflation(weekly_after_tax, inflation_rate, num_years)
    real_month = apply_inflation(monthly_after_tax, inflation_rate, num_years)

    principal, _ = calc_principal(balance, monthly_contribution)
    real_principal = apply_inflation(principal, inflation_rate, num_years)

    stats(real_week, "WEEKLY FIVE-YEAR PROJECTION", target_bal)
    stats(real_month, "MONTHLY FIVE-YEAR PROJECTION", target_bal)

    comparison_plot(real_week, real_month, target_bal, real_principal)


    # Split data into train and test
    weekly_folds = rolling_window(weekly_returns, train_periods=5*52, test_periods=52, step=52)
    monthly_folds = rolling_window(monthly_returns, train_periods=60, test_periods=12, step=12)

    # Store results from every fold
    all_weekly_paths = []
    all_weekly_actual = []
    weekly_coverages = []

    all_monthly_paths = []
    all_monthly_actual = []
    monthly_coverages = []

    # Weekly rolling validation
    for fold, (train, test) in enumerate(weekly_folds):
        test_contributions = weekly_contribution[:len(test)]

        simulated_paths = run_sim(balance, test_contributions, num_sims, train.to_numpy(), 
                                  weekly_expense_ratio, block_size=26, seed=42 + fold)

        _, actual_history = project_balance(balance, test_contributions, test.to_numpy(), weekly_expense_ratio)

        p10, p90 = np.percentile(simulated_paths, [10, 90], axis=0)

        coverage = np.mean((actual_history[1:] >= p10[1:]) & (actual_history[1:] <= p90[1:]))

        all_weekly_paths.append(simulated_paths)
        all_weekly_actual.append(actual_history)
        weekly_coverages.append(coverage)

    # Monthly rolling validation
    for fold, (train, test) in enumerate(monthly_folds):
        test_contributions = monthly_contribution[:len(test)]

        simulated_paths = run_sim(balance, test_contributions, num_sims, train.to_numpy(), 
                                  monthly_expense_ratio, block_size=6, seed=42 + fold)

        _, actual_history = project_balance(balance, test_contributions, test.to_numpy(), monthly_expense_ratio)

        p10, p90 = np.percentile(simulated_paths, [10, 90], axis=0)

        coverage = np.mean((actual_history[1:] >= p10[1:]) & (actual_history[1:] <= p90[1:]))

        all_monthly_paths.append(simulated_paths)
        all_monthly_actual.append(actual_history)
        monthly_coverages.append(coverage)

    # Combine all simulated paths across folds
    combined_weekly_paths = np.vstack(all_weekly_paths)
    combined_monthly_paths = np.vstack(all_monthly_paths)

    # Final balances from combined one-year validation simulations
    weekly_final_bal = combined_weekly_paths[:,-1]
    monthly_final_bal = combined_monthly_paths[:,-1]

    # Use one-year contribution schedules for tax basis
    weekly_test_contribution = weekly_contribution[:52]
    monthly_test_contribution = monthly_contribution[:12]

    # Apply simplified taxes
    weekly_after_tax = apply_taxes(weekly_final_bal, balance, weekly_test_contribution, capital_gains_rate)
    monthly_after_tax = apply_taxes(monthly_final_bal, balance, monthly_test_contribution, capital_gains_rate)

    # Convert one-year outcomes to today's dollars
    real_week = apply_inflation(weekly_after_tax, inflation_rate, 1)
    real_month = apply_inflation(monthly_after_tax, inflation_rate, 1)

    # No-investment baseline
    principal, _ = calc_principal(balance, monthly_test_contribution)
    real_principal = apply_inflation(principal, inflation_rate, 1)


    prediction_cone_plot([
        {
            "paths": combined_weekly_paths,
            "actuals": all_weekly_actual,
            "label": "Weekly Model",
            "color": "green"
        },
        {
            "paths": combined_monthly_paths,
            "actuals": all_monthly_actual,
            "label": "Monthly Model",
            "color": "blue"
        }
    ])
    input("Press Enter to close...")

if __name__ == "__main__":
    main()