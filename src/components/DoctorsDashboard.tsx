import React, { useState, useEffect } from "react";
import {
  Activity,
  Brain,
  FileText,
  Users,
  Clock,
  CheckCircle,
  AlertCircle,
  Search,
  Filter,
  Download,
  Eye,
  RefreshCw,
} from "lucide-react";
import { Client, Databases, Storage, Query, type Models } from 'appwrite';

const client = new Client();
client
  .setEndpoint(import.meta.env.VITE_APPWRITE_ENDPOINT) 
  .setProject(import.meta.env.VITE_APPWRITE_PROJECT_ID); 

const databases = new Databases(client);
const storage = new Storage(client);

const DATABASE_ID = import.meta.env.VITE_APPWRITE_DATABASE_ID;
const COLLECTION_ID = import.meta.env.VITE_APPWRITE_SCANS_COLLECTION_ID;
const BUCKET_ID = import.meta.env.VITE_APPWRITE_BUCKET_ID;

// Define the Report interface, extending Appwrite's Document model for type safety
interface Report extends Models.Document {
  type: string;
  patient: string;
  patientName: string;
  time: string;
  date: string;
  status: 'completed' | 'processing' | 'failed'; // Use specific string literal types for status
  diagnosis: string;
  doctor: string;
  fileId?: string; 
}

