import { apiClient } from './client';

/* Each wrapper maps to one endpoint of docs/API_CONTRACT.md. */

export const authService = {
  register: ({ email, password, full_name }) =>
    apiClient.post('/auth/register', { email, password, full_name }).then((r) => r.data),

  login: ({ email, password }) =>
    apiClient.post('/auth/login', { email, password }).then((r) => r.data),

  me: () => apiClient.get('/auth/me').then((r) => r.data),

  updateMe: (payload) => apiClient.patch('/auth/me', payload).then((r) => r.data),
};

export const familyService = {
  list: () => apiClient.get('/families').then((r) => r.data),

  get: (familyId) => apiClient.get(`/families/${encodeURIComponent(familyId)}`).then((r) => r.data),

  create: ({ name, description }) =>
    apiClient.post('/families', { name, ...(description ? { description } : {}) }).then((r) => r.data),

  join: ({ invite_code }) => apiClient.post('/families/join', { invite_code }).then((r) => r.data),

  createInvite: (familyId) =>
    apiClient.post(`/families/${encodeURIComponent(familyId)}/invites`).then((r) => r.data),

  updateMemberRole: (familyId, memberId, role) =>
    apiClient
      .patch(`/families/${encodeURIComponent(familyId)}/members/${encodeURIComponent(memberId)}`, { role })
      .then((r) => r.data),
};

export const scanService = {
  scanMessage: ({ text, family_id }) =>
    apiClient
      .post('/scan/message', { text, ...(family_id ? { family_id } : {}) })
      .then((r) => r.data),

  scanUrl: ({ url, family_id }) =>
    apiClient
      .post('/scan/url', { url, ...(family_id ? { family_id } : {}) })
      .then((r) => r.data),

  list: ({ risk_level, scan_type, search, limit = 50, offset = 0 } = {}) => {
    const params = new URLSearchParams();
    if (risk_level) params.set('risk_level', risk_level);
    if (scan_type) params.set('scan_type', scan_type);
    if (search) params.set('search', search);
    params.set('limit', String(limit));
    params.set('offset', String(offset));
    return apiClient.get(`/scans?${params.toString()}`).then((r) => r.data);
  },

  get: (scanId) => apiClient.get(`/scans/${encodeURIComponent(scanId)}`).then((r) => r.data),

  remove: (scanId) => apiClient.delete(`/scans/${encodeURIComponent(scanId)}`).then((r) => r.data),

  share: (scanId, { family_id } = {}) =>
    apiClient
      .post(`/scans/${encodeURIComponent(scanId)}/share`, family_id ? { family_id } : {})
      .then((r) => r.data),
};

export const alertService = {
  list: ({ status = 'all' } = {}) =>
    apiClient.get(`/alerts?status=${encodeURIComponent(status)}`).then((r) => r.data),

  review: (alertId) =>
    apiClient.post(`/alerts/${encodeURIComponent(alertId)}/review`).then((r) => r.data),
};

export const analyticsService = {
  overview: () => apiClient.get('/analytics/overview').then((r) => r.data),
};

export const awarenessService = {
  list: () => apiClient.get('/awareness').then((r) => r.data),
};
