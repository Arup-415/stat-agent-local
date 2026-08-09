import { useState } from "react";
import {
  Activity,
  BarChart3,
  BrainCircuit,
  Database,
  FileUp,
  Gauge,
  Menu,
  MessageSquare,
  Moon,
  Play,
  Send,
  ShieldCheck,
  Sparkles,
  Upload,
  X,
  Zap,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [dataset, setDataset] = useState(null);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [thinking, setThinking] = useState(false);
  const [dragging, setDragging] = useState(false);

  const handleFile = (selectedFile) => {
    if (!selectedFile) return;

    if (!selectedFile.name.toLowerCase().endsWith(".csv")) {
      alert("Please select a CSV file.");
      return;
    }

    setFile(selectedFile);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragging(false);

    const droppedFile = event.dataTransfer.files?.[0];
    handleFile(droppedFile);
  };

  const uploadDataset = async () => {
    if (!file) return;

    setUploading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok || data.error) {
        throw new Error(data.error || "Upload failed.");
      }

      setDataset(data);

      setMessages([
        {
          role: "assistant",
          text: `Dataset "${data.filename}" loaded successfully. I found ${data.rows.toLocaleString()} rows across ${data.columns} columns. What would you like me to analyze?`,
        },
      ]);
    } catch (error) {
      alert(error.message);
    } finally {
      setUploading(false);
    }
  };

  const sendQuestion = async () => {
    const trimmed = question.trim();

    if (!trimmed || thinking) return;

    if (!dataset) {
      alert("Upload a CSV dataset first.");
      return;
    }

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        text: trimmed,
      },
    ]);

    setQuestion("");
    setThinking(true);

    try {
      const response = await fetch(`${API_URL}/ai/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: trimmed,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Request failed.");
      }

      const answer =
        data.Explanation ||
        data.Response ||
        data.message ||
        JSON.stringify(data, null, 2);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          text: answer,
          data,
        },
      ]);
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          text: `Connection error: ${error.message}`,
        },
      ]);
    } finally {
      setThinking(false);
    }
  };

  const quickActions = [
    {
      icon: BarChart3,
      title: "Descriptive Analysis",
      question: "Give me the descriptive statistics of my dataset",
    },
    {
      icon: Activity,
      title: "Correlation",
      question: "Analyze the correlations in my dataset",
    },
    {
      icon: ShieldCheck,
      title: "Normality",
      question: "Check the normality of my numerical variables",
    },
    {
      icon: BrainCircuit,
      title: "Full Analysis",
      question: "Analyze my dataset completely",
    },
  ];

  return (
    <div className="min-h-screen overflow-hidden bg-[#05060a] text-slate-100">
      {/* Ambient cinematic lighting */}
      <div className="pointer-events-none fixed inset-0">
        <div className="absolute left-[-10%] top-[-15%] h-[500px] w-[500px] rounded-full bg-cyan-500/10 blur-[140px]" />
        <div className="absolute right-[-10%] top-[5%] h-[600px] w-[600px] rounded-full bg-violet-600/10 blur-[160px]" />
        <div className="absolute bottom-[-20%] left-[30%] h-[500px] w-[700px] rounded-full bg-blue-600/5 blur-[180px]" />
      </div>

      <div className="relative flex min-h-screen">
        {/* Sidebar */}
        <AnimatePresence>
          {sidebarOpen && (
            <motion.aside
              initial={{ x: -280, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -280, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="fixed z-30 flex h-screen w-[270px] flex-col border-r border-white/10 bg-black/40 p-5 backdrop-blur-2xl lg:relative"
            >
              <div className="mb-10 flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-cyan-400/30 bg-cyan-400/10 shadow-[0_0_30px_rgba(34,211,238,0.15)]">
                  <BrainCircuit className="h-6 w-6 text-cyan-300" />
                </div>

                <div>
                  <div className="text-sm font-bold tracking-[0.2em] text-white">
                    STAT<span className="text-cyan-300">CORE</span>
                  </div>
                  <div className="text-[10px] uppercase tracking-[0.25em] text-slate-500">
                    AI Statistics Engine
                  </div>
                </div>
              </div>

              <nav className="space-y-2">
                <SidebarItem
                  icon={Gauge}
                  label="Command Center"
                  active
                />
                <SidebarItem icon={Database} label="Dataset" />
                <SidebarItem icon={BarChart3} label="Analytics" />
                <SidebarItem icon={MessageSquare} label="AI Assistant" />
              </nav>

              <div className="mt-auto">
                <div className="rounded-2xl border border-cyan-400/10 bg-white/[0.03] p-4">
                  <div className="mb-3 flex items-center gap-2">
                    <div className="h-2 w-2 animate-pulse rounded-full bg-emerald-400 shadow-[0_0_12px_#34d399]" />
                    <span className="text-xs font-medium text-emerald-300">
                      SYSTEM ONLINE
                    </span>
                  </div>

                  <div className="space-y-2 text-[11px] text-slate-500">
                    <div className="flex justify-between">
                      <span>API</span>
                      <span className="text-slate-300">CONNECTED</span>
                    </div>
                    <div className="flex justify-between">
                      <span>ENGINE</span>
                      <span className="text-slate-300">READY</span>
                    </div>
                    <div className="flex justify-between">
                      <span>LLM</span>
                      <span className="text-slate-300">ONLINE</span>
                    </div>
                  </div>
                </div>
              </div>
            </motion.aside>
          )}
        </AnimatePresence>

        {/* Main */}
        <main className="min-w-0 flex-1">
          {/* Top bar */}
          <header className="flex h-20 items-center justify-between border-b border-white/10 bg-black/20 px-5 backdrop-blur-xl lg:px-8">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen((value) => !value)}
                className="rounded-lg border border-white/10 bg-white/5 p-2 text-slate-400 transition hover:border-cyan-400/30 hover:text-cyan-300"
              >
                {sidebarOpen ? (
                  <X className="h-5 w-5" />
                ) : (
                  <Menu className="h-5 w-5" />
                )}
              </button>

              <div>
                <div className="text-xs uppercase tracking-[0.35em] text-slate-500">
                  Operations
                </div>
                <h1 className="text-lg font-semibold text-white">
                  Statistical Command Center
                </h1>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="hidden items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] px-3 py-2 text-xs text-slate-400 sm:flex">
                <Moon className="h-4 w-4" />
                NIGHT MODE
              </div>

              <div className="flex h-9 w-9 items-center justify-center rounded-full border border-violet-400/20 bg-violet-400/10">
                <Sparkles className="h-4 w-4 text-violet-300" />
              </div>
            </div>
          </header>

          <div className="mx-auto max-w-[1500px] p-5 lg:p-8">
            {/* Hero */}
            <section className="mb-8">
              <div className="mb-3 flex items-center gap-2 text-xs uppercase tracking-[0.35em] text-cyan-300">
                <Zap className="h-3.5 w-3.5" />
                Neural Statistics Interface
              </div>

              <h2 className="max-w-4xl text-4xl font-black tracking-tight text-white md:text-6xl">
                Turn raw data into
                <span className="block bg-gradient-to-r from-cyan-300 via-blue-400 to-violet-400 bg-clip-text text-transparent">
                  intelligence.
                </span>
              </h2>

              <p className="mt-4 max-w-2xl text-sm leading-6 text-slate-400">
                Upload your dataset. Ask statistical questions. Let the
                analysis engine compute, interpret, and explain the results.
              </p>
            </section>

            {/* Stats */}
            <section className="mb-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <StatCard
                label="DATASET"
                value={dataset ? dataset.filename : "NO DATA"}
                subtext={
                  dataset
                    ? `${dataset.rows.toLocaleString()} rows`
                    : "Awaiting upload"
                }
                icon={Database}
              />

              <StatCard
                label="VARIABLES"
                value={dataset ? dataset.columns : "--"}
                subtext="Detected columns"
                icon={BarChart3}
              />

              <StatCard
                label="ANALYSIS ENGINE"
                value="READY"
                subtext="Statistical core"
                icon={Activity}
              />

              <StatCard
                label="AI STATUS"
                value="ONLINE"
                subtext="Assistant available"
                icon={BrainCircuit}
              />
            </section>

            <div className="grid gap-6 xl:grid-cols-[1fr_1.2fr]">
              {/* Upload */}
              <section className="rounded-3xl border border-white/10 bg-white/[0.035] p-5 shadow-2xl backdrop-blur-xl lg:p-6">
                <SectionHeader
                  icon={Upload}
                  title="Dataset Uplink"
                  subtitle="Load a CSV into the analysis engine"
                />

                <div
                  onDragOver={(event) => {
                    event.preventDefault();
                    setDragging(true);
                  }}
                  onDragLeave={() => setDragging(false)}
                  onDrop={handleDrop}
                  className={`mt-6 rounded-2xl border border-dashed p-8 text-center transition ${
                    dragging
                      ? "border-cyan-300 bg-cyan-400/10"
                      : "border-white/15 bg-black/20 hover:border-cyan-400/30"
                  }`}
                >
                  <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl border border-cyan-400/20 bg-cyan-400/10">
                    <FileUp className="h-7 w-7 text-cyan-300" />
                  </div>

                  <h3 className="font-semibold text-white">
                    Drop your CSV here
                  </h3>

                  <p className="mt-2 text-xs text-slate-500">
                    or select a file from your computer
                  </p>

                  <label className="mt-5 inline-flex cursor-pointer items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-5 py-3 text-sm font-medium text-slate-200 transition hover:border-cyan-400/30 hover:bg-cyan-400/10 hover:text-cyan-200">
                    <FileUp className="h-4 w-4" />
                    Choose CSV
                    <input
                      type="file"
                      accept=".csv"
                      className="hidden"
                      onChange={(event) =>
                        handleFile(event.target.files?.[0])
                      }
                    />
                  </label>
                </div>

                {file && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-4 rounded-xl border border-cyan-400/20 bg-cyan-400/5 p-4"
                  >
                    <div className="flex items-center justify-between">
                      <div className="min-w-0">
                        <div className="truncate text-sm font-medium text-white">
                          {file.name}
                        </div>
                        <div className="mt-1 text-xs text-slate-500">
                          {(file.size / 1024).toFixed(1)} KB
                        </div>
                      </div>

                      <button
                        onClick={uploadDataset}
                        disabled={uploading}
                        className="ml-4 flex shrink-0 items-center gap-2 rounded-lg bg-cyan-400 px-4 py-2 text-xs font-bold text-black transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        <Play className="h-3.5 w-3.5" />
                        {uploading ? "LOADING..." : "INITIALIZE"}
                      </button>
                    </div>
                  </motion.div>
                )}

                {dataset && (
                  <div className="mt-4 grid grid-cols-2 gap-3">
                    <MiniMetric
                      label="ROWS"
                      value={dataset.rows.toLocaleString()}
                    />
                    <MiniMetric
                      label="COLUMNS"
                      value={dataset.columns}
                    />
                  </div>
                )}
              </section>

              {/* AI */}
              <section className="flex min-h-[520px] flex-col rounded-3xl border border-violet-400/10 bg-white/[0.035] p-5 shadow-2xl backdrop-blur-xl lg:p-6">
                <SectionHeader
                  icon={BrainCircuit}
                  title="AI Analysis Core"
                  subtitle="Conversational statistical intelligence"
                />

                <div className="mt-5 flex-1 overflow-y-auto rounded-2xl border border-white/5 bg-black/20 p-4">
                  {!dataset && messages.length === 0 ? (
                    <div className="flex h-full min-h-[300px] flex-col items-center justify-center text-center">
                      <div className="mb-5 flex h-20 w-20 items-center justify-center rounded-3xl border border-violet-400/20 bg-violet-400/10">
                        <BrainCircuit className="h-9 w-9 text-violet-300" />
                      </div>

                      <h3 className="text-lg font-semibold text-white">
                        Awaiting dataset
                      </h3>

                      <p className="mt-2 max-w-sm text-xs leading-5 text-slate-500">
                        Upload a CSV to activate the statistical AI engine.
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {messages.map((message, index) => (
                        <ChatMessage
                          key={index}
                          message={message}
                        />
                      ))}

                      {thinking && (
                        <div className="flex items-center gap-3 text-xs text-slate-500">
                          <div className="flex gap-1">
                            <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-cyan-300" />
                            <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-cyan-300 [animation-delay:100ms]" />
                            <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-cyan-300 [animation-delay:200ms]" />
                          </div>
                          ANALYZING DATA...
                        </div>
                      )}
                    </div>
                  )}
                </div>

                <div className="mt-4 flex flex-wrap gap-2">
                  {quickActions.map((action) => {
                    const Icon = action.icon;

                    return (
                      <button
                        key={action.title}
                        onClick={() => setQuestion(action.question)}
                        disabled={!dataset}
                        className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-[11px] text-slate-400 transition hover:border-cyan-400/20 hover:bg-cyan-400/5 hover:text-cyan-200 disabled:cursor-not-allowed disabled:opacity-30"
                      >
                        <Icon className="h-3.5 w-3.5" />
                        {action.title}
                      </button>
                    );
                  })}
                </div>

                <div className="mt-3 flex gap-2 rounded-xl border border-white/10 bg-black/30 p-2 focus-within:border-cyan-400/30">
                  <input
                    value={question}
                    onChange={(event) => setQuestion(event.target.value)}
                    onKeyDown={(event) => {
                      if (event.key === "Enter") sendQuestion();
                    }}
                    disabled={!dataset || thinking}
                    placeholder={
                      dataset
                        ? "Ask your statistical question..."
                        : "Upload a dataset first..."
                    }
                    className="min-w-0 flex-1 bg-transparent px-3 text-sm text-white outline-none placeholder:text-slate-600 disabled:cursor-not-allowed"
                  />

                  <button
                    onClick={sendQuestion}
                    disabled={!dataset || !question.trim() || thinking}
                    className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-cyan-400 text-black transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-30"
                  >
                    <Send className="h-4 w-4" />
                  </button>
                </div>
              </section>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

function SidebarItem({ icon: Icon, label, active }) {
  return (
    <button
      className={`flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm transition ${
        active
          ? "border border-cyan-400/10 bg-cyan-400/10 text-cyan-200"
          : "text-slate-500 hover:bg-white/5 hover:text-slate-200"
      }`}
    >
      <Icon className="h-4 w-4" />
      {label}
    </button>
  );
}

function SectionHeader({ icon: Icon, title, subtitle }) {
  return (
    <div className="flex items-center gap-3">
      <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/5">
        <Icon className="h-5 w-5 text-cyan-300" />
      </div>

      <div>
        <h3 className="font-semibold text-white">{title}</h3>
        <p className="text-[11px] text-slate-500">{subtitle}</p>
      </div>
    </div>
  );
}

function StatCard({ label, value, subtext, icon: Icon }) {
  return (
    <motion.div
      whileHover={{ y: -3 }}
      className="rounded-2xl border border-white/10 bg-white/[0.035] p-4 backdrop-blur-xl"
    >
      <div className="mb-5 flex items-center justify-between">
        <span className="text-[10px] font-bold tracking-[0.25em] text-slate-600">
          {label}
        </span>

        <Icon className="h-4 w-4 text-cyan-400/70" />
      </div>

      <div className="truncate text-lg font-bold text-white">{value}</div>

      <div className="mt-1 truncate text-[11px] text-slate-500">
        {subtext}
      </div>
    </motion.div>
  );
}

function MiniMetric({ label, value }) {
  return (
    <div className="rounded-xl border border-white/5 bg-black/20 p-3">
      <div className="text-[9px] tracking-[0.2em] text-slate-600">
        {label}
      </div>
      <div className="mt-1 text-sm font-bold text-slate-200">{value}</div>
    </div>
  );
}

function ChatMessage({ message }) {
  const user = message.role === "user";

  return (
    <div className={`flex ${user ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-6 ${
          user
            ? "border border-cyan-400/20 bg-cyan-400/10 text-cyan-50"
            : "border border-white/5 bg-white/[0.04] text-slate-300"
        }`}
      >
        {!user && (
          <div className="mb-2 flex items-center gap-2 text-[9px] font-bold tracking-[0.2em] text-violet-300">
            <Sparkles className="h-3 w-3" />
            STATCORE AI
          </div>
        )}

        <div className="whitespace-pre-wrap">{message.text}</div>
      </div>
    </div>
  );
}

export default App;