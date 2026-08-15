from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import numpy as np
import pandas as pd

from app.profiler import (
    load_data,
    dataset_summary,
    numerical_summary,
    missing_value_percentage,
    categorical_summary,
    correlation_matrix,
    detect_outliers_iqr,
)

from app.stats_engine import (
    shapiro_test,
    descriptive_statistics,
    confidence_interval,
    pearson_corr,
    spearman_corr,
    adf_test,
    kpss_test,
    independent_ttest,
    paired_ttest,
    mann_whitney_test,
    wilcoxon_test,
    chi_square_test,
    one_way_anova,
    kruskal_test,
)

from app.models import (
    TwoSampleRequest,
    MultiGroupRequest,
    ChiSquareRequest,
)

from app.chat_api import router as chat_router
from app.dataset_store import dataset_store

app = FastAPI(
    title="Statistics AI Agent API",
    version="1.0.0",
    description="API for statistical profiling and hypothesis testing"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
],
    
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# Helper Functions
# ----------------------------------------------------

def read_uploaded_csv(file_path):
    return load_data(file_path)


async def save_uploaded_file(file: UploadFile):
    temp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".csv"
    )

    temp.write(await file.read())
    temp.close()

    return temp.name


# ----------------------------------------------------
# Home
# ----------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Welcome to Statistics AI Agent API",
        "version": "1.0.0"
    }


# ----------------------------------------------------
# Upload CSV
# ----------------------------------------------------

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):

    if not file.filename.endswith(".csv"):
        return {"error": "Please upload a CSV file."}

    temp_path = await save_uploaded_file(file)

    try:

        df = read_uploaded_csv(temp_path)

        # Store dataset for AI Chat
        dataset_store.set_dataset(df, file.filename)

        return {
            "message": "Dataset uploaded successfully.",
            "filename": file.filename,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns)
        }

    finally:
        os.remove(temp_path)


# ----------------------------------------------------
# Dataset Summary
# ----------------------------------------------------

@app.post("/summary")
async def summary(file: UploadFile = File(...)):

    temp_path = await save_uploaded_file(file)

    try:
        df = read_uploaded_csv(temp_path)
        return dataset_summary(df)

    finally:
        os.remove(temp_path)


# ----------------------------------------------------
# Numerical Summary
# ----------------------------------------------------

@app.post("/numerical-summary")
async def numerical(file: UploadFile = File(...)):

    temp_path = await save_uploaded_file(file)

    try:
        df = read_uploaded_csv(temp_path)
        return numerical_summary(df)

    finally:
        os.remove(temp_path)


# ----------------------------------------------------
# Missing Values
# ----------------------------------------------------

@app.post("/missing-values")
async def missing(file: UploadFile = File(...)):

    temp_path = await save_uploaded_file(file)

    try:
        df = read_uploaded_csv(temp_path)
        return missing_value_percentage(df).to_dict()

    finally:
        os.remove(temp_path)


# ----------------------------------------------------
# Categorical Summary
# ----------------------------------------------------

@app.post("/categorical-summary")
async def categorical(file: UploadFile = File(...)):

    temp_path = await save_uploaded_file(file)

    try:
        df = read_uploaded_csv(temp_path)
        return categorical_summary(df)

    finally:
        os.remove(temp_path)


# ----------------------------------------------------
# Correlation Matrix
# ----------------------------------------------------

@app.post("/correlation")
async def correlation(file: UploadFile = File(...)):

    temp_path = await save_uploaded_file(file)

    try:
        df = read_uploaded_csv(temp_path)
        return correlation_matrix(df).to_dict()

    finally:
        os.remove(temp_path)


# ----------------------------------------------------
# Outlier Detection
# ----------------------------------------------------

@app.post("/outliers")
async def outliers(file: UploadFile = File(...)):

    temp_path = await save_uploaded_file(file)

    try:
        df = read_uploaded_csv(temp_path)
        return detect_outliers_iqr(df)

    finally:
        os.remove(temp_path)


def make_json_serializable(obj):
    if isinstance(obj, dict):
        return {
            str(key): make_json_serializable(value)
            for key, value in obj.items()
        }

    if isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]

    if isinstance(obj, tuple):
        return [make_json_serializable(item) for item in obj]

    if isinstance(obj, np.integer):
        return int(obj)

    if isinstance(obj, np.floating):
        return float(obj)

    if isinstance(obj, np.ndarray):
        return obj.tolist()

    if pd.isna(obj):
        return None

    return obj


# ----------------------------------------------------
# Descriptive Statistics
# ----------------------------------------------------

