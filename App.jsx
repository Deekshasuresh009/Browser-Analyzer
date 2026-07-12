import React, { useState, useEffect } from 'react';
import Upload from './components/Upload';
import LinkAnalyzer from './components/LinkAnalyzer';
import ReportViewer from './components/ReportViewer';

export default function App() {
  const [report, setReport] = useState(null);
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    const stored = window.localStorage.getItem('browser-privacy-dark-mode');
    setDarkMode(stored === 'true');
  }, []);

  useEffect(() => {
    document.body.classList.toggle('dark-theme', darkMode);
    window.localStorage.setItem('browser-privacy-dark-mode', darkMode ? 'true' : 'false');
  }, [darkMode]);

  return (
    <div className="container">
      <header className="header">
        <div>
          <h1>Browser Privacy Analyzer</h1>
          <p>Analyze browser extensions and URLs for privacy risks, suspicious links, permissions, and sensitive APIs.</p>
        </div>
        <div className="header-actions">
          <div className="intro-badge">Trusted security analysis for extensions and links</div>
          <button className="btn btn-secondary theme-toggle" onClick={() => setDarkMode(!darkMode)}>
            {darkMode ? 'Light mode' : 'Dark mode'}
          </button>
        </div>
      </header>

      <div className="card">
        <div className="grid grid-2 card-grid">
          <Upload onReportReady={setReport} />
          <LinkAnalyzer />
        </div>
      </div>

      {report && <ReportViewer report={report} />}
    </div>
  );
}
