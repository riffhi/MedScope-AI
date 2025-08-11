import React from 'react';
import { 
  LayoutDashboard, 
  Brain, 
  Scan, 
  FileText, 
  MessageCircle, 
  Star,
  Activity,
  Image,
  Eye,
  Zap
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'visualization', label: '2D to 3D Viewer', icon: Eye },
    { id: 'analyzer', label: 'Report Analyzer', icon: FileText },
    { id: 'chatbot', label: 'AI Assistant', icon: MessageCircle },
    { id: 'feedback', label: 'Feedback', icon: Star }
  ];

  return (
    <aside className="w-64 bg-white shadow-lg border-r border-gray-200 h-screen sticky top-0">
      <nav className="mt-8 px-4">
        <ul className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            
            return (
              <li key={item.id}>
                <button
                  onClick={() => onTabChange(item.id)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 text-left rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-blue-50 text-blue-700 border-r-4 border-blue-600'
                      : 'text-gray-700 hover:bg-gray-50 hover:text-blue-600'
                  }`}
                >
                  <Icon className={`w-5 h-5 ${isActive ? 'text-blue-600' : 'text-gray-500'}`} />
                  <span className="font-medium">{item.label}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>
      
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
        <div className="flex items-center space-x-3 p-3 bg-gradient-to-r from-blue-50 to-teal-50 rounded-lg">
          <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-teal-600 rounded-full flex items-center justify-center">
            <Zap className="w-4 h-4 text-white" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-900">AI Processing</p>
            <p className="text-xs text-gray-500">Ready</p>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;