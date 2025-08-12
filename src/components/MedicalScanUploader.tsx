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
  Download,
} from "lucide-react";
import { databases, storage, AppwriteID, APPWRITE_CONFIG } from "../appwrite";

// --- Interfaces ---
interface MedicalFindings {
  potential_masses: number;
  asymmetry_detected: boolean;
  asymmetry_interpretation: string;
  texture_variations: string;
  variation_interpretation: string;
  contour_analysis: string;
}
// ... other interfaces remain the same

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
    // ... other analysis fields
    disclaimer: string;
    analysis_timestamp: string;
  };
  appwrite_document_id?: string;
  appwrite_file_id?: string;
}

// --- Mock AI Analysis Function ---
const runMockAnalysis = (
  filename: string,
  bodyPart: string
): AnalysisResult => {
  const riskLevels = ["Minimal", "Low", "Moderate", "High"];
  const urgencies = ["Routine", "Within_1_month", "Within_1_week", "Immediate"];
  const conditions = ["Normal_finding", "Benign_abnormality", "Suspicious_finding", "Critical_finding"];
  const randomRisk = riskLevels[Math.floor(Math.random() * riskLevels.length)];
  const randomUrgency = urgencies[Math.floor(Math.random() * urgencies.length)];
  const randomCondition = conditions[Math.floor(Math.random() * conditions.length)];
  const randomRiskScore = Math.floor(Math.random() * 80) + 10;

  return {
    success: true,
    filename,
    body_part: bodyPart,
    analysis: {
      summary: `The AI analysis of the ${bodyPart} scan indicates a ${randomRisk.toLowerCase()} risk. The primary finding is a ${randomCondition.replace("_", " ").toLowerCase()}.`,
      medical_classification: {
        condition: randomCondition,
        risk_level: randomRisk,
        urgency: randomUrgency,
        risk_score: randomRiskScore,
      },
      medical_findings: {
        potential_masses: Math.random() > 0.7 ? 1 : 0,
        asymmetry_detected: Math.random() > 0.5,
        asymmetry_interpretation: "Mild asymmetry noted.",
        texture_variations: "Minor variations observed.",
        variation_interpretation: "Variations appear benign.",
        contour_analysis: "Contours appear raegular.",
      },
      disclaimer: "This AI analysis is for informational purposes only and is not a substitute for professional medical advice.",
      analysis_timestamp: new Date().toISOString(),
    },
  };
};


