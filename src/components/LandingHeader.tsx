import React from "react";
import { Microscope } from "lucide-react";

interface LandingHeaderProps {
  onLogin: () => void;
  onSignup: () => void;
}

const LandingHeader: React.FC<LandingHeaderProps> = ({
  onLogin,
  onSignup,
}) => {
  return (
    <header className="absolute top-0 left-0 right-0 z-40 bg-gray-900/90 backdrop-blur-sm border-b border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
              <Microscope className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">MedScope AI</h1>
            </div>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <a
              href="#features"
              className="text-gray-300 hover:text-blue-400 font-medium transition-colors"
            >
              Features
            </a>
            <a
              href="#about"
              className="text-gray-300 hover:text-blue-400 font-medium transition-colors"
            >
              About
            </a>
            <a
              href="#contact"
              className="text-gray-300 hover:text-blue-400 font-medium transition-colors"
            >
              Contact
            </a>
          </nav>

          {/* Right side */}
          <div className="flex items-center space-x-4">
            {/* Auth Buttons */}
            <div className="flex items-center space-x-3">
              <button
                onClick={onLogin}
                className="text-gray-300 hover:text-blue-400 font-medium transition-colors"
              >
                Sign In
              </button>
              <button
                onClick={onSignup}
                className="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-6 py-2 rounded-lg font-medium hover:from-blue-600 hover:to-purple-600 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-blue-500/25"
              >
                Sign Up
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default LandingHeader;