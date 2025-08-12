// API service for 3D visualization functionality

const API_BASE_URL = "http://localhost:8000/api/v1/visualization";

export interface VolumeData {
  x: number[];
  y: number[];
  z: number[];
  values: number[];
  isomin: number;
  isomax: number;
  shape: number[];
  spacing: number[];
}

export interface VolumeStats {
  dimensions: string;
  voxel_spacing: string;
  data_range: string;
  volume_cm3: string;
  library_used: string;
}

export interface VolumeResponse {
  success: boolean;
  name: string;
  data: VolumeData;
  stats: VolumeStats;
  error?: string;
}

export interface LibraryStatus {
  libraries: {
    monai: boolean;
    nibabel: boolean;
    pydicom: boolean;
    simpleitk: boolean;
  };
  supported_formats: string[];
  max_file_size_mb: number;
}

class Visualization3DAPI {
  private baseURL: string;

  constructor() {
    this.baseURL = API_BASE_URL;
  }

  /**
   * Upload and process a medical image file
   */
  async uploadFile(file: File): Promise<VolumeResponse> {
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${this.baseURL}/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `HTTP error! status: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error("Upload error:", error);
      throw error;
    }
  }

  /**
   * Generate a demo volume for visualization
   */
  async generateDemoVolume(
    volumeType: "brain" | "heart" | "lung"
  ): Promise<VolumeResponse> {
    try {
      const response = await fetch(
        `${this.baseURL}/generate_volume/${volumeType}`,
        {
          method: "GET",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `HTTP error! status: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error("Demo volume generation error:", error);
      throw error;
    }
  }

  /**
   * Get the status of available medical imaging libraries
   */
  async getStatus(): Promise<LibraryStatus> {
    try {
      const response = await fetch(`${this.baseURL}/status`, {
        method: "GET",
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error("Status check error:", error);
      throw error;
    }
  }

  /**
   * Validate file format
   */
  validateFile(file: File): { valid: boolean; error?: string } {
    const allowedExtensions = [
      ".nii",
      ".nii.gz",
      ".dcm",
      ".mhd",
      ".mha",
      ".nrrd",
      ".img",
      ".hdr",
    ];
    const fileName = file.name.toLowerCase();

    const isValidExtension = allowedExtensions.some(
      (ext) =>
        fileName.endsWith(ext) ||
        (ext === ".nii.gz" && fileName.includes(".nii.gz"))
    );

    if (!isValidExtension) {
      return {
        valid: false,
        error: `Invalid file type. Supported formats: ${allowedExtensions.join(
          ", "
        )}`,
      };
    }

    // Check file size (500MB limit)
    const maxSizeBytes = 500 * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      return {
        valid: false,
        error: `File too large. Maximum size is 500MB, got ${(
          file.size /
          (1024 * 1024)
        ).toFixed(1)}MB`,
      };
    }

    return { valid: true };
  }
}

export const visualization3DAPI = new Visualization3DAPI();
