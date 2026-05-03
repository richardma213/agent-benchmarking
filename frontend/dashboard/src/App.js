import { useState } from 'react';
import './App.css';

function App() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runBenchmark = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/benchmark');
      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Agent Benchmarking Dashboard</h1>
        
        <button 
          onClick={runBenchmark}
          disabled={loading}
          style={{ padding: '10px 20px', fontSize: '16px', cursor: 'pointer' }}
        >
          {loading ? 'Running Benchmark...' : 'Run Benchmark'}
        </button>

        {error && <p style={{ color: 'red' }}>Error: {error}</p>}

        {results && (
          <div style={{ marginTop: '20px', padding: '20px', border: '1px solid #ccc', borderRadius: '5px' }}>
            <h2>Benchmark Results</h2>
            <p><strong>Accuracy:</strong> {(results.accuracy * 100).toFixed(2)}%</p>
            <p><strong>Latency:</strong> {(results.latency * 1000).toFixed(2)}ms</p>
            <p><strong>Tokens:</strong> {results.tokens}</p>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
