function DetailsPage({ agentRows, slowestAgent, formatLatency }) {
  return (
    <section className="panel-card">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Agent details</p>
          <h2>Compare rule-based and ML responses</h2>
        </div>
        <span className="timestamp">Latest run only</span>
      </div>

      {!agentRows.length ? (
        <p className="muted-copy">Run a benchmark first to inspect the agent-level breakdown.</p>
      ) : (
        <div className="agent-grid">
          {agentRows.map((row) => (
            <article key={row.agentName} className="agent-card">
              <p className="agent-name">{row.agentName}</p>
              <h3>{row.answer}</h3>
              <dl>
                <div>
                  <dt>Latency</dt>
                  <dd>{formatLatency(row.latency)}</dd>
                </div>
                <div>
                  <dt>Tokens</dt>
                  <dd>{row.tokens}</dd>
                </div>
              </dl>
            </article>
          ))}

          {slowestAgent && (
            <article className="agent-card accent">
              <p className="agent-name">Slowest agent</p>
              <h3>{slowestAgent.agentName}</h3>
              <p className="muted-copy">This is the agent with the highest runtime in the most recent benchmark.</p>
            </article>
          )}
        </div>
      )}
    </section>
  );
}

export default DetailsPage;
