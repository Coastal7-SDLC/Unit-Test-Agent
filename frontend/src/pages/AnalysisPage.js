import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from 'react-query';
import { toast } from 'react-hot-toast';
import { XCircle } from 'lucide-react';
import ProgressTracker from '../components/ProgressTracker';
import { analysisAPI } from '../services/api';

const AnalysisPage = () => {
  const { taskId } = useParams();
  const navigate = useNavigate();
  const [pollingInterval, setPollingInterval] = useState(2000);

  const { data: status, error, isLoading } = useQuery(
    ['taskStatus', taskId],
    () => analysisAPI.getTaskStatus(taskId),
    {
      refetchInterval: pollingInterval,
      refetchIntervalInBackground: true,
      retry: false,
    }
  );

  useEffect(() => {
    if (status?.status === 'completed') {
      setPollingInterval(false);
      toast.success('Analysis completed successfully!');
      navigate(`/results/${taskId}`);
    } else if (status?.status === 'failed') {
      setPollingInterval(false);
      toast.error('Analysis failed. Please try again.');
    }
  }, [status?.status, taskId, navigate]);

  if (isLoading) {
    return (
      <div className="card max-w-4xl mx-auto">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading task status...</p>
        </div>
      </div>
    );
  }

  if (error) {
    // Handle different error formats
    let errorMessage = 'An error occurred while loading the task';
    
    if (error.response?.data) {
      if (typeof error.response.data === 'string') {
        errorMessage = error.response.data;
      } else if (error.response.data.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response.data.message) {
        errorMessage = error.response.data.message;
      } else if (Array.isArray(error.response.data)) {
        errorMessage = error.response.data.map(err => 
          typeof err === 'string' ? err : err.msg || 'Validation error'
        ).join(', ');
      } else {
        errorMessage = JSON.stringify(error.response.data);
      }
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    return (
      <div className="card max-w-2xl mx-auto">
        <div className="text-center py-8">
          <XCircle className="h-12 w-12 text-error-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Task</h3>
          <p className="text-gray-600 mb-4">{errorMessage}</p>
          <button
            onClick={() => navigate('/')}
            className="btn-primary"
          >
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="card max-w-4xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Analysis in Progress
        </h2>
        <p className="text-gray-600">
          Your repository is being analyzed and tests are being generated. This process typically takes 3-5 minutes.
        </p>
      </div>

      {/* Progress Tracker */}
      <ProgressTracker 
        progress={status?.progress_percentage || 0}
        currentStep={status?.current_step || 'Initializing...'}
        status={status?.status || 'pending'}
      />

      {/* Task Information */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="font-medium text-gray-900">Started</div>
          <div className="text-gray-600">
            {status?.started_at 
              ? new Date(status.started_at).toLocaleTimeString()
              : 'Pending'
            }
          </div>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="font-medium text-gray-900">Duration</div>
          <div className="text-gray-600">
            {status?.started_at && status?.completed_at
              ? `${Math.round((new Date(status.completed_at) - new Date(status.started_at)) / 1000)}s`
              : status?.started_at
              ? `${Math.round((new Date() - new Date(status.started_at)) / 1000)}s`
              : '0s'
            }
          </div>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="font-medium text-gray-900">Estimated Time</div>
          <div className="text-gray-600">~5 minutes</div>
        </div>
      </div>

      {/* Error Message */}
      {status?.error_message && (
        <div className="mt-6 p-4 bg-error-50 border border-error-200 rounded-lg">
          <div className="flex items-center space-x-2 mb-2">
            <XCircle className="h-5 w-5 text-error-500" />
            <h4 className="font-medium text-error-900">Error</h4>
          </div>
          <p className="text-error-700 text-sm">{status.error_message}</p>
        </div>
      )}
    </div>
  );
};

export default AnalysisPage;
