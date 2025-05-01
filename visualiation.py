import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import json
import os

# --- Load Data ---
def load_data():
    try:
        with open("patients_data.json", "r") as f:
            patients = pd.DataFrame(json.load(f))
        
        with open("diagnoses_data.json", "r") as f:
            diagnoses = pd.DataFrame(json.load(f))
        
        with open("treatments_data.json", "r") as f:
            treatments = pd.DataFrame(json.load(f))
        
        return patients, diagnoses, treatments

    except Exception as e:
        raise SystemExit(f"Error loading files: {e}")

df_patients, df_diagnosis, df_treatments = load_data()

# Merge data
df = pd.merge(df_patients, df_diagnosis, on="patient_id", how="left")
df = pd.merge(df, df_treatments, on="diagnosis_id", how="left")

# --- Preprocess Data ---
df["date_of_birth"] = pd.to_datetime(df["date_of_birth"])
df["age"] = (pd.to_datetime("2025-05-05") - df["date_of_birth"]).dt.days // 365

def categorize_bmi(bmi):
    if bmi < 18.5: return "Underweight"
    elif 18.5 <= bmi < 24.9: return "Normal"
    elif 24.9 <= bmi < 29.9: return "Overweight"
    else: return "Obese"

df["bmi_category"] = df["bmi"].apply(categorize_bmi)

def categorize_bp(row):
    systolic, diastolic = row["systolic"], row["diastolic"]
    if systolic < 120 and diastolic < 80: return "Normal"
    elif 120 <= systolic <= 129 and diastolic < 80: return "Elevated"
    elif systolic >= 130 or diastolic >= 80: return "Hypertension"
    else: return "Other"

df["bp_category"] = df.apply(categorize_bp, axis=1)

def categorize_prescription(prescription):
    if not isinstance(prescription, str): return "Unknown"
    if any(drug in prescription for drug in ["Lisinopril", "Amlodipine"]): return "Medication"
    elif "diet" in prescription.lower() or "exercise" in prescription.lower(): return "Lifestyle"
    elif "No medication" in prescription or "No treatment" in prescription: return "Observation"
    elif "Orlistat" in prescription: return "Weight Loss"
    else: return "Other"

df["prescription"] = df["prescription"].fillna("")
df["prescription_type"] = df["prescription"].apply(categorize_prescription)

# --- Configure Theme ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# --- Initialize App ---
app = ctk.CTk()
app.title("Healthcare Dashboard")
app.geometry("1300x900")

# Main Frame (Dark Background)
main_frame = ctk.CTkFrame(app, fg_color="#1A1A1A")
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Title Label
title = ctk.CTkLabel(
    main_frame,
    text="🩺 Healthcare Analytics Dashboard",
    font=("Helvetica", 24, "bold"),
    text_color="white"
)
title.pack(pady=10)

# --- Filter Controls ---
filter_frame = ctk.CTkFrame(main_frame, fg_color="#2D2D2D")
filter_frame.pack(pady=10, padx=15, fill="x")

# Diagnosis Filter
ctk.CTkLabel(filter_frame, text="Diagnosis:", text_color="white").grid(row=0, column=0, padx=5, pady=5)
diag_options = ["All"] + df["disease_name"].dropna().unique().tolist()
diag_var = ctk.StringVar(value="All")
ctk.CTkOptionMenu(filter_frame, values=diag_options, variable=diag_var, fg_color="#4CAF50", text_color="white").grid(row=0, column=1, padx=5, pady=5)

# Gender Filter
ctk.CTkLabel(filter_frame, text="Gender:", text_color="white").grid(row=0, column=2, padx=5, pady=5)
gender_options = ["All"] + df["gender"].dropna().unique().tolist()
gender_var = ctk.StringVar(value="All")
ctk.CTkOptionMenu(filter_frame, values=gender_options, variable=gender_var, fg_color="#4CAF50", text_color="white").grid(row=0, column=3, padx=5, pady=5)

