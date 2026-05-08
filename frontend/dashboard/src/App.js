import { useEffect, useMemo, useState } from 'react';
import './App.css';
import DetailsPage from './pages/DetailsPage';
import HistoryPage from './pages/HistoryPage';
import OverviewPage from './pages/OverviewPage';
import RunnerPage from './pages/RunnerPage';

const DEFAULT_API_URL = 'http://localhost:8000';
const DEFAULT_PROBLEM = '2+2*3';
const DEFAULT_THEME = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
const STORAGE_KEYS = {
  settings: 'agent-benchmark-settings',
  history: 'agent-benchmark-history',
  theme: 'agent-benchmark-theme',
};

const NAV_ITEMS = [
  { id: 'overview', label: 'Home / Overview' },
  { id: 'runner', label: 'Benchmark Runner' },
  { id: 'history', label: 'History / Results' },
  { id: 'details', label: 'Agent Details' },
];

function loadJson(key, fallback) {
  try {
    const storedValue = localStorage.getItem(key);
    return storedValue ? JSON.parse(storedValue) : fallback;
  } catch {
    return fallback;
  }
}

function formatLatency(latencySeconds) {
  return `${(latencySeconds * 1000).toFixed(2)} ms`;
}

function formatTimestamp(timestamp) {
  return new Date(timestamp).toLocaleString();
}

function getAgentRows(results) {
  return Object.entries(results ?? {}).map(([agentName, metrics]) => ({
    agentName,
    answer: metrics.answer,
    tokens: metrics.tokens,
    latency: metrics.latency,
  }));
}

function App() {
  const [activePage, setActivePage] = useState('overview');
  const [apiUrl, setApiUrl] = useState(DEFAULT_API_URL);
  const [problem, setProblem] = useState(DEFAULT_PROBLEM);
  const [theme, setTheme] = useState(DEFAULT_THEME);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);
  const [showSettingsModal, setShowSettingsModal] = useState(false);

  useEffect(() => {
    const settings = loadJson(STORAGE_KEYS.settings, null);
    const savedHistory = loadJson(STORAGE_KEYS.history, []);

    if (settings?.apiUrl) {
      setApiUrl(settings.apiUrl);
    }

    if (settings?.problem) {
      setProblem(settings.problem);
    }

    const savedTheme = loadJson(STORAGE_KEYS.theme, null);
    if (savedTheme === 'light' || savedTheme === 'dark') {
      setTheme(savedTheme);
    }

    setHistory(savedHistory);
    if (savedHistory.length > 0) {
      setResults(savedHistory[0]);
    }
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem(STORAGE_KEYS.theme, JSON.stringify(theme));
  }, [theme]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.settings, JSON.stringify({ apiUrl, problem }));
  }, [apiUrl, problem]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.history, JSON.stringify(history));
  }, [history]);

  const runBenchmark = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiUrl}/benchmark?problem=${encodeURIComponent(problem)}`);

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const data = await response.json();
      const benchmarkRun = {
        id: crypto.randomUUID(),
        problem,
        createdAt: new Date().toISOString(),
        results: data,
      };

      setResults(benchmarkRun);
      setHistory((currentHistory) => [benchmarkRun, ...currentHistory].slice(0, 5));
      setActivePage('overview');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const latestRun = results ?? history[0] ?? null;
  const agentRows = useMemo(() => getAgentRows(latestRun?.results), [latestRun]);
  const totalTokens = agentRows.reduce((sum, row) => sum + (Number(row.tokens) || 0), 0);
  const slowestAgent = agentRows.reduce((slowest, row) => {
    if (!slowest || row.latency > slowest.latency) {
      return row;
    }

    return slowest;
  }, null);

  const renderedContent = {
    overview: (
      <OverviewPage
        apiUrl={apiUrl}
        problem={problem}
        agentRows={agentRows}
        totalTokens={totalTokens}
        latestRun={latestRun}
        loading={loading}
        onOpenRunner={() => setActivePage('runner')}
        onRunBenchmark={runBenchmark}
        formatTimestamp={formatTimestamp}
        formatLatency={formatLatency}
      />
    ),
    runner: (
      <RunnerPage
        problem={problem}
        onProblemChange={setProblem}
        apiUrl={apiUrl}
        onApiUrlChange={setApiUrl}
        onRunBenchmark={runBenchmark}
        loading={loading}
        onViewHistory={() => setActivePage('history')}
        error={error}
        latestRun={latestRun}
        agentRows={agentRows}
        formatTimestamp={formatTimestamp}
        formatLatency={formatLatency}
      />
    ),
    history: <HistoryPage history={history} onInspect={setResults} formatTimestamp={formatTimestamp} />,
    details: <DetailsPage agentRows={agentRows} slowestAgent={slowestAgent} formatLatency={formatLatency} />,
  };

  return (
    <div className="app-shell">
      <header className="navbar">
        <div className="navbar-brand">
          <p className="eyebrow">Agent Benchmarking</p>
          <h1>Agent Benchmarking Dashboard</h1>
        </div>

        <nav className="nav-list navbar-links">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              className={item.id === activePage ? 'nav-item active' : 'nav-item'}
              onClick={() => setActivePage(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>

        <div className="navbar-actions">
          <button className="secondary-button" onClick={runBenchmark} disabled={loading}>
            {loading ? 'Running...' : 'Run benchmark'}
          </button>
          <button className="primary-button" onClick={() => setShowSettingsModal(true)}>
            Settings
          </button>
        </div>
      </header>

      <main className="main-panel">
        {error && <p className="error-banner">{error}</p>}
        {renderedContent[activePage]}
      </main>

      {showSettingsModal && (
        <div className="modal-overlay" onClick={() => setShowSettingsModal(false)}>
          <section className="modal-card" onClick={(event) => event.stopPropagation()}>
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Settings</p>
                <h2>Dashboard Preferences</h2>
              </div>
              <button className="secondary-button" onClick={() => setShowSettingsModal(false)}>
                Close
              </button>
            </div>

            <div className="settings-grid">
              <label className="field">
                <span>Backend URL</span>
                <input value={apiUrl} onChange={(event) => setApiUrl(event.target.value)} />
              </label>

              <label className="field">
                <span>Default problem</span>
                <textarea value={problem} onChange={(event) => setProblem(event.target.value)} rows={4} />
              </label>
            </div>

            <div className="hero-actions">
              <button className="primary-button" onClick={() => setTheme((currentTheme) => (currentTheme === 'dark' ? 'light' : 'dark'))}>
                {theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
              </button>
              <button
                className="secondary-button"
                onClick={() => {
                  setApiUrl(DEFAULT_API_URL);
                  setProblem(DEFAULT_PROBLEM);
                }}
              >
                Reset defaults
              </button>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}

export default App;
