import React, { useState } from 'react';
import { Upload, FileImage, Zap, Download, CheckCircle, AlertCircle, Clock, Brain, Scan, Activity } from 'lucide-react';

const ReportAnalyzer: React.FC = () => {
  const [activeAnalyzer, setActiveAnalyzer] = useState<'MRI' | 'CT' | 'XRAY'>('MRI');
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [analysisStatus, setAnalysisStatus] = useState<'idle' | 'processing' | 'completed'>('idle');

  const handleFileUpload = (files: FileList | null) => {
    if (files) {
      setUploadedFiles(Array.from(files));
    }
  };

  const startAnalysis = () => {
    setAnalysisStatus('processing');
    // Simulate analysis
    setTimeout(() => {
      setAnalysisStatus('completed');
    }, 3000);
  };

  const analyzers = [
    { 
      type: 'MRI' as const, 
      label: 'MRI Analysis', 
      icon: Brain, 
      color: 'blue',
      description: 'Magnetic Resonance Imaging analysis with advanced AI',
      acceptedFiles: 'DICOM, JPEG, PNG files'
    },
    { 
      type: 'CT' as const, 
      label: 'CT Scan Analysis', 
      icon: Scan, 
      color: 'teal',
      description: 'Computed Tomography scan interpretation',
      acceptedFiles: 'DICOM, JPEG, PNG files'
    },
    { 
      type: 'XRAY' as const, 
      label: 'X-Ray Analysis', 
      icon: Activity, 
      color: 'purple',
      description: 'Radiographic image analysis and interpretation',
      acceptedFiles: 'DICOM, JPEG, PNG files'
    }
  ];

  const currentAnalyzer = analyzers.find(a => a.type === activeAnalyzer)!;
  const color = currentAnalyzer.color;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Medical Report Analyzer</h2>
        <p className="text-gray-600">AI-powered analysis for MRI, CT scans, and X-ray imaging</p>
      </div>

      {/* Analyzer Type Selector */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Select Analysis Type</h3>
        </div>
        <div className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {analyzers.map((analyzer) => {
              const Icon = analyzer.icon;
              const isActive = activeAnalyzer === analyzer.type;
              
              return (
                <button
                  key={analyzer.type}
                  onClick={() => {
                    setActiveAnalyzer(analyzer.type);
                    setUploadedFiles([]);
                    setAnalysisStatus('idle');
                  }}
                  className={`p-4 rounded-lg border-2 transition-all duration-200 text-left ${
                    isActive
                      ? `border-${analyzer.color}-500 bg-${analyzer.color}-50`
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center space-x-3 mb-2">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      isActive ? `bg-${analyzer.color}-100` : 'bg-gray-100'
                    }`}>
                      <Icon className={`w-5 h-5 ${
                        isActive ? `text-${analyzer.color}-600` : 'text-gray-600'
                      }`} />
                    </div>
                    <h4 className={`font-medium ${
                      isActive ? `text-${analyzer.color}-900` : 'text-gray-900'
                    }`}>
                      {analyzer.label}
                    </h4>
                  </div>
                  <p className={`text-sm ${
                    isActive ? `text-${analyzer.color}-700` : 'text-gray-600'
                  }`}>
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
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <Upload className={`w-5 h-5 mr-2 text-${color}-600`} />
                Upload {currentAnalyzer.type} Files
              </h3>
            </div>
            
            <div className="p-6">
              <div
                className={`border-2 border-dashed border-${color}-300 rounded-lg p-8 text-center hover:border-${color}-400 transition-colors`}
                onDrop={(e) => {
                  e.preventDefault();
                  handleFileUpload(e.dataTransfer.files);
                }}
                onDragOver={(e) => e.preventDefault()}
              >
                <FileImage className={`w-12 h-12 text-${color}-400 mx-auto mb-4`} />
                <p className="text-gray-600 mb-2">Drop {currentAnalyzer.type} files here or click to upload</p>
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
                  className={`inline-flex items-center px-4 py-2 bg-${color}-600 hover:bg-${color}-700 text-white text-sm font-medium rounded-lg cursor-pointer transition-colors`}
                >
                  Choose Files
                </label>
                <p className="text-xs text-gray-500 mt-2">
                  {currentAnalyzer.acceptedFiles}
                </p>
              </div>

              {uploadedFiles.length > 0 && (
                <div className="mt-4 space-y-2">
                  {uploadedFiles.map((file, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                      <span className="text-sm text-gray-700 truncate">{file.name}</span>
                      <span className="text-xs text-gray-500">{Math.round(file.size / 1024)}KB</span>
                    </div>
                  ))}
                  
                  <button
                    onClick={startAnalysis}
                    disabled={analysisStatus === 'processing'}
                    className={`w-full mt-4 bg-${color}-600 hover:bg-${color}-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg transition-colors flex items-center justify-center space-x-2`}
                  >
                    <Zap className="w-4 h-4" />
                    <span>
                      {analysisStatus === 'processing' ? 'Analyzing...' : `Analyze ${currentAnalyzer.type}`}
                    </span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Results Section */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                {analysisStatus === 'idle' && <Clock className={`w-5 h-5 mr-2 text-gray-400`} />}
                {analysisStatus === 'processing' && <AlertCircle className={`w-5 h-5 mr-2 text-yellow-500`} />}
                {analysisStatus === 'completed' && <CheckCircle className={`w-5 h-5 mr-2 text-green-500`} />}
                {currentAnalyzer.type} Analysis Results
              </h3>
            </div>
            
            <div className="p-6">
              {analysisStatus === 'idle' && (
                <div className="text-center py-12">
                  <div className={`w-16 h-16 bg-${color}-100 rounded-full flex items-center justify-center mx-auto mb-4`}>
                    <Zap className={`w-8 h-8 text-${color}-600`} />
                  </div>
                  <h4 className="text-lg font-medium text-gray-900 mb-2">Ready for {currentAnalyzer.type} Analysis</h4>
                  <p className="text-gray-500">Upload {currentAnalyzer.type.toLowerCase()} files to begin AI-powered medical image analysis</p>
                </div>
              )}

              {analysisStatus === 'processing' && (
                <div className="text-center py-12">
                  <div className="animate-spin w-16 h-16 border-4 border-yellow-200 border-t-yellow-600 rounded-full mx-auto mb-4"></div>
                  <h4 className="text-lg font-medium text-gray-900 mb-2">Processing {currentAnalyzer.type}...</h4>
                  <p className="text-gray-500">AI is analyzing your {currentAnalyzer.type.toLowerCase()} images</p>
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-4">
                    <div className="bg-yellow-600 h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
                  </div>
                </div>
              )}

              {analysisStatus === 'completed' && (
                <div className="space-y-6">
                  {/* Key Findings */}
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <h4 className="font-medium text-green-900 mb-2">Key Findings - {currentAnalyzer.type}</h4>
                    <ul className="text-sm text-green-800 space-y-1">
                      {currentAnalyzer.type === 'MRI' && (
                        <>
                          <li>• No significant abnormalities detected in brain tissue</li>
                          <li>• Normal white and gray matter distribution</li>
                          <li>• Clear ventricular system</li>
                        </>
                      )}
                      {currentAnalyzer.type === 'CT' && (
                        <>
                          <li>• No acute intracranial abnormalities</li>
                          <li>• Normal bone density patterns</li>
                          <li>• Clear anatomical structures</li>
                        </>
                      )}
                      {currentAnalyzer.type === 'XRAY' && (
                        <>
                          <li>• No fractures or dislocations identified</li>
                          <li>• Normal bone alignment and density</li>
                          <li>• Clear joint spaces</li>
                        </>
                      )}
                    </ul>
                  </div>

                  {/* Detailed Analysis */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h5 className="font-medium text-gray-900 mb-2">AI Confidence Score</h5>
                      <div className="flex items-center space-x-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div className="bg-green-600 h-2 rounded-full" style={{ width: '94%' }}></div>
                        </div>
                        <span className="text-sm font-medium text-gray-700">94%</span>
                      </div>
                    </div>
                    
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h5 className="font-medium text-gray-900 mb-2">Processing Time</h5>
                      <p className="text-2xl font-bold text-gray-900">2.3s</p>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex space-x-4">
                    <button className="flex items-center space-x-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors">
                      <Download className="w-4 h-4" />
                      <span>Download Report</span>
                    </button>
                    <button className={`flex items-center space-x-2 bg-${color}-600 hover:bg-${color}-700 text-white px-4 py-2 rounded-lg transition-colors`}>
                      <span>View Detailed Analysis</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportAnalyzer;