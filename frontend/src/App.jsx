import { lazy, Suspense, useRef, useState } from "react";
import {
  Activity,
  BarChart3,
  Brain,
  Database,
  Download,
  FileSpreadsheet,
  FlaskConical,
  Gauge,
  MessageSquare,
  Send,
  Upload,
} from "lucide-react";
import "./App.css";

const Histogram = lazy(() => import("./Histogram.jsx"));
const GroupComparison = lazy(() => import("./Histogram.jsx").then((module) => ({ default: module.GroupComparison })));

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function getSessionId() {
  let sessionId = sessionStorage.getItem("statcore.sessionId");
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    sessionStorage.setItem("statcore.sessionId", sessionId);
  }
  return sessionId;
}

const pages = [
  { name: "Overview", icon: Gauge },
  { name: "Dataset", icon: Database },
  { name: "Analysis", icon: BarChart3 },
  { name: "Statistical tests", icon: FlaskConical },
  { name: "AI assistant", icon: Brain },
];

const tests = [
  { id: "shapiro", label: "Shapiro-Wilk normality", fields: ["column"] },
  { id: "confidence-interval", label: "95% confidence interval", fields: ["column"] },
  { id: "adf", label: "Augmented Dickey-Fuller", fields: ["column"] },
  { id: "kpss", label: "KPSS stationarity", fields: ["column"] },
  { id: "pearson", label: "Pearson correlation", fields: ["column", "second_column"] },
  { id: "spearman", label: "Spearman rank correlation", fields: ["column", "second_column"] },
  { id: "paired-t-test", label: "Paired t-test", fields: ["column", "second_column"] },
  { id: "wilcoxon", label: "Wilcoxon signed-rank", fields: ["column", "second_column"] },
  { id: "independent-t-test", label: "Independent t-test", fields: ["column", "group_column"] },
  { id: "mann-whitney", label: "Mann-Whitney U", fields: ["column", "group_column"] },
  { id: "anova", label: "One-way ANOVA", fields: ["column", "group_column"] },
  { id: "kruskal", label: "Kruskal-Wallis", fields: ["column", "group_column"] },
  { id: "chi-square", label: "Chi-square association", fields: ["column", "second_column"] },
];

const fieldLabels = {
  column: "Numeric variable",
  second_column: "Second variable",
  group_column: "Group by",
};

async function postFile(path, file, values = {}) {
  const form = new FormData();
  form.append("file", file);
  Object.entries(values).forEach(([key, value]) => form.append(key, value));
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "X-Session-ID": getSessionId() },
    body: form,
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body.detail || body.error || "The request failed.");
  return body;
}

