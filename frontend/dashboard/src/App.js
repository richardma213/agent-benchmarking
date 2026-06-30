import { useEffect, useMemo, useState } from 'react';
import './App.css';
import HistoryPage from './pages/HistoryPage';
import OverviewPage from './pages/OverviewPage';
import RunnerPage from './pages/RunnerPage';
import MultiRunnerPage from './pages/MultiRunnerPage';
import { fetchBenchmark, getAgentRows } from './lib/benchmarkApi';
import {
  buildTrialOutcome,
  createBatchRunRecord,
  parseTrialsFile,
  summarizeRuns,
} from './lib/multiRunner';

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
  { id: 'runner', label: 'Single Runner' },
  { id: 'multi-runner', label: 'Multi Runner' },
  { id: 'history', label: 'History / Results' },
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

function isBatchRun(entry) {
  return entry?.runType === 'batch';
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
  const [multiRunner, setMultiRunner] = useState({
    batchId: null,
    fileName: '',
    trials: [],
    fileError: null,
    runError: null,
    running: false,
    progress: { current: 0, total: 0 },
    results: [],
    lastRunAt: null,
  });
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
      const rawResults = await fetchBenchmark(apiUrl, problem);

      const processedResults = await buildTrialOutcome(
        { problem, expected: problem },
        rawResults,
        apiUrl
      );

      const benchmarkRun = {
        id: crypto.randomUUID(),
        runType: 'single',
        problem,
        createdAt: new Date().toISOString(),
        rawResults,
        results: processedResults,
        agentRows: processedResults.agentRows ?? [],
        matchedAgents: processedResults.matchedAgents ?? [],
        matched: processedResults.matched ?? false,
        totalTokens: processedResults.totalTokens ?? 0,
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

  const latestRun =
    results ??
    history.find((entry) => !isBatchRun(entry)) ??
    null;

  const agentRows = useMemo(
    () => latestRun?.agentRows ?? getAgentRows(latestRun?.rawResults),
    [latestRun]
  );

  const totalTokens = agentRows.reduce(
    (sum, row) => sum + (Number(row.tokens) || 0),
    0
  );

  const handleMultiRunnerAttachFile = async (event) => {
    const file = event.target.files?.[0];
    event.target.value = '';

    if (!file) {
      return;
    }

    setMultiRunner((currentState) => ({
      ...currentState,
      fileError: null,
      runError: null,
    }));

    try {
      const parsedTrials = await parseTrialsFile(file);
      setMultiRunner({
        batchId: null,
        fileName: file.name,
        trials: parsedTrials,
        fileError: null,
        runError: null,
        running: false,
        progress: { current: 0, total: parsedTrials.length },
        results: [],
        lastRunAt: null,
      });
    } catch (err) {
      setMultiRunner({
        batchId: null,
        fileName: file.name,
        trials: [],
        fileError: err.message,
        runError: null,
        running: false,
        progress: { current: 0, total: 0 },
        results: [],
        lastRunAt: null,
      });
    }
  };

  const handleRunMultiRunner = async () => {
    if (!multiRunner.trials.length || multiRunner.running) {
      return;
    }

    const currentTrials = multiRunner.trials;
    const currentFileName = multiRunner.fileName;

    setMultiRunner((currentState) => ({
      ...currentState,
      running: true,
      runError: null,
      fileError: null,
      progress: { current: 0, total: currentTrials.length },
    }));

    const collectedResults = [];

    try {
      for (let index = 0; index < currentTrials.length; index += 1) {
        const trial = currentTrials[index];

        setMultiRunner((currentState) => ({
          ...currentState,
          progress: { current: index, total: currentTrials.length },
        }));

        try {
          const rawResults = await fetchBenchmark(apiUrl, trial.problem);
          const processedResults = await buildTrialOutcome(
            trial,
            rawResults,
            apiUrl
          );

          collectedResults.push({
            ...trial,
            createdAt: new Date().toISOString(),
            rawResults,
            results: processedResults,
            agentRows: processedResults.agentRows ?? [],
            matchedAgents: processedResults.matchedAgents ?? [],
            matched: processedResults.matched ?? false,
            totalTokens: processedResults.totalTokens ?? 0,
          });

        } catch (err) {
          collectedResults.push({
            ...trial,
            createdAt: new Date().toISOString(),
            error: err.message,
            rawResults: [],
            results: [],
            agentRows: [],
            matchedAgents: [],
            matched: false,
            totalTokens: 0,
          });
        }
      }

      const completedRun = createBatchRunRecord({
        fileName: currentFileName,
        trials: currentTrials,
        results: collectedResults,
      });

      setMultiRunner((currentState) => ({
        ...currentState,
        batchId: completedRun.id,
        running: false,
        progress: { current: currentTrials.length, total: currentTrials.length },
        results: collectedResults,
        lastRunAt: completedRun.createdAt,
      }));

      setHistory((currentHistory) => [completedRun, ...currentHistory].slice(0, 5));

    } catch (err) {
      setMultiRunner((currentState) => ({
        ...currentState,
        running: false,
        progress: { current: currentTrials.length, total: currentTrials.length },
        runError: err.message,
      }));
    }
  };

  const handleHistoryInspect = (entry) => {
    if (isBatchRun(entry)) {
      setMultiRunner({
        batchId: entry.id,
        fileName: entry.fileName ?? entry.title ?? 'Saved batch run',
        trials: entry.trials ?? [],
        fileError: null,
        runError: null,
        running: false,
        progress: { current: entry.results?.length ?? 0, total: entry.trials?.length ?? 0 },
        results: entry.results ?? [],
        lastRunAt: entry.createdAt ?? null,
      });
      setActivePage('multi-runner');
      return;
    }

    setResults(entry);
    setActivePage('overview');
  };

  const handleRemoveMultiRunnerTrial = (trialId) => {
    const nextResults = multiRunner.results.filter((trial) => trial.id !== trialId);

    setMultiRunner((currentState) => ({
      ...currentState,
      results: nextResults,
    }));

    if (!multiRunner.batchId) {
      return;
    }

    const updatedSummary = summarizeRuns(nextResults);

    setHistory((currentHistory) =>
      currentHistory.map((entry) =>
        entry.id === multiRunner.batchId
          ? {
              ...entry,
              results: nextResults,
              summary: updatedSummary,
            }
          : entry,
      ),
    );
  };

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
    history: <HistoryPage history={history} onInspect={handleHistoryInspect} formatTimestamp={formatTimestamp} />,
    'multi-runner': (
      <MultiRunnerPage
        apiUrl={apiUrl}
        formatTimestamp={formatTimestamp}
        formatLatency={formatLatency}
        fileName={multiRunner.fileName}
        trials={multiRunner.trials}
        fileError={multiRunner.fileError}
        runError={multiRunner.runError}
        running={multiRunner.running}
        progress={multiRunner.progress}
        results={multiRunner.results}
        lastRunAt={multiRunner.lastRunAt}
        onAttachFile={handleMultiRunnerAttachFile}
        onRunAllTrials={handleRunMultiRunner}
        onRemoveTrial={handleRemoveMultiRunnerTrial}
      />
    ),
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
