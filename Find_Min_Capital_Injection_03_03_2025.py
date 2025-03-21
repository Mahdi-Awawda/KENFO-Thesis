import matplotlib
matplotlib.use("Agg")  # Force a non-interactive backend

import Data_03_03_2025_de_facto
import matplotlib.pyplot as plt
import os
import glob

# Ensure the "plots_ROI" folder exists
plot_dir = "../src/plots_ROI"
os.makedirs(plot_dir, exist_ok=True)

def get_next_filename(base_name, extension, directory):
    """Finds the next available filename by counting existing numbered versions."""
    existing_files = glob.glob(os.path.join(directory, f"{base_name}_*.{extension}"))

    # Extract numbers from existing filenames
    existing_numbers = [
        int(f.split("_")[-1].split(".")[0]) for f in existing_files if f.split("_")[-1].split(".")[0].isdigit()
    ]

    next_number = max(existing_numbers, default=0) + 1  # Increment from the highest found
    return os.path.join(directory, f"{base_name}_{next_number}.{extension}")

def calculate_initial_balance(cost_projections, assumed_target_roi):
    lower_bound = 0
    upper_bound = 10 * sum(cost_projections)  # Reasonable upper bound
    tolerance = 0.00001  # Adjust tolerance as needed
    total_years = len(cost_projections)

    first_quarter = total_years // 4
    second_quarter = total_years // 2
    third_quarter = int(total_years * 0.75)

    while upper_bound - lower_bound > tolerance:
        initial_balance = (upper_bound + lower_bound) / 2
        balance = initial_balance
        cash_flow_percent = 0.08  # Starts at 8%

        for year in range(total_years):
            cost = cost_projections[year]

            # Apply the cash flow constraint for the first 8 years
            if year < 5:
                balance = balance * (1 + assumed_target_roi / 100) * (1 - cash_flow_percent) - cost
                cash_flow_percent -= 0.08 / 8  # Linearly decreasing
            else:
                balance = balance * (1 + assumed_target_roi / 100) - cost

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
            lower_bound = initial_balance
        else:
            upper_bound = initial_balance

    return (upper_bound + lower_bound) / 2

# Iterate through years dynamically from 2093 to 2120
years = list(range(2093, 2121))  # Generates a list [2093, 2094, ..., 2120]

target_roi = Data_03_03_2025_de_facto.targetROI
current_fund_value_2023 = Data_03_03_2025_de_facto.currentFundValue2023

year_labels = []
needed_top_ups = []

for year in years:
    scenario_name = f"Conclusion_in_{year}"  # Correctly match Data_03_03_2025_py attributes
    costs = getattr(Data_03_03_2025_de_facto, scenario_name, None)  # Retrieve costs dynamically

    if costs is None:
        print(f"No data available for {year}, skipping...\n")
        continue  # Skip years with no available cost data

    initial_balance = calculate_initial_balance(costs, target_roi)
    needed_top_up = initial_balance - current_fund_value_2023

    # Convert large numbers to billions
    needed_top_up_billion = needed_top_up / 1e9

    year_labels.append(year)
    needed_top_ups.append(needed_top_up_billion)

    # Print required capital injection for each year
    print(f"Year {year}: Required Capital Injection = {needed_top_up_billion:.2f} Billion €")

# Generate a unique filename for the plot
plot_path = get_next_filename("capital_injection", "png", plot_dir)

# Create the plot
plt.figure(figsize=(12, 6))
plt.plot(year_labels, needed_top_ups, marker='o', linestyle='-', color='b', label='Required Capital Injection')
plt.xlabel("Year", fontsize=14)
plt.ylabel("Required Capital Injection (Billion €)", fontsize=14)
plt.xticks(year_labels, roation=45)
plt.ylim(17.00, 30.50)  # Set y-axis range from 17.00 to 30.50
plt.yticks([round(i, 2) for i in [17.00 + x * 1.00 for x in range(14)]], fontsize=10)  # Show values with two decimal places but less cluttered
plt.grid(True)
plt.legend()
plt.savefig(plot_path)  # Save plot
plt.close()

print(f"Saved capital injection plot: {plot_path}")


