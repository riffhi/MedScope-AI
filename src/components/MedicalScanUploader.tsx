import React, { useState, useRef } from "react";
import {
  Upload,
  FileText,
  Brain,
  Heart,
  Activity,
  Bone,
  UserCheck,
  X,
  AlertTriangle,
} from "lucide-react";
import FeedbackPopup from "./FeedbackPopup";

interface MedicalScanUploaderProps {
  onAnalysisComplete?: (result: AnalysisResult) => void;
}

interface MedicalFindings {
  potential_masses: number;
  asymmetry_detected: boolean;
  asymmetry_interpretation: string;
  texture_variations: string;
  variation_interpretation: string;
  contour_analysis: string;
  condition_scores?: Record<string, number>;
  condition_evidence?: Record<string, string[]>;
}

interface DoctorRecommendations {
  risk_based_recommendations: string[];
  medical_recommendations: string[];
  quality_recommendations: string[];
  general_recommendations: string[];
}

interface QualityAssessment {
  overall_rating: string;
  sharpness_rating: string;
  contrast_rating: string;
  noise_rating: string;
}

interface TechnicalDetails {
  image_dimensions: string;
  color_channels: string | number;
  detected_contours: number;
  analysis_algorithm: string;
  processing_time: string;
  confidence_score: string;
}

interface AnalysisResult {
  success: boolean;
  filename: string;
  body_part: string;
  analysis: {
    summary: string;
    medical_classification: {
      condition: string;
      risk_level: string;
      urgency: string;
      risk_score: number;
    };
    medical_findings: MedicalFindings;
    doctor_recommendations: DoctorRecommendations;
    quality_assessment: QualityAssessment;
    technical_details: TechnicalDetails;
    medical_report: string;
    disclaimer: string;
    analysis_timestamp: string;
  };
}

