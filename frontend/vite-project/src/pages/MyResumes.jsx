import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { resumeService } from '../services/resumeService';
import Layout from '../components/Layout';

const MyResumes = () => {
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadResumes();
  }, []);

  const loadResumes = async () => {
    try {
      setLoading(true);
      const data = await resumeService.getAllResumes();
      setResumes(data);
    } catch (error) {
      console.error('Error loading resumes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleActive = async (resumeId, currentStatus) => {
    try {
      await resumeService.setResumeActive(resumeId, !currentStatus);
      loadResumes();
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to update resume status');
    }
  };

  const handleDelete = async (resumeId) => {
    if (!window.confirm('Are you sure you want to delete this resume?')) {
      return;
    }

    try {
      await resumeService.deleteResume(resumeId);
      loadResumes();
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to delete resume');
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">My Resumes</h1>
          <button
            onClick={() => navigate('/upload-resume')}
            className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
          >
            Upload New Resume
          </button>
        </div>

        {resumes.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-6 text-center">
            <p className="text-gray-600 mb-4">No resumes uploaded yet</p>
            <button
              onClick={() => navigate('/upload-resume')}
              className="px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
            >
              Upload Resume
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {resumes.map((resume) => (
              <div key={resume.resume_id} className="bg-white rounded-lg shadow p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{resume.filename}</h3>
                    <p className="text-sm text-gray-500 mt-1">
                      {new Date(resume.uploaded_at).toLocaleDateString()}
                    </p>
                  </div>
                  <span
                    className={`px-2 py-1 rounded text-xs ${
                      resume.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {resume.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>

                <div className="mb-4">
                  <span
                    className={`px-2 py-1 rounded text-xs ${
                      resume.status === 'analyzed'
                        ? 'bg-green-100 text-green-800'
                        : resume.status === 'failed'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}
                  >
                    {resume.status}
                  </span>
                </div>

                <div className="flex space-x-2">
                  <button
                    onClick={() => handleToggleActive(resume.resume_id, resume.is_active)}
                    className={`flex-1 px-3 py-2 text-sm rounded-md ${
                      resume.is_active
                        ? 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                        : 'bg-primary-600 text-white hover:bg-primary-700'
                    }`}
                  >
                    {resume.is_active ? 'Deactivate' : 'Set Active'}
                  </button>
                  <button
                    onClick={() => handleDelete(resume.resume_id)}
                    className="px-3 py-2 text-sm bg-red-600 text-white rounded-md hover:bg-red-700"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-6">
          <button
            onClick={() => navigate('/dashboard')}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    </Layout>
  );
};

export default MyResumes;

