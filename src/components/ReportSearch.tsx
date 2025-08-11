import React, { useState, useEffect, useCallback } from "react";
import {
  Search,
  Filter,
  Calendar,
  Download,
  Eye,
  RefreshCw,
  FileText,
} from "lucide-react";

interface Report {
  id: string;
  type: string;
  patient: string;
  patientName: string;
  time: string;
  date: string;
  status: "completed" | "processing" | "pending";
  diagnosis: string;
  doctor: string;
  createdAt?: string;
  updatedAt?: string;
}

interface ReportSearchProps {
  onViewReport?: (reportId: string) => void;
  onDownloadReport?: (reportId: string) => void;
}

// Sample data - this will be replaced with API calls to Flask backend
const sampleReports: Report[] = [
  {
    id: "RPT-2847",
    type: "MRI",
    patient: "Patient #2847",
    patientName: "John Smith",
    time: "2 minutes ago",
    date: "2025-08-11",
    status: "completed",
    diagnosis: "Normal brain scan",
    doctor: "Dr. Smith",
  },
  {
    id: "RPT-2846",
    type: "CT Scan",
    patient: "Patient #2846",
    patientName: "Jane Doe",
    time: "15 minutes ago",
    date: "2025-08-11",
    status: "processing",
    diagnosis: "Pending analysis",
    doctor: "Dr. Smith",
  },
  {
    id: "RPT-2845",
    type: "X-Ray",
    patient: "Patient #2845",
    patientName: "Bob Johnson",
    time: "1 hour ago",
    date: "2025-08-11",
    status: "completed",
    diagnosis: "Fractured rib",
    doctor: "Dr. Smith",
  },
];

