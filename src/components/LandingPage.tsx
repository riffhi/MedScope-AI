import React from "react";
import {
  Brain,
  Activity,
  Eye,
  FileText,
  Users,
  Shield,
  Zap,
  ArrowRight,
  Play,
  CheckCircle,
  Star,
} from "lucide-react";

interface LandingPageProps {
  onGetStarted: () => void;
}

const LandingPage: React.FC<LandingPageProps> = ({ onGetStarted }) => {
  const features = [
    {
      icon: <Brain className="w-8 h-8 text-blue-600" />,
      title: "AI-Powered Analysis",
      description:
        "Advanced machine learning algorithms for accurate medical image analysis and diagnosis assistance.",
    },
    {
      icon: <Eye className="w-8 h-8 text-green-600" />,
      title: "3D Visualization",
      description:
        "Convert 2D medical scans into interactive 3D models for better understanding and analysis.",
    },
    {
      icon: <FileText className="w-8 h-8 text-purple-600" />,
      title: "Report Analysis",
      description:
        "Intelligent parsing and analysis of medical reports with AI-powered insights.",
    },
    {
      icon: <Activity className="w-8 h-8 text-red-600" />,
      title: "Real-time Monitoring",
      description:
        "Continuous monitoring of patient data with instant alerts and recommendations.",
    },
    {
      icon: <Users className="w-8 h-8 text-orange-600" />,
      title: "Collaborative Platform",
      description:
        "Seamless collaboration between healthcare professionals with shared access to data.",
    },
    {
      icon: <Shield className="w-8 h-8 text-indigo-600" />,
      title: "HIPAA Compliant",
      description:
        "Enterprise-grade security ensuring patient data privacy and regulatory compliance.",
    },
  ];

  const stats = [
    { number: "10,000+", label: "Medical Images Analyzed" },
    { number: "95%", label: "Accuracy Rate" },
    { number: "500+", label: "Healthcare Professionals" },
    { number: "24/7", label: "AI Support Available" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Hero Section */}
      <section className="relative pt-20 pb-32 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <h1 className="text-4xl sm:text-6xl font-bold text-gray-900 mb-8">
              The Future of{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
                Medical AI
              </span>
            </h1>
            <p className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto">
              MedScope-AI revolutionizes healthcare with cutting-edge artificial
              intelligence, 3D visualization, and comprehensive medical analysis
              tools designed for modern healthcare professionals.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
              <button
                onClick={onGetStarted}
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-300 flex items-center gap-2 transform hover:scale-105"
              >
                Get Started Free
                <ArrowRight className="w-5 h-5" />
              </button>
              <button className="border-2 border-gray-300 text-gray-700 px-8 py-4 rounded-lg font-semibold text-lg hover:border-gray-400 transition-colors duration-300 flex items-center gap-2">
                <Play className="w-5 h-5" />
                Watch Demo
              </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-20">
              {stats.map((stat, index) => (
                <div key={index} className="text-center">
                  <div className="text-3xl font-bold text-gray-900 mb-2">
                    {stat.number}
                  </div>
                  <div className="text-gray-600">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Powerful Features for Modern Healthcare
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Comprehensive tools designed to enhance medical practice and
              improve patient outcomes.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="bg-gray-50 rounded-xl p-8 hover:shadow-lg transition-shadow duration-300"
              >
                <div className="mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-7xl mx-auto">
          <div className="text-center text-white">
            <h2 className="text-3xl sm:text-4xl font-bold mb-8">
              Why Choose MedScope-AI?
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-12">
              <div className="text-center">
                <Zap className="w-12 h-12 text-yellow-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-3">Lightning Fast</h3>
                <p className="text-blue-100">
                  Get results in seconds, not hours. Our AI processes medical
                  data at unprecedented speeds.
                </p>
              </div>

              <div className="text-center">
                <CheckCircle className="w-12 h-12 text-green-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-3">Proven Accuracy</h3>
                <p className="text-blue-100">
                  95% accuracy rate validated by leading medical institutions
                  worldwide.
                </p>
              </div>

              <div className="text-center">
                <Star className="w-12 h-12 text-yellow-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-3">Award Winning</h3>
                <p className="text-blue-100">
                  Recognized by healthcare innovation awards and trusted by
                  professionals globally.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-900">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-8">
            Ready to Transform Your Medical Practice?
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            Join thousands of healthcare professionals who trust MedScope-AI for
            their medical analysis needs.
          </p>
          <button
            onClick={onGetStarted}
            className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-10 py-4 rounded-lg font-semibold text-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-300 transform hover:scale-105"
          >
            Start Your Free Trial
          </button>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