const MedicalScanUploader: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedBodyPart, setSelectedBodyPart] = useState<string>("");
  const [isUploading, setIsUploading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string>("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const bodyParts = {
    brain: "Brain", heart: "Cardiac", chest: "Chest",
    abdomen: "Abdomen", spine: "Spine", extremities: "Extremities",
    breast: "Breast", unknown: "Unknown",
  };

  const bodyPartIcons: { [key: string]: React.ReactNode } = {
    brain: <Brain className="w-6 h-6" />, heart: <Heart className="w-6 h-6" />,
    chest: <Activity className="w-6 h-6" />, abdomen: <UserCheck className="w-6 h-6" />,
    spine: <Bone className="w-6 h-6" />, extremities: <Bone className="w-6 h-6" />,
    breast: <Heart className="w-6 h-6" />, unknown: <FileText className="w-6 h-6" />,
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const allowedTypes = ["image/jpeg", "image/png", "image/gif", "image/bmp", "image/tiff"];
      if (!allowedTypes.includes(file.type)) {
        setError("Please select a valid image file.");
        return;
      }
      if (file.size > 10 * 1024 * 1024) {
        setError("File size must be less than 10MB.");
        return;
      }
      setSelectedFile(file);
      setError("");
      setAnalysisResult(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !selectedBodyPart) {
      setError("Please select both a file and body part.");
      return;
    }

    setIsUploading(true);
    setError("");

    try {
      // Step 1: Upload file to Appwrite Storage
      const fileResponse = await storage.createFile(
        APPWRITE_CONFIG.storageBucketId,
        AppwriteID.unique(),
        selectedFile
      );
      const fileId = fileResponse.$id;

      // Step 2: Run mock analysis
      const result = runMockAnalysis(selectedFile.name, selectedBodyPart);

      // Step 3: Prepare data for Appwrite database (matching your attributes)
      const documentData = {
        filename: result.filename,
        bodyPart: result.body_part,
        riskLevel: result.analysis.medical_classification.risk_level,
        condition: result.analysis.medical_classification.condition,
        analysisData: JSON.stringify(result.analysis),
        appwrite_file_id: fileId, // Add this attribute to your collection
      };

      // Step 4: Create document in Appwrite Database
      const dbResponse = await databases.createDocument(
        APPWRITE_CONFIG.databaseId,
        APPWRITE_CONFIG.collections.scans,
        AppwriteID.unique(),
        documentData
      );

      // Step 5: Set state to display results
      setAnalysisResult({
        ...result,
        appwrite_document_id: dbResponse.$id,
        appwrite_file_id: fileId,
      });

    } catch (err: any) {
      console.error("Appwrite operation failed:", err);
      setError(err.message || "An error occurred during analysis.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleDownloadFile = () => {
    if (!analysisResult?.appwrite_file_id) return;
    const result = storage.getFileDownload(
      APPWRITE_CONFIG.storageBucketId,
      analysisResult.appwrite_file_id
    );
    window.open(result.href, '_blank');
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel.toLowerCase()) {
      case "high": return "text-red-600 bg-red-50 border-red-200";
      case "moderate": return "text-yellow-600 bg-yellow-50 border-yellow-200";
      case "low": return "text-blue-600 bg-blue-50 border-blue-200";
      case "minimal": return "text-green-600 bg-green-50 border-green-200";
      default: return "text-gray-600 bg-gray-50 border-gray-200";
    }
  };

  const resetUpload = () => {
    setSelectedFile(null);
    setSelectedBodyPart("");
    setAnalysisResult(null);
    setError("");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg font-sans">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">Medical Scan Analysis</h2>
        <p className="text-gray-600">Upload medical images for AI-assisted analysis</p>
      </div>

      {!analysisResult ? (
        <div className="space-y-6">
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors">
            <input ref={fileInputRef} type="file" accept="image/*" onChange={handleFileSelect} className="hidden" id="file-upload" />
            <label htmlFor="file-upload" className="cursor-pointer">
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-lg font-medium text-gray-700 mb-2">
                {selectedFile ? selectedFile.name : "Click to upload medical scan"}
              </p>
              <p className="text-sm text-gray-500">Max 10MB</p>
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">Select Body Part</label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {Object.entries(bodyParts).map(([key, value]) => (
                <button
                  key={key}
                  onClick={() => setSelectedBodyPart(key)}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    selectedBodyPart === key
                      ? "border-blue-500 bg-blue-50 text-blue-700 shadow-md"
                      : "border-gray-200 hover:border-gray-300 text-gray-700"
                  }`}
                >
                  <div className="flex flex-col items-center space-y-2">
                    {bodyPartIcons[key]}
                    <span className="text-sm font-medium capitalize">{value}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4 flex items-center">
              <AlertTriangle className="w-5 h-5 text-red-400 mr-3 flex-shrink-0" />
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={!selectedFile || !selectedBodyPart || isUploading}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-md font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all"
          >
            {isUploading ? "Analyzing..." : "Analyze Scan"}
          </button>
        </div>
      ) : (
        <div className="space-y-6 animate-fade-in">
          <div className="flex justify-between items-center">
            <h3 className="text-2xl font-bold text-gray-800">Analysis Results</h3>
            <button onClick={resetUpload} className="flex items-center px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 border rounded-md">
              <X className="w-4 h-4 mr-2" />
              New Analysis
            </button>
          </div>

          <div className="bg-gray-50 rounded-lg p-6">
            <h4 className="text-lg font-semibold text-gray-800 mb-2">Summary</h4>
            <p className="text-gray-700">{analysisResult.analysis.summary}</p>
          </div>

          <div className="bg-white border rounded-lg p-6">
            <h4 className="text-lg font-semibold text-gray-800 mb-4">Medical Classification</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className={`p-4 rounded-lg border ${getRiskLevelColor(analysisResult.analysis.medical_classification.risk_level)}`}>
                <div className="text-sm font-medium">Risk Level</div>
                <div className="text-xl font-bold">{analysisResult.analysis.medical_classification.risk_level}</div>
              </div>
              <div className="p-4 rounded-lg bg-gray-100">
                <div className="text-sm font-medium">Condition</div>
                <div className="text-xl font-bold capitalize">{analysisResult.analysis.medical_classification.condition.replace("_", " ")}</div>
              </div>
            </div>
          </div>

          <button
            onClick={handleDownloadFile}
            className="w-full bg-green-600 text-white py-3 px-6 rounded-md font-medium hover:bg-green-700 transition-colors flex items-center justify-center"
          >
            <Download className="w-5 h-5 mr-2"/>
            Download Original Scan
          </button>

          <div className="bg-yellow-50 border-l-4 border-yellow-400 rounded-r-md p-4">
            <p className="text-sm text-yellow-800">{analysisResult.analysis.disclaimer}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default MedicalScanUploader;