const ReportSearch: React.FC<ReportSearchProps> = ({
  onViewReport = (id) => console.log(`View report: ${id}`),
  onDownloadReport = (id) => console.log(`Download report: ${id}`),
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedFilter, setSelectedFilter] = useState("all");
  const [dateFilter, setDateFilter] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [reports, setReports] = useState<Report[]>([]);
  const [totalCount, setTotalCount] = useState(0);

  // Remove the local sampleReports since it's now defined outside the component

  // API Functions for Flask Backend Integration
  const searchReports = useCallback(
    async (term: string, filter: string, date: string) => {
      setIsLoading(true);
      try {
        // TODO: Replace with actual Flask API endpoint
        // const response = await fetch(`/api/reports/search`, {
        //   method: 'POST',
        //   headers: {
        //     'Content-Type': 'application/json',
        //     'Authorization': `Bearer ${localStorage.getItem('token')}`
        //   },
        //   body: JSON.stringify({
        //     searchTerm: term,
        //     filter: filter,
        //     dateFilter: date,
        //     limit: 20,
        //     offset: 0
        //   })
        // });

        // if (!response.ok) {
        //   throw new Error('Failed to fetch reports');
        // }

        // const data = await response.json();
        // setReports(data.reports);
        // setTotalCount(data.total);

        // Simulate API call with sample data
        setTimeout(() => {
          const filtered = sampleReports.filter((report) => {
            const matchesSearch =
              term === "" ||
              report.patientName.toLowerCase().includes(term.toLowerCase()) ||
              report.id.toLowerCase().includes(term.toLowerCase()) ||
              report.type.toLowerCase().includes(term.toLowerCase()) ||
              report.diagnosis.toLowerCase().includes(term.toLowerCase());

            const matchesFilter =
              filter === "all" ||
              report.status === filter ||
              report.type.toLowerCase() === filter.toLowerCase();

            const matchesDate = date === "" || report.date === date;

            return matchesSearch && matchesFilter && matchesDate;
          });

          setReports(filtered);
          setTotalCount(filtered.length);
          setIsLoading(false);
        }, 500);
      } catch (error) {
        console.error("Error searching reports:", error);
        setIsLoading(false);
      }
    },
    []
  );

  const refreshReports = useCallback(async () => {
    setIsLoading(true);
    try {
      // TODO: Replace with actual Flask API endpoint
      // const response = await fetch('/api/reports/recent', {
      //   headers: {
      //     'Authorization': `Bearer ${localStorage.getItem('token')}`
      //   }
      // });

      // if (!response.ok) {
      //   throw new Error('Failed to fetch reports');
      // }

      // const data = await response.json();
      // setReports(data.reports);
      // setTotalCount(data.total);

      // Simulate API call
      setTimeout(() => {
        setReports(sampleReports);
        setTotalCount(sampleReports.length);
        setIsLoading(false);
      }, 500);
    } catch (error) {
      console.error("Error refreshing reports:", error);
      setIsLoading(false);
    }
  }, []);

  // Search with debounce
  useEffect(() => {
    const delayedSearch = setTimeout(() => {
      searchReports(searchTerm, selectedFilter, dateFilter);
    }, 300);

    return () => clearTimeout(delayedSearch);
  }, [searchTerm, selectedFilter, dateFilter, searchReports]);

  // Load initial data
  useEffect(() => {
    refreshReports();
  }, [refreshReports]);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <FileText className="w-5 h-5 mr-2 text-blue-600" />
            Medical Reports Search
          </h3>
          <button
            onClick={refreshReports}
            className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors duration-200"
            disabled={isLoading}
          >
            <RefreshCw
              className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`}
            />
          </button>
        </div>

        {/* Search and Filter Controls */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search patients, IDs, diagnosis..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-sm"
            />
          </div>

          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <select
              value={selectedFilter}
              onChange={(e) => setSelectedFilter(e.target.value)}
              className="w-full pl-10 pr-8 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-sm bg-white"
            >
              <option value="all">All Types</option>
              <option value="completed">Completed</option>
              <option value="processing">Processing</option>
              <option value="pending">Pending</option>
              <option value="mri">MRI</option>
              <option value="ct scan">CT Scan</option>
              <option value="x-ray">X-Ray</option>
              <option value="ultrasound">Ultrasound</option>
            </select>
          </div>

          <div className="relative">
            <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="date"
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-sm"
            />
          </div>
        </div>

        {totalCount > 0 && (
          <p className="text-sm text-gray-600 mt-3">
            Found {totalCount} report{totalCount !== 1 ? "s" : ""}
          </p>
        )}
      </div>

      <div className="p-6">
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <RefreshCw className="w-6 h-6 text-blue-600 animate-spin" />
            <span className="ml-2 text-gray-600">Searching reports...</span>
          </div>
        ) : reports.length > 0 ? (
          <div className="space-y-3">
            {reports.map((report) => (
              <div
                key={report.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200 border border-gray-100"
              >
                <div className="flex items-center space-x-3 flex-1">
                  <div
                    className={`w-3 h-3 rounded-full ${
                      report.status === "completed"
                        ? "bg-green-500"
                        : report.status === "processing"
                        ? "bg-yellow-500"
                        : "bg-gray-400"
                    }`}
                  />

                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <h4 className="font-medium text-gray-900">
                        {report.type} Analysis
                      </h4>
                      <span className="text-xs text-gray-500 bg-gray-200 px-2 py-1 rounded">
                        {report.id}
                      </span>
                      <span
                        className={`text-xs px-2 py-1 rounded-full ${
                          report.status === "completed"
                            ? "bg-green-100 text-green-800"
                            : report.status === "processing"
                            ? "bg-yellow-100 text-yellow-800"
                            : "bg-gray-100 text-gray-800"
                        }`}
                      >
                        {report.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">
                      {report.patientName}
                    </p>
                    <p className="text-xs text-gray-500">{report.diagnosis}</p>
                    <p className="text-xs text-gray-400">
                      {report.time} • {report.date}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={() => onViewReport(report.id)}
                    className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors duration-200"
                    title="View Report"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  {report.status === "completed" && (
                    <button
                      onClick={() => onDownloadReport(report.id)}
                      className="p-2 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded transition-colors duration-200"
                      title="Download PDF"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">No reports found</p>
            <p className="text-sm text-gray-400">
              Try adjusting your search criteria
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReportSearch;
