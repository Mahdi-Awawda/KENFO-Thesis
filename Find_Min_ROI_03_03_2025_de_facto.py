import Data_03_03_2025_de_facto
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
    tolerance = 1e-15
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

# Monte Carlo Frequency Data (from the table provided)
years = list(range(2093, 2121))
frequency_percent = [
    0.17, 1.35, 4.54, 9.51, 12.85, 11.43, 6.69, 2.61, 0.76, 0.27, 0.56, 1.60,
    2.99, 4.30, 4.56, 4.91, 4.92, 5.10, 4.76, 4.84, 4.35, 3.46, 2.20, 1.01, 0.24,
    0.04, 0.02, 0.01
]

roi_values = []

# Calculate required ROIs and store them
for year in years:
    data = getattr(Data_03_03_2025_de_facto, f"Conclusion_in_{year}", [])
    required_ROI = calculate_roi(data, initial_balance_2024)
    roi_values.append(required_ROI)
    print(f"Required yearly ROI for {year}: {required_ROI:.6f}%")

# Generate unique filenames
line_plot_path = get_next_filename("plots_ROI_line", "png", plot_dir)
histogram_path = get_next_filename("plots_ROI_histogram", "png", plot_dir)

# Create line plot
plt.figure(figsize=(12, 6))
plt.plot(years, roi_values, marker='o', linestyle='-', color='b', label='Required ROI')
plt.xlabel("Year", fontsize=14)
plt.ylabel("Required ROI (%)", fontsize=14)
plt.xticks(years, rotation=45)
plt.ylim(5.90, 6.40)  # Set y-axis range from 5.90 to 6.40
plt.yticks([round(i, 2) for i in [5.90 + x * 0.05 for x in range(11)]])  # Show values with two decimal places as floats
plt.grid(True)
plt.legend()
plt.savefig(line_plot_path)  # Save line plot
plt.close()

# Create weighted histogram
plt.figure(figsize=(14, 6))
plt.bar(years, frequency_percent, color='g', alpha=0.7, label='Frequency (%)')
plt.xlabel("Year", fontsize=20)
plt.ylabel("Frequency (%)",fontsize=20)
plt.title("Required ROI Over the Years (de facto)")
plt.xticks(years, rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend()
plt.savefig(histogram_path)  # Save histogram
plt.close()

# Print confirmation with new paths
print(f"Saved line plot: {line_plot_path}")
print(f"Saved histogram: {histogram_path}")
