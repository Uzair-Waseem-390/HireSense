import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { resumeService } from '../services/resumeService';
import websocketService from '../services/websocketService';
import { useAuth } from '../contexts/AuthContext';
import Layout from '../components/Layout';

const UploadResume = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');
  const [message, setMessage] = useState('');
  const { token } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (token) {
      websocketService.connect(token);
      
      websocketService.on('resume_update', (data) => {
        setProgress(data.progress || 0);
        setStatus(data.status || '');
        setMessage(data.message || '');
        
        if (data.status === 'analyzed') {
          setTimeout(() => {
            navigate('/dashboard');
          }, 2000);
        }
      });

      return () => {
        websocketService.off('resume_update');
      };
    }
  }, [token, navigate]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.type !== 'application/pdf') {
        alert('Please upload a PDF file');
        return;
      }
      setFile(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert('Please select a file');
      return;
    }

    setUploading(true);
    setProgress(0);
    setStatus('uploading');
    setMessage('Uploading resume...');

    try {
      const result = await resumeService.uploadResume(file);
      setMessage(result.message);
      setStatus('processing');
      // WebSocket will handle progress updates
    } catch (error) {
      setStatus('error');
      setMessage(error.response?.data?.detail || 'Upload failed');
      setUploading(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Upload Resume</h1>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select PDF Resume
            </label>
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
              disabled={uploading}
            />
            {file && (
              <p className="mt-2 text-sm text-gray-600">Selected: {file.name}</p>
            )}
          </div>

          {status && (
            <div className="mb-6">
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
              onClick={handleUpload}
              disabled={!file || uploading}
              className="px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploading ? 'Uploading...' : 'Upload Resume'}
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              className="px-6 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default UploadResume;

