import React, { useState } from 'react';
import { 
  Play, 
  Pause, 
  RotateCw, 
  ZoomIn, 
  ZoomOut, 
  Layers, 
  Settings,
  Upload,
  Eye,
  Maximize
} from 'lucide-react';

const Visualization3D: React.FC = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentSlice, setCurrentSlice] = useState(50);
  const [zoom, setZoom] = useState(100);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">2D to 3D Visualization</h2>
        <p className="text-gray-600">Transform medical imaging data into interactive 3D models</p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        {/* Main Viewer */}
        <div className="xl:col-span-3">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">3D Model Viewer</h3>
                <div className="flex items-center space-x-2">
                  <button className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                    <Maximize className="w-4 h-4" />
                  </button>
                  <button className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                    <Settings className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
            
            <div className="relative">
              {/* 3D Viewer Placeholder */}
              <div className="h-96 bg-gradient-to-br from-gray-100 to-gray-200 rounded-b-xl flex items-center justify-center">
                <div className="text-center">
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Eye className="w-8 h-8 text-blue-600" />
                  </div>
                  <h4 className="text-lg font-medium text-gray-900 mb-2">3D Model Viewer</h4>
                  <p className="text-gray-500 mb-4">Upload MRI/CT scan data to generate 3D visualization</p>
                  <button className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors mx-auto">
                    <Upload className="w-4 h-4" />
                    <span>Upload DICOM Files</span>
                  </button>
                </div>
              </div>

              {/* Controls Overlay */}
              <div className="absolute bottom-4 left-4 right-4">
                <div className="bg-white/90 backdrop-blur-sm rounded-lg p-4 shadow-lg">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <button
                        onClick={() => setIsPlaying(!isPlaying)}
                        className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg transition-colors"
                      >
                        {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                        <span className="text-sm">{isPlaying ? 'Pause' : 'Rotate'}</span>
                      </button>
                      
                      <div className="flex items-center space-x-2">
                        <button className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                          <ZoomOut className="w-4 h-4" />
                        </button>
                        <span className="text-sm font-medium text-gray-700 min-w-12 text-center">{zoom}%</span>
                        <button className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                          <ZoomIn className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-600">Slice:</span>
                      <input
                        type="range"
                        min="1"
                        max="100"
                        value={currentSlice}
                        onChange={(e) => setCurrentSlice(parseInt(e.target.value))}
                        className="w-20"
                      />
                      <span className="text-sm font-medium text-gray-700 min-w-8">{currentSlice}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Side Panel */}
        <div className="space-y-6">
          {/* Layer Controls */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <Layers className="w-5 h-5 mr-2 text-blue-600" />
                Layer Controls
              </h3>
            </div>
            <div className="p-4 space-y-4">
              {['Bone', 'Soft Tissue', 'Blood Vessels', 'Organs'].map((layer, index) => (
                <div key={index} className="flex items-center justify-between">
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      defaultChecked={index < 2}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">{layer}</span>
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    defaultValue="80"
                    className="w-16"
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Rendering Options */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Rendering Options</h3>
            </div>
            <div className="p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Quality
                </label>
                <select className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
                  <option>High Quality</option>
                  <option>Medium Quality</option>
                  <option>Low Quality</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Lighting
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  defaultValue="70"
                  className="w-full"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Contrast
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  defaultValue="50"
                  className="w-full"
                />
              </div>
            </div>
          </div>

          {/* Export Options */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Export</h3>
            </div>
            <div className="p-4 space-y-3">
              <button className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors text-sm">
                Export as STL
              </button>
              <button className="w-full bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors text-sm">
                Export as OBJ
              </button>
              <button className="w-full bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors text-sm">
                Save as Image
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Visualization3D;