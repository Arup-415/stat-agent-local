from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException
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
    test_assumptions,
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

MAX_UPLOAD_BYTES = 25 * 1024 * 1024

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
    try:
        dataframe = load_data(file_path)
    except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError, ValueError) as error:
        raise HTTPException(status_code=400, detail=f"Could not read CSV: {error}") from error

    if dataframe.empty or len(dataframe.columns) == 0:
        raise HTTPException(status_code=400, detail="The CSV file contains no data rows.")
    return dataframe


async def save_uploaded_file(file: UploadFile):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        megabyte = 1024 * 1024
        size_limit = f"{MAX_UPLOAD_BYTES // megabyte} MB" if MAX_UPLOAD_BYTES >= megabyte else f"{MAX_UPLOAD_BYTES} bytes"
        raise HTTPException(status_code=413, detail=f"CSV uploads must be {size_limit} or smaller.")
    if not content.strip():
        raise HTTPException(status_code=400, detail="The CSV file is empty.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp:
        temp.write(content)

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
async def upload_csv(
    file: UploadFile = File(...),
    session_id: str = Header(..., alias="X-Session-ID", min_length=16, max_length=128),
):

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    temp_path = await save_uploaded_file(file)

    try:

        df = read_uploaded_csv(temp_path)

        # Store dataset for AI Chat
        dataset_store.set_dataset(df, file.filename, session_id)

        return {
            "message": "Dataset uploaded successfully.",
            "filename": file.filename,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "data_types": df.dtypes.astype(str).to_dict(),
            "numerical_columns": df.select_dtypes(include=np.number).columns.tolist(),
            "categorical_columns": df.select_dtypes(include=["object", "category", "str", "bool"]).columns.tolist(),
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
        return float(obj) if np.isfinite(obj) else None

    if isinstance(obj, np.bool_):
        return bool(obj)

    if isinstance(obj, np.ndarray):
        return obj.tolist()

    if obj is pd.NA or obj is pd.NaT:
        return None

    if isinstance(obj, float) and not np.isfinite(obj):
        return None

    return obj


def _numeric_histograms(df):
    histograms = {}
    numeric_columns = df.select_dtypes(include=np.number).columns

    for column in numeric_columns:
        values = pd.to_numeric(df[column], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna().to_numpy()
        if values.size == 0:
            continue
        bin_count = min(12, max(1, int(np.ceil(np.sqrt(values.size)))))
        counts, edges = np.histogram(values, bins=bin_count)
        histograms[column] = [
            {"interval": f"{edges[index]:.3g} to {edges[index + 1]:.3g}", "count": int(count)}
            for index, count in enumerate(counts)
        ]

    return histograms


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
            "summary": dataset_summary(df),
            "numerical": numerical,
            "categorical": categorical,
            "missing": missing,
            "correlation": correlation_matrix(df).round(3).to_dict(),
            "outliers": detect_outliers_iqr(df),
            "histograms": _numeric_histograms(df),
        })

    finally:
        os.remove(temp_path)


def _get_numeric_column(df, column):
    if not column or column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Select a valid numeric column: {column or 'none selected'}.")

    values = pd.to_numeric(df[column], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    if values.empty:
        raise HTTPException(status_code=400, detail=f"Column '{column}' has no usable numeric values.")
    return values


@app.post("/run-test")
async def run_test(
    file: UploadFile = File(...),
    test: str = Form(...),
    column: str = Form(default=""),
    second_column: str = Form(default=""),
    group_column: str = Form(default=""),
):
    """Run a supported statistical test using columns from an uploaded CSV."""
    temp_path = await save_uploaded_file(file)

    try:
        df = read_uploaded_csv(temp_path)
        selected_test = test.strip().lower().replace("_", "-")
        test_key = selected_test
        result = None
        columns = []
        sample_sizes = []
        group_summaries = []
        diagnostics = []

        if selected_test in {"shapiro", "normality", "confidence-interval", "adf", "kpss"}:
            values = _get_numeric_column(df, column)
            columns = [column]
            sample_sizes = [{"column": column, "n": int(len(values))}]
            if selected_test in {"shapiro", "normality"}:
                if len(values) < 3:
                    raise HTTPException(status_code=400, detail="Shapiro-Wilk requires at least 3 numeric observations.")
                if len(values) > 5000:
                    raise HTTPException(status_code=400, detail="Shapiro-Wilk supports at most 5,000 observations; select a representative sample.")
                if values.nunique() < 2:
                    raise HTTPException(status_code=400, detail="Shapiro-Wilk requires a column with non-zero variation.")
                result = shapiro_test(pd.DataFrame({column: values}), column)
                selected_test = "shapiro-wilk"
            elif selected_test == "confidence-interval":
                if len(values) < 2:
                    raise HTTPException(status_code=400, detail="A confidence interval requires at least 2 numeric observations.")
                result = confidence_interval(values)
            elif selected_test == "adf":
                if len(values) < 8 or values.nunique() < 2:
                    raise HTTPException(status_code=400, detail="ADF requires at least 8 ordered observations with non-zero variation.")
                result = adf_test(values)
                selected_test = "Augmented Dickey-Fuller"
            else:
                if len(values) < 8 or values.nunique() < 2:
                    raise HTTPException(status_code=400, detail="KPSS requires at least 8 ordered observations with non-zero variation.")
                result = kpss_test(values)
                selected_test = "KPSS"
        elif selected_test in {"pearson", "spearman"}:
            first = _get_numeric_column(df, column)
            second = _get_numeric_column(df, second_column)
            paired = pd.concat([first.rename("first"), second.rename("second")], axis=1).dropna()
            if len(paired) < 3:
                raise HTTPException(status_code=400, detail="Correlation requires at least 3 complete numeric pairs.")
            if paired["first"].nunique() < 2 or paired["second"].nunique() < 2:
                raise HTTPException(status_code=400, detail="Correlation requires non-constant values in both columns.")
            columns = [column, second_column]
            sample_sizes = [{"complete pairs": int(len(paired))}]
            result = pearson_corr(paired["first"], paired["second"]) if selected_test == "pearson" else spearman_corr(paired["first"], paired["second"])
        elif selected_test in {"paired-t-test", "wilcoxon"}:
            first = _get_numeric_column(df, column)
            second = _get_numeric_column(df, second_column)
            paired = pd.concat([first.rename("first"), second.rename("second")], axis=1).dropna()
            if len(paired) < 2:
                raise HTTPException(status_code=400, detail="Paired tests require at least 2 complete pairs.")
            columns = [column, second_column]
            sample_sizes = [{"complete pairs": int(len(paired))}]
            if selected_test == "wilcoxon" and np.allclose(paired["first"], paired["second"]):
                raise HTTPException(status_code=400, detail="Wilcoxon is undefined when every paired difference is zero.")
            result = paired_ttest(paired["first"], paired["second"]) if selected_test == "paired-t-test" else wilcoxon_test(paired["first"], paired["second"])
        elif selected_test in {"independent-t-test", "mann-whitney", "anova", "kruskal"}:
            values = _get_numeric_column(df, column)
            if not group_column or group_column not in df.columns:
                raise HTTPException(status_code=400, detail="Select a valid grouping column.")
            grouped = pd.DataFrame({"value": values, "group": df.loc[values.index, group_column]}).dropna()
            grouped_parts = list(grouped.groupby("group", observed=True, sort=False))
            groups = [part["value"].to_numpy() for _, part in grouped_parts]
            if len(groups) < 2 or any(len(group) < 2 for group in groups):
                raise HTTPException(status_code=400, detail="Each selected group must contain at least 2 numeric observations, with at least 2 groups.")
            columns = [column, group_column]
            sample_sizes = [{"group": str(name), "n": int(len(part))} for name, part in grouped_parts]
            group_summaries = [
                {
                    "group": str(name),
                    "mean": float(part["value"].mean()),
                    "median": float(part["value"].median()),
                }
                for name, part in grouped_parts
            ]
            if selected_test in {"independent-t-test", "mann-whitney"} and len(groups) != 2:
                raise HTTPException(status_code=400, detail="This test requires exactly 2 groups.")
            if selected_test == "independent-t-test":
                result = independent_ttest(*groups)
            elif selected_test == "mann-whitney":
                result = mann_whitney_test(*groups)
            elif selected_test == "anova":
                result = one_way_anova(*groups)
            else:
                result = kruskal_test(*groups)
        elif selected_test in {"chi-square", "chi-square-test"}:
            if not column or column not in df.columns or not second_column or second_column not in df.columns:
                raise HTTPException(status_code=400, detail="Select two valid categorical columns.")
            table = pd.crosstab(df[column], df[second_column])
            if table.shape[0] < 2 or table.shape[1] < 2:
                raise HTTPException(status_code=400, detail="Chi-square requires at least 2 categories in each selected column.")
            columns = [column, second_column]
            sample_sizes = [{"observations": int(table.to_numpy().sum())}]
            result = chi_square_test(table.to_numpy())
            expected = np.asarray(result["Expected Frequency"])
            low_cells = int((expected < 5).sum())
            if low_cells:
                diagnostics.append(f"{low_cells} expected cell count(s) are below 5; the chi-square approximation may be unreliable.")
            selected_test = "Chi-square"
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported statistical test: {test}.")

        response = {
            "Test": selected_test,
            "Columns": columns,
            "Result": result,
            "Sample sizes": sample_sizes,
            "Group summaries": group_summaries,
            "Assumptions and limitations": test_assumptions(test_key),
            "Diagnostics": diagnostics,
        }
        if test_key != "confidence-interval":
            response["Significance level"] = 0.05
        return make_json_serializable(response)
    except HTTPException:
        raise
    except (KeyError, ValueError, TypeError) as error:
        raise HTTPException(status_code=400, detail=f"Could not run {test}: {error}") from error
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