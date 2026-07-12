import axios from 'axios';
const BASE = (process.env.REACT_APP_API_URL || '').replace(/\/$/, '');

export const uploadFile = (file) => {
  const fd = new FormData();
  fd.append('file', file);
  return axios.post(`${BASE}/upload`, fd, { timeout: 120000 });
};
export const getStatus = (jobId) => axios.get(`${BASE}/status/${jobId}`);
export const getReport = (jobId) => axios.get(`${BASE}/report/${jobId}`);
export const analyzeUrl = (url) => axios.post(`${BASE}/analyze-url`, { url });
