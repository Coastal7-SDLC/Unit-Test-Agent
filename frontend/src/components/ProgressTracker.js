import React from 'react';
import { CheckCircle, Clock, Play, AlertCircle } from 'lucide-react';

const ProgressTracker = ({ progress, currentStep, status }) => {
  // Define the analysis phases with their progress ranges
  const phases = [
    {
      id: 'initialization',
      name: 'Initialization',
      description: 'Setting up analysis environment',
      startProgress: 0,
      endProgress: 10,
      icon: Clock
    },
    {
      id: 'cloning',
      name: 'Cloning Repository',
      description: 'Downloading repository from GitHub',
      startProgress: 10,
      endProgress: 20,
      icon: Play
    },
    {
      id: 'analysis',
      name: 'Code Analysis',
      description: 'Detecting languages and structure',
      startProgress: 20,
      endProgress: 30,
      icon: Play
    },
    {
      id: 'generation',
      name: 'Test Generation',
      description: 'AI generating unit tests',
      startProgress: 30,
      endProgress: 70,
      icon: Play
    },
    {
      id: 'execution',
      name: 'Test Execution',
      description: 'Running tests and coverage',
      startProgress: 70,
      endProgress: 90,
      icon: Play
    },
    {
      id: 'completion',
      name: 'Finalization',
      description: 'Preparing results and reports',
      startProgress: 90,
      endProgress: 100,
      icon: Play
    }
  ];

  // Determine which phases are completed, current, and pending
  const getPhaseStatus = (phase) => {
    if (progress >= phase.endProgress) {
      return 'completed';
    } else if (progress >= phase.startProgress && progress < phase.endProgress) {
      return 'current';
    } else {
      return 'pending';
    }
  };

  // Get the current active phase
  const getCurrentPhase = () => {
    return phases.find(phase => 
      progress >= phase.startProgress && progress < phase.endProgress
    ) || phases[phases.length - 1];
  };

  const currentPhase = getCurrentPhase();

  return (
    <div className="space-y-6">
      {/* Progress Bar */}
      <div className="relative">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>0%</span>
          <span>100%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div 
            className="bg-primary-600 h-3 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
        
        {/* Phase Markers */}
        <div className="relative -mt-1">
          {phases.map((phase, index) => {
            const phaseStatus = getPhaseStatus(phase);
            const isCompleted = phaseStatus === 'completed';
            const isCurrent = phaseStatus === 'current';
            
            return (
              <div
                key={phase.id}
                className="absolute transform -translate-x-1/2"
                style={{ left: `${phase.endProgress}%` }}
              >
                <div className={`
                  w-6 h-6 rounded-full border-2 flex items-center justify-center
                  ${isCompleted 
                    ? 'bg-green-500 border-green-500 text-white' 
                    : isCurrent 
                    ? 'bg-primary-500 border-primary-500 text-white' 
                    : 'bg-white border-gray-300 text-gray-400'
                  }
                `}>
                  {isCompleted ? (
                    <CheckCircle className="w-4 h-4" />
                  ) : isCurrent ? (
                    <Play className="w-3 h-3 ml-0.5" />
                  ) : (
                    <span className="text-xs font-medium">{index + 1}</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Current Status */}
      <div className="text-center">
        <div className="inline-flex items-center space-x-2 px-4 py-2 bg-primary-50 rounded-full">
          <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse" />
          <span className="text-primary-700 font-medium">
            {currentStep || 'Initializing...'}
          </span>
        </div>
        <p className="text-sm text-gray-600 mt-2">
          Phase: {currentPhase?.name} • {progress}% Complete
        </p>
      </div>

      {/* Phase Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {phases.map((phase) => {
          const phaseStatus = getPhaseStatus(phase);
          const isCompleted = phaseStatus === 'completed';
          const isCurrent = phaseStatus === 'current';
          const Icon = phase.icon;
          
          return (
            <div
              key={phase.id}
              className={`
                p-4 rounded-lg border-2 transition-all duration-200
                ${isCompleted 
                  ? 'border-green-200 bg-green-50' 
                  : isCurrent 
                  ? 'border-primary-200 bg-primary-50' 
                  : 'border-gray-200 bg-gray-50'
                }
              `}
            >
              <div className="flex items-start space-x-3">
                <div className={`
                  p-2 rounded-lg
                  ${isCompleted 
                    ? 'bg-green-100 text-green-600' 
                    : isCurrent 
                    ? 'bg-primary-100 text-primary-600' 
                    : 'bg-gray-100 text-gray-400'
                  }
                `}>
                  {isCompleted ? (
                    <CheckCircle className="w-5 h-5" />
                  ) : (
                    <Icon className="w-5 h-5" />
                  )}
                </div>
                
                <div className="flex-1 min-w-0">
                  <h3 className={`
                    font-medium text-sm
                    ${isCompleted 
                      ? 'text-green-800' 
                      : isCurrent 
                      ? 'text-primary-800' 
                      : 'text-gray-600'
                    }
                  `}>
                    {phase.name}
                  </h3>
                  <p className="text-xs text-gray-500 mt-1">
                    {phase.description}
                  </p>
                  
                  {/* Status indicator */}
                  <div className="mt-2">
                    {isCompleted && (
                      <span className="inline-flex items-center text-xs text-green-600 font-medium">
                        <CheckCircle className="w-3 h-3 mr-1" />
                        Completed
                      </span>
                    )}
                    {isCurrent && (
                      <span className="inline-flex items-center text-xs text-primary-600 font-medium">
                        <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse mr-1" />
                        In Progress
                      </span>
                    )}
                    {!isCompleted && !isCurrent && (
                      <span className="text-xs text-gray-400">
                        Pending
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Error Display */}
      {status === 'failed' && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-red-500" />
            <span className="text-red-800 font-medium">Analysis Failed</span>
          </div>
          <p className="text-red-700 text-sm mt-1">
            There was an error during the analysis. Please try again or check the repository URL.
          </p>
        </div>
      )}

      {/* Success Display */}
      {status === 'completed' && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-5 h-5 text-green-500" />
            <span className="text-green-800 font-medium">Analysis Completed!</span>
          </div>
          <p className="text-green-700 text-sm mt-1">
            All phases completed successfully. Your test files and coverage reports are ready for download.
          </p>
        </div>
      )}
    </div>
  );
};

export default ProgressTracker;
