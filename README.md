# STATCORE AI

STATCORE AI is a local statistical analysis workspace built with FastAPI and React. Upload a CSV to explore its columns, profile numeric and categorical data, run supported statistical tests, and ask dataset-aware questions.

## Features

- Dataset overview, descriptive statistics, missingness, categorical summaries, correlation matrix, IQR outlier flags, and numeric histograms.
- Shapiro-Wilk, 95% confidence interval, ADF, KPSS, Pearson, Spearman, paired t-test, Wilcoxon, independent Welch t-test, Mann-Whitney U, one-way ANOVA, Kruskal-Wallis, and chi-square tests.
- Test sample sizes, assumptions and limitations, and diagnostics for low expected chi-square counts.
- Group mean/median comparisons and JSON downloads for profiles and test results.
- Dataset-aware AI chat using Ollama. If Ollama or its model is unavailable, statistical endpoints still work and the assistant reports that it could not generate a response.

## Run Locally

Use separate terminals for the backend and frontend. The backend requirements include FastAPI, pandas, Ollama's Python client, and the test dependencies.

Backend, in PowerShell:

```powershell
Set-Location backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Frontend:

```powershell
Set-Location frontend
npm install
npm run dev
```

Open the Vite URL printed in the frontend terminal. The API documentation is at `http://127.0.0.1:8000/docs`. Set `VITE_API_URL` if the frontend should use a different backend URL.

For local AI responses, install Ollama and pull the configured model:

```powershell
ollama pull qwen2.5:7b
```

## Dataset and Session Limits

- Uploads must be CSV files of 25 MB or less.
- The frontend generates a random session ID and sends it with upload and chat requests. Direct API clients must send `X-Session-ID` with a 16- to 128-character value to `POST /upload` and `POST /ai/chat`.
- Datasets and chat history are held in server memory, scoped by session, and expire after 24 hours of inactivity. The server retains at most 128 active sessions and loses all session data when it restarts. This is not persistent storage or user authentication.
- Time-series tests use row order as time order and assume equally spaced observations. The app reports test assumptions but cannot verify that study design or sampling assumptions are true.
- A significant ANOVA or Kruskal-Wallis result is omnibus only; pairwise post-hoc tests are not included.

## Run Tests

From the backend directory:

```powershell
python -m pytest tests -q
```
