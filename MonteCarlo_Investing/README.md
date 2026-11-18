Monte Carlo Simulation Projects
This project started as a small Python exercise to learn how Monte Carlo simulation works. I originally wanted to estimate the possible outcomes of an investment portfolio, but the larger goal is to build a reusable framework for analyzing systems with uncertain inputs.

The investment model is currently on hold. It was a useful introduction to Monte Carlo methods, historical resampling, validation, and uncertainty analysis. I plan to reuse those ideas later in more engineering-focused projects, especially my UAV simulator.
Current investment project
The investment model estimates a range of possible portfolio balances instead of producing one deterministic answer. Each simulation uses a different sequence of historical market returns and projects the portfolio forward while accounting for contributions, fees, inflation, and a simplified tax model.

The model compares weekly and monthly contribution schedules.
Basic workflow
1. Load historical S&P 500 price data from a FRED CSV file.
2. Resample the data into weekly and monthly prices.
3. Calculate historical returns.
4. Generate contribution schedules from salary, salary growth, and savings rate.
5. Generate simulated return paths using block bootstrap sampling.
6. Project the portfolio balance for each path.
7. Calculate statistics such as percentiles and target probability.
8. Compare the results with a no-investment cash baseline.
9. Validate the model using rolling train/test windows.
Monte Carlo model
The portfolio balance is updated once per simulation period using:
B_(t+1) = B_t (1 + r_t) (1 - f) + C_t
where:
- B_t is the current balance;
- r_t is the sampled market return;
- f is the investment fee for that period; and
- C_t is the contribution made at the end of the period.
One trial represents one possible sequence of market returns and one resulting portfolio history. Running many trials produces a distribution of possible outcomes.
Historical returns and block bootstrap
The current model uses the FRED S&P 500 price index, so dividends are not included. The returns therefore represent price changes rather than total investment returns.

Instead of choosing every return independently, the model samples consecutive blocks of historical returns. This helps preserve short-term behavior such as consecutive market declines, periods of high volatility, clusters of positive returns, and short-term recovery patterns.

The blocks are sampled with replacement and joined together until they are long enough for the simulation horizon.
Inputs
- Starting portfolio balance
- Salary
- Salary growth rate
- Savings rate
- Investment horizon
- Number of simulations
- Historical weekly and monthly returns
- Bootstrap block size
- Investment expense ratio
- Inflation rate
- Simplified capital-gains tax rate
- Target balance
Outputs
- Minimum, maximum, mean, and median final balance
- 10th and 90th percentile balances
- Probability of reaching a target balance
- Comparison with a no-investment baseline
- Weekly versus monthly contribution comparison
- Histograms of final balances
- Prediction cones showing simulated ranges over time
Rolling validation
The model also includes rolling validation. The purpose is not to prove that the model can predict the future. Instead, it tests whether the simulated distributions behave reasonably when compared with later historical data that was not used to generate them.

The current setup uses five years of training data, one year of testing data, and a one-year step between folds.

Each fold follows this process:
Training returns → bootstrap simulations → prediction cone
Testing returns  → actual historical path
The simulated cone uses the 10th and 90th percentiles at every time step. This creates a pointwise interval containing 80% of the simulated outcomes. Coverage is calculated after excluding the initial balance, since the initial value is fixed for every trial.

The validation results provide some evidence about how the model behaves across historical market periods, but they do not guarantee future accuracy. The current dataset only supports a small number of validation folds, and the model still has several simplifying assumptions.
Assumptions and limitations
- The S&P 500 dataset is price-only and excludes dividends.
- Historical behavior may not represent future market behavior.
- The available historical window is relatively short.
- Returns are sampled from historical data with replacement.
- Inflation and salary growth are fixed rather than randomized.
- Contributions occur at the end of each period.
- Fees use a simplified accounting convention.
- Taxes are applied as a simplified final liquidation tax.
- The tax model does not track individual tax lots or holding periods.
- Weekly and monthly models use separate historical return paths.
- The model is for learning and analysis, not financial advice.
Verification and validation
Verification asks whether the code does what I intended. Examples include testing zero-return and zero-fee cases, checking a one-period calculation by hand, confirming matching contribution and return lengths, reproducing results with a fixed seed, and checking that simulated and actual paths have compatible dimensions.

Validation asks whether the model behaves reasonably compared with data outside the training set. Examples include rolling out-of-sample coverage, comparing simulated and actual final balances, checking return and volatility behavior, comparing drawdowns, and testing sensitivity to block size and training-window length.
Why Monte Carlo is useful here
The important result is not one predicted balance. It is the distribution of possible outcomes. This makes it possible to ask questions such as:
How likely is it that the portfolio reaches the target?
How wide is the range of possible outcomes?
How sensitive are the results to contribution timing?
How often does the actual result fall inside the simulated range?
Future engineering applications
The same approach should be useful for my UAV and 6DOF simulation work. The deterministic simulator can remain unchanged while Monte Carlo varies uncertain inputs across repeated trials.

Potential inputs to randomize include vehicle mass, center of gravity, moments of inertia, aerodynamic coefficients, actuator time constants, actuator saturation limits, sensor noise and bias, initial conditions, and wind or gust conditions.

Useful outputs could include RMS trajectory-tracking error, maximum position or attitude error, settling time, control effort, actuator saturation frequency, probability of losing stability, and probability of violating a mission requirement.

A typical UAV Monte Carlo study would look like this:
Sample uncertain vehicle and environment parameters
        ↓
Initialize the simulator
        ↓
Run the same controller and mission
        ↓
Record performance metrics
        ↓
Classify the trial as successful or unsuccessful
        ↓
Repeat many times
        ↓
Estimate performance and failure probabilities
Example results could be reported as:
Probability of staying within a 2 m trajectory tolerance: 94%
95th-percentile position error: 3.1 m
Probability of actuator saturation: 18%
Probability of loss of stability: 1.2%
General project structure
For future applications, it would be useful to keep the deterministic model separate from the Monte Carlo framework:
- model: deterministic physics or system simulation;
- uncertainty: distributions and parameter sampling;
- runner: repeated simulation trials;
- metrics: performance and failure calculations;
- validation: comparison against held-out or experimental data; and
- visualization: plots and summary statistics.
That structure would let the same Monte Carlo tools work with the investment model, UAV simulator, actuator models, guidance laws, or other engineering systems.
