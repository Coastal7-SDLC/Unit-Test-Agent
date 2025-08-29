import React from 'react';
import { Link } from 'react-router-dom';
import { Code, Zap, BarChart3 } from 'lucide-react';

const Header = () => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <Code className="h-8 w-8 text-primary-600" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">AI Unit Testing Agent</h1>
                <p className="text-sm text-gray-600">Automated Test Generation</p>
              </div>
            </div>
          </Link>
          
          <nav className="hidden md:flex items-center space-x-6">
            <Link 
              to="/" 
              className="text-gray-600 hover:text-primary-600 transition-colors duration-200"
            >
              Home
            </Link>
            <a 
              href="#features" 
              className="text-gray-600 hover:text-primary-600 transition-colors duration-200"
            >
              Features
            </a>
            <a 
              href="#about" 
              className="text-gray-600 hover:text-primary-600 transition-colors duration-200"
            >
              About
            </a>
          </nav>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Zap className="h-4 w-4" />
              <span>Powered by AI</span>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <BarChart3 className="h-4 w-4" />
              <span>Free Tier</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
