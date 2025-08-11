import React from 'react';
import { 
  Activity, 
  Brain, 
  FileText, 
  Users, 
  TrendingUp, 
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

const Dashboard: React.FC = () => {
  const stats = [
    { label: 'Total Scans Analyzed', value: '2,847', change: '+12%', icon: Activity, color: 'blue' },
    { label: 'Active Patients', value: '456', change: '+8%', icon: Users, color: 'green' },
    { label: 'Reports Generated', value: '1,234', change: '+15%', icon: FileText, color: 'purple' },
    { label: 'AI Accuracy Rate', value: '97.8%', change: '+2.1%', icon: Brain, color: 'teal' }
  ];

  const recentActivity = [
    { type: 'MRI', patient: 'Patient #2847', time: '2 minutes ago', status: 'completed' },
    { type: 'CT Scan', patient: 'Patient #2846', time: '15 minutes ago', status: 'processing' },
    { type: 'X-Ray', patient: 'Patient #2845', time: '1 hour ago', status: 'completed' },
    { type: 'MRI', patient: 'Patient #2844', time: '2 hours ago', status: 'completed' }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Dashboard Overview</h2>
        <p className="text-gray-600">Welcome back, Dr. Smith. Here's your medical imaging summary.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div
              key={index}
              className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow duration-200"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                  <p className={`text-sm font-medium mt-1 text-${stat.color}-600`}>
                    <TrendingUp className="w-4 h-4 inline mr-1" />
                    {stat.change}
                  </p>
                </div>
                <div className={`w-12 h-12 bg-${stat.color}-100 rounded-lg flex items-center justify-center`}>
                  <Icon className={`w-6 h-6 text-${stat.color}-600`} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Clock className="w-5 h-5 mr-2 text-blue-600" />
              Recent Activity
            </h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {recentActivity.map((activity, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    {activity.status === 'completed' ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-yellow-500" />
                    )}
                    <div>
                      <p className="font-medium text-gray-900">{activity.type} Analysis</p>
                      <p className="text-sm text-gray-500">{activity.patient}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-500">{activity.time}</p>
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                      activity.status === 'completed' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {activity.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Quick Actions</h3>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-2 gap-4">
              <button className="flex flex-col items-center p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors duration-200">
                <Brain className="w-8 h-8 text-blue-600 mb-2" />
                <span className="text-sm font-medium text-blue-900">New MRI Analysis</span>
              </button>
              <button className="flex flex-col items-center p-4 bg-teal-50 rounded-lg hover:bg-teal-100 transition-colors duration-200">
                <Activity className="w-8 h-8 text-teal-600 mb-2" />
                <span className="text-sm font-medium text-teal-900">CT Scan Review</span>
              </button>
              <button className="flex flex-col items-center p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors duration-200">
                <FileText className="w-8 h-8 text-purple-600 mb-2" />
                <span className="text-sm font-medium text-purple-900">Generate Report</span>
              </button>
              <button className="flex flex-col items-center p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors duration-200">
                <Users className="w-8 h-8 text-green-600 mb-2" />
                <span className="text-sm font-medium text-green-900">Patient Manager</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;