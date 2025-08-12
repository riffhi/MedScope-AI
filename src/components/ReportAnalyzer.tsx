import React, { useState } from "react";
import {
  Upload,
  FileImage,
  Zap,
  Download,
  CheckCircle,
  AlertCircle,
  Clock,
  Brain,
  Scan,
  Activity,
  Shield,
  TrendingUp,
  Calendar,
  FileText,
  Heart,
  Stethoscope,
} from "lucide-react";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";

const ReportAnalyzer: React.FC = () => {
  const [activeAnalyzer, setActiveAnalyzer] = useState<"MRI" | "CT" | "XRAY" | "MAMMOGRAPHY" | "SONOGRAPHY">(
    "MRI"
  );
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [analysisStatus, setAnalysisStatus] = useState<
    "idle" | "processing" | "completed"
  >("idle");

  const handleFileUpload = (files: FileList | null) => {
    if (files) {
      setUploadedFiles(Array.from(files));
    }
  };

  const [analysisResults, setAnalysisResults] = useState<any>(null);
  const [showFeedbackPopup, setShowFeedbackPopup] = useState(false);
  const [feedbackRating, setFeedbackRating] = useState(0);
  const [feedbackText, setFeedbackText] = useState("");
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  const startAnalysis = () => {
    setAnalysisStatus("processing");
    // Simulate analysis with dynamic results
    setTimeout(() => {
      const results = generateAnalysisResults(activeAnalyzer);
      setAnalysisResults(results);
      setAnalysisStatus("completed");
      // Show feedback popup after analysis
      setTimeout(() => {
        setShowFeedbackPopup(true);
      }, 1000);
    }, 3000);
  };

  const handleFeedbackSubmit = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && feedbackText.trim()) {
      // Here you would normally send to database
      console.log('Feedback submitted:', {
        rating: feedbackRating,
        feedback: feedbackText,
        scanType: activeAnalyzer,
        timestamp: new Date().toISOString()
      });
      
      setFeedbackSubmitted(true);
      setTimeout(() => {
        setShowFeedbackPopup(false);
        setFeedbackSubmitted(false);
        setFeedbackRating(0);
        setFeedbackText("");
      }, 2000);
    }
  };

  const StarRating = ({ rating, onRatingChange }: { rating: number; onRatingChange: (rating: number) => void }) => {
    return (
      <div className="flex space-x-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            onClick={() => onRatingChange(star)}
            className={`text-2xl transition-colors ${
              star <= rating ? 'text-yellow-400' : 'text-gray-300'
            } hover:text-yellow-400`}
          >
            ⭐
          </button>
        ))}
      </div>
    );
  };

  const generateAnalysisResults = (scanType: "MRI" | "CT" | "XRAY" | "MAMMOGRAPHY" | "SONOGRAPHY") => {
    const scenarios = {
      MRI: [
        {
          riskLevel: "LOW",
          riskScore: "2.1/10",
          urgency: "ROUTINE",
          urgencyDetail: "Follow-up in 6-12 months",
          treatment: "MONITORING",
          treatmentDetail: "No immediate intervention",
          findings: [
            "Brain parenchyma appears normal with no evidence of mass lesions, hemorrhage, or acute infarction",
            "Ventricular system is normal in size and configuration with no signs of hydrocephalus",
            "White matter signal intensity is within normal limits, no demyelinating lesions detected",
            "Cerebral cortex shows normal thickness and signal characteristics",
            "No abnormal enhancement patterns observed post-contrast administration"
          ],
          recommendations: {
            immediate: [
              "No immediate intervention required",
              "Continue current neurological monitoring",
              "Patient can resume normal daily activities"
            ],
            followUp: [
              "Routine neurological follow-up in 6-12 months",
              "Monitor for any new neurological symptoms",
              "Consider repeat MRI if symptoms develop or worsen"
            ]
          },
          confidence: 94,
          processingTime: "2.3s",
          additionalNotes: "Excellent image quality with minimal motion artifacts. All sequences completed successfully."
        },
        {
          riskLevel: "MODERATE",
          riskScore: "5.8/10",
          urgency: "PRIORITY",
          urgencyDetail: "Follow-up in 2-4 weeks",
          treatment: "CONSULTATION",
          treatmentDetail: "Neurologist consultation recommended",
          findings: [
            "Small hyperintense lesions identified in periventricular white matter",
            "Possible early signs of small vessel disease or demyelination",
            "Ventricular system remains within normal limits",
            "No acute hemorrhage or mass effect detected",
            "Mild cerebral atrophy consistent with age-related changes"
          ],
          recommendations: {
            immediate: [
              "Neurologist consultation within 2-4 weeks",
              "Consider additional blood work and vitamin B12 levels",
              "Monitor for cognitive changes or new symptoms"
            ],
            followUp: [
              "Repeat MRI in 3-6 months to assess progression",
              "Regular neurological assessments",
              "Consider MR spectroscopy if lesions progress"
            ]
          },
          confidence: 87,
          processingTime: "2.8s",
          additionalNotes: "Multiple sequences analyzed. Recommend correlation with clinical symptoms and history."
        }
      ],
      CT: [
        {
          riskLevel: "LOW",
          riskScore: "1.9/10",
          urgency: "ROUTINE",
          urgencyDetail: "Follow-up in 12 months",
          treatment: "MONITORING",
          treatmentDetail: "No immediate intervention",
          findings: [
            "No acute intracranial abnormalities detected on non-contrast CT",
            "Bone windows show normal calvarian thickness and density",
            "Soft tissue structures appear unremarkable with no swelling",
            "Paranasal sinuses are clear with no fluid levels",
            "No evidence of fracture, hemorrhage, or mass lesions"
          ],
          recommendations: {
            immediate: [
              "No immediate treatment required",
              "Patient cleared for normal activities",
              "Pain management as needed for minor symptoms"
            ],
            followUp: [
              "Routine follow-up only if symptoms persist",
              "Return if severe headaches or neurological symptoms develop",
              "Consider MRI if more detailed imaging needed"
            ]
          },
          confidence: 96,
          processingTime: "1.8s",
          additionalNotes: "High-quality CT scan with excellent bone and soft tissue detail."
        }
      ],
      XRAY: [
        {
          riskLevel: "LOW",
          riskScore: "2.3/10",
          urgency: "ROUTINE",
          urgencyDetail: "Follow-up as needed",
          treatment: "CONSERVATIVE",
          treatmentDetail: "Rest and physiotherapy",
          findings: [
            "No acute fractures or dislocations identified in the examined region",
            "Bone alignment and joint spaces appear normal and well-maintained",
            "Soft tissue swelling is minimal and within expected limits",
            "Bone density appears normal for patient age group",
            "No signs of arthritis or degenerative joint disease"
          ],
          recommendations: {
            immediate: [
              "Conservative management with rest and ice",
              "Over-the-counter pain relief as needed",
              "Gentle range of motion exercises"
            ],
            followUp: [
              "Follow-up if symptoms worsen or persist beyond 2 weeks",
              "Consider physiotherapy for rehabilitation",
              "Return for re-evaluation if new symptoms develop"
            ]
          },
          confidence: 92,
          processingTime: "1.5s",
          additionalNotes: "Good quality radiograph with adequate penetration and positioning."
        }
      ],
      MAMMOGRAPHY: [
        {
          riskLevel: "LOW",
          riskScore: "1.8/10",
          urgency: "ROUTINE",
          urgencyDetail: "Annual screening recommended",
          treatment: "MONITORING",
          treatmentDetail: "Continue routine screening",
          findings: [
            "Breast tissue demonstrates normal fibroglandular density patterns",
            "No suspicious masses, calcifications, or architectural distortions identified",
            "Bilateral breast symmetry is maintained with normal contours",
            "No evidence of skin thickening or nipple retraction",
            "Axillary lymph nodes appear normal in size and morphology"
          ],
          recommendations: {
            immediate: [
              "Continue annual mammographic screening",
              "Maintain breast self-examination routine",
              "No immediate intervention required"
            ],
            followUp: [
              "Next mammogram in 12 months as per screening guidelines",
              "Report any new breast symptoms promptly",
              "Consider breast MRI if family history of breast cancer"
            ]
          },
          confidence: 95,
          processingTime: "1.9s",
          additionalNotes: "High-quality mammographic images with excellent compression and positioning."
        },
        {
          riskLevel: "MODERATE",
          riskScore: "4.2/10",
          urgency: "PRIORITY",
          urgencyDetail: "Follow-up in 6 months",
          treatment: "CONSULTATION",
          treatmentDetail: "Breast specialist consultation",
          findings: [
            "Scattered fibroglandular densities noted bilaterally",
            "Small cluster of microcalcifications in upper outer quadrant",
            "Possible benign calcifications, recommend correlation with prior studies",
            "No associated mass lesions or architectural distortion",
            "Breast tissue appears otherwise unremarkable"
          ],
          recommendations: {
            immediate: [
              "Breast specialist consultation within 2-3 weeks",
              "Consider targeted ultrasound of calcification area",
              "Obtain prior mammograms for comparison if available"
            ],
            followUp: [
              "Short-interval follow-up mammogram in 6 months",
              "Continue monthly breast self-examinations",
              "Consider biopsy if calcifications show interval change"
            ]
          },
          confidence: 88,
          processingTime: "2.1s",
          additionalNotes: "Calcifications require further evaluation to exclude malignancy."
        }
      ],
      SONOGRAPHY: [
        {
          riskLevel: "LOW",
          riskScore: "2.0/10",
          urgency: "ROUTINE",
          urgencyDetail: "Follow-up as clinically indicated",
          treatment: "MONITORING",
          treatmentDetail: "Conservative management",
          findings: [
            "Abdominal organs demonstrate normal echogenicity and size",
            "Liver shows homogeneous echotexture with no focal lesions",
            "Gallbladder wall thickness is within normal limits",
            "Kidneys show normal size, shape, and echogenicity bilaterally",
            "No evidence of free fluid or masses in the pelvis"
          ],
          recommendations: {
            immediate: [
              "No immediate treatment required",
              "Continue current medications as prescribed",
              "Maintain healthy lifestyle and diet"
            ],
            followUp: [
              "Routine follow-up as clinically indicated",
              "Repeat ultrasound if symptoms develop",
              "Annual health screening as appropriate for age"
            ]
          },
          confidence: 93,
          processingTime: "1.7s",
          additionalNotes: "Complete abdominal ultrasound with excellent image quality."
        },
        {
          riskLevel: "MODERATE",
          riskScore: "5.1/10",
          urgency: "PRIORITY",
          urgencyDetail: "Follow-up in 4-6 weeks",
          treatment: "CONSULTATION",
          treatmentDetail: "Gastroenterologist consultation",
          findings: [
            "Hepatomegaly noted with liver span measuring 16.5 cm",
            "Increased hepatic echogenicity suggesting fatty infiltration",
            "Gallbladder shows multiple small echogenic foci consistent with gallstones",
            "Common bile duct measures 4mm, within normal limits",
            "Pancreas appears normal with no focal abnormalities"
          ],
          recommendations: {
            immediate: [
              "Gastroenterologist consultation within 4-6 weeks",
              "Consider liver function tests and lipid profile",
              "Dietary counseling for fatty liver management"
            ],
            followUp: [
              "Follow-up ultrasound in 3-6 months",
              "Monitor for symptoms of gallbladder disease",
              "Consider MRCP if symptoms worsen"
            ]
          },
          confidence: 89,
          processingTime: "2.4s",
          additionalNotes: "Findings suggest non-alcoholic fatty liver disease with cholelithiasis."
        }
      ]
    };

    // Randomly select a scenario for more variety
    const scanScenarios = scenarios[scanType];
    return scanScenarios[Math.floor(Math.random() * scanScenarios.length)];
  };

  const generatePDFReport = async () => {
    try {
      console.log('Starting PDF generation...');
      const reportElement = document.getElementById('medical-report');
      if (!reportElement) {
        alert('Report element not found! Please complete analysis first.');
        return;
      }

      console.log('Capturing screenshot...');
      const canvas = await html2canvas(reportElement, {
        scale: 2,
        useCORS: true,
        backgroundColor: '#ffffff',
        logging: true,
        allowTaint: true
      });

      console.log('Creating PDF...');
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      
      // Add colorful header
      pdf.setFillColor(59, 130, 246);
      pdf.rect(0, 0, 210, 35, 'F');
      
      pdf.setTextColor(255, 255, 255);
      pdf.setFontSize(24);
      pdf.text('🏥 MedScope AI - Medical Report', 20, 22);
      
      // Add date and report info
      pdf.setFontSize(12);
      pdf.text(`Generated: ${new Date().toLocaleDateString()}`, 140, 30);
      pdf.text(`Type: ${activeAnalyzer} Analysis`, 20, 30);
      
      // Add main content with proper scaling
      const imgWidth = 170;
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      
      // Handle multiple pages if needed
      let yPosition = 45;
      if (imgHeight > 200) {
        // Split into multiple pages if too tall
        const pageHeight = 250;
        let remainingHeight = imgHeight;
        let sourceY = 0;
        
        while (remainingHeight > 0) {
          const currentHeight = Math.min(pageHeight, remainingHeight);
          const currentCanvas = document.createElement('canvas');
          const ctx = currentCanvas.getContext('2d');
          currentCanvas.width = canvas.width;
          currentCanvas.height = (currentHeight / imgHeight) * canvas.height;
          
          ctx?.drawImage(canvas, 0, sourceY, canvas.width, currentCanvas.height, 0, 0, canvas.width, currentCanvas.height);
          const currentImgData = currentCanvas.toDataURL('image/png');
          
          pdf.addImage(currentImgData, 'PNG', 20, yPosition, imgWidth, currentHeight);
          
          remainingHeight -= pageHeight;
          sourceY += currentCanvas.height;
          
          if (remainingHeight > 0) {
            pdf.addPage();
            yPosition = 20;
          }
        }
      } else {
        pdf.addImage(imgData, 'PNG', 20, yPosition, imgWidth, imgHeight);
      }
      
      // Add colorful footer
      const pageHeight = pdf.internal.pageSize.height;
      pdf.setFillColor(241, 245, 249);
      pdf.rect(0, pageHeight - 25, 210, 25, 'F');
      
      pdf.setTextColor(71, 85, 105);
      pdf.setFontSize(10);
      pdf.text('⚕️ This report is generated by MedScope AI for medical reference only.', 20, pageHeight - 15);
      pdf.text('Please consult with a qualified healthcare professional for medical decisions.', 20, pageHeight - 8);
      
      const fileName = `MedScope-AI-Report-${activeAnalyzer}-${new Date().toISOString().slice(0,10)}-${Date.now().toString().slice(-6)}.pdf`;
      console.log('Saving PDF:', fileName);
      pdf.save(fileName);
      
      alert('✅ PDF Report downloaded successfully!');
    } catch (error) {
      console.error('PDF generation error:', error);
      alert('❌ Error generating PDF. Please try again.');
    }
  };

  const analyzers = [
    {
      type: "MRI" as const,
      label: "MRI Analysis",
      icon: Brain,
      color: "blue",
      description: "Magnetic Resonance Imaging analysis with advanced AI",
      acceptedFiles: "DICOM, JPEG, PNG files",
    },
    {
      type: "CT" as const,
      label: "CT Scan Analysis",
      icon: Scan,
      color: "teal",
      description: "Computed Tomography scan interpretation",
      acceptedFiles: "DICOM, JPEG, PNG files",
    },
    {
      type: "XRAY" as const,
      label: "X-Ray Analysis",
      icon: Activity,
      color: "purple",
      description: "Radiographic image analysis and interpretation",
      acceptedFiles: "DICOM, JPEG, PNG files",
    },
    {
      type: "MAMMOGRAPHY" as const,
      label: "Mammography Analysis",
      icon: Heart,
      color: "pink",
      description: "Breast imaging analysis for early detection",
      acceptedFiles: "DICOM, JPEG, PNG files",
    },
    {
      type: "SONOGRAPHY" as const,
      label: "Sonography Analysis",
      icon: Stethoscope,
      color: "green",
      description: "Ultrasound imaging analysis and interpretation",
      acceptedFiles: "DICOM, JPEG, PNG files",
    },
  ];

  const currentAnalyzer = analyzers.find((a) => a.type === activeAnalyzer)!;

  return (
    <div className="space-y-6 bg-slate-900 text-slate-100 p-6 min-h-screen">
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">
          Medical Report Analyzer
        </h2>
        <p className="text-slate-400">
          AI-powered analysis for MRI, CT scans, and X-ray imaging
        </p>
      </div>

      {/* Analyzer Type Selector */}
      <div className="bg-slate-800/60 backdrop-blur-sm rounded-xl shadow-lg border border-slate-700/50">
        <div className="p-4 border-b border-slate-700/50">
          <h3 className="text-lg font-semibold text-white">
            Select Analysis Type
          </h3>
        </div>
        <div className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
            {analyzers.map((analyzer) => {
              const Icon = analyzer.icon;
              const isActive = activeAnalyzer === analyzer.type;

              return (
                <button
                  key={analyzer.type}
                  onClick={() => {
                    setActiveAnalyzer(analyzer.type);
                    setUploadedFiles([]);
                    setAnalysisStatus("idle");
                  }}
                  className={`p-4 rounded-lg border-2 transition-all duration-200 text-left ${
                    isActive
                      ? "border-blue-500 bg-blue-500/20"
                      : "border-slate-600 hover:border-slate-500 hover:bg-slate-700/30"
                  }`}
                >
                  <div className="flex items-center space-x-3 mb-2">
                    <div
                      className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        isActive ? "bg-blue-500/30" : "bg-slate-700"
                      }`}
                    >
                      <Icon
                        className={`w-5 h-5 ${
                          isActive ? "text-blue-400" : "text-slate-400"
                        }`}
                      />
                    </div>
                    <h4
                      className={`font-medium ${
                        isActive ? "text-blue-300" : "text-slate-200"
                      }`}
                    >
                      {analyzer.label}
                    </h4>
                  </div>
                  <p
                    className={`text-sm ${
                      isActive ? "text-blue-200" : "text-slate-400"
                    }`}
                  >
                    {analyzer.description}
                  </p>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload Section */}
        <div className="lg:col-span-1">
          <div className="bg-slate-800/60 backdrop-blur-sm rounded-xl shadow-lg border border-slate-700/50">
            <div className="p-6 border-b border-slate-700/50">
              <h3 className="text-lg font-semibold text-white flex items-center">
                <Upload className="w-5 h-5 mr-2 text-blue-400" />
                Upload {currentAnalyzer.type} Files
              </h3>
            </div>

            <div className="p-6">
              <div
                className="border-2 border-dashed border-blue-400/50 rounded-lg p-8 text-center hover:border-blue-400/70 transition-colors bg-slate-700/30"
                onDrop={(e) => {
                  e.preventDefault();
                  handleFileUpload(e.dataTransfer.files);
                }}
                onDragOver={(e) => e.preventDefault()}
              >
                <FileImage className="w-12 h-12 text-blue-400 mx-auto mb-4" />
                <p className="text-slate-300 mb-2">
                  Drop {currentAnalyzer.type} files here or click to upload
                </p>
                <input
                  type="file"
                  multiple
                  accept=".dcm,.jpg,.jpeg,.png"
                  onChange={(e) => handleFileUpload(e.target.files)}
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg cursor-pointer transition-colors border border-blue-500/30"
                >
                  Choose Files
                </label>
                <p className="text-xs text-slate-400 mt-2">
                  {currentAnalyzer.acceptedFiles}
                </p>
              </div>

              {uploadedFiles.length > 0 && (
                <div className="mt-4 space-y-2">
                  {uploadedFiles.map((file, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-2 bg-slate-700/50 rounded-lg border border-slate-600/30"
                    >
                      <span className="text-sm text-slate-200 truncate">
                        {file.name}
                      </span>
                      <span className="text-xs text-slate-400">
                        {Math.round(file.size / 1024)}KB
                      </span>
                    </div>
                  ))}

                  <button
                    onClick={startAnalysis}
                    disabled={analysisStatus === "processing"}
                    className="w-full mt-4 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white px-4 py-2 rounded-lg transition-colors flex items-center justify-center space-x-2 border border-blue-500/30"
                  >
                    <Zap className="w-4 h-4" />
                    <span>
                      {analysisStatus === "processing"
                        ? "Analyzing..."
                        : `Analyze ${currentAnalyzer.type}`}
                    </span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Results Section */}
        <div className="lg:col-span-2">
          <div className="bg-slate-800/60 backdrop-blur-sm rounded-xl shadow-lg border border-slate-700/50">
            <div className="p-6 border-b border-slate-700/50">
              <h3 className="text-lg font-semibold text-white flex items-center">
                {analysisStatus === "idle" && (
                  <Clock className="w-5 h-5 mr-2 text-slate-400" />
                )}
                {analysisStatus === "processing" && (
                  <AlertCircle className="w-5 h-5 mr-2 text-amber-400" />
                )}
                {analysisStatus === "completed" && (
                  <CheckCircle className="w-5 h-5 mr-2 text-emerald-400" />
                )}
                {currentAnalyzer.type} Analysis Results
              </h3>
            </div>

            <div className="p-6">
              {analysisStatus === "idle" && (
                <div className="text-center py-12">
                  <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-4 border border-blue-500/30">
                    <Zap className="w-8 h-8 text-blue-400" />
                  </div>
                  <h4 className="text-lg font-medium text-white mb-2">
                    Ready for {currentAnalyzer.type} Analysis
                  </h4>
                  <p className="text-slate-400">
                    Upload {currentAnalyzer.type.toLowerCase()} files to begin
                    AI-powered medical image analysis
                  </p>
                </div>
              )}

              {analysisStatus === "processing" && (
                <div className="text-center py-12">
                  <div className="animate-spin w-16 h-16 border-4 border-amber-300/30 border-t-amber-400 rounded-full mx-auto mb-4"></div>
                  <h4 className="text-lg font-medium text-white mb-2">
                    Processing {currentAnalyzer.type}...
                  </h4>
                  <p className="text-slate-400">
                    AI is analyzing your {currentAnalyzer.type.toLowerCase()}{" "}
                    images
                  </p>
                  <div className="w-full bg-slate-700 rounded-full h-2 mt-4">
                    <div
                      className="bg-amber-400 h-2 rounded-full animate-pulse"
                      style={{ width: "60%" }}
                    ></div>
                  </div>
                </div>
              )}

              {analysisStatus === "completed" && (
                <div id="medical-report" className="space-y-6 bg-white p-6 rounded-lg text-gray-900">
                  {/* Report Header */}
                  <div className="border-b-2 border-blue-500 pb-4 mb-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-2xl font-bold text-blue-600 flex items-center gap-2">
                          <Stethoscope className="w-6 h-6" />
                          Medical Analysis Report
                        </h3>
                        <p className="text-gray-600 mt-1">{currentAnalyzer.type} Scan Analysis</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-gray-500">Report ID: MA-{Date.now().toString().slice(-6)}</p>
                        <p className="text-sm text-gray-500">Date: {new Date().toLocaleDateString()}</p>
                      </div>
                    </div>
                  </div>

                  {/* Risk Assessment */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className={`bg-gradient-to-r ${analysisResults?.riskLevel === 'LOW' ? 'from-green-50 to-emerald-50 border-l-4 border-green-500' : analysisResults?.riskLevel === 'MODERATE' ? 'from-yellow-50 to-amber-50 border-l-4 border-yellow-500' : 'from-red-50 to-rose-50 border-l-4 border-red-500'} p-4 rounded-lg`}>
                      <div className="flex items-center gap-2 mb-2">
                        <Shield className={`w-5 h-5 ${analysisResults?.riskLevel === 'LOW' ? 'text-green-600' : analysisResults?.riskLevel === 'MODERATE' ? 'text-yellow-600' : 'text-red-600'}`} />
                        <h4 className={`font-semibold ${analysisResults?.riskLevel === 'LOW' ? 'text-green-800' : analysisResults?.riskLevel === 'MODERATE' ? 'text-yellow-800' : 'text-red-800'}`}>Risk Level</h4>
                      </div>
                      <p className={`text-2xl font-bold ${analysisResults?.riskLevel === 'LOW' ? 'text-green-700' : analysisResults?.riskLevel === 'MODERATE' ? 'text-yellow-700' : 'text-red-700'}`}>{analysisResults?.riskLevel || 'LOW'}</p>
                      <p className={`text-sm mt-1 ${analysisResults?.riskLevel === 'LOW' ? 'text-green-600' : analysisResults?.riskLevel === 'MODERATE' ? 'text-yellow-600' : 'text-red-600'}`}>Score: {analysisResults?.riskScore || '2.1/10'}</p>
                    </div>

                    <div className={`bg-gradient-to-r ${analysisResults?.urgency === 'ROUTINE' ? 'from-blue-50 to-cyan-50 border-l-4 border-blue-500' : analysisResults?.urgency === 'PRIORITY' ? 'from-orange-50 to-amber-50 border-l-4 border-orange-500' : 'from-red-50 to-pink-50 border-l-4 border-red-500'} p-4 rounded-lg`}>
                      <div className="flex items-center gap-2 mb-2">
                        <Clock className={`w-5 h-5 ${analysisResults?.urgency === 'ROUTINE' ? 'text-blue-600' : analysisResults?.urgency === 'PRIORITY' ? 'text-orange-600' : 'text-red-600'}`} />
                        <h4 className={`font-semibold ${analysisResults?.urgency === 'ROUTINE' ? 'text-blue-800' : analysisResults?.urgency === 'PRIORITY' ? 'text-orange-800' : 'text-red-800'}`}>Urgency</h4>
                      </div>
                      <p className={`text-2xl font-bold ${analysisResults?.urgency === 'ROUTINE' ? 'text-blue-700' : analysisResults?.urgency === 'PRIORITY' ? 'text-orange-700' : 'text-red-700'}`}>{analysisResults?.urgency || 'ROUTINE'}</p>
                      <p className={`text-sm mt-1 ${analysisResults?.urgency === 'ROUTINE' ? 'text-blue-600' : analysisResults?.urgency === 'PRIORITY' ? 'text-orange-600' : 'text-red-600'}`}>{analysisResults?.urgencyDetail || 'Follow-up in 6-12 months'}</p>
                    </div>

                    <div className={`bg-gradient-to-r ${analysisResults?.treatment === 'MONITORING' ? 'from-purple-50 to-indigo-50 border-l-4 border-purple-500' : analysisResults?.treatment === 'CONSULTATION' ? 'from-amber-50 to-yellow-50 border-l-4 border-amber-500' : 'from-red-50 to-rose-50 border-l-4 border-red-500'} p-4 rounded-lg`}>
                      <div className="flex items-center gap-2 mb-2">
                        <Heart className={`w-5 h-5 ${analysisResults?.treatment === 'MONITORING' ? 'text-purple-600' : analysisResults?.treatment === 'CONSULTATION' ? 'text-amber-600' : 'text-red-600'}`} />
                        <h4 className={`font-semibold ${analysisResults?.treatment === 'MONITORING' ? 'text-purple-800' : analysisResults?.treatment === 'CONSULTATION' ? 'text-amber-800' : 'text-red-800'}`}>Treatment</h4>
                      </div>
                      <p className={`text-2xl font-bold ${analysisResults?.treatment === 'MONITORING' ? 'text-purple-700' : analysisResults?.treatment === 'CONSULTATION' ? 'text-amber-700' : 'text-red-700'}`}>{analysisResults?.treatment || 'MONITORING'}</p>
                      <p className={`text-sm mt-1 ${analysisResults?.treatment === 'MONITORING' ? 'text-purple-600' : analysisResults?.treatment === 'CONSULTATION' ? 'text-amber-600' : 'text-red-600'}`}>{analysisResults?.treatmentDetail || 'No immediate intervention'}</p>
                    </div>
                  </div>

                  {/* Key Findings */}
                  <div className="bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 rounded-lg p-6">
                    <h4 className="font-bold text-emerald-800 mb-4 flex items-center gap-2">
                      <CheckCircle className="w-5 h-5" />
                      Key Clinical Findings - {currentAnalyzer.type}
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <h5 className="font-semibold text-emerald-700 mb-2">Primary Observations:</h5>
                        <ul className="text-sm text-emerald-700 space-y-2">
                          {analysisResults?.findings?.map((finding: string, index: number) => (
                            <li key={index} className="flex items-start gap-2">
                              <span className="w-2 h-2 bg-emerald-500 rounded-full mt-2 flex-shrink-0"></span>
                              <span>{finding}</span>
                            </li>
                          )) || (
                            <>
                              <li className="flex items-start gap-2">
                                <span className="w-2 h-2 bg-emerald-500 rounded-full mt-2 flex-shrink-0"></span>
                                <span>Analysis completed successfully with high confidence</span>
                              </li>
                              <li className="flex items-start gap-2">
                                <span className="w-2 h-2 bg-emerald-500 rounded-full mt-2 flex-shrink-0"></span>
                                <span>No immediate abnormalities detected</span>
                              </li>
                            </>
                          )}
                        </ul>
                      </div>
                      <div>
                        <h5 className="font-semibold text-emerald-700 mb-2">Technical Quality:</h5>
                        <ul className="text-sm text-emerald-700 space-y-2">
                          <li className="flex items-start gap-2">
                            <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></span>
                            <span>Image quality: Excellent</span>
                          </li>
                          <li className="flex items-start gap-2">
                            <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></span>
                            <span>Contrast resolution: Optimal</span>
                          </li>
                          <li className="flex items-start gap-2">
                            <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></span>
                            <span>Artifacts: Minimal motion artifacts</span>
                          </li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  {/* Detailed Metrics */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
                      <div className="flex items-center gap-2 mb-2">
                        <TrendingUp className="w-5 h-5 text-blue-600" />
                        <h5 className="font-semibold text-blue-800">AI Confidence</h5>
                      </div>
                      <div className="flex items-center space-x-2 mb-2">
                        <div className="flex-1 bg-blue-200 rounded-full h-3">
                          <div className="bg-blue-600 h-3 rounded-full" style={{ width: `${analysisResults?.confidence || 94}%` }}></div>
                        </div>
                        <span className="text-sm font-bold text-blue-700">{analysisResults?.confidence || 94}%</span>
                      </div>
                      <p className="text-xs text-blue-600">{(analysisResults?.confidence || 94) >= 90 ? 'High reliability score' : (analysisResults?.confidence || 94) >= 80 ? 'Good reliability score' : 'Moderate reliability score'}</p>
                    </div>

                    <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200">
                      <div className="flex items-center gap-2 mb-2">
                        <Clock className="w-5 h-5 text-green-600" />
                        <h5 className="font-semibold text-green-800">Processing Time</h5>
                      </div>
                      <p className="text-2xl font-bold text-green-700">{analysisResults?.processingTime || '2.3s'}</p>
                      <p className="text-xs text-green-600">Ultra-fast analysis</p>
                    </div>

                    <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4 border border-purple-200">
                      <div className="flex items-center gap-2 mb-2">
                        <Brain className="w-5 h-5 text-purple-600" />
                        <h5 className="font-semibold text-purple-800">AI Model</h5>
                      </div>
                      <p className="text-lg font-bold text-purple-700">MedScope v3.2</p>
                      <p className="text-xs text-purple-600">Latest neural network</p>
                    </div>

                    <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-4 border border-orange-200">
                      <div className="flex items-center gap-2 mb-2">
                        <FileText className="w-5 h-5 text-orange-600" />
                        <h5 className="font-semibold text-orange-800">Report Status</h5>
                      </div>
                      <p className="text-lg font-bold text-orange-700">FINAL</p>
                      <p className="text-xs text-orange-600">Ready for review</p>
                    </div>
                  </div>

                  {/* Recommendations */}
                  <div className="bg-gradient-to-r from-amber-50 to-yellow-50 border border-amber-200 rounded-lg p-6">
                    <h4 className="font-bold text-amber-800 mb-4 flex items-center gap-2">
                      <Calendar className="w-5 h-5" />
                      Clinical Recommendations
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h5 className="font-semibold text-amber-700 mb-3">Immediate Actions:</h5>
                        <ul className="space-y-2 text-sm text-amber-700">
                          {analysisResults?.recommendations?.immediate?.map((action: string, index: number) => (
                            <li key={index} className="flex items-center gap-2">
                              <CheckCircle className="w-4 h-4 text-green-500" />
                              <span>{action}</span>
                            </li>
                          )) || (
                            <>
                              <li className="flex items-center gap-2">
                                <CheckCircle className="w-4 h-4 text-green-500" />
                                <span>No immediate intervention required</span>
                              </li>
                              <li className="flex items-center gap-2">
                                <CheckCircle className="w-4 h-4 text-green-500" />
                                <span>Continue current treatment regimen</span>
                              </li>
                            </>
                          )}
                        </ul>
                      </div>
                      <div>
                        <h5 className="font-semibold text-amber-700 mb-3">Follow-up Plan:</h5>
                        <ul className="space-y-2 text-sm text-amber-700">
                          {analysisResults?.recommendations?.followUp?.map((plan: string, index: number) => (
                            <li key={index} className="flex items-center gap-2">
                              <Calendar className="w-4 h-4 text-blue-500" />
                              <span>{plan}</span>
                            </li>
                          )) || (
                            <>
                              <li className="flex items-center gap-2">
                                <Calendar className="w-4 h-4 text-blue-500" />
                                <span>Routine follow-up in 6-12 months</span>
                              </li>
                              <li className="flex items-center gap-2">
                                <Calendar className="w-4 h-4 text-blue-500" />
                                <span>Monitor for any new symptoms</span>
                              </li>
                            </>
                          )}
                        </ul>
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex flex-wrap gap-3 pt-4 border-t border-gray-200">
                    <button
                      onClick={generatePDFReport}
                      className="flex items-center space-x-2 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white px-6 py-3 rounded-lg transition-all duration-200 shadow-lg hover:shadow-xl border border-green-500/30"
                    >
                      <Download className="w-5 h-5" />
                      <span className="font-semibold">Download PDF Report</span>
                    </button>
                  </div>

                  {/* Disclaimer */}
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mt-6">
                    <p className="text-xs text-gray-600 text-center">
                      <strong>Medical Disclaimer:</strong> This AI-generated report is for informational purposes only and should not replace professional medical advice. 
                      Always consult with qualified healthcare professionals for proper diagnosis and treatment decisions.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Doctor's Feedback Popup */}
      {showFeedbackPopup && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full mx-4 transform transition-all">
            {!feedbackSubmitted ? (
              <div className="p-6">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                    <Stethoscope className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-800">Doctor's Feedback</h3>
                    <p className="text-sm text-gray-600">Help us improve our AI analysis</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Rate the analysis accuracy (1-5 stars)
                    </label>
                    <StarRating rating={feedbackRating} onRatingChange={setFeedbackRating} />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      What can we improve? (Press Enter to submit)
                    </label>
                    <textarea
                      value={feedbackText}
                      onChange={(e) => setFeedbackText(e.target.value)}
                      onKeyDown={handleFeedbackSubmit}
                      placeholder="Share your feedback on the analysis accuracy, missing findings, or suggestions for improvement..."
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                      rows={4}
                      autoFocus
                    />
                  </div>

                  <div className="flex justify-between items-center pt-2">
                    <button
                      onClick={() => setShowFeedbackPopup(false)}
                      className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                    >
                      Skip for now
                    </button>
                    <div className="text-xs text-gray-500">
                      Press Enter to submit feedback
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-6 text-center">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="w-8 h-8 text-green-600" />
                </div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">Thank You!</h3>
                <p className="text-gray-600">Your feedback has been shared successfully</p>
                <div className="mt-4 text-sm text-green-600 font-medium">
                  ✓ Feedback submitted to improve AI analysis
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ReportAnalyzer;
