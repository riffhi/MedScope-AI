import { useState } from "react";
import Header from "./components/Header";
import LandingHeader from "./components/LandingHeader";
import LandingPage from "./components/LandingPage";
import LoginModal from "./components/LoginModal";
import SignupModal from "./components/SignupModal";
import Sidebar from "./Sidebar";
import Dashboard from "./components/Dashboard";
import Visualization3D from "./Visualization3D";
import ReportAnalyzer from "./components/ReportAnalyzer";
import Feedback from "./components/Feedback";

interface User {
  email: string;
  name: string;
  role?: string;
  organization?: string;
}

interface UserData {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  confirmPassword: string;
  organization: string;
  role: string;
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [activeTab, setActiveTab] = useState("dashboard");
  const [currentLanguage, setCurrentLanguage] = useState("en");
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showSignupModal, setShowSignupModal] = useState(false);
  const [user, setUser] = useState<User | null>(null);

  const handleLogin = (email: string) => {
    // Simulate login - in real app, this would call your API
    setUser({ email, name: "Dr. Smith" });
    setIsAuthenticated(true);
    setShowLoginModal(false);
  };

  const handleSignup = (userData: UserData) => {
    // Simulate signup - in real app, this would call your API
    setUser({
      email: userData.email,
      name: `${userData.firstName} ${userData.lastName}`,
      role: userData.role,
      organization: userData.organization,
    });
    setIsAuthenticated(true);
    setShowSignupModal(false);
  };

  const handleLogout = () => {
    setUser(null);
    setIsAuthenticated(false);
    setActiveTab("dashboard");
  };

  const renderContent = () => {
    switch (activeTab) {
      case "dashboard":
        return <Dashboard />;
      case "visualization":
        return <Visualization3D />;
      case "analyzer":
        return <ReportAnalyzer />;
      case "feedback":
        return <Feedback />;
      default:
        return <Dashboard />;
    }
  };

  // Show landing page if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen">
        <LandingHeader
          currentLanguage={currentLanguage}
          onLanguageChange={setCurrentLanguage}
          onLogin={() => setShowLoginModal(true)}
          onSignup={() => setShowSignupModal(true)}
        />

        <LandingPage onGetStarted={() => setShowSignupModal(true)} />

        <LoginModal
          isOpen={showLoginModal}
          onClose={() => setShowLoginModal(false)}
          onLogin={handleLogin}
          onSwitchToSignup={() => {
            setShowLoginModal(false);
            setShowSignupModal(true);
          }}
        />

        <SignupModal
          isOpen={showSignupModal}
          onClose={() => setShowSignupModal(false)}
          onSignup={handleSignup}
          onSwitchToLogin={() => {
            setShowSignupModal(false);
            setShowLoginModal(true);
          }}
        />
      </div>
    );
  }

  // Show main application if authenticated
  return (
    <div className="min-h-screen bg-slate-900">
      <Header
        currentLanguage={currentLanguage}
        onLanguageChange={setCurrentLanguage}
        user={user}
        onLogout={handleLogout}
      />

      <div className="flex">
        <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />

        <main className="flex-1">{renderContent()}</main>
      </div>
    </div>
  );
}

export default App;
