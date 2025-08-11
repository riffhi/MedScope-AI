import React, { useState } from "react";
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
  Maximize,
} from "lucide-react";

const Visualization3D: React.FC = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentSlice, setCurrentSlice] = useState(50);
  const [zoom, setZoom] = useState(100);

  return (
    <div className="space-y-6 bg-slate-900 text-slate-100 p-6 min-h-screen">
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">
          2D to 3D Visualization
        </h2>
        <p className="text-slate-400">
          Transform medical imaging data into interactive 3D models
        </p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        {/* Main Viewer */}
        <div className="xl:col-span-3">
          <div className="bg-slate-800/60 backdrop-blur-sm rounded-xl shadow-lg border border-slate-700/50">
            <div className="p-4 border-b border-slate-700/50">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white">
                  3D Model Viewer
                </h3>
                <div className="flex items-center space-x-2">
                  <button className="p-2 text-slate-400 hover:text-blue-400 hover:bg-slate-700/50 rounded-lg transition-colors">
                    <Maximize className="w-4 h-4" />
                  </button>
                  <button className="p-2 text-slate-400 hover:text-blue-400 hover:bg-slate-700/50 rounded-lg transition-colors">
                    <Settings className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

            <div className="relative">
              {/* 3D Viewer Placeholder */}
              <div className="h-96 bg-gradient-to-br from-slate-800 to-slate-900 rounded-b-xl flex items-center justify-center border-t border-slate-700/30">
                <div className="text-center">
                  <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-4 border border-blue-500/30">
                    <Eye className="w-8 h-8 text-blue-400" />
                  </div>
                  <h4 className="text-lg font-medium text-white mb-2">
                    3D Model Viewer
                  </h4>
                  <p className="text-slate-400 mb-4">
                    Upload MRI/CT scan data to generate 3D visualization
                  </p>
                  <button className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors mx-auto border border-blue-500/30">
                    <Upload className="w-4 h-4" />
                    <span>Upload DICOM Files</span>
                  </button>
                </div>
              </div>

              {/* Controls Overlay */}
              <div className="absolute bottom-4 left-4 right-4">
                <div className="bg-slate-800/90 backdrop-blur-sm rounded-lg p-4 shadow-lg border border-slate-600/50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <button
                        onClick={() => setIsPlaying(!isPlaying)}
                        className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg transition-colors border border-blue-500/30"
                      >
                        {isPlaying ? (
                          <Pause className="w-4 h-4" />
                        ) : (
                          <Play className="w-4 h-4" />
                        )}
                        <span className="text-sm">
                          {isPlaying ? "Pause" : "Rotate"}
                        </span>
                      </button>

                      <div className="flex items-center space-x-2">
                        <button className="p-2 text-slate-400 hover:text-blue-400 hover:bg-slate-700/50 rounded-lg transition-colors">
                          <ZoomOut className="w-4 h-4" />
                        </button>
                        <span className="text-sm font-medium text-slate-200 min-w-12 text-center">
                          {zoom}%
                        </span>
                        <button className="p-2 text-slate-400 hover:text-blue-400 hover:bg-slate-700/50 rounded-lg transition-colors">
                          <ZoomIn className="w-4 h-4" />
                        </button>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-slate-400">Slice:</span>
                      <input
                        type="range"
                        min="1"
                        max="100"
                        value={currentSlice}
                        onChange={(e) =>
                          setCurrentSlice(parseInt(e.target.value))
                        }
                        className="w-20 accent-blue-500"
                      />
                      <span className="text-sm font-medium text-slate-200 min-w-8">
                        {currentSlice}
                      </span>
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
          <div className="bg-slate-800/60 backdrop-blur-sm rounded-xl shadow-lg border border-slate-700/50">
            <div className="p-4 border-b border-slate-700/50">
              <h3 className="text-lg font-semibold text-white flex items-center">
                <Layers className="w-5 h-5 mr-2 text-blue-400" />
                Layer Controls
              </h3>
            </div>
            <div className="p-4 space-y-4">
              {["Bone", "Soft Tissue", "Blood Vessels", "Organs"].map(
                (layer, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between"
                  >
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        defaultChecked={index < 2}
                        className="w-4 h-4 text-blue-500 bg-slate-700 border-slate-600 rounded focus:ring-blue-500 focus:ring-2"
                      />
                      <span className="text-sm text-slate-200">{layer}</span>
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      defaultValue="80"
                      className="w-16 accent-blue-500"
                    />
                  </div>
                )
              )}
            </div>
          </div>

          {/* Rendering Options */}
          <div className="bg-slate-800/60 backdrop-blur-sm rounded-xl shadow-lg border border-slate-700/50">
            <div className="p-4 border-b border-slate-700/50">
              <h3 className="text-lg font-semibold text-white">
                Rendering Options
              </h3>
            </div>
            <div className="p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Quality
                </label>
                <select className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                  <option>High Quality</option>
                  <option>Medium Quality</option>
                  <option>Low Quality</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Lighting
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  defaultValue="70"
                  className="w-full accent-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Contrast
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  defaultValue="50"
                  className="w-full accent-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Export Options */}
          <div className="bg-slate-800/60 backdrop-blur-sm rounded-xl shadow-lg border border-slate-700/50">
            <div className="p-4 border-b border-slate-700/50">
              <h3 className="text-lg font-semibold text-white">Export</h3>
            </div>
            <div className="p-4 space-y-3">
              <button className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors text-sm border border-blue-500/30">
                Export as STL
              </button>
              <button className="w-full bg-slate-600 hover:bg-slate-700 text-white px-4 py-2 rounded-lg transition-colors text-sm border border-slate-500/30">
                Export as OBJ
              </button>
              <button className="w-full bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg transition-colors text-sm border border-emerald-500/30">
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
