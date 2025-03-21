import Data_14_03_2025_de_jure
import matplotlib
import os
import glob
import matplotlib.pyplot as plt

# Force a non-interactive backend for Matplotlib
matplotlib.use("Agg")

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

            # Apply cash flow constraint for the first 8 years
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


initial_balance_2023 = 21411768000.0  # 21.4 billion €
initial_balance_2024 = 21410889500.0  # TO BE CHECKED!!!

# Use the initial fund value from the data file
initial_balance = Data_14_03_2025_de_jure.currentFundValue2023

# Calculate the required yearly ROI for each inflation rate
roi_160 = calculate_roi(Data_14_03_2025_de_jure.Conclusion_in_2080_IR_160, initial_balance)
roi_172 = calculate_roi(Data_14_03_2025_de_jure.Conclusion_in_2080_IR_172, initial_balance)
roi_202 = calculate_roi(Data_14_03_2025_de_jure.Conclusion_in_2080_IR_202, initial_balance)
roi_370 = calculate_roi(Data_14_03_2025_de_jure.Conclusion_in_2080_IR_370, initial_balance)

# Print the results with the specified formatting
print(f"Required yearly ROI for inflation rate 1.60%: + {roi_160}")
print(f"Required yearly ROI for inflation rate 1.72%: + {roi_172}")
print(f"Required yearly ROI for inflation rate 2.02%: + {roi_202}")
print(f"Required yearly ROI for inflation rate 3.70%: + {roi_370}")
