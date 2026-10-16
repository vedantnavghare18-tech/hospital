from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__, template_folder="templates")
print("CURRENT FOLDER:", os.getcwd())
print("TEMPLATE FOLDER:", app.template_folder)
print("TEMPLATES PATH:", os.path.abspath(app.template_folder))

# Load Dataset
df = pd.read_csv("hospital data analysis.csv")

# Clean Dataset
df = df.drop_duplicates()
df = df.dropna()


# -----------------------------
# HOME / DASHBOARD
# -----------------------------
@app.route("/")
def home():

    total_patients = len(df)

    total_cost = df["Cost"].sum()

    average_stay = round(df["Length_of_Stay"].mean(), 2)

    readmissions = (df["Readmission"] == "Yes").sum()

    readmission_rate = round((readmissions / total_patients) * 100, 2)

    average_satisfaction = round(df["Satisfaction"].mean(), 2)

    most_common_condition = df["Condition"].mode()[0]

    return render_template(
        "index.html",
        total_patients=total_patients,
        total_cost=total_cost,
        average_stay=average_stay,
        readmission_rate=readmission_rate,
        average_satisfaction=average_satisfaction,
        most_common_condition=most_common_condition
    )


# -----------------------------
# PATIENT SEARCH
# -----------------------------
@app.route("/patient")
def patient():

    patient_id = request.args.get("patient_id")

    patient_data = None

    if patient_id:

        try:
            patient_id = int(patient_id)

            result = df[df["Patient_ID"] == patient_id]

            if not result.empty:
                patient_data = result.iloc[0].to_dict()

        except:
            patient_data = None

    return render_template(
        "patient.html",
        patient_data=patient_data
    )


# -----------------------------
# CONDITION ANALYSIS
# -----------------------------
@app.route("/condition")
def condition():

    search = request.args.get("search", "")

    data = df.copy()

    if search:
        data = data[
            data["Condition"]
            .str.contains(search, case=False, na=False)
        ]

    condition_count = (
        data["Condition"]
        .value_counts()
        .to_dict()
    )

    average_cost = (
        data.groupby("Condition")["Cost"]
        .mean()
        .round(2)
        .to_dict()
    )

    average_stay = (
        data.groupby("Condition")["Length_of_Stay"]
        .mean()
        .round(2)
        .to_dict()
    )

    return render_template(
        "condition.html",
        condition_count=condition_count,
        average_cost=average_cost,
        average_stay=average_stay,
        search=search
    )


# -----------------------------
# TREATMENT & COST
# -----------------------------
@app.route("/treatment")
def treatment():

    search = request.args.get("search", "")

    data = df.copy()

    if search:
        data = data[
            data["Procedure"]
            .str.contains(search, case=False, na=False)
        ]

    treatment_data = (
        data.groupby("Procedure")
        .agg(
            Average_Cost=("Cost", "mean"),
            Average_Stay=("Length_of_Stay", "mean")
        )
        .round(2)
        .reset_index()
    )

    records = treatment_data.to_dict("records")

    return render_template(
        "treatment.html",
        records=records,
        search=search
    )

@app.route("/procedure")
def procedure():
    search = request.args.get("search", "")

    data = df.copy()

    if search:
        data = data[data["Procedure"].str.contains(search, case=False, na=False)]

    total_patients = len(data)

    if total_patients > 0:
        average_cost = round(data["Cost"].mean(), 2)
        recovered = (data["Outcome"] == "Recovered").sum()
        stable = (data["Outcome"] == "Stable").sum()
    else:
        average_cost = 0
        recovered = 0
        stable = 0

    return render_template(
        "procedure.html",
        search=search,
        total_patients=total_patients,
        average_cost=average_cost,
        recovered=recovered,
        stable=stable
    )

# -----------------------------
# OUTCOME & READMISSION
# -----------------------------
@app.route("/outcome")
def outcome():

    search = request.args.get("search", "")

    data = df.copy()

    if search:
        data = data[
            data["Condition"]
            .str.contains(search, case=False, na=False)
        ]

    outcome_count = (
        data["Outcome"]
        .value_counts()
        .to_dict()
    )

    readmission_count = (
        data["Readmission"]
        .value_counts()
        .to_dict()
    )

    return render_template(
        "outcome.html",
        outcome_count=outcome_count,
        readmission_count=readmission_count,
        search=search
    )


# -----------------------------
# RUN WEBSITE
# -----------------------------
import webbrowser

if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=True)