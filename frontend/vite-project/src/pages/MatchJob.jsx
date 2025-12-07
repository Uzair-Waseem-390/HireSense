import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { jobService } from '../services/jobService';
import websocketService from '../services/websocketService';
import { useAuth } from '../contexts/AuthContext';
import Layout from '../components/Layout';

const MatchJob = () => {
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [matching, setMatching] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');
  const [message, setMessage] = useState('');
  const [matchResult, setMatchResult] = useState(null);
  const { token } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (token) {
      websocketService.connect(token);
      
      websocketService.on('job_match_update', (data) => {
        setProgress(data.progress || 0);
        setStatus(data.status || '');
        setMessage(data.message || '');
        
        if (data.status === 'completed' && data.data?.match_id) {
          // Fetch the match detail
          jobService.getMatchDetail(data.data.match_id).then((result) => {
            setMatchResult(result);
            setMatching(false);
          });
        }
      });

      return () => {
        websocketService.off('job_match_update');
      };
    }
  }, [token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!jobDescription.trim()) {
      alert('Please enter a job description');
      return;
    }

    setMatching(true);
    setProgress(0);
    setStatus('queued');
    setMessage('Submitting job match request...');
    setMatchResult(null);

    try {
      const result = await jobService.matchJob({
        title: jobTitle || undefined,
        job_description: jobDescription,
      });
      setMessage(result.message);
      // WebSocket will handle progress updates
    } catch (error) {
      setStatus('error');
      setMessage(error.response?.data?.detail || 'Job matching failed');
      setMatching(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Match Job</h1>

        {!matchResult ? (
          <div className="bg-white rounded-lg shadow p-6">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Job Title (Optional)
                </label>
                <input
                  type="text"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder="e.g., Senior Python Developer"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Job Description *
                </label>
                <textarea
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  rows={10}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Paste the job description here..."
                />
              </div>

              {status && (
                <div>
                  <div className="flex justify-between text-sm text-gray-600 mb-2">
                    <span>{status}</span>
                    <span>{progress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                  {message && (
                    <p className="mt-2 text-sm text-gray-700">{message}</p>
                  )}
                </div>
              )}

              <div className="flex space-x-4">
                <button
                  type="submit"
                  disabled={matching}
                  className="px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {matching ? 'Matching...' : 'Match Job'}
                </button>
                <button
                  type="button"
                  onClick={() => navigate('/dashboard')}
                  className="px-6 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Match Results</h2>
            
            <div className="mb-6">
              <div className="text-4xl font-bold text-primary-600 mb-2">
                {matchResult.fit_score}%
              </div>
              <p className="text-gray-600">Fit Score</p>
            </div>

            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Strengths</h3>
                <ul className="list-disc list-inside space-y-1">
                  {matchResult.strengths?.map((strength, idx) => (
                    <li key={idx} className="text-gray-700">{strength}</li>
                  ))}
                </ul>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Missing Skills</h3>
                <ul className="list-disc list-inside space-y-1">
                  {matchResult.missing_skills?.map((skill, idx) => (
                    <li key={idx} className="text-gray-700">{skill}</li>
                  ))}
                </ul>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Recommendations</h3>
                <div className="text-gray-700 whitespace-pre-line">
                  {matchResult.recommendations}
                </div>
              </div>
            </div>

            <div className="mt-6 flex space-x-4">
              <button
                onClick={() => {
                  setMatchResult(null);
                  setJobTitle('');
                  setJobDescription('');
                }}
                className="px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
              >
                Match Another Job
              </button>
              <button
                onClick={() => navigate('/dashboard')}
                className="px-6 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default MatchJob;

