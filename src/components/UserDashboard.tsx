import React from "react";
import { FileText } from "lucide-react";

// Define the User type structure
interface User {
  name: string;
  email: string;
  role?: string;
}

interface UserDashboardProps {
  user: User | null;
}

// Sample data for the user's reports
const userReports = [
  {
    id: "RPT-101",
    type: "Brain MRI",
    date: "2025-08-10",
    status: "Completed",
  },
  {
    id: "RPT-102",
    type: "Chest X-Ray",
    date: "2025-07-22",
    status: "Completed",
  },
];

const UserDashboard: React.FC<UserDashboardProps> = ({ user }) => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white mb-1">
          Welcome, {user?.name || "User"}!
        </h1>
        <p className="text-slate-400">
          Here's a summary of your medical imaging activity.
        </p>
      </div>

      {/* Main Content */}
      <div className="bg-slate-800/60 rounded-xl border border-slate-700/50">
        <div className="p-6 border-b border-slate-700/50">
          <h3 className="text-lg font-semibold text-white flex items-center">
            <FileText className="w-5 h-5 mr-2 text-emerald-400" />
            My Recent Reports
          </h3>
        </div>
        <div className="p-6">
          {userReports.length > 0 ? (
            <div className="space-y-4">
              {userReports.map((report) => (
                <div
                  key={report.id}
                  className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg hover:bg-slate-700/50 transition-colors"
                >
                  <div>
                    <p className="font-medium text-white">{report.type}</p>
                    <p className="text-sm text-slate-400">
                      Date: {report.date}
                    </p>
                  </div>
                  <span className="text-sm bg-emerald-500/20 text-emerald-400 px-3 py-1 rounded-full font-medium">
                    {report.status}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <FileText className="w-12 h-12 text-slate-500 mx-auto mb-3" />
              <p className="text-slate-400">You have no reports yet.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UserDashboard;