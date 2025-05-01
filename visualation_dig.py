import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import json
import os

# --- Load Data Without Merging ---
def load_data():
    try:
        with open("Patients_data.json", "r", encoding="utf-8") as f:
            df_patients = pd.DataFrame(json.load(f))

        with open("diagnoses_data.json", "r", encoding="utf-8") as f:
            df_diagnosis = pd.DataFrame(json.load(f))

        return df_patients, df_diagnosis

    except FileNotFoundError as e:
        raise SystemExit(f"Missing file: {e.filename}")

    except json.JSONDecodeError:
        raise SystemExit("One of the JSON files is malformed.")

# Load data
df_patients, df_diagnosis = load_data()

# Add BMI category to patients
def categorize_bmi(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 24.9:
        return "Normal"
    elif 24.9 <= bmi < 29.9:
        return "Overweight"
    else:
        return "Obese"

df_patients['bmi_category'] = df_patients['bmi'].apply(categorize_bmi)

# --- Initialize GUI ---
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

app = ctk.CTk()
app.title("Diagnosis Dashboard")
app.geometry("1100x800")

main_frame = ctk.CTkFrame(app, fg_color="#C1E1C1")
main_frame.pack(fill="both", expand=True)

# --- Filter Controls ---
filter_frame = ctk.CTkFrame(main_frame, fg_color="#A8D8B9")
filter_frame.pack(pady=10, padx=20, fill="x")

# Diagnosis Filter
ctk.CTkLabel(filter_frame, text="Diagnosis:").grid(row=0, column=0, padx=5, pady=5)
diag_options = ["All"] + df_diagnosis["disease_name"].dropna().unique().tolist()
diag_var = ctk.StringVar(value="All")
diag_menu = ctk.CTkOptionMenu(filter_frame, values=diag_options, variable=diag_var)
diag_menu.grid(row=0, column=1, padx=5, pady=5)

# Gender Filter
ctk.CTkLabel(filter_frame, text="Gender:").grid(row=0, column=2, padx=5, pady=5)
gender_options = ["All"] + df_patients["gender"].dropna().unique().tolist()
gender_var = ctk.StringVar(value="All")
gender_menu = ctk.CTkOptionMenu(filter_frame, values=gender_options, variable=gender_var)
gender_menu.grid(row=0, column=3, padx=5, pady=5)

# BMI Filter
ctk.CTkLabel(filter_frame, text="BMI Category:").grid(row=0, column=4, padx=5, pady=5)
bmi_options = ["All"] + df_patients["bmi_category"].dropna().unique().tolist()
bmi_var = ctk.StringVar(value="All")
bmi_menu = ctk.CTkOptionMenu(filter_frame, values=bmi_options, variable=bmi_var)
bmi_menu.grid(row=0, column=5, padx=5, pady=5)

# Apply Filters
def apply_filters():
    diag = diag_var.get()
    gender = gender_var.get()
    bmi_cat = bmi_var.get()

    # Get filtered patient IDs from diagnosis data
    filtered_diag_ids = df_diagnosis["patient_id"]
    if diag != "All":
        filtered_diag_ids = df_diagnosis[df_diagnosis["disease_name"] == diag]["patient_id"]

    # Filter patient data
    filtered_patients = df_patients.copy()

    # Apply gender filter
    if gender != "All":
        filtered_patients = filtered_patients[filtered_patients["gender"] == gender]

    # Apply BMI filter
    if bmi_cat != "All":
        filtered_patients = filtered_patients[filtered_patients["bmi_category"] == bmi_cat]

    # Match patients who are in the filtered diagnosis
    filtered_patients = filtered_patients[filtered_patients["patient_id"].isin(filtered_diag_ids)]

    update_charts(filtered_patients, diag)

ctk.CTkButton(filter_frame, text="Apply Filters", command=apply_filters).grid(
    row=0, column=6, padx=10, pady=5
)

# --- Visualization Tabs ---
tabview = ctk.CTkTabview(main_frame, width=1060, height=600, fg_color="#A8D8B9")
tabview.pack(padx=10, pady=10)

tab_diag = tabview.add("Diagnosis Distribution")
tab_gender = tabview.add("Gender Distribution")
tab_bmi_diag = tabview.add("BMI vs Diagnosis")

def embed_plot(fig, tab):
    for widget in tab.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(fig, master=tab)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

# --- Plotting Functions ---
def update_charts(filtered_patients, diag_filter):
    plot_diagnosis_distribution(diag_filter)
    plot_gender_distribution(filtered_patients)
    plot_bmi_vs_diagnosis(filtered_patients, diag_filter)

def plot_diagnosis_distribution(diag_filter):
    fig, ax = plt.subplots(figsize=(6, 4))
    if diag_filter == "All":
        df_diagnosis["disease_name"].value_counts().plot.bar(ax=ax, color="mediumseagreen")
    else:
        df_diagnosis[df_diagnosis["disease_name"] == diag_filter]["disease_name"].value_counts().plot.bar(ax=ax, color="mediumseagreen")
    ax.set_title("Diagnosis Distribution")
    ax.set_ylabel("Count")
    ax.set_xlabel("Diagnosis")
    embed_plot(fig, tab_diag)

def plot_gender_distribution(df):
    fig, ax = plt.subplots(figsize=(5, 4))
    df["gender"].value_counts().plot.pie(ax=ax, autopct='%1.1f%%', startangle=90, colors=['#66BB6A', '#98FB98'])
    ax.set_title("Gender Distribution")
    ax.axis("equal")
    embed_plot(fig, tab_gender)

def plot_bmi_vs_diagnosis(df, diag_filter):
    fig, ax = plt.subplots(figsize=(8, 5))
    if diag_filter == "All":
        grouped = df.groupby("bmi_category")["patient_id"].count()
    else:
        diag_ids = df_diagnosis[df_diagnosis["disease_name"] == diag_filter]["patient_id"]
        grouped = df[df["patient_id"].isin(diag_ids)].groupby("bmi_category")["patient_id"].count()

    grouped.plot.bar(ax=ax, color="olivedrab")
    ax.set_title("BMI Distribution for Diagnosis")
    ax.set_ylabel("Count")
    ax.set_xlabel("BMI Category")
    embed_plot(fig, tab_bmi_diag)

# --- Initial Chart Render ---
apply_filters()

# --- Run App ---
app.mainloop()