# BMI Filter
ctk.CTkLabel(filter_frame, text="BMI Category:", text_color="white").grid(row=0, column=4, padx=5, pady=5)
bmi_options = ["All"] + df["bmi_category"].dropna().unique().tolist()
bmi_var = ctk.StringVar(value="All")
ctk.CTkOptionMenu(filter_frame, values=bmi_options, variable=bmi_var, fg_color="#4CAF50", text_color="white").grid(row=0, column=5, padx=5, pady=5)

# Status Filter
ctk.CTkLabel(filter_frame, text="Treatment Status:", text_color="white").grid(row=0, column=6, padx=5, pady=5)
status_options = ["All"] + df["status"].dropna().unique().tolist()
status_var = ctk.StringVar(value="All")
ctk.CTkOptionMenu(filter_frame, values=status_options, variable=status_var, fg_color="#4CAF50", text_color="white").grid(row=0, column=7, padx=5, pady=5)

# Apply Filters Button
def apply_filters():
    diag = diag_var.get()
    gender = gender_var.get()
    bmi_cat = bmi_var.get()
    status = status_var.get()

    filtered = df.copy()
    
    if diag != "All": filtered = filtered[filtered["disease_name"] == diag]
    if gender != "All": filtered = filtered[filtered["gender"] == gender]
    if bmi_cat != "All": filtered = filtered[filtered["bmi_category"] == bmi_cat]
    if status != "All": filtered = filtered[filtered["status"] == status]
    
    update_charts(filtered)

ctk.CTkButton(
    filter_frame,
    text="Apply",
    command=apply_filters,
    fg_color="#4CAF50",
    hover_color="#388E3C",
    text_color="white"
).grid(row=0, column=8, padx=10, pady=5)

# --- Info Cards ---
info_frame = ctk.CTkFrame(main_frame, fg_color="#2D2D2D")
info_frame.pack(pady=5, padx=15, fill="x")

def create_info_card(parent, title, value):
    card = ctk.CTkFrame(parent, fg_color="#1F1F1F", border_color="#4CAF50", border_width=1)
    card.pack(side="left", expand=True, padx=5, pady=5, fill="x")
    ctk.CTkLabel(card, text=title, font=("Arial", 14, "bold"), text_color="white").pack(pady=2)
    ctk.CTkLabel(card, text=value, font=("Arial", 16), text_color="white").pack(pady=5)

create_info_card(info_frame, "Total Patients", "N/A")
create_info_card(info_frame, "Active Treatments", "N/A")
create_info_card(info_frame, "Avg BMI", "N/A")
create_info_card(info_frame, "Most Common Diagnosis", "N/A")

# --- Visualization Tabs ---
tabview = ctk.CTkTabview(main_frame, width=1280, height=600, fg_color="#2D2D2D", segmented_button_fg_color="#4CAF50")
tabview.pack(padx=10, pady=10)

tabs = {
    "Diagnosis Distribution": None,
    "Blood Pressure": None,
    "BMI vs Diagnosis": None,
    "Treatment Status": None,
    "Prescription Types": None
}

for tab_name in tabs:
    tabs[tab_name] = tabview.add(tab_name)

# Function to embed plot
def embed_plot(fig, tab):
    for widget in tab.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(fig, master=tab)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

