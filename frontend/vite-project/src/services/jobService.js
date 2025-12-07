import api from '../utils/api';

export const jobService = {
  matchJob: async (matchRequest) => {
    const response = await api.post('/jobs/match', matchRequest);
    return response.data;
  },

  quickMatch: async (matchRequest) => {
    const response = await api.post('/jobs/quick-match', matchRequest);
    return response.data;
  },

  getMatches: async (limit = 20, offset = 0) => {
    const response = await api.get('/jobs/matches', {
      params: { limit, offset },
    });
    return response.data;
  },

  getMatchDetail: async (matchId) => {
    const response = await api.get(`/jobs/matches/${matchId}`);
    return response.data;
  },

  deleteMatch: async (matchId) => {
    const response = await api.delete(`/jobs/matches/${matchId}`);
    return response.data;
  },

  getJobDescriptions: async () => {
    const response = await api.get('/jobs/descriptions');
    return response.data;
  },

  getJobDescription: async (jobId) => {
    const response = await api.get(`/jobs/descriptions/${jobId}`);
    return response.data;
  },

  createJobDescription: async (jobData) => {
    const response = await api.post('/jobs/descriptions', jobData);
    return response.data;
  },

  getStats: async () => {
    const response = await api.get('/jobs/stats');
    return response.data;
  },
};

