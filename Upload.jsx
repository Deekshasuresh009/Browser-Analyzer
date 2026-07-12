import React, { useState, useEffect, useRef } from 'react';
import { uploadFile, getStatus, getReport } from '../api';
import Spinner from './Spinner';

const statusLabels = {
  uploading: 'Uploading',
  queued: 'Queued',
  polling: 'Analyzing',
  done: 'Complete',
  error: 'Error',
};

export default function Upload({ onReportReady }) {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState(null);
  const [jobId, setJobId] = useState(null);
  const pollRef = useRef(null);

  useEffect(() => () => { if (pollRef.current) clearInterval(pollRef.current); }, []);

  const startUpload = async () => {
    if (!file) return alert('Select a .zip/.crx/.xpi file first');
    setStatus('uploading');
    try {
      const res = await uploadFile(file);
      const id = res.data.job_id;
      setJobId(id);
      setStatus('queued');
      startPolling(id);
    } catch (err) {
      console.error(err);
      setStatus('error');
      alert('Upload failed: ' + (err?.response?.data?.detail || err.message));
    }
  };

  const startPolling = (id) => {
    setStatus('polling');
    pollRef.current = setInterval(async () => {
      try {
        const s = await getStatus(id);
        if (s?.data?.status === 'finished') {
          clearInterval(pollRef.current);
          setStatus('done');
          const rep = await getReport(id);
          onReportReady && onReportReady(rep.data);
        } else if (s?.data?.status === 'error') {
          clearInterval(pollRef.current);
          setStatus('error');
          alert('Analysis error: ' + (s?.data?.error || s?.data?.traceback || 'unknown'));
        }
      } catch (e) {
        console.warn('poll error', e.message);
      }
    }, 1500);
  };

  return (
    <div className="panel upload-panel">
      <div className="panel-header">
        <div>
          <h3>Upload extension</h3>
          <p className="small-note">Upload a browser extension package and receive a detailed privacy report.</p>
        </div>
        <div className={`status-pill ${status || 'ready'}`}>
          {statusLabels[status] || 'Ready'}
        </div>
      </div>

      <div className="form-row">
        <label className="file-input-wrapper">
          <input type="file" accept=".zip,.crx,.xpi" onChange={(e) => setFile(e.target.files?.[0] || null)} />
          <span>{file?.name || 'Choose a file'}</span>
        </label>

        <button
          className="btn btn-primary"
          onClick={startUpload}
          disabled={!file || status === 'uploading' || status === 'polling'}
        >
          {status === 'uploading' || status === 'polling'
            ? <><Spinner size={14} /> {status === 'uploading' ? 'Uploading...' : 'Analyzing...'}</>
            : 'Upload & Analyze'}
        </button>
      </div>

      <div className="help-row">Allowed file types: <strong>.zip, .crx, .xpi</strong></div>
      {jobId && <div className="info-row">Job ID: <code>{jobId}</code></div>}
    </div>
  );
}
