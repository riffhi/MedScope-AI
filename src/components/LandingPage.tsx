import React from "react";
import { motion } from "framer-motion"; // Import framer-motion
import {
  Brain,
  Activity,
  Eye,
  FileText,
  Users,
  Shield,
  Zap,
  ArrowRight,
  Code,
} from "lucide-react";

const LandingPage = ({ onGetStarted }) => {
  const features = [
    {
      icon: <Brain className="w-8 h-8 text-cyan-400" />,
      title: "AI-Powered Analysis",
      description:
        "Utilizes machine learning algorithms for medical image analysis and diagnosis assistance.",
    },
    {
      icon: <Eye className="w-8 h-8 text-emerald-400" />,
      title: "3D Visualization",
      description:
        "Convert 2D medical scans into interactive 3D models for better understanding and analysis.",
    },
    {
      icon: <FileText className="w-8 h-8 text-violet-400" />,
      title: "Report Analysis",
      description:
        "Intelligent parsing and analysis of medical reports with AI-powered insights.",
    },
    {
      icon: <Activity className="w-8 h-8 text-rose-400" />,
      title: "Real-time Monitoring",
      description:
        "Demonstrates continuous monitoring of data with instant alerts and recommendations.",
    },
    {
      icon: <Users className="w-8 h-8 text-amber-400" />,
      title: "Collaborative Platform",
      description:
        "Enables seamless collaboration between users with shared access to data and insights.",
    },
    {
      icon: <Shield className="w-8 h-8 text-lime-400" />,
      title: "Secure & Private",
      description:
        "Built with a focus on data security to handle sensitive information responsibly.",
    },
  ];

  const principles = [
    {
      icon: <Brain className="w-8 h-8 text-cyan-400" />,
      title: "AI Powered",
      description: "Leveraging advanced machine learning models.",
      color: "from-cyan-500 to-violet-500",
    },
    {
      icon: <Eye className="w-8 h-8 text-emerald-400" />,
      title: "Intuitive Visualization",
      description: "Interactive and insightful 3D data representation.",
      color: "from-emerald-500 to-lime-500",
    },
    {
      icon: <Users className="w-8 h-8 text-amber-400" />,
      title: "Student Developed",
      description: "A passion project by aspiring engineers.",
      color: "from-amber-500 to-rose-500",
    },
    {
      icon: <Zap className="w-8 h-8 text-yellow-400" />,
      title: "Accessible Anytime",
      description: "A robust and always-available platform concept.",
      color: "from-yellow-500 to-orange-500",
    },
  ];
  
  // Animation variants for staggering children
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5,
      },
    },
  };
  
  const sectionVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        ease: "easeOut",
      },
    },
  };


  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-gray-900 to-black text-white">
      {/* Hero Section */}
      <section className="relative pt-20 pb-32 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="text-4xl sm:text-6xl font-bold mb-8"
            >
              Exploring the Future of{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-violet-400">
                Medical AI
              </span>
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-xl text-gray-300 mb-12 max-w-3xl mx-auto"
            >
              MedScope-AI is a student-led project exploring cutting-edge
              artificial intelligence, 3D visualization, and medical analysis
              tools.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.4 }}
            >
              <button
                onClick={onGetStarted}
                className="bg-gradient-to-r from-cyan-500 to-violet-600 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:from-cyan-400 hover:to-violet-500 transition-all duration-300 flex items-center gap-2 transform hover:scale-105 shadow-lg hover:shadow-cyan-500/25 mx-auto"
              >
                Get Started
                <ArrowRight className="w-5 h-5" />
              </button>
            </motion.div>
          </div>

          {/* Principles Section - Horizontal */}
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 pt-24"
          >
            {principles.map((item, index) => (
              <motion.div
                key={index}
                variants={itemVariants}
                className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 p-6 rounded-xl flex flex-col text-left space-y-4 h-full"
              >
                <div className="flex-shrink-0 bg-gray-900 p-3 rounded-full w-fit">
                  {item.icon}
                </div>
                <div className="flex-grow">
                  <p className="font-semibold text-white text-lg">
                    {item.title}
                  </p>
                  <p className="text-sm text-gray-400">{item.description}</p>
                </div>
                <div
                  className={`h-1.5 w-full rounded-full bg-gradient-to-r ${item.color}`}
                ></div>
              </motion.div>
            ))}
          </motion.div>
        </div>
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-gray-900/50 pointer-events-none"></div>
      </section>

      {/* --- Features Section --- */}
      <hr className="border-gray-800" />
      <motion.section
        variants={sectionVariants}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.2 }}
        className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-900/50 backdrop-blur-sm"
      >
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
              Powerful Features
            </h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Comprehensive tools designed to showcase how technology can
              enhance medical practice.
            </p>
          </div>
          <motion.div
             variants={containerVariants}
             initial="hidden"
             whileInView="visible"
             viewport={{ once: true, amount: 0.2 }}
             className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                variants={itemVariants}
                className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-xl p-8 hover:bg-gray-800/70 hover:border-gray-600/50 hover:shadow-lg hover:shadow-cyan-500/10 transition-all duration-300 group"
              >
                <div className="mb-4 group-hover:scale-110 transition-transform duration-300">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-white mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-300">{feature.description}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </motion.section>

      {/* --- About Us Section (Improved UI) --- */}
      <hr className="border-gray-800" />
      <section className="py-24 px-4 sm:px-6 lg:px-8 bg-black overflow-hidden">
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          {/* Left Column: Text */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.6 }}
            className="text-left"
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
              About The Project
            </h2>
            <div className="text-lg text-gray-300 space-y-4">
              <p>
                MedScope-AI is a portfolio project from Loni Kalbhor,
                Maharashtra, developed by passionate computer science students.
                Our goal was to apply our knowledge of AI and software
                development to a challenging, meaningful problem in healthcare.
              </p>
              <p>
                Our mission is to demonstrate AI's potential in assisting
                medical professionals with image analysis. Built with React,
                Python, and TensorFlow, this project represents our cumulative
                skills in creating modern, scalable applications.
              </p>
            </div>
          </motion.div>

          {/* Right Column: Visual Collage */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.6 }}
            className="relative w-full h-80 flex items-center justify-center lg:h-96"
          >
            <motion.div
              animate={{ rotate: -6 }}
              transition={{ type: "spring" }}
              className="absolute w-full h-full bg-gradient-to-br from-cyan-900/40 to-violet-900/40 rounded-3xl"
            ></motion.div>

            {[
              { icon: <Brain className="w-10 h-10 text-cyan-400" />, pos: "top-8 left-8 sm:left-16", delay: 0.2 },
              { icon: <Eye className="w-12 h-12 text-emerald-400" />, pos: "bottom-8 right-8 sm:right-16", delay: 0.3 },
              { icon: <Users className="w-8 h-8 text-amber-400" />, pos: "bottom-24 left-20 sm:left-32", delay: 0.4 },
              { icon: <Code className="w-10 h-10 text-violet-400" />, pos: "top-16 right-20 sm:right-32", delay: 0.5 },
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, scale: 0.5 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: item.delay }}
                className={`absolute ${item.pos} bg-gray-800/80 backdrop-blur-sm p-4 rounded-full shadow-lg`}
              >
                {item.icon}
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* --- CTA Section --- */}
      <hr className="border-gray-800" />
      <motion.section
        variants={sectionVariants}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.5 }}
        className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-900/50"
      >
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-8">
            Ready to See Our Project in Action?
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            Explore the potential of AI in medical imaging. Get started with our
            tool demonstration.
          </p>
          <button
            onClick={onGetStarted}
            className="bg-gradient-to-r from-cyan-500 to-violet-600 text-white px-10 py-4 rounded-lg font-semibold text-lg hover:from-cyan-400 hover:to-violet-500 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-cyan-500/25"
          >
            Try the Demo
          </button>
        </div>
      </motion.section>
    </div>
  );
};

export default LandingPage;