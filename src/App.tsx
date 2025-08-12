import { useState } from "react";
import Header from "./components/Header";
import LandingHeader from "./components/LandingHeader";
import LandingPage from "./components/LandingPage";
import LoginModal from "./components/LoginModal";
import SignupModal from "./components/SignupModal";
import Sidebar from "./Sidebar";
import DoctorDashboard from "./components/DoctorsDashboard";
import UserDashboard from "./components/UserDashboard";
import Visualization3D from "./Visualization3D";
import ReportAnalyzer from "./components/ReportAnalyzer";
import Feedback from "./components/Feedback";
import FindMRICentre from "./components/FindMRICentre";
import FloatingAIChatbot from "./components/FloatingAIChatbot";

// Define the User and UserData types for type safety
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
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showSignupModal, setShowSignupModal] = useState(false);
  const [user, setUser] = useState<User | null>(null);

  const handleLogin = (email: string) => {
    // Simulate login for a doctor
    setUser({ email, name: "Dr. Smith", role: "doctor" });
    setIsAuthenticated(true);
    setShowLoginModal(false);
    setActiveTab("dashboard");
  };

  const handleSignup = (userData: UserData) => {
    // Simulate signup
    setUser({
      email: userData.email,
      name: `${userData.firstName} ${userData.lastName}`,
      role: userData.role,
      organization: userData.organization,
    });
    setIsAuthenticated(true);
    setShowSignupModal(false);
    setActiveTab("dashboard");
  };

  const handleLogout = () => {
    setUser(null);
    setIsAuthenticated(false);
    setActiveTab("dashboard");
  };

  // Renders the main content based on the active sidebar tab and user role
  const renderContent = () => {
    const isDoctor = user?.role && user.role !== "patient";

    if (isDoctor) {
      switch (activeTab) {
        case "dashboard":
          return <DoctorDashboard />;
        case "visualization":
          return <Visualization3D />;
        case "scan-analysis":
          return <ReportAnalyzer />;
        case "feedback":
          return <Feedback />;
        default:
          return <DoctorDashboard />;
      }
    } else {
      // Patient View
      switch (activeTab) {
        case "dashboard":
          return <UserDashboard user={user} />;
        case "find-centre":
          return <FindMRICentre />;
        case "feedback":
          return <Feedback />;
        default:
          return <UserDashboard user={user} />;
      }
    }
  };

  // --- View for Unauthenticated (Logged-Out) Users ---
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50">
        <LandingHeader
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

  return (
    <div className="min-h-screen bg-slate-900">
      <Header user={user} onLogout={handleLogout} />

      <div className="flex">
        <Sidebar
          activeTab={activeTab}
          onTabChange={setActiveTab}
          userRole={user?.role}
        />
        <main className="flex-1 p-6">{renderContent()}</main>
      </div>

      {/* Floating AI Chatbot - appears on all authenticated pages */}
      <FloatingAIChatbot />
    </div>
  );
}

export default App;
