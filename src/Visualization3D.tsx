import React, { useState, useRef, useCallback, useEffect } from "react";
import Plot from "react-plotly.js";
import {
  Play,
  Pause,
  ZoomIn,
  ZoomOut,
  Upload,
  Eye,
  RefreshCw,
  AlertCircle,
  CheckCircle,
} from "lucide-react";
import {
  visualization3DAPI,
  VolumeResponse,
  VolumeStats,
  LibraryStatus,
} from "./services/visualization3dAPI";

// Define a single type for our volume data
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type PlotData = any; // Using any to bypass TypeScript errors for now

const Visualization3D: React.FC = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [zoom, setZoom] = useState(100);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [plotData, setPlotData] = useState<PlotData | null>(null);
  const [volumeStats, setVolumeStats] = useState<VolumeStats | null>(null);
  const [volumeName, setVolumeName] = useState<string>("");
  const [libraryStatus, setLibraryStatus] = useState<LibraryStatus | null>(
    null
  );

  // Simplified rendering options
  const renderingOptions = {
    quality: "high",
    opacity: 25,
  };

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Fetch library status on component mount
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const status = await visualization3DAPI.getStatus();
        setLibraryStatus(status);
      } catch (error) {
        console.error("Failed to fetch library status:", error);
      }
    };
    fetchStatus();
  }, []);

  const processVolumeResponse = useCallback(
    (response: VolumeResponse) => {
      const { data, stats, name } = response;

      setVolumeName(name);
      setVolumeStats(stats);

      const plotTrace: PlotData = {
        type: "volume",
        x: data.x,
        y: data.y,
        z: data.z,
        value: data.values,
        isomin: data.isomin,
        isomax: data.isomax,
        opacity: renderingOptions.opacity / 100,
        surface_count: renderingOptions.quality === "high" ? 20 : 15,
        colorscale: [
          [0.0, "rgba(0,0,50,0)"],
          [0.2, "rgba(0,100,200,0.3)"],
          [0.4, "rgba(0,200,200,0.5)"],
          [0.6, "rgba(100,255,100,0.7)"],
          [0.8, "rgba(255,255,0,0.8)"],
          [1.0, "rgba(255,100,0,0.9)"],
        ],
        showscale: true,
        colorbar: {
          title: { text: "Intensity", side: "right" },
          tickmode: "linear",
          tick0: data.isomin,
          dtick: (data.isomax - data.isomin) / 5,
        },
      };

      setPlotData(plotTrace);
    },
    [renderingOptions.opacity, renderingOptions.quality]
  );

  const handleFileUpload = useCallback(
    async (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      if (!file) return;

      // Validate file
      const validation = visualization3DAPI.validateFile(file);
      if (!validation.valid) {
        setError(validation.error || "Invalid file");
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const response = await visualization3DAPI.uploadFile(file);
        processVolumeResponse(response);
      } catch (error) {
        setError(
          error instanceof Error ? error.message : "Failed to upload file"
        );
      } finally {
        setIsLoading(false);
        if (fileInputRef.current) {
          fileInputRef.current.value = "";
        }
      }
    },
    [processVolumeResponse]
  );

  // No unused functions anymore

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const plotLayout: any = {
    title: {
      text: `3D Medical Visualization - ${volumeName}`,
      x: 0.5,
      xanchor: "center",
      font: { size: 20, color: "white" },
    },
    scene: {
      xaxis: {
        title: "X-axis",
        showgrid: true,
        gridcolor: "rgba(100,100,100,0.3)",
        showbackground: true,
        backgroundcolor: "rgba(20,20,40,0.8)",
        color: "white",
      },
      yaxis: {
        title: "Y-axis",
        showgrid: true,
        gridcolor: "rgba(100,100,100,0.3)",
        showbackground: true,
        backgroundcolor: "rgba(20,20,40,0.8)",
        color: "white",
      },
      zaxis: {
        title: "Z-axis",
        showgrid: true,
        gridcolor: "rgba(100,100,100,0.3)",
        showbackground: true,
        backgroundcolor: "rgba(20,20,40,0.8)",
        color: "white",
      },
      aspectmode: "auto",
      camera: {
        eye: { x: 1.8, y: 1.8, z: 1.8 },
        center: { x: 0, y: 0, z: 0 },
        up: { x: 0, y: 0, z: 1 },
      },
      bgcolor: "rgba(10,10,20,0.9)",
    },
    paper_bgcolor: "rgba(20,20,30,0)",
    plot_bgcolor: "rgba(10,10,20,0)",
    margin: { l: 10, r: 10, b: 10, t: 60 },
    font: { color: "white" },
    showlegend: false,
  };

  const plotConfig = {
    displayModeBar: true,
    displaylogo: false,
    responsive: true,
  };

  return (
    <div className="space-y-4 bg-slate-900 text-slate-100 p-3 min-h-screen max-w-[2000px] mx-auto">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-white">
            2D to 3D Visualization
          </h2>
          <p className="text-slate-400">
            Transform medical imaging data into interactive 3D models
          </p>
        </div>
        {libraryStatus && (
          <div className="flex items-center space-x-4 text-sm">
            <span className="text-slate-500">Backend Libraries:</span>
            {libraryStatus.libraries.monai && (
              <span className="flex items-center text-green-400">
                <CheckCircle className="w-3 h-3 mr-1" />
                MONAI
              </span>
            )}
            {libraryStatus.libraries.nibabel && (
              <span className="flex items-center text-blue-400">
                <CheckCircle className="w-3 h-3 mr-1" />
                NiBabel
              </span>
            )}
            {libraryStatus.libraries.pydicom && (
              <span className="flex items-center text-purple-400">
                <CheckCircle className="w-3 h-3 mr-1" />
                PyDICOM
              </span>
            )}
          </div>
        )}
      </div>

      {/* Upload Controls - Simplified and more compact */}
      <div className="bg-slate-800/60 backdrop-blur-sm rounded-xl shadow-lg border border-slate-700/50 p-2 flex items-center">
        <input
          ref={fileInputRef}
          type="file"
          accept=".nii,.nii.gz,.dcm,.mhd,.mha,.nrrd,.img,.hdr"
          onChange={handleFileUpload}
          className="hidden"
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isLoading}
          className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white px-4 py-2 rounded-lg transition-colors border border-blue-500/30"
        >
          <Upload className="w-4 h-4" />
          <span>Upload Medical File</span>
        </button>
        <p className="text-xs text-slate-400 ml-3">
          Supports: NIfTI, DICOM, MHD, NRRD formats
        </p>
        {error && (
          <div className="ml-4 flex items-center space-x-2 text-red-400">
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm">{error}</span>
            <button
              onClick={() => setError(null)}
              className="ml-2 text-red-400 hover:text-red-300"
            >
              ×
            </button>
          </div>
        )}
      </div>

      {/* Error Display moved to the upload bar */}

      {/* Main 3D Viewer - Simplified header */}
      <div className="bg-slate-800/60 backdrop-blur-sm rounded-xl shadow-lg border border-slate-700/50">
        <div className="p-2 border-b border-slate-700/30">
          {volumeStats ? (
            <div className="flex items-center justify-between">
              <h3 className="text-base font-semibold text-white">
                {volumeName}
              </h3>
              <div className="flex items-center space-x-4 text-xs">
                <span className="text-slate-400">
                  Dimensions:{" "}
                  <span className="text-white">{volumeStats.dimensions}</span>
                </span>
                <span className="text-slate-400">
                  Volume:{" "}
                  <span className="text-white">
                    {volumeStats.volume_cm3} cm³
                  </span>
                </span>
                <span className="text-slate-400">
                  Library:{" "}
                  <span className="text-white">{volumeStats.library_used}</span>
                </span>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-between">
              <h3 className="text-base font-semibold text-white">
                3D Medical Visualization
              </h3>
              <div className="flex items-center space-x-4 text-xs">
                <span className="text-slate-400">Ready for visualization</span>
              </div>
            </div>
          )}
        </div>

        <div className="relative">
          {/* 3D Viewer - Increased height to 90vh */}
          <div className="h-[90vh] bg-gradient-to-br from-slate-800 to-slate-900 rounded-b-xl">
            {isLoading ? (
              <div className="h-full flex items-center justify-center">
                <div className="text-center">
                  <RefreshCw className="w-10 h-10 text-blue-400 animate-spin mx-auto mb-4" />
                  <h4 className="text-xl font-medium text-white mb-2">
                    Processing Medical Image...
                  </h4>
                  <p className="text-slate-400">Generating 3D visualization</p>
                </div>
              </div>
            ) : plotData ? (
              <Plot
                data={[plotData]}
                layout={plotLayout}
                config={plotConfig}
                style={{ width: "100%", height: "100%" }}
                useResizeHandler={true}
              />
            ) : (
              <div className="h-full flex items-center justify-center">
                <div className="text-center">
                  <div className="w-24 h-24 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-6 border border-blue-500/30">
                    <Eye className="w-12 h-12 text-blue-400" />
                  </div>
                  <h4 className="text-2xl font-medium text-white mb-4">
                    3D Medical Visualization
                  </h4>
                  <p className="text-slate-400 mb-6 text-lg max-w-lg">
                    Upload your medical scan to generate an interactive 3D
                    visualization
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Minimal Controls Overlay */}
          {plotData && (
            <div className="absolute top-4 right-4">
              <div className="bg-slate-800/60 backdrop-blur-sm rounded-lg p-2 shadow-lg border border-slate-600/30 flex items-center space-x-2">
                <button
                  onClick={() => setIsPlaying(!isPlaying)}
                  className="p-2 text-slate-300 hover:text-blue-400 hover:bg-slate-700/50 rounded-lg transition-colors"
                >
                  {isPlaying ? (
                    <Pause className="w-5 h-5" />
                  ) : (
                    <Play className="w-5 h-5" />
                  )}
                </button>

                <button
                  onClick={() => setZoom(Math.max(10, zoom - 10))}
                  className="p-2 text-slate-300 hover:text-blue-400 hover:bg-slate-700/50 rounded-lg transition-colors"
                >
                  <ZoomOut className="w-5 h-5" />
                </button>
                <span className="text-xs font-medium text-slate-300 min-w-8 text-center">
                  {zoom}%
                </span>
                <button
                  onClick={() => setZoom(Math.min(500, zoom + 10))}
                  className="p-2 text-slate-300 hover:text-blue-400 hover:bg-slate-700/50 rounded-lg transition-colors"
                >
                  <ZoomIn className="w-5 h-5" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Visualization3D;
