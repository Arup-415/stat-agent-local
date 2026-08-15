import { useState } from "react";
import {
  Activity,
  BarChart3,
  Brain,
  Database,
  FileSpreadsheet,
  FlaskConical,
  Gauge,
  MessageSquare,
  Upload,
  Zap,
} from "lucide-react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [active, setActive] = useState("Dashboard");
  const [datasetInfo, setDatasetInfo] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState("dashboard");

  const menu = [
    { name: "Dashboard", icon: Gauge },
    { name: "Dataset", icon: Database },
    { name: "Descriptive", icon: BarChart3 },
    { name: "Tests", icon: FlaskConical },
    { name: "AI Assistant", icon: Brain },
  ];

const handleFile = async (event) => {
  const selected = event.target.files?.[0];

  if (!selected) return;

  if (!selected.name.toLowerCase().endsWith(".csv")) {
    alert("Please upload a CSV file.");
    return;
  }

  setFile(selected);

  const formData = new FormData();
  formData.append("file", selected);

  try {
    const response = await fetch("http://127.0.0.1:8000/upload", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`);
    }

    const data = await response.json();

    console.log("Backend upload response:", data);

    // Store dataset information
    setDatasetInfo(data);

    alert(
      `Dataset loaded successfully!\n\nRows: ${data.rows}\nColumns: ${data.columns}`
    );

  } catch (error) {
    console.error("Upload error:", error);

    alert(
      "Could not connect to STATCORE backend.\n\nMake sure FastAPI is running on port 8000."
    );
  }
};

const handleDescriptiveAnalysis = async () => {
  if (!file) {
    alert("Please upload a CSV dataset first.");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/descriptive-statistics",
      {
        method: "POST",
        body: formData,
      }
    );

    if (!response.ok) {
      throw new Error(`Analysis failed: ${response.status}`);
    }

    const data = await response.json();

    console.log("Descriptive analysis:", data);

    alert("Descriptive analysis completed successfully!");

  } catch (error) {
    console.error("Descriptive analysis error:", error);

    alert(
      "Could not perform descriptive analysis.\n\nMake sure FastAPI is running."
    );
  }
};



const runDescriptiveAnalysis = async () => {
  if (!file) {
    alert("Please upload a dataset first.");
    return;
  }

  try {
    setAnalysisLoading(true);
    setCurrentPage("descriptive");

    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(
      "http://127.0.0.1:8000/descriptive-statistics",
      {
        method: "POST",
        body: formData,
      }
    );

    if (!response.ok) {
      throw new Error(`Analysis failed: ${response.status}`);
    }

    const data = await response.json();

    console.log("Descriptive Analysis:", data);

    setAnalysisResult(data);

  } catch (error) {
    console.error("Analysis error:", error);
    alert("Analysis failed.");
  } finally {
    setAnalysisLoading(false);
  }
};

const DescriptivePage = () => {
  return (
    <main className="main-content">
      <div className="analysis-page">

        <button
          className="back-button"
          onClick={() => setCurrentPage("dashboard")}
        >
          ← BACK TO DASHBOARD
        </button>

        <div className="analysis-header">
          <p className="section-label">
            STATISTICAL ANALYSIS
          </p>

          <h2>DESCRIPTIVE ANALYSIS</h2>

          <p>
            {file ? file.name : "No dataset loaded"}
          </p>
        </div>

        {analysisLoading ? (
          <div className="analysis-loading">
            <Brain size={40} />

            <h3>RUNNING ANALYSIS</h3>

            <p>
              STATCORE is analyzing your dataset...
            </p>
          </div>
       ) : analysisResult ? (
  <div className="analysis-results">

    {/* DATASET OVERVIEW */}
    <section className="result-section">
      <p className="section-label">
        DATASET
      </p>

      <h3>OVERVIEW</h3>

      <div className="result-cards">

        <div className="result-card">
          <span>ROWS</span>
          <strong>
            {datasetInfo?.rows ?? "—"}
          </strong>
        </div>

        <div className="result-card">
          <span>VARIABLES</span>
          <strong>
            {datasetInfo?.columns ?? "—"}
          </strong>
        </div>

        <div className="result-card">
          <span>NUMERICAL</span>
          <strong>
            {analysisResult.statistics &&
            Object.keys(analysisResult.statistics).length > 0
              ? Object.keys(analysisResult.statistics).length
              : "0"}
          </strong>
        </div>

      </div>
    </section>


    {/* NUMERICAL STATISTICS */}
    <section className="result-section">
      <p className="section-label">
        NUMERICAL DATA
      </p>

      <h3>DESCRIPTIVE STATISTICS</h3>

      {analysisResult.available &&
      Object.keys(analysisResult.statistics).length > 0 ? (

        <div className="statistics-table">
          <table>
            <thead>
              <tr>
                <th>VARIABLE</th>
                <th>COUNT</th>
                <th>MEAN</th>
                <th>STD DEV</th>
                <th>MIN</th>
                <th>MEDIAN</th>
                <th>MAX</th>
              </tr>
            </thead>

            <tbody>
              {Object.entries(
                analysisResult.statistics
              ).map(([variable, stats]) => (
                <tr key={variable}>
                  <td>{variable}</td>
                  <td>{stats.count ?? "—"}</td>
                  <td>
                    {stats.mean !== undefined
                      ? Number(stats.mean).toFixed(3)
                      : "—"}
                  </td>
                  <td>
                    {stats.std !== undefined
                      ? Number(stats.std).toFixed(3)
                      : "—"}
                  </td>
                  <td>{stats.min ?? "—"}</td>
                  <td>
                    {stats["50%"] !== undefined
                      ? Number(stats["50%"]).toFixed(3)
                      : "—"}
                  </td>
                  <td>{stats.max ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

      ) : (

        <div className="no-data-card">
          <Brain size={32} />

          <h4>NO NUMERICAL VARIABLES DETECTED</h4>

          <p>
            This dataset contains categorical data only.
            Numerical statistics such as mean, median,
            variance and standard deviation are not
            applicable.
          </p>
        </div>

      )}
    </section>


    {/* CATEGORICAL DATA */}
    <section className="result-section">
      <p className="section-label">
        CATEGORICAL DATA
      </p>

      <h3>CATEGORY SUMMARY</h3>

      <div className="no-data-card">
        <p>
          Categorical analysis will be displayed here.
        </p>
      </div>
    </section>


    {/* DATA QUALITY */}
    <section className="result-section">
      <p className="section-label">
        DATA QUALITY
      </p>

      <h3>MISSING VALUES</h3>

      <div className="no-data-card">
        <p>
          Missing-value analysis will be displayed here.
        </p>
      </div>
    </section>


    {/* AI INTERPRETATION */}
    <section className="result-section">
      <p className="section-label">
        AI INTERPRETATION
      </p>

      <h3>AI REPORT</h3>

      <div className="ai-report">
        <p>
          AI interpretation will be displayed here.
        </p>
      </div>
    </section>

  </div>
        ) : (
          <div className="analysis-loading">
            <h3>NO RESULT YET</h3>

            <p>
              Run the descriptive analysis to see the results.
            </p>
          </div>
        )}

      </div>
    </main>
  );
};

if (currentPage === "descriptive") {
  return (
    <div className="app-shell">
      <DescriptivePage />
    </div>
  );
}
  return (
    <div className="app-shell">
      <div className="background-grid" />
      <div className="glow glow-one" />
      <div className="glow glow-two" />

      {/* SIDEBAR */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <Activity size={22} />
          </div>

          <div>
            <h1>STATCORE</h1>
            <span>AI ANALYTICS ENGINE</span>
          </div>
        </div>

        <div className="system-status">
          <span className="status-dot" />
          SYSTEM ONLINE
        </div>

        <nav>
          {menu.map(({ name, icon: Icon }) => (
            <button
              key={name}
              className={`nav-item ${active === name ? "active" : ""}`}
              onClick={() => setActive(name)}
            >
              <Icon size={18} />
              <span>{name}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="engine-card">
            <div className="engine-icon">
              <Zap size={18} />
            </div>

            <div>
              <strong>AI ENGINE</strong>
              <span>READY</span>
            </div>
          </div>

          <div className="version">
            STATCORE v1.0.0
          </div>
        </div>
      </aside>

      {/* MAIN */}
      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">STATISTICAL INTELLIGENCE SYSTEM</p>
            <h2>{active}</h2>
          </div>

          <div className="topbar-right">
            <div className="live-indicator">
              <span />
              LIVE
            </div>

            <div className="avatar">SC</div>
          </div>
        </header>

        {/* HERO */}
        <section className="hero">
          <div className="hero-content">
            <div className="hero-tag">
              <Brain size={15} />
              AI-POWERED STATISTICS
            </div>

            <h3>
              TURN DATA INTO
              <br />
              <span>INTELLIGENCE.</span>
            </h3>

            <p>
              Upload your dataset and let STATCORE analyze,
              visualize and explain your data.
            </p>

            <div className="hero-actions">
              <label className="upload-button">
                <Upload size={18} />
                UPLOAD DATASET
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFile}
                />
              </label>

              <button className="secondary-button">
                <MessageSquare size={18} />
                ASK AI
              </button>
            </div>
          </div>

          <div className="hero-visual">
            <div className="orb">
              <div className="orb-core">
                <Brain size={42} />
              </div>

              <div className="orb-ring ring-one" />
              <div className="orb-ring ring-two" />
              <div className="orb-ring ring-three" />
            </div>
          </div>
        </section>

        {/* DATASET STATUS */}
        <section className="dataset-panel">
          <div className="panel-header">
            <div>
              <p className="section-label">ACTIVE DATASET</p>

              <h3>
                {file ? file.name : "NO DATASET LOADED"}
              </h3>

             {datasetInfo && (
               <p className="dataset-meta">
                {datasetInfo.rows} rows · {datasetInfo.columns} variables
              </p>
          )} 
            </div>

            <div className="dataset-status">
              <span className={file ? "status-dot" : "status-dot idle"} />
              {file ? "READY FOR ANALYSIS" : "WAITING FOR DATA"}
            </div>
          </div>

          {!file ? (
            <label className="drop-zone">
              <input
                type="file"
                accept=".csv"
                onChange={handleFile}
              />

              <FileSpreadsheet size={38} />

              <strong>DROP CSV DATASET HERE</strong>

              <span>
                or click to browse your computer
              </span>
            </label>
          ) : (
           <div className="file-loaded">
  <FileSpreadsheet size={32} />

  <div>
    <strong>{file.name}</strong>

    <span>
      {datasetInfo
        ? `${datasetInfo.rows} rows × ${datasetInfo.columns} columns`
        : `${(file.size / 1024).toFixed(1)} KB`}
    </span>

    {datasetInfo && (
      <span>
        Columns: {datasetInfo.column_names.join(", ")}
      </span>
    )}
  </div>

  <div className="loaded-badge">
    LOADED
  </div>
</div>
          )}
        </section>

       {/* STAT CARDS */}

<StatCard
  icon={<Database />}
  label="ROWS"
  value={datasetInfo ? datasetInfo.rows : "0"}
/>

<StatCard
  icon={<BarChart3 />}
  label="VARIABLES"
  value={datasetInfo ? datasetInfo.columns : "0"}
/>

<StatCard
  icon={<Activity />}
  label="ANALYSES"
  value="12+"
/>

<StatCard
  icon={<Brain />}
  label="AI STATUS"
  value="READY"
/>
        {/* ANALYSIS MODULES */}
        <section className="modules">
          <div className="section-heading">
            <div>
              <p className="section-label">ANALYSIS CORE</p>
              <h3>STATISTICAL MODULES</h3>
            </div>

            <span>AVAILABLE</span>
          </div>

          <div className="module-grid">
            <Module
              number="01"
              title="DESCRIPTIVE ANALYSIS"
              description="Mean, median, variance, standard deviation and distribution statistics."
              onClick={runDescriptiveAnalysis}
            />

            <Module
              number="02"
              title="CORRELATION"
              description="Pearson and Spearman relationships between numerical variables."
            />

            <Module
              number="03"
              title="NORMALITY"
              description="Shapiro-Wilk testing and distribution diagnostics."
            />

            <Module
              number="04"
              title="TIME SERIES"
              description="ADF and KPSS stationarity analysis."
            />

            <Module
              number="05"
              title="HYPOTHESIS TESTING"
              description="T-tests, ANOVA and non-parametric statistical tests."
            />

            <Module
              number="06"
              title="AI ANALYSIS"
              description="Let the AI interpret your statistical results."
            />
          </div>
        </section>
        {analysisLoading && (
  <div className="dataset-panel">
    <h3>Running Analysis...</h3>
  </div>
)}

{analysisResult && (
  <div className="dataset-panel">
    <h3>Descriptive Statistics</h3>

    <pre
      style={{
        whiteSpace: "pre-wrap",
        overflowX: "auto",
      }}
    >
      {JSON.stringify(analysisResult, null, 2)}
    </pre>
  </div>
)}
      </main>
    </div>
  );
}

function StatCard({ icon, label, value }) {
  return (
    <div className="stat-card">
      <div className="stat-icon">{icon}</div>

      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </div>
  );
}

function Module({ number, title, description, onClick }) {
  return (
    <div className="module" onClick={onClick}>
      <div className="module-number">
        {number}
      </div>

      <div className="module-content">
        <h4>{title}</h4>
        <p>{description}</p>
      </div>

      <div className="module-arrow">
        →
      </div>
    </div>
  );
}

export default App;