const MedicalScanUploader: React.FC<MedicalScanUploaderProps> = ({
  onAnalysisComplete,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedBodyPart, setSelectedBodyPart] = useState<string>("");
  const [isUploading, setIsUploading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(
    null
  );
  const [error, setError] = useState<string>("");
  const [bodyParts, setBodyParts] = useState<{ [key: string]: string }>({});
  const [showFeedback, setShowFeedback] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Body part icons mapping
  const bodyPartIcons: { [key: string]: React.ReactNode } = {
    brain: <Brain className="w-6 h-6" />,
    heart: <Heart className="w-6 h-6" />,
    chest: <Activity className="w-6 h-6" />,
    abdomen: <UserCheck className="w-6 h-6" />,
    spine: <Bone className="w-6 h-6" />,
    extremities: <Bone className="w-6 h-6" />,
    breast: <Heart className="w-6 h-6" />,
    unknown: <FileText className="w-6 h-6" />,
  };

  // Fetch body parts on component mount
  React.useEffect(() => {
    fetchBodyParts();
  }, []);

  const fetchBodyParts = async () => {
    try {
      const response = await fetch(
        "http://localhost:8000/api/v1/scan/body-parts"
      );
      if (response.ok) {
        const data = await response.json();
        setBodyParts(data.body_parts);
      }
    } catch (error) {
      console.error("Failed to fetch body parts:", error);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      const allowedTypes = [
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/gif",
        "image/bmp",
        "image/tiff",
      ];
      if (!allowedTypes.includes(file.type)) {
        setError(
          "Please select a valid image file (JPEG, PNG, GIF, BMP, TIFF)"
        );
        return;
      }

      // Validate file size (10MB max)
      if (file.size > 10 * 1024 * 1024) {
        setError("File size must be less than 10MB");
        return;
      }

      setSelectedFile(file);
      setError("");
      setAnalysisResult(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !selectedBodyPart) {
      setError("Please select both a file and body part");
      return;
    }

    setIsUploading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("body_part", selectedBodyPart);

      const response = await fetch(
        "http://localhost:8000/api/v1/scan/analyze",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Analysis failed");
      }

      const result: AnalysisResult = await response.json();
      setAnalysisResult(result);

      if (onAnalysisComplete) {
        onAnalysisComplete(result);
      }

      // Show feedback popup after successful analysis
      setTimeout(() => {
        setShowFeedback(true);
      }, 1000);
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "An error occurred during analysis"
      );
    } finally {
      setIsUploading(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!analysisResult) return;

    try {
      const response = await fetch(
        "http://localhost:8000/api/v1/scan/generate-pdf",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            filename: analysisResult.filename,
            body_part: analysisResult.body_part,
            analysis: analysisResult.analysis,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to generate PDF");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.style.display = "none";
      a.href = url;
      a.download = `${analysisResult.filename}_medical_report.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch {
      setError("Failed to download PDF report");
    }
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel.toLowerCase()) {
      case "high":
        return "text-red-600 bg-red-50 border-red-200";
      case "moderate":
        return "text-yellow-600 bg-yellow-50 border-yellow-200";
      case "low":
        return "text-blue-600 bg-blue-50 border-blue-200";
      case "minimal":
        return "text-green-600 bg-green-50 border-green-200";
      default:
        return "text-gray-600 bg-gray-50 border-gray-200";
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency.toLowerCase()) {
      case "immediate":
        return "text-red-700 bg-red-100";
      case "within_1_week":
        return "text-orange-700 bg-orange-100";
      case "within_1_month":
        return "text-yellow-700 bg-yellow-100";
      case "routine":
        return "text-green-700 bg-green-100";
      default:
        return "text-gray-700 bg-gray-100";
    }
  };

  const resetUpload = () => {
    setSelectedFile(null);
    setSelectedBodyPart("");
    setAnalysisResult(null);
    setError("");
    setShowFeedback(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">
          Medical Scan Analysis
        </h2>
        <p className="text-gray-600">
          Upload medical images for AI-assisted analysis
        </p>
      </div>

      {!analysisResult ? (
        <div className="space-y-6">
          {/* File Upload Section */}
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
              id="file-upload"
            />
            <label htmlFor="file-upload" className="cursor-pointer">
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-lg font-medium text-gray-700 mb-2">
                {selectedFile
                  ? selectedFile.name
                  : "Click to upload medical scan"}
              </p>
              <p className="text-sm text-gray-500">
                Supported formats: JPEG, PNG, GIF, BMP, TIFF (Max 10MB)
              </p>
            </label>
          </div>

          {/* Body Part Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Select Body Part/Region
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {Object.entries(bodyParts).map(([key]) => (
                <button
                  key={key}
                  onClick={() => setSelectedBodyPart(key)}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    selectedBodyPart === key
                      ? "border-blue-500 bg-blue-50 text-blue-700"
                      : "border-gray-200 hover:border-gray-300 text-gray-700"
                  }`}
                >
                  <div className="flex flex-col items-center space-y-2">
                    {bodyPartIcons[key]}
                    <span className="text-sm font-medium capitalize">
                      {key}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <div className="flex">
                <AlertTriangle className="w-5 h-5 text-red-400 mr-2" />
                <p className="text-red-700">{error}</p>
              </div>
            </div>
          )}

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={!selectedFile || !selectedBodyPart || isUploading}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-md font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {isUploading ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Analyzing...
              </div>
            ) : (
              "Analyze Scan"
            )}
          </button>
        </div>
      ) : (
        /* Analysis Results */
        <div className="space-y-6">
          {/* Header with Reset Button */}
          <div className="flex justify-between items-center">
            <h3 className="text-2xl font-bold text-gray-800">
              Analysis Results
            </h3>
            <button
              onClick={resetUpload}
              className="flex items-center px-4 py-2 text-gray-600 hover:text-gray-800 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              <X className="w-4 h-4 mr-2" />
              New Analysis
            </button>
          </div>

          {/* Summary */}
          <div className="bg-gray-50 rounded-lg p-6">
            <h4 className="text-lg font-semibold text-gray-800 mb-2">
              Summary
            </h4>
            <p className="text-gray-700">{analysisResult.analysis.summary}</p>
          </div>

          {/* Medical Classification */}
          <div className="bg-white border rounded-lg p-6">
            <h4 className="text-lg font-semibold text-gray-800 mb-4">
              Medical Classification
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div
                className={`p-4 rounded-lg border ${getRiskLevelColor(
                  analysisResult.analysis.medical_classification.risk_level
                )}`}
              >
                <div className="text-sm font-medium">Risk Level</div>
                <div className="text-lg font-bold">
                  {analysisResult.analysis.medical_classification.risk_level}
                </div>
                <div className="text-sm">
                  Score:{" "}
                  {analysisResult.analysis.medical_classification.risk_score}
                  /100
                </div>
              </div>
              <div
                className={`p-4 rounded-lg ${getUrgencyColor(
                  analysisResult.analysis.medical_classification.urgency
                )}`}
              >
                <div className="text-sm font-medium">Urgency</div>
                <div className="text-lg font-bold">
                  {analysisResult.analysis.medical_classification.urgency.replace(
                    "_",
                    " "
                  )}
                </div>
              </div>
            </div>
            <div className="mt-4">
              <div className="text-sm font-medium text-gray-600">Condition</div>
              <div className="text-lg font-semibold">
                {analysisResult.analysis.medical_classification.condition.replace(
                  "_",
                  " "
                )}
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-4">
            <button
              onClick={handleDownloadPDF}
              className="flex-1 bg-green-600 text-white py-3 px-6 rounded-md font-medium hover:bg-green-700 transition-colors"
            >
              Download PDF Report
            </button>
          </div>

          {/* Disclaimer */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
            <p className="text-sm text-yellow-800">
              {analysisResult.analysis.disclaimer}
            </p>
          </div>
        </div>
      )}

      {/* Feedback Popup */}
      <FeedbackPopup
        isVisible={showFeedback}
        onClose={() => setShowFeedback(false)}
        analysisId={analysisResult?.analysis.analysis_timestamp}
        onFeedbackSubmitted={() => setShowFeedback(false)}
      />
    </div>
  );
};

export default MedicalScanUploader;
