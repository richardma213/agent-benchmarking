function HistoryPage({ history, onInspect, formatTimestamp }) {
  return (
    <section className="panel-card">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">History</p>
          <h2>Recent runs</h2>
        </div>
        <span className="timestamp">Stored locally in your browser</span>
      </div>

      {history.length === 0 ? (
        <p className="muted-copy">No saved runs yet. Use the runner to generate results and they will appear here.</p>
      ) : (
        <div className="history-list">
          {history.map((entry) => (
            <article key={entry.id} className="history-item">
              <div>
                <h3>{entry.problem}</h3>
                <p>{formatTimestamp(entry.createdAt)}</p>
              </div>
              <button className="secondary-button" onClick={() => onInspect(entry)}>
                Inspect
              </button>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

export default HistoryPage;
