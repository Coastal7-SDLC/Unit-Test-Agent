import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from 'react-query';
import { toast } from 'react-hot-toast';
import { 
  Download, 
  BarChart3, 
  FileText, 
  Code, 
  CheckCircle, 
  XCircle,
  ArrowLeft,
  ExternalLink
} from 'lucide-react';
import { analysisAPI } from '../services/api';

const ResultsPage = () => {
  const { taskId } = useParams();
  const navigate = useNavigate();
  const [downloading, setDownloading] = useState({ tests: false, coverage: false });

  const { data: results, error, isLoading } = useQuery(
    ['analysisResults', taskId],
    () => analysisAPI.getAnalysisResults(taskId),
    {
      retry: false,
    }
  );

  const handleDownload = async (type) => {
    setDownloading(prev => ({ ...prev, [type]: true }));
    
    try {
      let data, filename;
      
      if (type === 'tests') {
        data = await analysisAPI.downloadTestFiles(taskId);
        filename = `test_files_${taskId}.zip`;
      } else {
        data = await analysisAPI.downloadCoverageReport(taskId);
        filename = `coverage_report_${taskId}.zip`;
      }
      
      const url = window.URL.createObjectURL(new Blob([data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success(`${type === 'tests' ? 'Test files' : 'Coverage report'} downloaded successfully!`);
    } catch (error) {
      console.error(`Error downloading ${type}:`, error);
      
      // Handle different error response formats
      let errorMessage = `Failed to download ${type === 'tests' ? 'test files' : 'coverage report'}`;
      
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
      
      toast.error(errorMessage);
    } finally {
      setDownloading(prev => ({ ...prev, [type]: false }));
    }
  };

  if (isLoading) {
    return (
      <div className="card max-w-2xl mx-auto">
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading results...</p>
        </div>
      </div>
    );
  }

  if (error) {
    // Handle different error formats
    let errorMessage = 'An error occurred while loading the results';
    
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
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Results</h3>
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

  if (!results) {
    return (
      <div className="card max-w-2xl mx-auto">
        <div className="text-center py-8">
          <p className="text-gray-600">No results found.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/')}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors duration-200"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Home</span>
        </button>
        
        <div className="text-right">
          <h1 className="text-2xl font-bold text-gray-900">Analysis Results</h1>
          <p className="text-gray-600">Task ID: {taskId}</p>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card text-center">
          <div className="flex justify-center mb-2">
            <FileText className="h-8 w-8 text-primary-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900">{results.total_files}</h3>
          <p className="text-gray-600">Total Files</p>
        </div>
        
        <div className="card text-center">
          <div className="flex justify-center mb-2">
            <Code className="h-8 w-8 text-success-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900">{results.generated_tests}</h3>
          <p className="text-gray-600">Tests Generated</p>
        </div>
        
        <div className="card text-center">
          <div className="flex justify-center mb-2">
            <BarChart3 className="h-8 w-8 text-warning-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900">{results.coverage_percentage.toFixed(1)}%</h3>
          <p className="text-gray-600">Coverage</p>
        </div>
        
        <div className="card text-center">
          <div className="flex justify-center mb-2">
            <CheckCircle className="h-8 w-8 text-success-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900">{results.detected_languages.length}</h3>
          <p className="text-gray-600">Languages</p>
        </div>
      </div>

      {/* Repository Info */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Repository Information</h2>
        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <span className="font-medium text-gray-700">Repository:</span>
            <a
              href={results.repository_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary-600 hover:text-primary-700 flex items-center space-x-1"
            >
              <span>{results.repository_url}</span>
              <ExternalLink className="h-4 w-4" />
            </a>
          </div>
          <div className="flex items-center space-x-2">
            <span className="font-medium text-gray-700">Languages Detected:</span>
            <div className="flex space-x-2">
              {results.detected_languages.map((lang, index) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-primary-100 text-primary-700 rounded-full text-sm"
                >
                  {lang}
                </span>
              ))}
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className="font-medium text-gray-700">Analysis Duration:</span>
            <span className="text-gray-600">
              {results.started_at && results.completed_at
                ? `${Math.round((new Date(results.completed_at) - new Date(results.started_at)) / 1000)} seconds`
                : 'N/A'
              }
            </span>
          </div>
        </div>
      </div>

      {/* Test Generation Results */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Test Generation Results</h2>
        <div className="space-y-4">
          {Object.entries(results.test_files).map(([language, data]) => (
            <div key={language} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-medium text-gray-900 capitalize">{language}</h3>
                <span className="px-2 py-1 bg-success-100 text-success-700 rounded-full text-sm">
                  {data.framework}
                </span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="font-medium text-gray-700">Files Generated:</span>
                  <span className="ml-2 text-gray-600">{data.files?.length || 0}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Total Tests:</span>
                  <span className="ml-2 text-gray-600">
                    {data.files?.reduce((sum, file) => sum + (file.test_count || 0), 0) || 0}
                  </span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Status:</span>
                  <span className={`ml-2 px-2 py-1 rounded-full text-xs ${
                    data.success 
                      ? 'bg-success-100 text-success-700' 
                      : 'bg-error-100 text-error-700'
                  }`}>
                    {data.success ? 'Success' : 'Failed'}
                  </span>
                </div>
              </div>
              
              {data.files && data.files.length > 0 && (
                <div className="mt-3">
                  <h4 className="font-medium text-gray-700 mb-2">Generated Test Files:</h4>
                  <div className="space-y-1">
                    {data.files.slice(0, 5).map((file, index) => (
                      <div key={index} className="flex items-center justify-between text-sm">
                        <span className="text-gray-600 font-mono">{file.test_file}</span>
                        <span className="text-gray-500">{file.test_count} tests</span>
                      </div>
                    ))}
                    {data.files.length > 5 && (
                      <div className="text-sm text-gray-500">
                        ... and {data.files.length - 5} more files
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Coverage Results */}
      {results.coverage_report && Object.keys(results.coverage_report).length > 0 && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Coverage Results</h2>
          <div className="space-y-4">
            {Object.entries(results.coverage_report).map(([language, data]) => (
              <div key={language} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-medium text-gray-900 capitalize">{language}</h3>
                  <span className="text-lg font-semibold text-gray-900">
                    {data.coverage?.toFixed(1) || 0}%
                  </span>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">Tests Passed:</span>
                    <span className="ml-2 text-success-600">{data.tests_passed || 0}</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Tests Failed:</span>
                    <span className="ml-2 text-error-600">{data.tests_failed || 0}</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Total Tests:</span>
                    <span className="ml-2 text-gray-600">{data.tests_total || 0}</span>
                  </div>
                </div>
                
                {data.error && (
                  <div className="mt-3 p-3 bg-error-50 border border-error-200 rounded-lg">
                    <div className="flex items-center space-x-2 mb-1">
                      <XCircle className="h-4 w-4 text-error-500" />
                      <span className="font-medium text-error-900">Error</span>
                    </div>
                    <p className="text-error-700 text-sm">{data.error}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Download Section */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Download Results</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => handleDownload('tests')}
            disabled={downloading.tests}
            className="btn-primary flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            {downloading.tests ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            ) : (
              <Download className="h-4 w-4" />
            )}
            <span>{downloading.tests ? 'Downloading...' : 'Download Test Files'}</span>
          </button>
          
          <button
            onClick={() => handleDownload('coverage')}
            disabled={downloading.coverage}
            className="btn-secondary flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            {downloading.coverage ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
            ) : (
              <BarChart3 className="h-4 w-4" />
            )}
            <span>{downloading.coverage ? 'Downloading...' : 'Download Coverage Report'}</span>
          </button>
        </div>
      </div>

      {/* Analysis Summary */}
      {results.analysis_summary && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Analysis Summary</h2>
          <div className="bg-gray-50 rounded-lg p-4">
            <pre className="text-sm text-gray-700 whitespace-pre-wrap">
              {results.analysis_summary}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultsPage;
