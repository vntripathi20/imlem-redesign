const API_BASE = 'http://localhost:4000/api';

async function fetchJSON(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Request failed' }));
    throw new Error(error.error || error.message || 'API error');
  }
  return response.json();
}

export function getStudyMaterials() {
  return fetchJSON(`${API_BASE}/study-materials`);
}

export function getMeets() {
  return fetchJSON(`${API_BASE}/meets`);
}

export function getClusters() {
  return fetchJSON(`${API_BASE}/clusters`);
}

export function getStatistics() {
  return fetchJSON(`${API_BASE}/statistics`);
}

export function getUsers() {
  return fetchJSON(`${API_BASE}/users`);
}

export async function uploadStudyFile(formData) {
  return fetchJSON(`${API_BASE}/upload-file`, {
    method: 'POST',
    body: formData,
  });
}

export async function createMeet(meetData) {
  return fetchJSON(`${API_BASE}/meets`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(meetData),
  });
}

export async function updateMeet(id, updates) {
  return fetchJSON(`${API_BASE}/meets/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates),
  });
}

export async function postAnnouncement(payload) {
  return fetchJSON(`${API_BASE}/announcements`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}
