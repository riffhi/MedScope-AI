import React from "react";
import { LayoutDashboard, Star, Eye, Zap, Scan, MapPin } from "lucide-react";

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  userRole?: string;
}

const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onTabChange,
  userRole,
}) => {
  const doctorMenuItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "visualization", label: "2D to 3D Viewer", icon: Eye },
    { id: "scan-analysis", label: "Medical Scan Analysis", icon: Scan },
    { id: "feedback", label: "Feedback", icon: Star },
  ];

  const userMenuItems = [
    { id: "dashboard", label: "My Dashboard", icon: LayoutDashboard },
    { id: "find-centre", label: "Find MRI Centre", icon: MapPin },
    { id: "visualization", label: "2D to 3D Viewer", icon: Eye },
    { id: "scan-analysis", label: "Medical Scan Analysis", icon: Scan },
    { id: "feedback", label: "Feedback", icon: Star },
  ];

  const menuItems = userRole === "patient" ? userMenuItems : doctorMenuItems;

  return (
    <aside className="w-64 bg-slate-900 shadow-2xl border-r border-slate-700 h-screen sticky top-0">
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
                      ? "bg-blue-600/20 text-blue-400 border-r-4 border-blue-500 shadow-lg"
                      : "text-slate-300 hover:bg-slate-800 hover:text-blue-400"
                  }`}
                >
                  <Icon
                    className={`w-5 h-5 ${
                      isActive ? "text-blue-400" : "text-slate-400"
                    }`}
                  />
                  <span className="font-medium">{item.label}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-700">
        <div className="flex items-center space-x-3 p-3 bg-gradient-to-r from-slate-800 to-slate-700 rounded-lg border border-slate-600/50">
          <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full flex items-center justify-center shadow-lg">
            <Zap className="w-4 h-4 text-white" />
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
