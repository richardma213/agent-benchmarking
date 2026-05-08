function OverviewPage({
  apiUrl,
  problem,
  agentRows,
  totalTokens,
  latestRun,
  loading,
  onOpenRunner,
  onRunBenchmark,
  formatTimestamp,
  formatLatency,
}) {
  return (
    <div className="page-grid">
      <section className="hero-card">
        <p className="eyebrow">Agent benchmarking dashboard</p>
        <h1>Run the backend benchmark and compare agent results.</h1>
        <p className="hero-copy">
          Use the runner to hit your FastAPI endpoint, inspect per-agent answers, and keep a short history of recent runs.
        </p>
        <div className="hero-actions">
          <button className="primary-button" onClick={onOpenRunner}>
            Open Runner
          </button>
          <button className="secondary-button" onClick={onRunBenchmark} disabled={loading}>
            {loading ? 'Running...' : 'Run Latest Benchmark'}
          </button>
        </div>
      </section>

      <section className="stats-grid">
        <article className="stat-card">
          <span className="stat-label">API URL</span>
          <strong>{apiUrl}</strong>
        </article>
        <article className="stat-card">
          <span className="stat-label">Benchmark problem</span>
          <strong>{problem}</strong>
        </article>
        <article className="stat-card">
          <span className="stat-label">Agents compared</span>
          <strong>{agentRows.length || 2}</strong>
        </article>
        <article className="stat-card">
          <span className="stat-label">Total tokens</span>
          <strong>{totalTokens || '—'}</strong>
        </article>
      </section>

      <section className="panel-card">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Latest run</p>
            <h2>Results snapshot</h2>
          </div>
          {latestRun && <span className="timestamp">{formatTimestamp(latestRun.createdAt)}</span>}
        </div>

        {!latestRun ? (
          <p className="muted-copy">No benchmark has been run yet. Switch to the Runner page to create your first result.</p>
        ) : (
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
        )}
      </section>
    </div>
  );
}

export default OverviewPage;
