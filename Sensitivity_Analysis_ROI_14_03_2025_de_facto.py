import Data_14_03_2025_de_facto
import os
import glob
import matplotlib
import matplotlib.pyplot as plt

# Force a non-interactive backend for Matplotlib
matplotlib.use("Agg")

# Ensure the "plots_ROI" folder exists (for existing plots)
plot_dir = "../src/plots_ROI"
os.makedirs(plot_dir, exist_ok=True)

def get_next_filename(base_name, extension, directory):
    """Finds the next available filename by counting existing numbered versions."""
    existing_files = glob.glob(os.path.join(directory, f"{base_name}_*.{extension}"))
    existing_numbers = [
        int(f.split("_")[-1].split(".")[0])
        for f in existing_files if f.split("_")[-1].split(".")[0].isdigit()
    ]
    next_number = max(existing_numbers, default=0) + 1
    return os.path.join(directory, f"{base_name}_{next_number}.{extension}")

def calculate_roi(costs, initial_balance):
    lower_bound = 0
    upper_bound = 100
    tolerance = 0.0000001
    total_years = len(costs)

    first_quarter = total_years // 4
    second_quarter = total_years // 2
    third_quarter = int(total_years * 0.75)

    while upper_bound - lower_bound > tolerance:
        assumed_roi = (upper_bound + lower_bound) / 2
        balance = initial_balance

        cash_flow_percent = 0.08  # Starts at 8%

        for year in range(total_years):
            cost = costs[year]
            # Apply cash flow constraint for the first 5 years
            if year < 5:
                balance = balance * (1 + assumed_roi / 100) * (1 - cash_flow_percent) - cost
                cash_flow_percent -= 0.08 / 8  # Linearly decreasing
            else:
                balance = balance * (1 + assumed_roi / 100) - cost

            # Determine liquid assets based on the time frame
            if year < first_quarter:
                liquid_assets = balance * 0.70
            elif year < second_quarter:
                liquid_assets = balance * 0.60
            elif year < third_quarter:
                liquid_assets = balance * 0.50
            else:
                liquid_assets = balance * 0.40

            if liquid_assets < cost or balance < 0:
                balance = -1
                break

        if balance < 0:
            lower_bound = assumed_roi
        else:
            upper_bound = assumed_roi

    return (upper_bound + lower_bound) / 2

# Use the initial fund value from the data file
initial_balance = Data_14_03_2025_de_facto.currentFundValue2023

# Define the inflation rate scenarios.
# For the baseline 1.60%, we use the original arrays.
# For the other scenarios, we use the arrays with suffixes (e.g., _1.72, _2.02, _3.70)
inflation_scenarios = ["1.60", "1.72", "2.02", "3.70"]

# Create a dictionary to store the results:
# results[year][inflation_scenario] = calculated ROI
results = {}

# Loop over years from 2093 to 2120
for year in range(2093, 2121):
    results[year] = {}
    for scenario in inflation_scenarios:
        if scenario == "1.60":
            # Baseline arrays are named without a suffix.
            array_name = f"Conclusion_in_{year}"
        else:
            # Other scenarios have the suffix.
            array_name = f"Conclusion_in_{year}_{scenario}"
        # Get the cost array from the module using getattr
        costs = getattr(Data_14_03_2025_de_facto, array_name)
        roi = calculate_roi(costs, initial_balance)
        results[year][scenario] = roi

# Print the results
for year in range(2093, 2121):
    print(f"Year {year}:")
    for scenario in inflation_scenarios:
        print(f"  Inflation rate {scenario}%: required ROI = {results[year][scenario]}")

# --------------------------
# Create a sensitivity analysis plot
# --------------------------
sensitivity_dir = "../src/sensitivity_analysis"
os.makedirs(sensitivity_dir, exist_ok=True)

years_list = list(range(2093, 2121))

plt.figure(figsize=(12, 6))
for scenario in inflation_scenarios:
    roi_list = [results[year][scenario] for year in years_list]
    plt.plot(years_list, roi_list, marker='o', linestyle='-', label=f"Inflation rate {scenario}%")

plt.xlabel("Year", fontsize=14)
plt.ylabel("Required ROI (%)", fontsize=14)
plt.xticks(years_list, rotation=45)
plt.grid(True)

# Adjust y-axis ticks: show ticks every 0.25 with two decimals
import numpy as np
y_min, y_max = plt.ylim()
yticks = np.arange(np.floor(y_min), np.ceil(y_max) + 0.5, 0.5)
plt.yticks(yticks, [f"{y:.2f}" for y in yticks])

# Adjust legend position: move it further left and a bit lower
plt.legend(loc='upper left', bbox_to_anchor=(0.79, 0.72), borderaxespad=0.)

# Generate a unique filename for the sensitivity plot
sensitivity_plot_path = get_next_filename("sensitivity_analysis_de_facto_no_CISF", "png", sensitivity_dir)
plt.savefig(sensitivity_plot_path, bbox_inches='tight')
plt.close()

print(f"Saved sensitivity analysis plot: {sensitivity_plot_path}")

