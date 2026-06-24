import { useMemo, useRef } from 'react';
import { summarizeRuns } from '../lib/multiRunner';
import { normalizeComparableText } from '../lib/benchmarkApi';

function StatusPill({ matched, error }) {
  const label = error ? 'Failed' : matched ? 'Matched' : 'No exact match';
  const className = error ? 'status-pill failed' : matched ? 'status-pill matched' : 'status-pill';

  return <span className={className}>{label}</span>;
}

function MultiRunnerPage({
  fileName,
  trials,
  fileError,
  runError,
  running,
  progress,
  results,
  lastRunAt,
  apiUrl,
  formatTimestamp,
  formatLatency,
  onAttachFile,
  onRunAllTrials,
}) {
  const inputRef = useRef(null);
  const summary = useMemo(() => summarizeRuns(results), [results]);

  return (
    <div className="page-grid single-column">
      <section className="panel-card">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Multi runner</p>
            <h2>Attach a JSON file and run every trial</h2>
          </div>
          <span className="timestamp">Batch mode</span>
        </div>

        <div className="multi-runner-upload">
          <div>
            <p className="muted-copy">
              Upload an array of trial objects with <strong>problem</strong> and <strong>expected</strong> fields. The page will run each trial against your backend in order and compare the returned answers.
            </p>
            <p className="sidebar-copy">Example format: one array, one problem per entry, one expected answer per entry.</p>
          </div>

          <pre className="sample-json-block">{`[
  {
    "problem": "integrate x^4 * ln(x)",
    "expected": "x^5/5 * ln(x) - x^5/25 + C"
  }
]`}</pre>

          <div className="dropzone-actions">
            <button className="primary-button" onClick={() => inputRef.current?.click()}>
              Attach JSON file
            </button>
            <button className="secondary-button" onClick={onRunAllTrials} disabled={!trials.length || running}>
              {running ? 'Running trials...' : 'Run all trials'}
            </button>
            <input ref={inputRef} type="file" accept="application/json,.json" onChange={onAttachFile} hidden />
          </div>

          <div className="upload-meta">
            {fileName ? <span>Loaded file: {fileName}</span> : <span>No file attached yet.</span>}
            {trials.length > 0 && <span>Trial count: {trials.length}</span>}
            {apiUrl && <span>Backend: {apiUrl}</span>}
          </div>

          {(fileError || runError) && <p className="error-banner">{fileError || runError}</p>}
          {running && progress.total > 0 && (
            <p className="timestamp">
              Running trial {Math.min(progress.current + 1, progress.total)} of {progress.total}
            </p>
          )}
        </div>
      </section>

      {results.length > 0 && (
        <>
          <section className="stats-grid batch-summary-grid">
            <article className="stat-card">
              <span className="stat-label">Trials</span>
              <strong>{summary.total}</strong>
            </article>
            <article className="stat-card">
              <span className="stat-label">Completed</span>
              <strong>{summary.completed}</strong>
            </article>
            <article className="stat-card">
              <span className="stat-label">Matched</span>
              <strong>{summary.matched}</strong>
            </article>
            <article className="stat-card">
              <span className="stat-label">Total tokens</span>
              <strong>{summary.totalTokens || '—'}</strong>
            </article>
          </section>

          <section className="panel-card">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Batch results</p>
                <h2>Per-trial breakdown</h2>
              </div>
              {lastRunAt && <span className="timestamp">{formatTimestamp(lastRunAt)}</span>}
            </div>

            <div className="trial-results-list">
              {results.map((trial) => (
                <article key={trial.id} className="trial-result-card">
                  <div className="trial-result-header">
                    <div>
                      <p className="agent-name">Trial {trial.index}</p>
                      <h3>{trial.problem}</h3>
                    </div>
                    <StatusPill matched={trial.matched} error={trial.error} />
                  </div>

                  <div className="trial-details-grid">
                    <div>
                      <span className="stat-label">Expected</span>
                      <p className="trial-detail-text">{trial.expected}</p>
                    </div>
                    <div>
                      <span className="stat-label">Matched agents</span>
                      <p className="trial-detail-text">
                        {trial.error
                          ? 'Run failed'
                          : trial.matchedAgents.length
                            ? trial.matchedAgents.map((agent) => agent.agentName).join(', ')
                            : 'None'}
                      </p>
                    </div>
                    <div>
                      <span className="stat-label">Tokens</span>
                      <p className="trial-detail-text">{trial.totalTokens || '—'}</p>
                    </div>
                    <div>
                      <span className="stat-label">Run status</span>
                      <p className="trial-detail-text">{trial.error || 'Completed'}</p>
                    </div>
                  </div>

                  {!trial.error && (
                    <div className="results-table multi-runner-results">
                      <div className="results-row results-row-head">
                        <span>Agent</span>
                        <span>Answer</span>
                        <span>Latency</span>
                        <span>Tokens</span>
                        <span>Match</span>
                      </div>
                      {trial.agentRows.map((row) => {
                        const matchesExpected = normalizeComparableText(row.answer) === normalizeComparableText(trial.expected);

                        return (
                          <div key={row.agentName} className={matchesExpected ? 'results-row matched-row' : 'results-row'}>
                            <span>{row.agentName}</span>
                            <span>{row.answer}</span>
                            <span>{formatLatency(row.latency)}</span>
                            <span>{row.tokens}</span>
                            <span>{matchesExpected ? 'Yes' : 'No'}</span>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </article>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  );
}

export default MultiRunnerPage;
