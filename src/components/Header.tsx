import React from "react";
import { User, Globe, LogOut } from "lucide-react";

interface User {
  email: string;
  name: string;
  role?: string;
  organization?: string;
}

interface HeaderProps {
  currentLanguage: string;
  onLanguageChange: (lang: string) => void;
  user?: User | null;
  onLogout?: () => void;
}

const Header: React.FC<HeaderProps> = ({
  currentLanguage,
  onLanguageChange,
  user,
  onLogout,
}) => {
  const languages = [
    { code: "en", name: "English" },
    { code: "es", name: "Español" },
    { code: "fr", name: "Français" },
    { code: "de", name: "Deutsch" },
    { code: "zh", name: "中文" },
    { code: "ja", name: "日本語" },
    { code: "ar", name: "العربية" },
  ];

  return (
    <header className="bg-slate-900 shadow-lg border-b border-slate-700 px-6 py-4">
      <div className="flex items-center justify-between">
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
          {/* Language Selector */}
          <div className="relative">
            <select
              value={currentLanguage}
              onChange={(e) => onLanguageChange(e.target.value)}
              className="appearance-none bg-slate-800 border border-slate-600 rounded-lg px-4 py-2 pr-8 text-sm font-medium text-slate-200 hover:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {languages.map((lang) => (
                <option
                  key={lang.code}
                  value={lang.code}
                  className="bg-slate-800 text-slate-200"
                >
                  {lang.name}
                </option>
              ))}
            </select>
            <Globe className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
          </div>

          {/* Profile */}
          <div className="relative">
            <button className="flex items-center space-x-2 p-2 text-slate-400 hover:text-blue-400 hover:bg-slate-800 rounded-lg transition-colors duration-200">
              <User className="w-5 h-5" />
              <span className="text-sm font-medium text-slate-200">
                {user?.name || "User"}
              </span>
            </button>
          </div>

          {/* Logout */}
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
