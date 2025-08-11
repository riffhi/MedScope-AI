import React, { useState } from 'react';
import Header from './components/Header';
import Sidebar from './Sidebar';
import Dashboard from './components/Dashboard';
import Visualization3D from './Visualization3D';
import ReportAnalyzer from './components/ReportAnalyzer';
import Chatbot from './components/Chatbot';
import Feedback from './components/Feedback';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [currentLanguage, setCurrentLanguage] = useState('en');

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'visualization':
        return <Visualization3D />;
      case 'analyzer':
        return <ReportAnalyzer />;
      case 'chatbot':
        return <Chatbot />;
      case 'feedback':
        return <Feedback />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header currentLanguage={currentLanguage} onLanguageChange={setCurrentLanguage} />
      
      <div className="flex">
        <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
        
        <main className="flex-1 p-8">
          {renderContent()}
        </main>
      </div>
    </div>
  );
}

export default App;