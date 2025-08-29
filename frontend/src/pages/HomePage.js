import React from 'react';
import { 
  Code, 
  Zap, 
  BarChart3, 
  Globe, 
  Shield, 
  Download,
  CheckCircle,
  Clock,
  FileText
} from 'lucide-react';
import AnalysisForm from '../components/AnalysisForm';

const HomePage = () => {
  const features = [
    {
      icon: <Code className="h-6 w-6" />,
      title: 'Multi-Language Support',
      description: 'Automatically detects and supports Python, JavaScript, Java, C#, Go, Ruby, and PHP'
    },
    {
      icon: <Zap className="h-6 w-6" />,
      title: 'AI-Powered Generation',
      description: 'Uses advanced AI models to generate comprehensive unit tests with high coverage'
    },
    {
      icon: <BarChart3 className="h-6 w-6" />,
      title: 'Coverage Reports',
      description: 'Generates detailed coverage reports and test execution results'
    },
    {
      icon: <Globe className="h-6 w-6" />,
      title: 'GitHub Integration',
      description: 'Directly analyze any public GitHub repository with a simple URL'
    },
    {
      icon: <Shield className="h-6 w-6" />,
      title: 'Best Practices',
      description: 'Follows testing best practices including AAA pattern, mocking, and edge cases'
    },
    {
      icon: <Download className="h-6 w-6" />,
      title: 'Easy Download',
      description: 'Download generated test files and coverage reports as ZIP archives'
    }
  ];

  const supportedLanguages = [
    { name: 'Python', framework: 'pytest', icon: '🐍' },
    { name: 'JavaScript', framework: 'Jest', icon: '🟨' },
    { name: 'Java', framework: 'JUnit 5', icon: '☕' },
    { name: 'C#', framework: 'xUnit', icon: '🔷' },
    { name: 'Go', framework: 'Go testing', icon: '🐹' },
    { name: 'Ruby', framework: 'RSpec', icon: '💎' },
    { name: 'PHP', framework: 'PHPUnit', icon: '🐘' }
  ];

  const processSteps = [
    {
      icon: <Download className="h-8 w-8" />,
      title: 'Clone Repository',
      description: 'Automatically clones your GitHub repository for analysis'
    },
    {
      icon: <FileText className="h-8 w-8" />,
      title: 'Analyze Code',
      description: 'Detects programming languages and analyzes code structure'
    },
    {
      icon: <Code className="h-8 w-8" />,
      title: 'Generate Tests',
      description: 'AI generates comprehensive unit tests using appropriate frameworks'
    },
    {
      icon: <BarChart3 className="h-8 w-8" />,
      title: 'Run & Report',
      description: 'Executes tests and generates coverage reports'
    }
  ];

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="text-center py-12">
        <div className="max-w-4xl mx-auto">
          <div className="flex justify-center mb-6">
            <div className="flex items-center space-x-3 bg-primary-100 px-4 py-2 rounded-full">
              <Code className="h-6 w-6 text-primary-600" />
              <span className="text-primary-700 font-medium">AI Unit Testing Agent</span>
            </div>
          </div>
          
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Automate Your Unit Testing
            <span className="text-primary-600"> with AI</span>
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Generate comprehensive unit tests for any GitHub repository using advanced AI models. 
            Support for multiple programming languages with automatic framework detection and coverage reporting.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <CheckCircle className="h-4 w-4 text-success-500" />
              <span>Free to use</span>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Clock className="h-4 w-4 text-primary-500" />
              <span>~5 minutes analysis</span>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Zap className="h-4 w-4 text-warning-500" />
              <span>Powered by AI</span>
            </div>
          </div>
        </div>
      </section>

      {/* Analysis Form */}
      <section>
        <AnalysisForm />
      </section>

      {/* Features Section */}
      <section id="features" className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Powerful Features
            </h2>
            <p className="text-lg text-gray-600">
              Everything you need for automated unit test generation
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="card hover:shadow-md transition-shadow duration-200">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="p-2 bg-primary-100 rounded-lg text-primary-600">
                    {feature.icon}
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900">{feature.title}</h3>
                </div>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Supported Languages */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Supported Languages & Frameworks
            </h2>
            <p className="text-lg text-gray-600">
              Automatic detection and support for popular programming languages
            </p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-6">
            {supportedLanguages.map((lang, index) => (
              <div key={index} className="text-center">
                <div className="text-4xl mb-2">{lang.icon}</div>
                <h3 className="font-semibold text-gray-900">{lang.name}</h3>
                <p className="text-sm text-gray-600">{lang.framework}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Process Section */}
      <section className="py-16 bg-primary-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-lg text-gray-600">
              Simple 4-step process to generate comprehensive unit tests
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {processSteps.map((step, index) => (
              <div key={index} className="text-center">
                <div className="flex justify-center mb-4">
                  <div className="p-4 bg-white rounded-full shadow-sm text-primary-600">
                    {step.icon}
                  </div>
                </div>
                <div className="mb-2">
                  <span className="inline-flex items-center justify-center w-8 h-8 bg-primary-600 text-white rounded-full text-sm font-medium">
                    {index + 1}
                  </span>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{step.title}</h3>
                <p className="text-gray-600">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 text-center">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Ready to Automate Your Testing?
          </h2>
          <p className="text-lg text-gray-600 mb-8">
            Get started with AI-powered unit test generation in minutes. 
            No setup required, just provide a GitHub URL and your OpenRouter API key.
          </p>
          <a
            href="#top"
            className="btn-primary text-lg px-8 py-3"
          >
            Start Analysis Now
          </a>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