@app.post("/descriptive-statistics")
async def descriptive(file: UploadFile = File(...)):

    temp_path = await save_uploaded_file(file)

    try:
        df = read_uploaded_csv(temp_path)

        numerical = descriptive_statistics(df)
        categorical = categorical_summary(df)
        missing = missing_value_percentage(df).to_dict()

        return make_json_serializable({
            "numerical": numerical,
            "categorical": categorical,
            "missing": missing,
        })

    finally:
        os.remove(temp_path)



# ----------------------------------------------------
# Confidence Interval
# ----------------------------------------------------

@app.post("/confidence-interval/{column}")
async def confidence(file: UploadFile = File(...), column: str = ""):

    temp_path = await save_uploaded_file(file)

    try:
        df = read_uploaded_csv(temp_path)
        return confidence_interval(df[column])

    finally:
        os.remove(temp_path)   


# ----------------------------------------------------
# Shapiro-Wilk Normality Test
# ----------------------------------------------------

@app.post("/shapiro/{column}")
async def shapiro(
    file: UploadFile = File(...),
    column: str = ""
):

    temp_path = await save_uploaded_file(file)

    try:
        df = read_uploaded_csv(temp_path)

        return shapiro_test(df, column)

    finally:
        os.remove(temp_path)


# ----------------------------------------------------
# Pearson Correlation
# ----------------------------------------------------

@app.post("/pearson/{col1}/{col2}")
async def pearson(
    file: UploadFile = File(...),
    col1: str = "",
    col2: str = ""
):

    temp_path = await save_uploaded_file(file)

    try:
        df = read_uploaded_csv(temp_path)

        return pearson_corr(
            df[col1],
            df[col2]
        )

    finally:
        os.remove(temp_path)


# ----------------------------------------------------
# Spearman Correlation
# ----------------------------------------------------

@app.post("/spearman/{col1}/{col2}")
async def spearman(
    file: UploadFile = File(...),
    col1: str = "",
    col2: str = ""
):

    temp_path = await save_uploaded_file(file)

    try:
        df = read_uploaded_csv(temp_path)

        return spearman_corr(
            df[col1],
            df[col2]
        )

    finally:
        os.remove(temp_path)


# ----------------------------------------------------
# Augmented Dickey-Fuller Test
# ----------------------------------------------------

@app.post("/adf/{column}")
async def adf(
    file: UploadFile = File(...),
    column: str = ""
):

    temp_path = await save_uploaded_file(file)

    try:
        df = read_uploaded_csv(temp_path)

        return adf_test(df[column])

    finally:
        os.remove(temp_path)


# ----------------------------------------------------
# KPSS Test
# ----------------------------------------------------

@app.post("/kpss/{column}")
async def kpss(
    file: UploadFile = File(...),
    column: str = ""
):

    temp_path = await save_uploaded_file(file)

    try:
        df = read_uploaded_csv(temp_path)

        return kpss_test(df[column])

    finally:
        os.remove(temp_path)


# ====================================================
# TWO-SAMPLE STATISTICAL TESTS
# ====================================================


# ----------------------------------------------------
# Independent T-Test
# ----------------------------------------------------

@app.post("/ttest")
def ttest(data: TwoSampleRequest):

    return independent_ttest(
        data.group1,
        data.group2
    )


# ----------------------------------------------------
# Paired T-Test
# ----------------------------------------------------

@app.post("/paired-ttest")
def paired_ttest_endpoint(data: TwoSampleRequest):

    return paired_ttest(
        data.group1,
        data.group2
    )


# ----------------------------------------------------
# Mann-Whitney U Test
# ----------------------------------------------------

@app.post("/mann-whitney")
def mann_whitney(data: TwoSampleRequest):

    return mann_whitney_test(
        data.group1,
        data.group2
    )


# ----------------------------------------------------
# Wilcoxon Signed-Rank Test
# ----------------------------------------------------

@app.post("/wilcoxon")
def wilcoxon(data: TwoSampleRequest):

    return wilcoxon_test(
        data.group1,
        data.group2
    )


# ====================================================
# MULTI-GROUP STATISTICAL TESTS
# ====================================================


# ----------------------------------------------------
# Chi-Square Test
# ----------------------------------------------------

@app.post("/chi-square")
def chi_square(data: ChiSquareRequest):

    return chi_square_test(
        data.table
    )


# ----------------------------------------------------
# One-Way ANOVA
# ----------------------------------------------------

@app.post("/anova")
def anova(data: MultiGroupRequest):

    return one_way_anova(
        *data.groups
    )


# ----------------------------------------------------
# Kruskal-Wallis Test
# ----------------------------------------------------

@app.post("/kruskal")
def kruskal(data: MultiGroupRequest):

    return kruskal_test(
        *data.groups
    )


# ====================================================
# AI CHAT ROUTER
# ====================================================

app.include_router(
    chat_router,
    prefix="/ai",
    tags=["AI Assistant"]
)