const DoctorDashboard: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedFilter, setSelectedFilter] = useState("all");
  const [isLoading, setIsLoading] = useState(false);
  const [reports, setReports] = useState<Report[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Helper function to format time (e.g., "5 minutes ago")
  const formatTime = (dateString: string): string => {
    const now = new Date();
    const date = new Date(dateString);
    const diffInMs = now.getTime() - date.getTime();
    const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
    const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
    const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));

    if (diffInMinutes < 60) {
      return `${diffInMinutes} minute${diffInMinutes !== 1 ? 's' : ''} ago`;
    } else if (diffInHours < 24) {
      return `${diffInHours} hour${diffInHours !== 1 ? 's' : ''} ago`;
    } else {
      return `${diffInDays} day${diffInDays !== 1 ? 's' : ''} ago`;
    }
  };

  // Sample data fallback
  const getSampleData = (): Report[] => [
    {
      $id: "RPT-2847",
      $createdAt: new Date(new Date().getTime() - 2 * 60 * 1000).toISOString(),
      $updatedAt: '',
      $collectionId: COLLECTION_ID,
      $databaseId: DATABASE_ID,
      type: "MRI",
      patient: "Patient #2847",
      patientName: "John Smith",
      time: "2 minutes ago",
      date: "2025-08-11",
      status: "completed",
      diagnosis: "Normal brain scan",
      doctor: "Dr. Smith",
      fileId: "sample-file-1"
    },
    {
      $id: "RPT-2846",
      $createdAt: new Date(new Date().getTime() - 15 * 60 * 1000).toISOString(),
      $updatedAt: '',
      $collectionId: COLLECTION_ID,
      $databaseId: DATABASE_ID,
      type: "CT Scan",
      patient: "Patient #2846",
      patientName: "Jane Doe",
      time: "15 minutes ago",
      date: "2025-08-11",
      status: "processing",
      diagnosis: "Pending analysis",
      doctor: "Dr. Smith",
      fileId: "sample-file-2"
    },
    {
      $id: "RPT-2845",
      $createdAt: new Date(new Date().getTime() - 60 * 60 * 1000).toISOString(),
      $updatedAt: '',
      $collectionId: COLLECTION_ID,
      $databaseId: DATABASE_ID,
      type: "X-Ray",
      patient: "Patient #2845",
      patientName: "Bob Johnson",
      time: "1 hour ago",
      date: "2025-08-11",
      status: "completed",
      diagnosis: "Fractured rib",
      doctor: "Dr. Smith",
      fileId: "sample-file-3"
    },
  ];

  // Primary effect hook for fetching and filtering reports
  useEffect(() => {
    let queries = [
      Query.orderDesc('$createdAt'),
      Query.limit(50) 
    ];

    // Apply filters based on state
    if (selectedFilter !== 'all') {
        queries.push(Query.equal('status', selectedFilter));
        queries.push(Query.equal('type', selectedFilter));
    }
    
    // Apply search query if a search term is present
    if (searchTerm.length > 2) {
      queries.push(Query.search('patientName', searchTerm));
    }
    
    // Debounce the search to prevent excessive API calls
    const delayedFetch = setTimeout(async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await databases.listDocuments(
          DATABASE_ID,
          COLLECTION_ID,
          queries
        );

        const fetchedReports: Report[] = response.documents.map((doc: any) => ({
          ...doc, // Spread all Appwrite document properties
          $id: doc.$id,
          type: doc.scanType || doc.type,
          patientName: doc.patientName,
          time: formatTime(doc.$createdAt),
          date: new Date(doc.$createdAt).toISOString().split('T')[0],
          status: doc.status as Report['status'], // Type assertion
          diagnosis: doc.diagnosis || 'Pending analysis',
          doctor: doc.doctorName || 'Dr. Smith',
        }));
        
        setReports(fetchedReports);
      } catch (err: any) {
        console.error('Error fetching reports:', err);
        setError(err.message || 'Failed to fetch reports from Appwrite');
        setReports(getSampleData()); // Fallback to sample data
      } finally {
        setIsLoading(false);
      }
    }, searchTerm ? 300 : 0); // Apply 300ms debounce on search

    return () => clearTimeout(delayedFetch);
  }, [searchTerm, selectedFilter]);

  // Handle refresh
  const handleRefresh = () => {
    // A simple way to trigger a re-fetch is to change a state variable,
    // which in turn triggers the useEffect hook.
    setSearchTerm("");
    setSelectedFilter("all");
  };

  // Handle view report
  const handleViewReport = (report: Report) => {
    if (report.fileId) {
      try {
        const fileUrl = storage.getFilePreview(BUCKET_ID, report.fileId);
        window.open(fileUrl.toString(), '_blank');
      } catch (err) {
        console.error('Error viewing report:', err);
      }
    } else {
      alert(`Report ${report.$id} has no associated file.`);
    }
  };

  // Handle download report
  const handleDownloadReport = (report: Report) => {
    if (report.fileId) {
      try {
        const downloadUrl = storage.getFileDownload(BUCKET_ID, report.fileId);
        const link = document.createElement('a');
        link.href = downloadUrl.toString();
        link.download = `${report.$id}-${report.type}-${report.patientName}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } catch (err) {
        console.error('Error downloading report:', err);
      }
    } else {
      alert(`Report ${report.$id} has no associated file.`);
    }
  };

  return (
    <div className="bg-slate-900 text-slate-100 min-h-screen">
      {/* Header Section */}
      <div className="bg-gradient-to-r from-slate-800 to-slate-900 border-b border-slate-700 px-6 py-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white mb-1">
              Medical Dashboard
            </h1>
            <p className="text-slate-400">
              Welcome back •{" "}
              {new Date().toLocaleDateString("en-US", {
                weekday: "long",
                year: "numeric",
                month: "long",
                day: "numeric",
              })}
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="bg-slate-800/50 px-4 py-2 rounded-lg border border-slate-700">
              <span className="text-sm text-slate-400">Current Time:</span>
              <span className="text-white font-mono ml-2">
                {new Date().toLocaleTimeString()}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="px-6 pb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-slate-800/60 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50 hover:border-slate-600 transition-all duration-300">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-400 mb-1">
                  Total Scans Analyzed
                </p>
                <p className="text-3xl font-bold text-white">{reports.length}</p>
                <div className="flex items-center mt-2">
                  <span className="text-emerald-400 text-sm font-medium">
                    +12%
                  </span>
                  <span className="text-slate-500 text-sm ml-2">
                    vs last month
                  </span>
                </div>
              </div>
              <div className="bg-blue-500/20 p-3 rounded-lg border border-blue-500/30">
                <Activity className="h-6 w-6 text-blue-400" />
              </div>
            </div>
          </div>

          <div className="bg-slate-800/60 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50 hover:border-slate-600 transition-all duration-300">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-400 mb-1">
                  Active Patients
                </p>
                <p className="text-3xl font-bold text-white">
                  {new Set(reports.map(r => r.patientName)).size}
                </p>
                <div className="flex items-center mt-2">
                  <span className="text-emerald-400 text-sm font-medium">
                    +8%
                  </span>
                  <span className="text-slate-500 text-sm ml-2">this week</span>
                </div>
              </div>
              <div className="bg-emerald-500/20 p-3 rounded-lg border border-emerald-500/30">
                <Users className="h-6 w-6 text-emerald-400" />
              </div>
            </div>
          </div>

          <div className="bg-slate-800/60 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50 hover:border-slate-600 transition-all duration-300">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-400 mb-1">
                  Reports Generated
                </p>
                <p className="text-3xl font-bold text-white">
                  {reports.filter(r => r.status === 'completed').length}
                </p>
                <div className="flex items-center mt-2">
                  <span className="text-emerald-400 text-sm font-medium">
                    +15%
                  </span>
                  <span className="text-slate-500 text-sm ml-2">
                    this month
                  </span>
                </div>
              </div>
              <div className="bg-purple-500/20 p-3 rounded-lg border border-purple-500/30">
                <FileText className="h-6 w-6 text-purple-400" />
              </div>
            </div>
          </div>

          <div className="bg-slate-800/60 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50 hover:border-slate-600 transition-all duration-300">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-400 mb-1">
                  AI Accuracy Rate
                </p>
                <p className="text-3xl font-bold text-white">97.8%</p>
                <div className="flex items-center mt-2">
                  <span className="text-emerald-400 text-sm font-medium">
                    +2.1%
                  </span>
                  <span className="text-slate-500 text-sm ml-2">optimized</span>
                </div>
              </div>
              <div className="bg-teal-500/20 p-3 rounded-lg border border-teal-500/30">
                <Brain className="h-6 w-6 text-teal-400" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="px-6 space-y-6">
        <div className="w-full max-w-full">
          <div className="bg-slate-800/60 backdrop-blur-sm rounded-xl border border-slate-700/50">
            <div className="p-6 border-b border-slate-700/50">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white flex items-center">
                  <Clock className="w-5 h-5 mr-2 text-blue-400" />
                  Recent Reports & Activity
                </h3>
                <button
                  onClick={handleRefresh}
                  className="p-2 text-slate-400 hover:text-blue-400 hover:bg-slate-700/50 rounded-lg transition-colors duration-200"
                  disabled={isLoading}
                >
                  <RefreshCw
                    className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`}
                  />
                </button>
              </div>

              {error && (
                <div className="mb-4 p-3 bg-red-500/20 border border-red-500/30 rounded-lg">
                  <p className="text-red-400 text-sm">
                    Error: {error}. Showing sample data.
                  </p>
                </div>
              )}

              <div className="flex flex-col sm:flex-row gap-3">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
                  <input
                    type="text"
                    placeholder="Search by patient name, report ID, or diagnosis..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-sm"
                  />
                </div>

                <div className="relative">
                  <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
                  <select
                    value={selectedFilter}
                    onChange={(e) => setSelectedFilter(e.target.value)}
                    className="pl-10 pr-8 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-sm"
                  >
                    <option value="all">All Reports</option>
                    <option value="completed">Completed</option>
                    <option value="processing">Processing</option>
                    <option value="mri">MRI</option>
                    <option value="ct scan">CT Scan</option>
                    <option value="x-ray">X-Ray</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="p-6">
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <RefreshCw className="w-6 h-6 text-blue-400 animate-spin" />
                  <span className="ml-2 text-slate-400">
                    Loading reports...
                  </span>
                </div>
              ) : reports.length > 0 ? (
                <div className="space-y-4">
                  {reports.map((report) => (
                    <div
                      key={report.$id}
                      className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg hover:bg-slate-700/50 transition-colors duration-200 border border-slate-700/50"
                    >
                      <div className="flex items-center space-x-3">
                        {report.status === "completed" ? (
                          <CheckCircle className="w-5 h-5 text-emerald-400" />
                        ) : (
                          <AlertCircle className="w-5 h-5 text-amber-400" />
                        )}
                        <div>
                          <div className="flex items-center space-x-2">
                            <p className="font-medium text-white">
                              {report.type} Analysis
                            </p>
                            <span className="text-xs text-slate-400 bg-slate-700/50 px-2 py-1 rounded border border-slate-600">
                              {report.$id}
                            </span>
                          </div>
                          <p className="text-sm text-slate-300">
                            {report.patientName}
                          </p>
                          <p className="text-xs text-slate-400">
                            {report.diagnosis}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center space-x-2">
                        <div className="text-right mr-3">
                          <p className="text-sm text-slate-400">
                            {report.time}
                          </p>
                          <span
                            className={`inline-flex px-2 py-1 text-xs font-medium rounded-full border ${
                              report.status === "completed"
                                ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                                : "bg-amber-500/20 text-amber-400 border-amber-500/30"
                            }`}
                          >
                            {report.status}
                          </span>
                        </div>

                        <div className="flex space-x-1">
                          <button
                            onClick={() => handleViewReport(report)}
                            className="p-2 text-slate-400 hover:text-blue-400 hover:bg-slate-700/50 rounded transition-colors duration-200"
                            title="View Report"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          {report.status === "completed" && (
                            <button
                              onClick={() => handleDownloadReport(report)}
                              className="p-2 text-slate-400 hover:text-emerald-400 hover:bg-slate-700/50 rounded transition-colors duration-200"
                              title="Download Report"
                            >
                              <Download className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <FileText className="w-12 h-12 text-slate-500 mx-auto mb-3" />
                  <p className="text-slate-400">No reports found</p>
                  <p className="text-sm text-slate-500">
                    Try adjusting your search or filter criteria
                  </p>
                </div>
              )}

              {reports.length > 6 && (
                <div className="mt-4 text-center">
                  <button className="text-blue-400 hover:text-blue-300 font-medium text-sm">
                    View All Reports ({reports.length})
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="pb-8"></div>
    </div>
  );
};

export default DoctorDashboard;