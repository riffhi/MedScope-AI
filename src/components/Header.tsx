import React from "react";
import { User as UserIcon, LogOut } from "lucide-react";

// Define the structure for the User object
interface UserType {
  email: string;
  name: string;
  role?: string;
  organization?: string;
}

// Define the props for the Header component
interface HeaderProps {
  user?: UserType | null;
  onLogout?: () => void;
}

const Header: React.FC<HeaderProps> = ({ user, onLogout }) => {
  return (
    <header className="bg-slate-900 shadow-lg border-b border-slate-700 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Logo and Application Title */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center shadow-lg border border-blue-400/30">
              <span className="text-white font-bold text-lg">M</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">MedScope AI</h1>
              <p className="text-sm text-slate-400">
                Medical Imaging Intelligence
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          {/* Profile */}
          <div className="relative">
            <button className="flex items-center space-x-2 p-2 text-slate-400 hover:text-blue-400 hover:bg-slate-800 rounded-lg transition-colors duration-200">
              <UserIcon className="w-5 h-5" />
              <span className="text-sm font-medium text-slate-200">
                {user?.name || "User"}
              </span>
            </button>
          </div>

          {/* Logout Button */}
          {onLogout && (
            <button
              onClick={onLogout}
              className="flex items-center space-x-2 p-2 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-lg transition-colors duration-200"
            >
              <LogOut className="w-5 h-5" />
              <span className="text-sm font-medium">Logout</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
