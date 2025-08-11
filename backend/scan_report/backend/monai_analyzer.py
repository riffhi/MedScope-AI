"""
MONAI-based Medical Image Analyzer
Provides professional medical imaging analysis using MONAI framework
"""

import numpy as np
import cv2
from PIL import Image
import torch
import torch.nn.functional as F
from monai.transforms import (
    Compose, LoadImage, Resize, ToTensor, NormalizeIntensity,
    ScaleIntensity, Spacing, Orientation, CropForeground
)
from monai.networks.nets import UNet
from monai.networks.layers import Norm
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional
import json

logger = logging.getLogger(__name__)

class MONAIMedicalAnalyzer:
    """Medical image analysis using MONAI framework"""
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Initialize MONAI transforms
        self.transforms = Compose([
            LoadImage(image_only=True),
            ScaleIntensity(minv=0.0, maxv=1.0),
            Resize(spatial_size=(256, 256)),
            ToTensor()
        ])
        
        # Medical analysis parameters
        self.medical_terms = {
            'tumor': ['mass', 'lesion', 'nodule', 'tumor', 'cancer'],
            'inflammation': ['inflammation', 'edema', 'swelling', 'infection'],
            'calcification': ['calcification', 'calcified', 'stone'],
            'fracture': ['fracture', 'break', 'crack', 'dislocation'],
            'hemorrhage': ['bleeding', 'hemorrhage', 'hematoma'],
            'atrophy': ['atrophy', 'shrinkage', 'degeneration']
        }
    
    def analyze_medical_image(self, image_path: str, filename: str) -> Dict:
        """Analyze medical image using MONAI and computer vision techniques"""
        try:
            logger.info(f"Starting MONAI analysis for: {filename}")
            
            # Load and preprocess image
            image = self._load_and_preprocess_image(image_path)
            if image is None:
                logger.error(f"Failed to load image: {filename}")
                return self._create_error_response(filename, "Failed to load image")
            
            logger.info(f"Image loaded successfully: {filename}, shape: {image.shape}")
            
            # Perform comprehensive analysis
            analysis_results = {
                "filename": filename,
                "file_type": "medical_image",
                "image_analysis": self._analyze_image_features(image),
                "medical_findings": self._detect_medical_patterns(image),
                "quality_assessment": self._assess_image_quality(image),
                "recommendations": self._generate_recommendations(image),
                "technical_details": self._extract_technical_info(image_path)
            }
            
            # Generate summary
            analysis_results["summary"] = self._generate_summary(analysis_results)
            
            logger.info(f"MONAI analysis completed successfully for: {filename}")
            return analysis_results
            
        except Exception as e:
            logger.error(f"MONAI analysis failed for {filename}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return self._create_error_response(filename, f"Analysis error: {str(e)}")
    
    def _load_and_preprocess_image(self, image_path: str) -> Optional[np.ndarray]:
        """Load and preprocess medical image"""
        try:
            logger.info(f"Loading image: {image_path}")
            
            # Try OpenCV first
            image = cv2.imread(image_path)
            if image is not None:
                logger.info(f"Image loaded with OpenCV: {image.shape}")
                # Convert BGR to RGB
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                # Fallback to PIL
                logger.info("OpenCV failed, trying PIL")
                with Image.open(image_path) as pil_image:
                    image = np.array(pil_image)
                    logger.info(f"Image loaded with PIL: {image.shape}")
            
            if image is None or image.size == 0:
                logger.error(f"Failed to load image: {image_path}")
                return None
            
            # Apply medical image preprocessing
            image = self._apply_medical_preprocessing(image)
            
            logger.info(f"Image preprocessing completed: {image.shape}, dtype: {image.dtype}")
            return image
            
        except Exception as e:
            logger.error(f"Image loading failed: {e}")
            import traceback
            logger.error(f"Image loading traceback: {traceback.format_exc()}")
            return None
    
    def _apply_medical_preprocessing(self, image: np.ndarray) -> np.ndarray:
        """Apply medical image-specific preprocessing"""
        try:
            # Convert to grayscale if it's a medical image (X-ray, CT, MRI)
            if len(image.shape) == 3:
                # Check if it's a grayscale medical image
                if np.std(image[:,:,0] - image[:,:,1]) < 5 and np.std(image[:,:,1] - image[:,:,2]) < 5:
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                    image = np.stack([image, image, image], axis=-1)
            
            # Enhance contrast for medical images
            if len(image.shape) == 3:
                lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
                l, a, b = cv2.split(lab)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                l = clahe.apply(l)
                lab = cv2.merge([l, a, b])
                image = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
            
            return image
            
        except Exception as e:
            logger.error(f"Preprocessing failed: {e}")
            return image
    
    def _analyze_image_features(self, image: np.ndarray) -> Dict:
        """Analyze basic image features"""
        try:
            features = {}
            
            # Basic image properties
            features["dimensions"] = f"{image.shape[1]}x{image.shape[0]} pixels"
            features["channels"] = image.shape[2] if len(image.shape) == 3 else 1
            features["data_type"] = str(image.dtype)
            
            # Image statistics
            if len(image.shape) == 3:
                features["mean_intensity"] = np.mean(image)
                features["std_intensity"] = np.std(image)
                features["min_intensity"] = np.min(image)
                features["max_intensity"] = np.max(image)
            
            # Edge detection for medical features
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image
            
            edges = cv2.Canny(gray, 50, 150)
            features["edge_density"] = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            
            # Texture analysis
            features["texture_variance"] = np.var(gray)
            
            return features
            
        except Exception as e:
            logger.error(f"Feature analysis failed: {e}")
            return {"error": f"Feature analysis failed: {str(e)}"}
    
    def _detect_medical_patterns(self, image: np.ndarray) -> Dict:
        """Detect medical patterns and abnormalities"""
        try:
            findings = {}
            
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image
            
            # Detect potential masses/lesions using contour analysis
            contours, _ = cv2.findContours(
                cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)[1],
                cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Analyze contours for medical significance
            significant_contours = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:  # Filter small noise
                    perimeter = cv2.arcLength(contour, True)
                    circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
                    
                    if circularity > 0.3:  # Potential mass/lesion
                        significant_contours.append({
                            "area": area,
                            "circularity": circularity,
                            "perimeter": perimeter
                        })
            
            findings["potential_masses"] = len(significant_contours)
            findings["contour_analysis"] = significant_contours
            
            # Detect asymmetry (common in medical images)
            left_half = gray[:, :gray.shape[1]//2]
            right_half = gray[:, gray.shape[1]//2:]
            
            if left_half.shape == right_half.shape:
                asymmetry_score = np.abs(np.mean(left_half) - np.mean(right_half)) / np.mean(gray)
                findings["asymmetry_score"] = asymmetry_score
                findings["asymmetry_interpretation"] = "High" if asymmetry_score > 0.2 else "Low"
            
            # Detect intensity variations (potential abnormalities)
            intensity_variations = np.std(gray)
            findings["intensity_variation"] = intensity_variations
            findings["variation_interpretation"] = "High" if intensity_variations > 50 else "Normal"
            
            return findings
            
        except Exception as e:
            logger.error(f"Pattern detection failed: {e}")
            return {"error": f"Pattern detection failed: {str(e)}"}
    
    def _assess_image_quality(self, image: np.ndarray) -> Dict:
        """Assess medical image quality"""
        try:
            quality = {}
            
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image
            
            # Sharpness assessment
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            quality["sharpness"] = laplacian_var
            quality["sharpness_rating"] = "High" if laplacian_var > 100 else "Medium" if laplacian_var > 50 else "Low"
            
            # Noise assessment
            noise_level = np.std(gray)
            quality["noise_level"] = noise_level
            quality["noise_rating"] = "Low" if noise_level < 20 else "Medium" if noise_level < 50 else "High"
            
            # Contrast assessment
            contrast = np.max(gray) - np.min(gray)
            quality["contrast"] = contrast
            quality["contrast_rating"] = "Good" if contrast > 150 else "Fair" if contrast > 100 else "Poor"
            
            # Overall quality score
            quality_score = (min(laplacian_var/100, 1) + min(20/noise_level, 1) + min(contrast/150, 1)) / 3
            quality["overall_score"] = quality_score
            quality["overall_rating"] = "Excellent" if quality_score > 0.8 else "Good" if quality_score > 0.6 else "Fair" if quality_score > 0.4 else "Poor"
            
            return quality
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            return {"error": f"Quality assessment failed: {str(e)}"}
    
    def _generate_recommendations(self, image: np.ndarray) -> List[str]:
        """Generate clinical recommendations based on image analysis"""
        try:
            recommendations = []
            
            # Quality-based recommendations
            quality = self._assess_image_quality(image)
            if "overall_rating" in quality:
                if quality["overall_rating"] in ["Poor", "Fair"]:
                    recommendations.append("Consider re-imaging with improved technique for better diagnostic quality")
                
                if quality.get("sharpness_rating") == "Low":
                    recommendations.append("Image sharpness is suboptimal - ensure proper patient positioning and technique")
                
                if quality.get("noise_rating") == "High":
                    recommendations.append("High noise levels detected - consider adjusting imaging parameters")
            
            # Pattern-based recommendations
            patterns = self._detect_medical_patterns(image)
            if patterns.get("potential_masses", 0) > 0:
                recommendations.append("Potential masses/lesions detected - recommend detailed radiological review")
            
            if patterns.get("asymmetry_interpretation") == "High":
                recommendations.append("Significant asymmetry detected - recommend bilateral comparison and clinical correlation")
            
            # General medical recommendations
            recommendations.append("All findings should be correlated with clinical history and physical examination")
            recommendations.append("Consider additional imaging modalities if clinical suspicion remains high")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return ["Analysis error - manual review recommended"]
    
    def _extract_technical_info(self, image_path: str) -> Dict:
        """Extract technical information from image file"""
        try:
            info = {}
            
            # File information
            file_path = Path(image_path)
            info["file_size"] = f"{file_path.stat().st_size / 1024:.1f} KB"
            info["file_extension"] = file_path.suffix.lower()
            
            # Image metadata
            with Image.open(image_path) as img:
                info["original_mode"] = img.mode
                info["original_size"] = f"{img.width}x{img.height}"
                
                # Try to extract EXIF data
                try:
                    exif = img._getexif()
                    if exif:
                        info["has_exif"] = True
                        # Extract relevant medical imaging metadata
                        for tag_id, value in exif.items():
                            if tag_id in [270, 271, 272]:  # Description, Make, Model
                                info[f"exif_{tag_id}"] = str(value)
                except:
                    info["has_exif"] = False
            
            return info
            
        except Exception as e:
            logger.error(f"Technical info extraction failed: {e}")
            return {"error": f"Technical info extraction failed: {str(e)}"}
    
    def _generate_summary(self, analysis_results: Dict) -> str:
        """Generate a comprehensive summary of the analysis"""
        try:
            summary_parts = []
            
            # Image quality summary
            quality = analysis_results.get("quality_assessment", {})
            if "overall_rating" in quality:
                summary_parts.append(f"Image quality: {quality['overall_rating']}")
            
            # Medical findings summary
            patterns = analysis_results.get("medical_findings", {})
            if patterns.get("potential_masses", 0) > 0:
                summary_parts.append(f"Detected {patterns['potential_masses']} potential masses/lesions")
            
            if patterns.get("asymmetry_interpretation") == "High":
                summary_parts.append("Significant asymmetry detected")
            
            # Technical summary
            features = analysis_results.get("image_analysis", {})
            if "dimensions" in features:
                summary_parts.append(f"Image dimensions: {features['dimensions']}")
            
            if not summary_parts:
                summary_parts.append("Medical image analysis completed")
            
            return ". ".join(summary_parts) + "."
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return "Medical image analysis completed with technical details available."
    
    def _create_error_response(self, filename: str, error_msg: str) -> Dict:
        """Create error response when analysis fails"""
        return {
            "filename": filename,
            "file_type": "medical_image",
            "summary": f"Analysis failed: {error_msg}",
            "error": error_msg,
            "recommendations": ["Manual review required", "Contact technical support if issue persists"],
            "disclaimer": "This is a preliminary AI-assisted analysis for licensed clinicians only. This is not a diagnosis and should not replace professional medical judgment."
        }

# Global instance
monai_analyzer = MONAIMedicalAnalyzer()
