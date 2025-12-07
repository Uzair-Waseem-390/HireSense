import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { jobService } from '../services/jobService';
import Layout from '../components/Layout';

const MatchHistory = () => {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMatch, setSelectedMatch] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadMatches();
  }, []);

  const loadMatches = async () => {
    try {
      setLoading(true);
      const data = await jobService.getMatches();
      setMatches(data);
    } catch (error) {
      console.error('Error loading matches:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetail = async (matchId) => {
    try {
      const detail = await jobService.getMatchDetail(matchId);
      setSelectedMatch(detail);
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to load match details');
    }
  };

  const handleDelete = async (matchId) => {
    if (!window.confirm('Are you sure you want to delete this match?')) {
      return;
    }

    try {
      await jobService.deleteMatch(matchId);
      loadMatches();
      if (selectedMatch?.match_id === matchId) {
        setSelectedMatch(null);
      }
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to delete match');
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
          <h1 className="text-3xl font-bold text-gray-900">Match History</h1>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
          >
            Back to Dashboard
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className={selectedMatch ? 'lg:col-span-2' : 'lg:col-span-3'}>
            {matches.length === 0 ? (
              <div className="bg-white rounded-lg shadow p-6 text-center">
                <p className="text-gray-600 mb-4">No matches found</p>
                <button
                  onClick={() => navigate('/match-job')}
                  className="px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
                >
                  Match a Job
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {matches.map((match) => (
                  <div key={match.match_id} className="bg-white rounded-lg shadow p-6">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center space-x-4 mb-2">
                          <div className="text-3xl font-bold text-primary-600">
                            {match.fit_score || 0}%
                          </div>
                          <div>
                            <p className="text-sm text-gray-500">
                              {new Date(match.created_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        {match.strengths && match.strengths.length > 0 && (
                          <p className="text-sm text-gray-600 mt-2">
                            {match.strengths.length} strengths identified
                          </p>
                        )}
                      </div>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleViewDetail(match.match_id)}
                          className="px-3 py-1 text-sm bg-primary-600 text-white rounded-md hover:bg-primary-700"
                        >
                          View Details
                        </button>
                        <button
                          onClick={() => handleDelete(match.match_id)}
                          className="px-3 py-1 text-sm bg-red-600 text-white rounded-md hover:bg-red-700"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {selectedMatch && (
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow p-6 sticky top-4">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-xl font-semibold">Match Details</h2>
                  <button
                    onClick={() => setSelectedMatch(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ×
                  </button>
                </div>

                <div className="mb-4">
                  <div className="text-4xl font-bold text-primary-600 mb-2">
                    {selectedMatch.fit_score}%
                  </div>
                  <p className="text-gray-600">Fit Score</p>
                </div>

                <div className="space-y-4">
                  <div>
                    <h3 className="text-sm font-semibold text-gray-900 mb-2">Strengths</h3>
                    <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                      {selectedMatch.strengths?.map((strength, idx) => (
                        <li key={idx}>{strength}</li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-sm font-semibold text-gray-900 mb-2">Missing Skills</h3>
                    <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                      {selectedMatch.missing_skills?.map((skill, idx) => (
                        <li key={idx}>{skill}</li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-sm font-semibold text-gray-900 mb-2">Recommendations</h3>
                    <p className="text-sm text-gray-700 whitespace-pre-line">
                      {selectedMatch.recommendations}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default MatchHistory;

