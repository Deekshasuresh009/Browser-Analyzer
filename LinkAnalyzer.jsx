import React, { useState } from 'react';
import { analyzeUrl } from '../api';

export default function LinkAnalyzer() {
  const [url, setUrl] = useState('');
  const [report, setReport] = useState(null);
  const [status, setStatus] = useState(null);

  const handleAnalyze = async () => {
    if (!url.trim()) {
      return alert('Enter a URL to analyze.');
    }
    setStatus('analyzing');
    try {
      const res = await analyzeUrl(url.trim());
      setReport(res.data);
      setStatus('done');
    } catch (err) {
      console.error(err);
      setStatus('error');
      alert('URL analysis failed: ' + (err?.response?.data?.detail || err.message));
    }
  };

  return (
    <div className="panel analyzer-panel">
      <div className="panel-header">
        <div>
          <h3>Link Analyzer</h3>
          <p className="small-note">Inspect URLs for suspicious domains, redirects, and privacy risk.</p>
        </div>
        <div className="badge">URL</div>
      </div>

      <div className="form-row">
        <input
          className="input-text"
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com/path"
        />
        <button className="btn btn-success" onClick={handleAnalyze}>
          {status === 'analyzing' ? 'Analyzing...' : 'Analyze URL'}
        </button>
      </div>

      {status === 'done' && report && (
        <div className="result-card">
          <div className="result-header">
            <div>
              <strong>{report.url}</strong>
              <div className="text-muted">Risk: {report.risk_level.toUpperCase()} — {report.overall_score}%</div>
            </div>
            <span className={`status-pill ${report.risk_level}`}>{report.risk_level}</span>
          </div>

          <div className="result-grid">
            <div className="result-item">
              <div className="result-label">Recommendation</div>
              <div>{report.recommendation}</div>
            </div>
            <div className="result-item">
              <div className="result-label">HTTPS</div>
              <div>{report.is_https ? 'Yes' : 'No'}</div>
            </div>
            <div className="result-item">
              <div className="result-label">IP address</div>
              <div>{report.is_ip_address ? 'Yes' : 'No'}</div>
            </div>
            <div className="result-item">
              <div className="result-label">Homograph</div>
              <div>{report.homograph_suspicious ? 'Possible' : 'No'}</div>
            </div>
          </div>

          <div className="result-section">
            <div className="result-label">Suspicious keywords</div>
            <div>{report.suspicious_keywords.length ? report.suspicious_keywords.join(', ') : 'None detected'}</div>
          </div>

          <div className="result-section">
            <div className="result-label">Reasons</div>
            {report.reasons.length ? (
              <ul className="result-list">
                {report.reasons.map((reason, index) => (
                  <li key={index}>{reason}</li>
                ))}
              </ul>
            ) : (
              <div className="text-muted">No specific risk reasons found</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
