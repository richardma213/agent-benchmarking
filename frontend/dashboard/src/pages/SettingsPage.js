function SettingsPage({
  apiUrl,
  problem,
  onApiUrlChange,
  onProblemChange,
  onGoToRunner,
  onReset,
}) {
  return (
    <section className="panel-card">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Settings</p>
          <h2>Configure the benchmark UI</h2>
        </div>
        <span className="timestamp">Frontend-only preferences</span>
      </div>

      <div className="settings-grid">
        <label className="field">
          <span>Backend URL</span>
          <input value={apiUrl} onChange={(event) => onApiUrlChange(event.target.value)} />
        </label>
        <label className="field">
          <span>Default problem</span>
          <textarea value={problem} onChange={(event) => onProblemChange(event.target.value)} rows={4} />
        </label>
      </div>

      <div className="hero-actions">
        <button className="primary-button" onClick={onGoToRunner}>
          Go to runner
        </button>
        <button className="secondary-button" onClick={onReset}>
          Reset settings
        </button>
      </div>
    </section>
  );
}

export default SettingsPage;