# --- Plotting Functions ---
def update_charts(df_filtered):
    # Update info cards
    for i, val in enumerate([
        len(df_filtered),
        len(df_filtered[df_filtered["status"] == "Active"]),
        round(df_filtered["bmi"].mean(), 1),
        df_filtered["disease_name"].mode()[0] if not df_filtered.empty else "None"
    ]):
        for widget in info_frame.winfo_children()[i].winfo_children():
            if isinstance(widget, ctk.CTkLabel) and widget.cget("font") == ("Arial", 16):
                widget.configure(text=str(val))

    # Diagnosis Distribution
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    df_filtered["disease_name"].value_counts().plot.bar(ax=ax1, color="#4CAF50")
    ax1.set_title("Diagnosis Distribution", color="white")
    ax1.set_ylabel("Count", color="white")
    ax1.set_xlabel("Diagnosis", color="white")
    ax1.tick_params(colors="white")
    ax1.set_facecolor("#1A1A1A")
    fig1.set_facecolor("#1A1A1A")
    embed_plot(fig1, tabs["Diagnosis Distribution"])

    # Blood Pressure Categories
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    df_filtered["bp_category"].value_counts().plot.bar(ax=ax2, color="#4CAF50")
    ax2.set_title("Blood Pressure Categories", color="white")
    ax2.set_ylabel("Count", color="white")
    ax2.set_xlabel("Category", color="white")
    ax2.tick_params(colors="white")
    ax2.set_facecolor("#1A1A1A")
    fig2.set_facecolor("#1A1A1A")
    embed_plot(fig2, tabs["Blood Pressure"])

    # BMI vs Diagnosis
    fig3, ax3 = plt.subplots(figsize=(8, 5))
    df_filtered.groupby(["disease_name", "bmi_category"]).size().unstack().plot.bar(stacked=True, ax=ax3, color=["#4CAF50", "#81C784", "#A5D6A7", "#C8E6C9"])
    ax3.set_title("BMI vs Diagnosis", color="white")
    ax3.set_ylabel("Count", color="white")
    ax3.set_xlabel("Diagnosis", color="white")
    ax3.tick_params(colors="white")
    ax3.set_facecolor("#1A1A1A")
    fig3.set_facecolor("#1A1A1A")
    embed_plot(fig3, tabs["BMI vs Diagnosis"])

    # Treatment Status
    update_treatment_status(df_filtered)

    # Prescription Types
    fig5, ax5 = plt.subplots(figsize=(6, 4))
    df_filtered["prescription_type"].value_counts().plot.bar(ax=ax5, color="#4CAF50")
    ax5.set_title("Prescription Types", color="white")
    ax5.set_ylabel("Count", color="white")
    ax5.set_xlabel("Type", color="white")
    ax5.tick_params(colors="white")
    ax5.set_facecolor("#1A1A1A")
    fig5.set_facecolor("#1A1A1A")
    embed_plot(fig5, tabs["Prescription Types"])

# --- Treatment Status Pie Chart (Fixed) ---
def update_treatment_status(df_filtered):
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # Get value counts and filter out unknown/empty statuses
    status_counts = df_filtered["status"].value_counts()
    labels = status_counts.index.tolist()
    sizes = status_counts.values.tolist()

    # Define green colors
    colors = ['#4CAF50', '#81C784', '#A5D6A7', '#C8E6C9']

    # Plot pie chart
    wedges, texts = ax.pie(
        sizes,
        labels=labels,
        startangle=90,
        colors=[colors[i % len(colors)] for i in range(len(labels))],
        wedgeprops=dict(width=0.4),
        textprops={'color': "white", 'fontsize': 10}
    )

    # Add percentage labels inside slices
    autopct = lambda pct: f"{pct:.1f}%" if pct > 0 else ""
    ax.pie(
        sizes,
        autopct=autopct,
        startangle=90,
        colors=[colors[i % len(colors)] for i in range(len(labels))],
        wedgeprops=dict(width=0.4),
        textprops={'color': "white", 'fontsize': 10},
        labeldistance=0.75
    )

    # Add legend with corrected labelcolor
    ax.legend(wedges, labels,
              title="Status",
              loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1),
              prop={'size': 10},
              title_fontsize=10,
              labelcolor='white')  # ✅ Fixed: use labelcolor instead of prop['color']

    plt.setp(texts, color='white')  # Set label text color
    ax.set_title("Treatment Status", color="white")
    ax.axis("equal")  # Equal aspect ratio
    fig.set_facecolor("#1A1A1A")  # Match dark theme
    ax.set_facecolor("#1A1A1A")

    embed_plot(fig, tabs["Treatment Status"])

# --- Initial Render ---
apply_filters()

# --- Run App ---
app.mainloop()