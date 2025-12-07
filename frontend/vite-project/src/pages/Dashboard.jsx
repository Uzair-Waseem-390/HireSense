import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { resumeService } from '../services/resumeService';
import { jobService } from '../services/jobService';
import Layout from '../components/Layout';

const Dashboard = () => {
  const [resume, setResume] = useState(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [resumeData, statsData] = await Promise.all([
        resumeService.getMyResume().catch(() => null),
        jobService.getStats().catch(() => null),
      ]);
      setResume(resumeData);
      setStats(statsData);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
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
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

        {!resume ? (
          <div className="bg-white rounded-lg shadow p-6 text-center">
            <h2 className="text-xl font-semibold mb-4">No Resume Uploaded</h2>
            <p className="text-gray-600 mb-6">
              Upload your resume to get started with AI-powered job matching
            </p>
            <button
              onClick={() => navigate('/upload-resume')}
              className="px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700"
            >
              Upload Resume
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            {stats && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-sm font-medium text-gray-500">Total Matches</h3>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total_matches}</p>
                </div>
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-sm font-medium text-gray-500">Total Jobs</h3>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total_jobs}</p>
                </div>
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-sm font-medium text-gray-500">Average Fit Score</h3>
                  <p className="text-3xl font-bold text-gray-900 mt-2">
                    {stats.average_fit_score}%
                  </p>
                </div>
              </div>
            )}

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">Active Resume</h2>
                <span
                  className={`px-3 py-1 rounded-full text-sm ${
                    resume.status === 'analyzed'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}
                >
                  {resume.status}
                </span>
              </div>
              <p className="text-gray-600 mb-4">{resume.filename}</p>
              <div className="flex space-x-4">
                <button
                  onClick={() => navigate('/match-job')}
                  className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
                >
                  Match Job
                </button>
                <button
                  onClick={() => navigate('/my-resumes')}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
                >
                  View All Resumes
                </button>
                <button
                  onClick={() => navigate('/match-history')}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
                >
                  Match History
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Dashboard;

