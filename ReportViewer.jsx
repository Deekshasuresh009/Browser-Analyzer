import React from 'react';
export default function ReportViewer({ report }) {
  if (!report) return null;
  const {
    job_id,
    name,
    version,
    permissions = [],
    hosts = [],
    links = [],
    api_findings = [],
    overall_score,
    recommendation,
    homograph_warnings = [],
  } = report;

  return (
    <div className="report-card">
      <div className="summary-row">
        <div className="summary-card">
          <strong>{name || 'Security report'}</strong>
          <div className="text-muted">Version: {version || 'N/A'}</div>
        </div>

        <div className="summary-card">
          <strong>{overall_score ?? '—'}</strong>
          <div className="text-muted">Risk: {recommendation || 'Unknown'}</div>
        </div>

        <div className="summary-card">
          <strong>Report ID</strong>
          <div className="text-muted"><code className="code-inline">{job_id || 'direct URL'}</code></div>
        </div>
      </div>

      <div className="panel report-details">
        <section className="section-card">
          <h3>Permissions</h3>
          {permissions.length ? (
            <div className="report-grid report-grid-2">
              {permissions.map((permission, index) => (
                <div key={index} className="detail-box">
                  <div className="detail-title">{permission.value}</div>
                  <div className="text-muted">Weight: {permission.weight}</div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-muted">No permissions found</div>
          )}
        </section>

        <section className="section-card">
          <h3>Hosts</h3>
          {hosts.length ? (
            <div className="report-grid report-grid-2">
              {hosts.map((host, index) => (
                <div key={index} className="detail-box">
                  <div className="detail-title">{host.host}</div>
                  <div className="text-muted">{(host.reasons || []).join(', ') || 'No flags'}</div>
                  {host.punycode && <div className="text-muted">Punycode: {host.punycode}</div>}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-muted">No hosts detected</div>
          )}
        </section>

        <section className="section-card">
          <h3>Links</h3>
          {links.length ? (
            <div className="report-grid">
              {links.map((link, index) => (
                <div key={index} className="detail-box">
                  <div className="detail-title link-url">{link.url}</div>
                  <div className="text-muted">Host: {link.host}</div>
                  <div className="text-muted">Score: {link.score}</div>
                  <div className="text-muted">{(link.reasons || []).join(', ') || 'No special flags'}</div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-muted">No links detected</div>
          )}
        </section>

        <section className="section-card">
          <h3>API Findings</h3>
          {api_findings.length ? (
            <ul className="api-list">
              {api_findings.map((finding, index) => (
                <li key={index} className="api-item">
                  <code className="code-inline">{finding.pattern}</code>
                  <span className="text-muted">{finding.file}</span>
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-muted">No sensitive APIs detected</div>
          )}
        </section>

        <section className="section-card">
          <h3>Homograph warnings</h3>
          {homograph_warnings.length ? (
            <div className="report-grid">
              {homograph_warnings.map((warning, index) => (
                <div key={index} className="detail-box warning-box">
                  <div className="detail-title">{warning.original} → {warning.punycode}</div>
                  <div className="text-muted">Unicode: {warning.unicode}</div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-muted">No homograph issues</div>
          )}
        </section>
      </div>
    </div>
  );
}
