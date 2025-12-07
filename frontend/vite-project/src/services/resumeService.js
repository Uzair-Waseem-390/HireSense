import api from '../utils/api';

export const resumeService = {
  uploadResume: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/resumes/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getMyResume: async () => {
    const response = await api.get('/resumes/my-resume');
    return response.data;
  },

  getResumeAnalysis: async () => {
    const response = await api.get('/resumes/my-resume/analysis');
    return response.data;
  },

  getAllResumes: async () => {
    const response = await api.get('/resumes/me/');
    return response.data;
  },

  getResumeById: async (resumeId) => {
    const response = await api.get(`/resumes/${resumeId}/`);
    return response.data;
  },

  deleteResume: async (resumeId) => {
    const response = await api.delete(`/resumes/${resumeId}/`);
    return response.data;
  },

  setResumeActive: async (resumeId, isActive) => {
    const response = await api.put(`/resumes/${resumeId}/${isActive}`);
    return response.data;
  },
};