function displayValue(value) {
  if (value === null || value === undefined) return "-";
  if (typeof value === "number") return Number.isFinite(value) ? value.toLocaleString(undefined, { maximumFractionDigits: 4 }) : "-";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function downloadJson(filename, value) {
  const blob = new Blob([JSON.stringify(value, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function ResultTable({ rows }) {
  return (
    <div className="data-table-wrap">
      <table>
        <thead><tr><th>Measure</th><th>Result</th></tr></thead>
        <tbody>
          {Object.entries(rows || {}).map(([key, value]) => (
            <tr key={key}><td>{key}</td><td>{displayValue(value)}</td></tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function CorrelationHeatmap({ matrix }) {
  const columns = Object.keys(matrix || {});
  if (!columns.length) return <p className="muted-copy">No numeric correlations are available.</p>;

  return (
    <div className="data-table-wrap heatmap-wrap">
      <table>
        <thead><tr><th>Variable</th>{columns.map((column) => <th key={column}>{column}</th>)}</tr></thead>
        <tbody>{columns.map((row) => (
          <tr key={row}><th>{row}</th>{columns.map((column) => {
            const value = matrix[row]?.[column];
            const colorStrength = typeof value === "number" ? 0.1 + Math.abs(value) * 0.58 : 0;
            const tint = value >= 0 ? `rgba(0, 207, 234, ${colorStrength})` : `rgba(255, 121, 92, ${colorStrength})`;
            return <td className="correlation-cell" key={`${row}-${column}`} style={{ backgroundColor: tint }} title={`${row} and ${column}: ${displayValue(value)}`}>{displayValue(value)}</td>;
          })}</tr>
        ))}</tbody>
      </table>
    </div>
  );
}

function App() {
  const uploadRef = useRef(null);
  const [page, setPage] = useState("Overview");
  const [file, setFile] = useState(null);
  const [datasetInfo, setDatasetInfo] = useState(null);
  const [profile, setProfile] = useState(null);
  const [histogramColumn, setHistogramColumn] = useState("");
  const [selectedTest, setSelectedTest] = useState(tests[0].id);
  const [testForm, setTestForm] = useState({ column: "", second_column: "", group_column: "" });
  const [testResult, setTestResult] = useState(null);
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [busy, setBusy] = useState(false);
  const [chatBusy, setChatBusy] = useState(false);
  const [error, setError] = useState("");

  const numericColumns = datasetInfo?.numerical_columns || [];
  const categoricalColumns = datasetInfo?.categorical_columns || [];
  const activeTest = tests.find((test) => test.id === selectedTest) || tests[0];

  async function handleUpload(event) {
    const selected = event.target.files?.[0];
    event.target.value = "";
    if (!selected) return;
    if (!selected.name.toLowerCase().endsWith(".csv")) {
      setError("Choose a CSV file to continue.");
      return;
    }

    setBusy(true);
    setError("");
    setProfile(null);
    setTestResult(null);
    setMessages([]);
    try {
      const info = await postFile("/upload", selected);
      setFile(selected);
      setDatasetInfo(info);
      const result = await postFile("/descriptive-statistics", selected);
      setProfile(result);
      setHistogramColumn(info.numerical_columns?.[0] || "");
      setPage("Analysis");
      setTestForm({
        column: info.numerical_columns?.[0] || "",
        second_column: info.numerical_columns?.[1] || info.numerical_columns?.[0] || "",
        group_column: info.categorical_columns?.[0] || "",
      });
    } catch (uploadError) {
      setFile(null);
      setDatasetInfo(null);
      setError(uploadError.message);
    } finally {
      setBusy(false);
    }
  }

  async function refreshProfile() {
    if (!file) return;
    setBusy(true);
    setError("");
    try {
      setProfile(await postFile("/descriptive-statistics", file));
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setBusy(false);
    }
  }

  async function runTest(event) {
    event.preventDefault();
    if (!file) return;
    setBusy(true);
    setError("");
    setTestResult(null);
    try {
      setTestResult(await postFile("/run-test", file, { test: selectedTest, ...testForm }));
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setBusy(false);
    }
  }

  async function sendQuestion(event) {
    event.preventDefault();
    const text = question.trim();
    if (!text || !file || chatBusy) return;
    setQuestion("");
    setMessages((current) => [...current, { role: "user", text }]);
    setChatBusy(true);
    setError("");
    try {
      const response = await fetch(`${API_BASE}/ai/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Session-ID": getSessionId() },
        body: JSON.stringify({ question: text }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail || result.error || "The assistant request failed.");
      const answer = result.Explanation || result.Response || result.Recommendation || result.error || result.Error || JSON.stringify(result, null, 2);
      const detail = result.Result ? JSON.stringify(result.Result, null, 2) : "";
      setMessages((current) => [...current, { role: "assistant", text: typeof answer === "string" ? answer : JSON.stringify(answer), detail }]);
    } catch (requestError) {
      setMessages((current) => [...current, { role: "assistant", text: requestError.message }]);
    } finally {
      setChatBusy(false);
    }
  }

  function updateTestField(field, value) {
    setTestForm((current) => ({ ...current, [field]: value }));
  }

  function renderSelect(field) {
    const options = field === "group_column"
      ? [...categoricalColumns, ...numericColumns]
      : selectedTest === "chi-square"
        ? categoricalColumns
        : numericColumns;
    return (
      <label className="form-field" key={field}>
        <span>{fieldLabels[field]}</span>
        <select value={testForm[field]} onChange={(event) => updateTestField(field, event.target.value)} required>
          <option value="" disabled>Select a column</option>
          {options.map((column) => <option key={column} value={column}>{column}</option>)}
        </select>
      </label>
    );
  }

  const profileNumerical = profile?.numerical?.statistics || {};
  const pageHeading = page === "Overview" ? "Your data, made legible." : page;

  return (
    <div className="app-shell">
      <div className="background-grid" />
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><Activity size={22} /></div>
          <div><h1>STATCORE</h1><span>STATISTICAL WORKSPACE</span></div>
        </div>
        <div className="system-status"><span className="status-dot" /> ANALYSIS ENGINE</div>
        <nav aria-label="Workspace navigation">
          {pages.map(({ name, icon: Icon }) => (
            <button key={name} className={`nav-item ${page === name ? "active" : ""}`} onClick={() => setPage(name)}>
              <Icon size={18} /><span>{name}</span>
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="engine-card"><Brain size={18} /><div><strong>LOCAL AI</strong><span>DATASET-AWARE</span></div></div>
          <div className="version">STATCORE v1.0.0</div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div><p className="eyebrow">STATISTICAL INTELLIGENCE</p><h2>{pageHeading}</h2></div>
          <div className="topbar-right">
            <span className="dataset-chip"><span className={`status-dot ${file ? "" : "idle"}`} />{file ? file.name : "No dataset"}</span>
            <button className="icon-button" title="Upload a CSV dataset" onClick={() => uploadRef.current?.click()}><Upload size={18} /></button>
          </div>
        </header>

        <input ref={uploadRef} className="visually-hidden" type="file" accept=".csv,text/csv" onChange={handleUpload} />
        {error && <div className="notice error-notice" role="alert">{error}<button onClick={() => setError("")} aria-label="Dismiss error">×</button></div>}

        {page === "Overview" && (
          <>
            <section className="hero">
              <div className="hero-content">
                <div className="hero-tag"><Brain size={15} /> STATISTICAL ANALYSIS WORKSPACE</div>
                <h3>Find the signal.<br /><span>Understand the data.</span></h3>
                <p>Profile a dataset, run statistical tests, and ask questions grounded in your results.</p>
                <div className="hero-actions">
                  <button className="upload-button" onClick={() => uploadRef.current?.click()} disabled={busy}><Upload size={17} />{busy ? "LOADING DATA" : "UPLOAD CSV"}</button>
                  {file && <button className="secondary-button" onClick={() => setPage("Analysis")}><BarChart3 size={17} /> OPEN ANALYSIS</button>}
                </div>
              </div>
              <div className="hero-visual" aria-hidden="true"><div className="orb"><div className="orb-core"><BarChart3 size={36} /></div><div className="orb-ring ring-one" /><div className="orb-ring ring-two" /><div className="orb-ring ring-three" /></div></div>
            </section>
            <section className="dataset-panel">
              <div className="panel-header"><div><p className="section-label">CURRENT DATASET</p><h3>{file?.name || "No dataset loaded"}</h3></div><span className="dataset-status">{file ? "READY" : "CSV REQUIRED"}</span></div>
              {file ? <DatasetFacts datasetInfo={datasetInfo} /> : <button className="drop-zone" onClick={() => uploadRef.current?.click()}><FileSpreadsheet size={34} /><strong>SELECT A CSV DATASET</strong><span>Upload a local file to begin analysis</span></button>}
            </section>
            {datasetInfo && <div className="stats-grid">
              <StatCard icon={<Database />} label="ROWS" value={datasetInfo.rows} />
              <StatCard icon={<BarChart3 />} label="VARIABLES" value={datasetInfo.columns} />
              <StatCard icon={<Activity />} label="NUMERIC" value={numericColumns.length} />
              <StatCard icon={<FlaskConical />} label="AVAILABLE TESTS" value={tests.length} />
            </div>}
            <section className="modules">
              <div className="section-heading"><div><p className="section-label">WORKSPACE</p><h3>CHOOSE A STARTING POINT</h3></div></div>
              <div className="module-grid">
                <Module icon={<Database />} title="Dataset" text="Inspect variables, data types, and missingness." onClick={() => setPage("Dataset")} />
                <Module icon={<BarChart3 />} title="Analysis" text="Review descriptive statistics, correlations, and outliers." onClick={() => setPage("Analysis")} disabled={!file} />
                <Module icon={<FlaskConical />} title="Statistical tests" text="Run hypothesis and time-series tests on selected columns." onClick={() => setPage("Statistical tests")} disabled={!file} />
                <Module icon={<MessageSquare />} title="AI assistant" text="Ask questions about this dataset and your results." onClick={() => setPage("AI assistant")} disabled={!file} />
              </div>
            </section>
          </>
        )}

        {page === "Dataset" && (
          <section className="workspace-section">
            <SectionTitle label="DATASET EXPLORER" title="Variables" action={<button className="secondary-button" onClick={() => uploadRef.current?.click()}><Upload size={16} /> REPLACE CSV</button>} />
            {datasetInfo ? <>
              <div className="stats-grid"><StatCard icon={<Database />} label="ROWS" value={datasetInfo.rows} /><StatCard icon={<BarChart3 />} label="COLUMNS" value={datasetInfo.columns} /><StatCard icon={<Activity />} label="NUMERIC" value={numericColumns.length} /><StatCard icon={<FileSpreadsheet />} label="CATEGORICAL" value={categoricalColumns.length} /></div>
              <DatasetFacts datasetInfo={datasetInfo} />
              <div className="data-table-wrap"><table><thead><tr><th>Variable</th><th>Type</th><th>Role</th></tr></thead><tbody>{datasetInfo.column_names.map((column) => <tr key={column}><td>{column}</td><td>{datasetInfo.data_types?.[column] || "unknown"}</td><td>{numericColumns.includes(column) ? "Numeric" : categoricalColumns.includes(column) ? "Categorical" : "Other"}</td></tr>)}</tbody></table></div>
            </> : <EmptyState onUpload={() => uploadRef.current?.click()} />}
          </section>
        )}

        {page === "Analysis" && (
          <section className="workspace-section">
            <SectionTitle label="AUTOMATED PROFILE" title="Descriptive analysis" action={<div className="section-actions"><button className="icon-button" onClick={() => downloadJson(`${file?.name.replace(/\.csv$/i, "") || "dataset"}-profile.json`, profile)} disabled={!profile} title="Download profile as JSON" aria-label="Download profile as JSON"><Download size={17} /></button><button className="secondary-button" onClick={refreshProfile} disabled={!file || busy}><Activity size={16} /> {busy ? "RUNNING" : "REFRESH PROFILE"}</button></div>} />
            {!file ? <EmptyState onUpload={() => uploadRef.current?.click()} /> : !profile ? <p className="muted-copy">{busy ? "Calculating dataset profile..." : "No analysis available yet."}</p> : <>
              <div className="stats-grid"><StatCard icon={<Database />} label="ROWS" value={profile.summary?.Rows} /><StatCard icon={<BarChart3 />} label="VARIABLES" value={profile.summary?.Columns} /><StatCard icon={<Activity />} label="NUMERIC VARIABLES" value={Object.keys(profileNumerical).length} /><StatCard icon={<FlaskConical />} label="OUTLIER FLAGS" value={Object.values(profile.outliers || {}).reduce((total, indices) => total + indices.length, 0)} /></div>
              <section className="result-section"><p className="section-label">NUMERIC VARIABLES</p><h3>DESCRIPTIVE STATISTICS</h3>{Object.keys(profileNumerical).length ? <div className="data-table-wrap"><table><thead><tr><th>Variable</th><th>Count</th><th>Mean</th><th>Std. dev.</th><th>Min</th><th>Median</th><th>Max</th></tr></thead><tbody>{Object.entries(profileNumerical).map(([name, stats]) => <tr key={name}><td>{name}</td><td>{displayValue(stats.count)}</td><td>{displayValue(stats.mean)}</td><td>{displayValue(stats.std)}</td><td>{displayValue(stats.min)}</td><td>{displayValue(stats["50%"] )}</td><td>{displayValue(stats.max)}</td></tr>)}</tbody></table></div> : <p className="muted-copy">No numeric variables were detected.</p>}</section>
              {Object.keys(profile.histograms || {}).length > 0 && <section className="result-section chart-panel"><div className="chart-header"><div><p className="section-label">DISTRIBUTION</p><h3>VALUE FREQUENCY</h3></div><label className="form-field"><span>Variable</span><select value={histogramColumn} onChange={(event) => setHistogramColumn(event.target.value)}>{Object.keys(profile.histograms).map((name) => <option key={name} value={name}>{name}</option>)}</select></label></div><div className="histogram-chart"><Suspense fallback={<p className="muted-copy">Loading chart...</p>}><Histogram data={profile.histograms[histogramColumn] || []} /></Suspense></div></section>}
              <div className="analysis-columns">
                <section className="result-section"><p className="section-label">CATEGORICAL VARIABLES</p><h3>CATEGORY PROFILE</h3><ResultTable rows={profile.categorical} /></section>
                <section className="result-section"><p className="section-label">DATA QUALITY</p><h3>MISSING VALUES</h3><ResultTable rows={Object.fromEntries((datasetInfo?.column_names || []).map((name) => [name, `${displayValue(profile.missing?.["Missing Count"]?.[name])} (${displayValue(profile.missing?.["Missing Percentage"]?.[name])}%)`]))} /></section>
              </div>
              <div className="analysis-columns">
                <section className="result-section"><p className="section-label">ASSOCIATION</p><h3>NUMERIC CORRELATIONS</h3><CorrelationHeatmap matrix={profile.correlation} /></section>
                <section className="result-section"><p className="section-label">DISTRIBUTION CHECK</p><h3>IQR OUTLIER ROWS</h3><ResultTable rows={Object.fromEntries(Object.entries(profile.outliers || {}).map(([name, indices]) => [name, `${indices.length} flagged`]))} /></section>
              </div>
            </>}
          </section>
        )}

        {page === "Statistical tests" && (
          <section className="workspace-section">
            <SectionTitle label="INFERENTIAL STATISTICS" title="Run a test" />
            {!file ? <EmptyState onUpload={() => uploadRef.current?.click()} /> : <>
              <form className="test-form" onSubmit={runTest}>
                <label className="form-field"><span>Statistical test</span><select value={selectedTest} onChange={(event) => { const nextTest = event.target.value; setSelectedTest(nextTest); setTestResult(null); if (nextTest === "chi-square") setTestForm((current) => ({ ...current, column: categoricalColumns[0] || "", second_column: categoricalColumns[1] || "" })); }}>
                  {tests.map((test) => <option key={test.id} value={test.id}>{test.label}</option>)}
                </select></label>
                <div className="test-fields">{activeTest.fields.map(renderSelect)}</div>
                <button className="upload-button" type="submit" disabled={busy || !activeTest.fields.every((field) => testForm[field])}><FlaskConical size={17} />{busy ? "RUNNING TEST" : "RUN TEST"}</button>
              </form>
              {testResult && <section className="test-result"><div className="section-heading"><div><p className="section-label">{testResult.Test}</p><h3>RESULT</h3></div><div className="result-actions"><span>{testResult.Columns?.join(" · ")}</span><button className="icon-button" onClick={() => downloadJson(`${selectedTest}-result.json`, testResult)} title="Download test result as JSON" aria-label="Download test result as JSON"><Download size={17} /></button></div></div><ResultTable rows={testResult.Result} />{testResult["Group summaries"]?.length > 1 && <div className="group-comparison"><h4>GROUP MEANS AND MEDIANS</h4><div className="group-chart"><Suspense fallback={<p className="muted-copy">Loading chart...</p>}><GroupComparison data={testResult["Group summaries"]} /></Suspense></div><p className="muted-copy">Descriptive group summaries; these are not pairwise post-hoc tests.</p></div>}{testResult["Sample sizes"]?.length > 0 && <div className="sample-sizes"><strong>Sample sizes</strong>{testResult["Sample sizes"].map((item, index) => <span key={`${item.group || item.column || item.observations}-${index}`}>{item.group ? `${item.group}: n = ${item.n}` : `${item.column || "Observations"}: n = ${item.n ?? item["complete pairs"] ?? item.observations}`}</span>)}</div>}{testResult.Diagnostics?.map((diagnostic) => <p className="diagnostic-note" key={diagnostic}>{diagnostic}</p>)}{testResult["Assumptions and limitations"]?.length > 0 && <div className="assumptions"><strong>Assumptions and limitations</strong><ul>{testResult["Assumptions and limitations"].map((item) => <li key={item}>{item}</li>)}</ul></div>}{typeof testResult.Result?.["P-Value"] === "number" && <p className="result-note">P-value: {displayValue(testResult.Result["P-Value"])} · Significance threshold: {displayValue(testResult["Significance level"])}</p>}</section>}
            </>}
          </section>
        )}

        {page === "AI assistant" && (
          <section className="workspace-section assistant-section">
            <SectionTitle label="DATASET-AWARE CHAT" title="Ask the assistant" />
            {!file ? <EmptyState onUpload={() => uploadRef.current?.click()} /> : <>
              <div className="chat-history" aria-live="polite">
                {messages.length === 0 && <div className="chat-empty"><Brain size={24} /><p>Ask for a summary, a test recommendation, or an interpretation of a statistical result.</p></div>}
                {messages.map((message, index) => <article className={`chat-message ${message.role}`} key={`${message.role}-${index}`}><span>{message.role === "user" ? "YOU" : "STATCORE"}</span><p>{message.text}</p>{message.detail && <pre>{message.detail}</pre>}</article>)}
                {chatBusy && <p className="muted-copy">Thinking about your dataset...</p>}
              </div>
              <form className="chat-form" onSubmit={sendQuestion}><input value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask about your uploaded dataset" aria-label="Your question" /><button className="icon-button" type="submit" disabled={chatBusy || !question.trim()} title="Send question"><Send size={18} /></button></form>
            </>}
          </section>
        )}
      </main>
      <nav className="mobile-nav" aria-label="Workspace navigation">
        {pages.map(({ name, icon: Icon }) => <button key={name} className={page === name ? "active" : ""} onClick={() => setPage(name)} aria-label={name}><Icon size={19} /></button>)}
      </nav>
    </div>
  );
}

function DatasetFacts({ datasetInfo }) {
  return <div className="file-loaded"><FileSpreadsheet size={28} /><div><strong>{datasetInfo.filename}</strong><span>{datasetInfo.rows} rows × {datasetInfo.columns} columns</span><span>{datasetInfo.column_names.join(", ")}</span></div><span className="loaded-badge">LOADED</span></div>;
}

function SectionTitle({ label, title, action }) {
  return <div className="section-title"><div><p className="section-label">{label}</p><h3>{title}</h3></div>{action}</div>;
}

function StatCard({ icon, label, value }) {
  return <div className="stat-card"><div className="stat-icon">{icon}</div><div><span>{label}</span><strong>{value ?? "-"}</strong></div></div>;
}

function Module({ icon, title, text, onClick, disabled }) {
  return <button className="module-card" onClick={onClick} disabled={disabled}><span className="module-icon">{icon}</span><div className="module-content"><h4>{title}</h4><p>{text}</p></div><span className="module-arrow">→</span></button>;
}

function EmptyState({ onUpload }) {
  return <div className="empty-state"><FileSpreadsheet size={32} /><h3>Upload a dataset to continue</h3><p>CSV files are profiled locally by the STATCORE backend.</p><button className="upload-button" onClick={onUpload}><Upload size={16} /> CHOOSE CSV</button></div>;
}

export default App;