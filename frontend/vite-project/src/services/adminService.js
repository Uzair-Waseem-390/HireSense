import api from '../utils/api';

export const adminService = {
  getAllUsers: async (skip = 0, limit = 100) => {
    const response = await api.get('/admin/users', {
      params: { skip, limit },
    });
    return response.data;
  },

  getAllResumes: async (skip = 0, limit = 100) => {
    const response = await api.get('/admin/resumes', {
      params: { skip, limit },
    });
    return response.data;
  },

  getAllMatches: async (skip = 0, limit = 100) => {
    const response = await api.get('/admin/matches', {
      params: { skip, limit },
    });
    return response.data;
  },

  getStats: async () => {
    const response = await api.get('/admin/stats');
    return response.data;
  },
};

