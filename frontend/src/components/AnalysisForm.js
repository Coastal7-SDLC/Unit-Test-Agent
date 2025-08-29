import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { toast } from 'react-hot-toast';
import { Github, Key, Settings, Play } from 'lucide-react';
import { analysisAPI } from '../services/api';

const AnalysisForm = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const navigate = useNavigate();
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const onSubmit = async (data) => {
    setIsLoading(true);
    
    try {
      const response = await analysisAPI.startAnalysis({
        repository_url: data.repositoryUrl,
        api_key: data.apiKey,
        include_dependencies: Boolean(data.includeDependencies),
        generate_mocks: Boolean(data.generateMocks),
        target_coverage: parseInt(data.targetCoverage) || 80,
        max_files: data.maxFiles ? parseInt(data.maxFiles) : null,
      });

      toast.success('Analysis started successfully!');
      navigate(`/analysis/${response.task_id}`);
      
    } catch (error) {
      console.error('Error starting analysis:', error);
      
      // Handle different error response formats
      let errorMessage = 'Failed to start analysis';
      
      if (error.response?.data) {
        if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        } else if (error.response.data.detail) {
          errorMessage = error.response.data.detail;
        } else if (error.response.data.message) {
          errorMessage = error.response.data.message;
        } else if (Array.isArray(error.response.data)) {
          // Handle validation error array
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
      setIsLoading(false);
    }
  };

  return (
    <div className="card max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Start Repository Analysis
        </h2>
        <p className="text-gray-600">
          Enter a GitHub repository URL and your OpenRouter API key to begin automated test generation
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Repository URL */}
        <div>
          <label htmlFor="repositoryUrl" className="block text-sm font-medium text-gray-700 mb-2">
            <Github className="inline h-4 w-4 mr-2" />
            GitHub Repository URL
          </label>
          <input
            type="url"
            id="repositoryUrl"
            placeholder="https://github.com/username/repository"
            className="input-field"
            {...register('repositoryUrl', {
              required: 'Repository URL is required',
              pattern: {
                value: /^https:\/\/github\.com\/[^/]+\/[^/]+$/,
                message: 'Please enter a valid GitHub repository URL',
              },
            })}
          />
          {errors.repositoryUrl && (
            <p className="mt-1 text-sm text-error-600">{errors.repositoryUrl.message}</p>
          )}
        </div>

        {/* API Key */}
        <div>
          <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700 mb-2">
            <Key className="inline h-4 w-4 mr-2" />
            OpenRouter API Key
          </label>
          <input
            type="password"
            id="apiKey"
            placeholder="sk-or-v1-..."
            className="input-field"
            {...register('apiKey', {
              required: 'API key is required',
              pattern: {
                value: /^sk-or-v1-[a-zA-Z0-9]+$/,
                message: 'Please enter a valid OpenRouter API key',
              },
            })}
          />
          {errors.apiKey && (
            <p className="mt-1 text-sm text-error-600">{errors.apiKey.message}</p>
          )}
          <p className="mt-1 text-sm text-gray-500">
            Get your free API key from{' '}
            <a
              href="https://openrouter.ai/keys"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary-600 hover:text-primary-700 underline"
            >
              OpenRouter
            </a>
          </p>
        </div>

        {/* Advanced Options Toggle */}
        <div>
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center text-sm text-gray-600 hover:text-gray-900 transition-colors duration-200"
          >
            <Settings className="h-4 w-4 mr-2" />
            Advanced Options
            <svg
              className={`ml-2 h-4 w-4 transform transition-transform duration-200 ${
                showAdvanced ? 'rotate-180' : ''
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>

        {/* Advanced Options */}
        {showAdvanced && (
          <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Include Dependencies */}
              <div>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    defaultChecked={true}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    {...register('includeDependencies')}
                  />
                  <span className="ml-2 text-sm text-gray-700">Include Dependencies</span>
                </label>
              </div>

              {/* Generate Mocks */}
              <div>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    defaultChecked={true}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    {...register('generateMocks')}
                  />
                  <span className="ml-2 text-sm text-gray-700">Generate Mocks</span>
                </label>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Target Coverage */}
              <div>
                <label htmlFor="targetCoverage" className="block text-sm font-medium text-gray-700 mb-1">
                  Target Coverage (%)
                </label>
                <input
                  type="number"
                  id="targetCoverage"
                  min="0"
                  max="100"
                  defaultValue="80"
                  className="input-field"
                  {...register('targetCoverage', {
                    min: { value: 0, message: 'Coverage must be at least 0%' },
                    max: { value: 100, message: 'Coverage must be at most 100%' },
                  })}
                />
                {errors.targetCoverage && (
                  <p className="mt-1 text-sm text-error-600">{errors.targetCoverage.message}</p>
                )}
              </div>

              {/* Max Files */}
              <div>
                <label htmlFor="maxFiles" className="block text-sm font-medium text-gray-700 mb-1">
                  Max Files (optional)
                </label>
                <input
                  type="number"
                  id="maxFiles"
                  min="1"
                  placeholder="No limit"
                  className="input-field"
                  {...register('maxFiles', {
                    min: { value: 1, message: 'Max files must be at least 1' },
                  })}
                />
                {errors.maxFiles && (
                  <p className="mt-1 text-sm text-error-600">{errors.maxFiles.message}</p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading}
          className="btn-primary w-full flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Starting Analysis...</span>
            </>
          ) : (
            <>
              <Play className="h-4 w-4" />
              <span>Start Analysis</span>
            </>
          )}
        </button>
      </form>

      {/* Info Section */}
      <div className="mt-8 p-4 bg-primary-50 rounded-lg">
        <h3 className="font-medium text-primary-900 mb-2">What happens next?</h3>
        <ul className="text-sm text-primary-800 space-y-1">
          <li>• Repository will be cloned and analyzed</li>
          <li>• Programming languages will be detected</li>
          <li>• Unit tests will be generated using AI</li>
          <li>• Tests will be executed and coverage measured</li>
          <li>• Results will be available for download</li>
        </ul>
      </div>
    </div>
  );
};

export default AnalysisForm;
