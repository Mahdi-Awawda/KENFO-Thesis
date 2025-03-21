import matplotlib
matplotlib.use('TkAgg')  # Set a compatible backend

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import os  # For file and folder operations
import pandas as pd  # For exporting data

# Function to generate an incremented file name within a folder
def get_incremented_filename(folder, base_name, extension=".png"):
    os.makedirs(folder, exist_ok=True)  # Ensure the folder exists
    counter = 1
    while os.path.exists(os.path.join(folder, f"{base_name}_{counter}{extension}")):
        counter += 1
    return os.path.join(folder, f"{base_name}_{counter}{extension}")

# Function to generate an incremented file name for Excel output
def get_incremented_excel_filename(folder, base_name):
    os.makedirs(folder, exist_ok=True)  # Ensure the folder exists
    counter = 1
    while os.path.exists(os.path.join(folder, f"{base_name}_{counter}.xlsx")):
        counter += 1
    return os.path.join(folder, f"{base_name}_{counter}.xlsx")

# Risk definitions (converted delays to years)
risks = {
    "Phase I": [
        {"prob_min": 0.05, "prob_max": 0.05, "delay_min": 6 / 12, "delay_max": 12 / 12},
        {"prob_min": 0.05, "prob_max": 0.05, "delay_min": 2 / 12, "delay_max": 6 / 12},
        {"prob_min": 0.50, "prob_max": 0.50, "delay_min": 2 / 12, "delay_max": 6 / 12},
        {"prob_min": 0.05, "prob_max": 0.05, "delay_min": 12 / 12, "delay_max": 24 / 12},
        {"prob_min": 0.05, "prob_max": 0.05, "delay_min": 6 / 12, "delay_max": 12 / 12},
    ],
    "Phase II": [
        {"prob_min": 0.70, "prob_max": 0.80, "delay_min": 6 / 12, "delay_max": 12 / 12},
        {"prob_min": 0.50, "prob_max": 0.60, "delay_min": 6 / 12, "delay_max": 12 / 12},
    ],
    "Phase III": [
        {"prob_min": 0.30, "prob_max": 0.50, "delay_min": 6 / 12, "delay_max": 12 / 12},
        {"prob_min": 0.50, "prob_max": 0.60, "delay_min": 1 / 12, "delay_max": 1 / 12},
    ],
}

# Simulation parameters
num_simulations = 10000
phase1_end = 2027.5  # Base end time for Phase I
phase_durations = {
    "Phase II": [10, 12],  # Corrected time frames
    "Phase III": [5, 6, 13, 23],  # Scenario A (5-6), Scenario B (13-23)
}

# Storage for End Disposal years
end_disposal_years = []

for _ in range(num_simulations):
    current_time = phase1_end

    # Apply risks to Phase I
    for risk in risks["Phase I"]:
        if np.random.rand() < np.random.uniform(risk["prob_min"], risk["prob_max"]):
            delay = np.random.uniform(risk["delay_min"], risk["delay_max"])
            current_time += delay

    # Phase II duration and risks
    phase2_duration = np.random.uniform(phase_durations["Phase II"][0], phase_durations["Phase II"][1])
    for risk in risks["Phase II"]:
        if np.random.rand() < np.random.uniform(risk["prob_min"], risk["prob_max"]):
            delay = np.random.uniform(risk["delay_min"], risk["delay_max"])
            phase2_duration += delay
    current_time += phase2_duration

    # Phase III scenario selection
    if np.random.rand() < 0.5:
        phase3_duration = np.random.uniform(phase_durations["Phase III"][0], phase_durations["Phase III"][1])
    else:
        phase3_duration = np.random.uniform(phase_durations["Phase III"][2], phase_durations["Phase III"][3])

    current_time += phase3_duration
    end_disposal_years.append(round(current_time))

# Convert to DataFrame
end_disposal_df = pd.DataFrame({
    "Reality": range(1, num_simulations + 1),
    "End_Disposal_Completion_Year": end_disposal_years
})

# Compute frequency counts
year_counts = end_disposal_df["End_Disposal_Completion_Year"].value_counts().sort_index()
# Compute proportions
year_proportions = (year_counts / num_simulations) * 100

# Save table to Excel
output_path = get_incremented_excel_filename("outputs", "end_disposal_completion_data")
with pd.ExcelWriter(output_path) as writer:
    end_disposal_df.to_excel(writer, sheet_name="End_Disposal_Data", index=False)
    year_counts.to_frame(name="Frequency").assign(Proportion=year_proportions).to_excel(writer, sheet_name="Year_Frequency")

# Create histogram
plt.figure(figsize=(10, 6))
plt.hist(end_disposal_years, bins=range(min(end_disposal_years), max(end_disposal_years) + 1),
         weights=np.ones(len(end_disposal_years)) / len(end_disposal_years) * 100,
         edgecolor='black', alpha=0.7)
plt.xlabel("Years")
plt.ylabel("Percentage of occurrence of a year")
plt.title("Normalized Histogram of Conclusion of all Final Disposal Activities")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.xticks(range(min(end_disposal_years), max(end_disposal_years) + 1), rotation=45)

# Save histogram plot
hist_file_name = get_incremented_filename("plots", "end_disposal_histogram")
plt.savefig(hist_file_name)
plt.close()

print(f"Excel file saved as: {output_path}")
print(f"Histogram saved as: {hist_file_name}")