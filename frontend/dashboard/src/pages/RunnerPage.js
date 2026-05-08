function RunnerPage({
  problem,
  onProblemChange,
  apiUrl,
  onApiUrlChange,
  onRunBenchmark,
  loading,
  onViewHistory,
  error,
  latestRun,
  agentRows,
  formatTimestamp,
  formatLatency,
}) {
  return (
    <div className="page-grid single-column">
      <section className="panel-card">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Benchmark runner</p>
            <h2>Test the FastAPI endpoint</h2>
          </div>
          <span className="timestamp">GET request</span>
        </div>

        <label className="field">
          <span>Benchmark problem</span>
          <textarea value={problem} onChange={(event) => onProblemChange(event.target.value)} rows={4} />
        </label>

        <label className="field">
          <span>Backend URL</span>
          <input value={apiUrl} onChange={(event) => onApiUrlChange(event.target.value)} />
        </label>

        <div className="hero-actions">
          <button className="primary-button" onClick={onRunBenchmark} disabled={loading}>
            {loading ? 'Running benchmark...' : 'Run benchmark'}
          </button>
          <button className="secondary-button" onClick={onViewHistory}>
            View history
          </button>
        </div>

        {error && <p className="error-banner">{error}</p>}
      </section>

      {latestRun && (
        <section className="panel-card">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Last response</p>
              <h2>Backend results</h2>
            </div>
            <span className="timestamp">{formatTimestamp(latestRun.createdAt)}</span>
          </div>
          <div className="results-table">
            <div className="results-row results-row-head">
              <span>Agent</span>
              <span>Answer</span>
              <span>Latency</span>
              <span>Tokens</span>
            </div>
            {agentRows.map((row) => (
              <div key={row.agentName} className="results-row">
                <span>{row.agentName}</span>
                <span>{row.answer}</span>
                <span>{formatLatency(row.latency)}</span>
                <span>{row.tokens}</span>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

export default RunnerPage;
