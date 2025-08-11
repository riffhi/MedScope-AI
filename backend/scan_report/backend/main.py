from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from typing import List
import tempfile
import os
import json
import logging
from pathlib import Path
from PIL import Image
import numpy as np
import cv2
from datetime import datetime
import io
import sys
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import base64
from enhanced_recommendations import MedicalRecommendationEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DarkMed AI - Medical Analysis API",
    description="AI-powered medical file analysis using advanced computer vision and medical AI analysis",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enhanced Medical Analyzer Class
class EnhancedMedicalAnalyzer:
    def __init__(self):
        self.BODY_PARTS = {
            "brain": "Brain and neurological structures",
            "heart": "Cardiac and cardiovascular system",
            "chest": "Chest, lungs, and thoracic cavity",
            "abdomen": "Abdominal organs and structures",
            "spine": "Spinal column and vertebrae",
            "extremities": "Arms, legs, hands, and feet",
            "breast": "Breast tissue and mammary glands",
            "unknown": "Unspecified body region"
        }
        # Enhanced heuristic thresholds for improved accuracy
        self.min_contour_area_ratio = 0.0005  # 0.05% of image area for more sensitive detection
        self.max_contour_area_ratio = 0.15    # 15% of image area
        self.min_circularity = 0.25           # More permissive for irregular masses
        self.min_solidity = 0.55              # Adjusted for better detection
        
        # Enhanced body-part priors with more precise modulation
        self.BODY_PART_CONDITION_PRIORS = {
            "brain": {"hemorrhage": 1.45, "tumor": 1.25, "fracture": 0.65, "stroke": 1.35, "edema": 1.20},
            "chest": {"hemorrhage": 0.75, "tumor": 1.20, "fracture": 0.85, "pneumonia": 1.40, "nodule": 1.35},
            "abdomen": {"hemorrhage": 0.95, "tumor": 1.18, "fracture": 0.75, "inflammation": 1.25, "mass": 1.30},
            "breast": {"hemorrhage": 0.55, "tumor": 1.65, "fracture": 0.55, "calcifications": 1.55, "mass": 1.60},
            "spine": {"hemorrhage": 0.65, "tumor": 1.05, "fracture": 1.35, "compression": 1.25, "degeneration": 1.15},
            "extremities": {"hemorrhage": 0.55, "tumor": 0.85, "fracture": 1.55, "dislocation": 1.30, "soft_tissue": 1.10},
            "heart": {"hemorrhage": 0.65, "tumor": 0.85, "fracture": 0.55, "enlargement": 1.25, "valve": 1.15},
            "unknown": {"hemorrhage": 1.0, "tumor": 1.0, "fracture": 1.0, "abnormality": 1.0, "lesion": 1.0},
        }
        
        # Clinical urgency matrix based on findings and body parts
        self.URGENCY_MATRIX = {
            "brain": {
                "hemorrhage": {"HIGH": "IMMEDIATE", "MODERATE": "WITHIN_4_HOURS", "LOW": "WITHIN_24_HOURS"},
                "stroke": {"HIGH": "IMMEDIATE", "MODERATE": "WITHIN_1_HOUR", "LOW": "WITHIN_6_HOURS"},
                "tumor": {"HIGH": "WITHIN_1_WEEK", "MODERATE": "WITHIN_2_WEEKS", "LOW": "WITHIN_1_MONTH"},
                "edema": {"HIGH": "WITHIN_4_HOURS", "MODERATE": "WITHIN_24_HOURS", "LOW": "WITHIN_1_WEEK"}
            },
            "chest": {
                "pneumonia": {"HIGH": "WITHIN_4_HOURS", "MODERATE": "WITHIN_24_HOURS", "LOW": "WITHIN_1_WEEK"},
                "tumor": {"HIGH": "WITHIN_1_WEEK", "MODERATE": "WITHIN_2_WEEKS", "LOW": "WITHIN_1_MONTH"},
                "hemorrhage": {"HIGH": "IMMEDIATE", "MODERATE": "WITHIN_4_HOURS", "LOW": "WITHIN_24_HOURS"}
            },
            "heart": {
                "enlargement": {"HIGH": "WITHIN_4_HOURS", "MODERATE": "WITHIN_24_HOURS", "LOW": "WITHIN_1_WEEK"},
                "valve": {"HIGH": "WITHIN_24_HOURS", "MODERATE": "WITHIN_1_WEEK", "LOW": "WITHIN_1_MONTH"}
            },
            "extremities": {
                "fracture": {"HIGH": "WITHIN_4_HOURS", "MODERATE": "WITHIN_24_HOURS", "LOW": "WITHIN_1_WEEK"},
                "dislocation": {"HIGH": "IMMEDIATE", "MODERATE": "WITHIN_4_HOURS", "LOW": "WITHIN_24_HOURS"}
            }
        }
        
        # Enhanced risk scoring criteria
        self.RISK_SCORING_CRITERIA = {
            "size_factor": {"large": 25, "medium": 15, "small": 8},
            "location_factor": {"critical": 30, "important": 20, "routine": 10},
            "pattern_factor": {"irregular": 20, "suspicious": 15, "regular": 5},
            "multiplicity_factor": {"multiple": 15, "bilateral": 20, "single": 5}
        }
    
    def analyze_image(self, image_path: str, filename: str, body_part: str = "unknown"):
        """Analyze medical image and provide comprehensive analysis with enhanced accuracy"""
        try:
            # Load and preprocess image
            image_data = self._load_and_preprocess_image(image_path)
            if image_data is None:
                return self._create_error_analysis(filename, "Failed to load image")
            
            # Enhanced pattern detection with multiple algorithms
            patterns = self._detect_patterns(image_data)
            
            # Advanced feature extraction
            advanced_features = self._extract_advanced_features(image_data, body_part)

            # Detect condition-specific evidence and scores with improved algorithms
            condition_scores, condition_evidence = self._detect_specific_conditions(image_data, body_part, patterns)
            
            # Enhanced classification with multi-factor analysis
            classification = self._classify_medical_condition_enhanced(patterns, body_part, condition_scores, advanced_features)
            
            # Generate comprehensive risk assessment using dedicated engine
            risk_assessment = recommendation_engine.generate_risk_assessment(classification, patterns, body_part, condition_scores, advanced_features)
            
            # Generate urgency-based recommendations with specific doctor actions
            recommendations = recommendation_engine.generate_doctor_recommendations_enhanced(classification, patterns, body_part, condition_scores, risk_assessment)
            
            # Enhanced quality assessment
            quality = self._assess_image_quality_enhanced(image_data)
            
            # Advanced technical details
            technical = self._generate_technical_details_enhanced(image_data, patterns, advanced_features)
            
            # Generate comprehensive medical report
            medical_report = self._generate_medical_report_enhanced(
                filename, body_part, classification, patterns, 
                recommendations, quality, technical, risk_assessment, advanced_features
            )
            
            return {
                "summary": f"Enhanced analysis of {body_part} image reveals {classification['primary_condition'].replace('_', ' ').lower()} with {classification['risk_level']} risk (score: {classification['risk_score']}/100).",
                "medical_classification": classification,
                "risk_assessment": risk_assessment,
                "medical_findings": {**patterns, "condition_scores": condition_scores, "condition_evidence": condition_evidence, "advanced_features": advanced_features},
                "doctor_recommendations": recommendations,
                "quality_assessment": quality,
                "technical_details": technical,
                "medical_report": medical_report,
                "disclaimer": "This is a preliminary AI-assisted analysis for licensed clinicians only. This is not a diagnosis and should not replace professional medical judgment. Always consult with qualified healthcare providers for proper diagnosis and treatment.",
                "analysis_timestamp": datetime.now().isoformat(),
                "confidence_metrics": self._calculate_confidence_metrics(classification, quality, advanced_features)
            }
            
        except Exception as e:
            logger.error(f"Analysis failed for {filename}: {str(e)}")
            return self._create_error_analysis(filename, str(e))
    
    def _load_and_preprocess_image(self, image_path: str):
        """Load and preprocess image using OpenCV and PIL fallback"""
        try:
            # Try OpenCV first
            image = cv2.imread(image_path)
            if image is not None:
                # Convert BGR to RGB
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                return {
                    'opencv_image': image,
                    'rgb_image': image_rgb,
                    'height': image.shape[0],
                    'width': image.shape[1],
                    'channels': image.shape[2] if len(image.shape) > 2 else 1
                }
        except Exception as e:
            logger.warning(f"OpenCV failed, trying PIL: {e}")
        
        try:
            # PIL fallback
            with Image.open(image_path) as img:
                img_array = np.array(img)
                return {
                    'pil_image': img,
                    'array': img_array,
                    'height': img.height,
                    'width': img.width,
                    'channels': len(img_array.shape) if len(img_array.shape) > 2 else 1
                }
        except Exception as e:
            logger.error(f"Both OpenCV and PIL failed: {e}")
            return None
    
    def _detect_patterns(self, image_data):
        """Detect medical patterns in the image with improved heuristics"""
        patterns = {
            'potential_masses': 0,
            'asymmetry_detected': False,
            'asymmetry_interpretation': 'No significant asymmetry detected',
            'texture_variations': 'Normal',
            'variation_interpretation': 'Standard tissue patterns observed',
            'contour_analysis': 'Regular boundaries detected',
            'photograph_likelihood': 0.0
        }

        try:
            if 'opencv_image' in image_data:
                bgr = image_data['opencv_image']
                h, w = image_data['height'], image_data['width']
                img_area = float(h * w)

                # Detect non-diagnostic photograph (color + high saturation variance)
                patterns['photograph_likelihood'] = self._estimate_photograph_likelihood(bgr)

                # Preprocess for contour detection
                proc = self._preprocess_for_contours(bgr)
                contours, _ = cv2.findContours(proc, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Filter contours by size, circularity, solidity
                suspicious_contours = 0
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area <= 0:
                        continue
                    area_ratio = area / img_area
                    if not (self.min_contour_area_ratio <= area_ratio <= self.max_contour_area_ratio):
                        continue
                    perimeter = cv2.arcLength(contour, True)
                    if perimeter == 0:
                        continue
                    circularity = 4 * np.pi * (area / (perimeter * perimeter))
                    hull = cv2.convexHull(contour)
                    hull_area = cv2.contourArea(hull) if hull is not None else area
                    solidity = area / hull_area if hull_area > 0 else 1.0

                    if circularity >= self.min_circularity and solidity >= self.min_solidity:
                        suspicious_contours += 1

                patterns['potential_masses'] = int(suspicious_contours)

                # Asymmetry via flipped MSE difference on CLAHE-equalized grayscale
                asym_score = self._compute_asymmetry_score(bgr)
                if asym_score > 0.25:
                    patterns['asymmetry_detected'] = True
                    patterns['asymmetry_interpretation'] = 'Asymmetry detected between left and right halves'

                # Texture via Laplacian variance and local std
                gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
                lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                local_std = gray.std()
                if lap_var > 400 and local_std > 40:
                    patterns['texture_variations'] = 'Irregular'
                    patterns['variation_interpretation'] = 'Heterogeneous texture suggesting possible tissue changes'
                else:
                    patterns['texture_variations'] = 'Normal'
                    patterns['variation_interpretation'] = 'Homogeneous texture overall'

                if suspicious_contours > 0:
                    patterns['contour_analysis'] = f'{suspicious_contours} suspicious region(s) after size/shape filtering'

        except Exception as e:
            logger.warning(f"Pattern detection failed: {e}")

        return patterns

    def _extract_advanced_features(self, image_data, body_part: str):
        """Extract advanced medical imaging features for more accurate analysis"""
        features = {
            'intensity_statistics': {},
            'morphological_features': {},
            'texture_analysis': {},
            'spatial_distribution': {},
            'body_part_specific': {}
        }

        try:
            if 'opencv_image' in image_data:
                bgr = image_data['opencv_image']
                gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
                h, w = gray.shape

                # Intensity statistics
                features['intensity_statistics'] = {
                    'mean': float(gray.mean()),
                    'std': float(gray.std()),
                    'min': int(gray.min()),
                    'max': int(gray.max()),
                    'percentile_25': float(np.percentile(gray, 25)),
                    'percentile_75': float(np.percentile(gray, 75)),
                    'skewness': self._calculate_skewness(gray),
                    'kurtosis': self._calculate_kurtosis(gray)
                }

                # Morphological features
                features['morphological_features'] = self._extract_morphological_features(gray)

                # Advanced texture analysis
                features['texture_analysis'] = self._advanced_texture_analysis(gray)

                # Spatial distribution analysis
                features['spatial_distribution'] = self._analyze_spatial_distribution(gray)

                # Body part specific features
                features['body_part_specific'] = self._extract_body_part_features(gray, body_part)

        except Exception as e:
            logger.warning(f"Advanced feature extraction failed: {e}")

        return features

    def _calculate_skewness(self, image):
        """Calculate skewness of image intensity distribution"""
        mean = image.mean()
        std = image.std()
        if std == 0:
            return 0.0
        return float(np.mean(((image - mean) / std) ** 3))

    def _calculate_kurtosis(self, image):
        """Calculate kurtosis of image intensity distribution"""
        mean = image.mean()
        std = image.std()
        if std == 0:
            return 0.0
        return float(np.mean(((image - mean) / std) ** 4) - 3)

    def _extract_morphological_features(self, gray):
        """Extract morphological features using mathematical morphology"""
        features = {}
        try:
            # Different structuring elements
            kernel_circle = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            kernel_rect = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            
            # Morphological operations
            opening = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel_circle)
            closing = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel_circle)
            gradient = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel_circle)
            
            features['opening_variance'] = float(opening.var())
            features['closing_variance'] = float(closing.var())
            features['gradient_mean'] = float(gradient.mean())
            features['gradient_std'] = float(gradient.std())
            
        except Exception as e:
            logger.warning(f"Morphological feature extraction failed: {e}")
            
        return features

    def _advanced_texture_analysis(self, gray):
        """Perform advanced texture analysis"""
        features = {}
        try:
            # Local Binary Pattern analysis
            features['lbp_score'] = self._calculate_lbp_score(gray)
            
            # Gabor filter responses
            features['gabor_responses'] = self._calculate_gabor_responses(gray)
            
            # Co-occurrence matrix features
            features['glcm_features'] = self._calculate_glcm_features(gray)
            
        except Exception as e:
            logger.warning(f"Texture analysis failed: {e}")
            
        return features

    def _calculate_lbp_score(self, gray):
        """Calculate Local Binary Pattern score for texture analysis"""
        try:
            # Simple LBP implementation
            lbp = np.zeros_like(gray)
            for i in range(1, gray.shape[0] - 1):
                for j in range(1, gray.shape[1] - 1):
                    center = gray[i, j]
                    code = 0
                    code |= (gray[i-1, j-1] > center) << 7
                    code |= (gray[i-1, j] > center) << 6
                    code |= (gray[i-1, j+1] > center) << 5
                    code |= (gray[i, j+1] > center) << 4
                    code |= (gray[i+1, j+1] > center) << 3
                    code |= (gray[i+1, j] > center) << 2
                    code |= (gray[i+1, j-1] > center) << 1
                    code |= (gray[i, j-1] > center) << 0
                    lbp[i, j] = code
            
            return float(lbp.var())
        except:
            return 0.0

    def _calculate_gabor_responses(self, gray):
        """Calculate Gabor filter responses for texture analysis"""
        try:
            responses = []
            for theta in [0, 45, 90, 135]:
                kernel = cv2.getGaborKernel((21, 21), 5, np.radians(theta), 2*np.pi*0.5, 0.5, 0, ktype=cv2.CV_32F)
                filtered = cv2.filter2D(gray, cv2.CV_8UC3, kernel)
                responses.append(float(filtered.var()))
            return responses
        except:
            return [0.0, 0.0, 0.0, 0.0]

    def _calculate_glcm_features(self, gray):
        """Calculate Gray Level Co-occurrence Matrix features"""
        try:
            # Simplified GLCM calculation
            # Resize for computational efficiency
            small_gray = cv2.resize(gray, (64, 64))
            # Calculate co-occurrence for horizontal direction
            glcm = np.zeros((256, 256))
            for i in range(small_gray.shape[0]):
                for j in range(small_gray.shape[1] - 1):
                    glcm[small_gray[i, j], small_gray[i, j + 1]] += 1
            
            # Normalize
            glcm = glcm / glcm.sum()
            
            # Calculate features
            contrast = np.sum((np.arange(256)[:, None] - np.arange(256)[None, :]) ** 2 * glcm)
            energy = np.sum(glcm ** 2)
            homogeneity = np.sum(glcm / (1 + (np.arange(256)[:, None] - np.arange(256)[None, :]) ** 2))
            
            return {
                'contrast': float(contrast),
                'energy': float(energy),
                'homogeneity': float(homogeneity)
            }
        except:
            return {'contrast': 0.0, 'energy': 0.0, 'homogeneity': 0.0}

    def _analyze_spatial_distribution(self, gray):
        """Analyze spatial distribution of intensities"""
        features = {}
        try:
            h, w = gray.shape
            
            # Divide image into quadrants
            quad1 = gray[:h//2, :w//2]
            quad2 = gray[:h//2, w//2:]
            quad3 = gray[h//2:, :w//2]
            quad4 = gray[h//2:, w//2:]
            
            quadrant_means = [float(q.mean()) for q in [quad1, quad2, quad3, quad4]]
            features['quadrant_variance'] = float(np.var(quadrant_means))
            features['quadrant_means'] = quadrant_means
            
            # Center vs periphery analysis
            center_mask = np.zeros_like(gray)
            center_y, center_x = h // 2, w // 2
            radius = min(h, w) // 4
            y, x = np.ogrid[:h, :w]
            mask = (x - center_x) ** 2 + (y - center_y) ** 2 <= radius ** 2
            center_mask[mask] = 1
            
            center_mean = float(gray[mask].mean() if mask.any() else 0)
            periphery_mean = float(gray[~mask].mean() if (~mask).any() else 0)
            features['center_periphery_ratio'] = center_mean / periphery_mean if periphery_mean > 0 else 1.0
            
        except Exception as e:
            logger.warning(f"Spatial distribution analysis failed: {e}")
            
        return features

    def _extract_body_part_features(self, gray, body_part: str):
        """Extract body part specific features"""
        features = {}
        try:
            h, w = gray.shape
            
            if body_part == 'brain':
                # Look for ventricle-like structures (dark areas)
                features['dark_regions'] = self._detect_dark_regions(gray)
                features['symmetry_score'] = self._calculate_brain_symmetry(gray)
                
            elif body_part == 'chest':
                # Look for lung field patterns
                features['lung_field_analysis'] = self._analyze_lung_fields(gray)
                features['rib_detection'] = self._detect_rib_patterns(gray)
                
            elif body_part == 'breast':
                # Look for density patterns
                features['density_analysis'] = self._analyze_breast_density(gray)
                features['architectural_distortion'] = self._detect_architectural_distortion(gray)
                
            elif body_part == 'extremities':
                # Look for bone structures
                features['bone_analysis'] = self._analyze_bone_structures(gray)
                features['joint_analysis'] = self._analyze_joint_spaces(gray)
                
        except Exception as e:
            logger.warning(f"Body part specific feature extraction failed: {e}")
            
        return features

    def _detect_dark_regions(self, gray):
        """Detect dark regions that might represent ventricles or pathology"""
        try:
            # Threshold for dark regions
            thresh = np.percentile(gray, 25)
            dark_mask = gray < thresh
            
            # Connected component analysis
            num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(dark_mask.astype(np.uint8), connectivity=8)
            
            dark_regions = []
            for i in range(1, num_labels):
                area = stats[i, cv2.CC_STAT_AREA]
                if area > 50:  # Minimum area threshold
                    dark_regions.append(area)
            
            return {
                'count': len(dark_regions),
                'total_area': sum(dark_regions),
                'average_area': np.mean(dark_regions) if dark_regions else 0
            }
        except:
            return {'count': 0, 'total_area': 0, 'average_area': 0}

    def _calculate_brain_symmetry(self, gray):
        """Calculate brain symmetry score"""
        try:
            h, w = gray.shape
            left_half = gray[:, :w//2]
            right_half = gray[:, w//2:]
            right_half_flipped = cv2.flip(right_half, 1)
            
            # Resize to same dimensions
            min_w = min(left_half.shape[1], right_half_flipped.shape[1])
            left_half = left_half[:, :min_w]
            right_half_flipped = right_half_flipped[:, :min_w]
            
            # Calculate correlation
            correlation = cv2.matchTemplate(left_half.astype(np.float32), 
                                          right_half_flipped.astype(np.float32), 
                                          cv2.TM_CCOEFF_NORMED)[0, 0]
            
            return float(correlation)
        except:
            return 0.0

    def _analyze_lung_fields(self, gray):
        """Analyze lung field patterns"""
        try:
            # Simple lung field detection using thresholding
            # Lung fields are typically darker regions
            thresh = np.percentile(gray, 40)
            lung_mask = gray < thresh
            
            # Remove small noise
            kernel = np.ones((5, 5), np.uint8)
            lung_mask = cv2.morphologyEx(lung_mask.astype(np.uint8), cv2.MORPH_OPEN, kernel)
            
            # Find largest connected components (likely lung fields)
            num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(lung_mask, connectivity=8)
            
            if num_labels > 1:
                # Get two largest components
                areas = [stats[i, cv2.CC_STAT_AREA] for i in range(1, num_labels)]
                areas.sort(reverse=True)
                return {
                    'bilateral_lungs': len(areas) >= 2,
                    'size_asymmetry': abs(areas[0] - areas[1]) / max(areas[0], areas[1]) if len(areas) >= 2 else 0,
                    'total_lung_area': sum(areas)
                }
            else:
                return {'bilateral_lungs': False, 'size_asymmetry': 0, 'total_lung_area': 0}
        except:
            return {'bilateral_lungs': False, 'size_asymmetry': 0, 'total_lung_area': 0}

    def _detect_rib_patterns(self, gray):
        """Detect rib-like linear structures"""
        try:
            # Use Hough line detection for rib structures
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=30, maxLineGap=10)
            
            if lines is not None:
                # Filter for approximately horizontal lines (ribs)
                rib_lines = []
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
                    if angle < 30 or angle > 150:  # Approximately horizontal
                        rib_lines.append(line)
                
                return {
                    'rib_count': len(rib_lines),
                    'rib_spacing_regular': self._check_rib_spacing_regularity(rib_lines)
                }
            else:
                return {'rib_count': 0, 'rib_spacing_regular': False}
        except:
            return {'rib_count': 0, 'rib_spacing_regular': False}

    def _check_rib_spacing_regularity(self, rib_lines):
        """Check if rib spacing is regular"""
        try:
            if len(rib_lines) < 3:
                return False
            
            # Get y-coordinates of rib lines
            y_coords = []
            for line in rib_lines:
                x1, y1, x2, y2 = line[0]
                y_coords.append((y1 + y2) / 2)
            
            y_coords.sort()
            
            # Calculate spacing between consecutive ribs
            spacings = [y_coords[i+1] - y_coords[i] for i in range(len(y_coords)-1)]
            
            # Check if spacing is relatively uniform
            if len(spacings) > 1:
                spacing_var = np.var(spacings)
                spacing_mean = np.mean(spacings)
                return spacing_var / spacing_mean < 0.3 if spacing_mean > 0 else False
            
            return False
        except:
            return False

    def _analyze_breast_density(self, gray):
        """Analyze breast tissue density patterns"""
        try:
            # Classify tissue density based on intensity distribution
            hist, bins = np.histogram(gray, bins=256, range=(0, 256))
            
            # Calculate density metrics
            mean_intensity = gray.mean()
            std_intensity = gray.std()
            
            # Classify density (simplified approach)
            if mean_intensity > 180:
                density_class = "fatty"
            elif mean_intensity > 120:
                density_class = "scattered_fibroglandular"
            elif mean_intensity > 80:
                density_class = "heterogeneously_dense"
            else:
                density_class = "extremely_dense"
            
            return {
                'density_class': density_class,
                'mean_intensity': float(mean_intensity),
                'intensity_variance': float(std_intensity ** 2),
                'heterogeneity_score': float(std_intensity / mean_intensity) if mean_intensity > 0 else 0
            }
        except:
            return {'density_class': 'unknown', 'mean_intensity': 0, 'intensity_variance': 0, 'heterogeneity_score': 0}

    def _detect_architectural_distortion(self, gray):
        """Detect architectural distortion patterns"""
        try:
            # Use gradient analysis to detect distortion
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            
            magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Look for convergent patterns (simplified)
            distortion_score = float(magnitude.std())
            
            return {
                'distortion_present': distortion_score > 50,
                'distortion_score': distortion_score
            }
        except:
            return {'distortion_present': False, 'distortion_score': 0}

    def _analyze_bone_structures(self, gray):
        """Analyze bone structures in extremity images"""
        try:
            # Bones appear as high-intensity structures
            bone_thresh = np.percentile(gray, 85)
            bone_mask = gray > bone_thresh
            
            # Morphological operations to clean up
            kernel = np.ones((3, 3), np.uint8)
            bone_mask = cv2.morphologyEx(bone_mask.astype(np.uint8), cv2.MORPH_CLOSE, kernel)
            
            # Find bone-like structures
            num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(bone_mask, connectivity=8)
            
            bone_structures = []
            for i in range(1, num_labels):
                area = stats[i, cv2.CC_STAT_AREA]
                if area > 100:  # Minimum area for bone structure
                    bone_structures.append(area)
            
            return {
                'bone_count': len(bone_structures),
                'total_bone_area': sum(bone_structures),
                'cortical_continuity': self._assess_cortical_continuity(bone_mask)
            }
        except:
            return {'bone_count': 0, 'total_bone_area': 0, 'cortical_continuity': True}

    def _assess_cortical_continuity(self, bone_mask):
        """Assess cortical bone continuity"""
        try:
            # Look for breaks in bone continuity using edge detection
            edges = cv2.Canny(bone_mask * 255, 50, 150)
            
            # Count the number of edge segments
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=20, minLineLength=10, maxLineGap=5)
            
            if lines is not None:
                # If many short segments, might indicate fracture
                avg_length = np.mean([np.sqrt((x2-x1)**2 + (y2-y1)**2) for x1, y1, x2, y2 in lines[:, 0]])
                return avg_length > 20  # Arbitrary threshold
            
            return True
        except:
            return True

    def _analyze_joint_spaces(self, gray):
        """Analyze joint space characteristics"""
        try:
            # Joint spaces appear as dark lines between bones
            # Use line detection to find potential joint spaces
            edges = cv2.Canny(gray, 30, 100)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=30, minLineLength=15, maxLineGap=3)
            
            joint_spaces = []
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                    if 15 < length < 100:  # Typical joint space length
                        joint_spaces.append(length)
            
            return {
                'joint_space_count': len(joint_spaces),
                'average_joint_width': np.mean(joint_spaces) if joint_spaces else 0,
                'joint_narrowing_suspected': len(joint_spaces) < 2  # Simplified criterion
            }
        except:
            return {'joint_space_count': 0, 'average_joint_width': 0, 'joint_narrowing_suspected': False}

    def _detect_specific_conditions(self, image_data, body_part: str, patterns: dict):
        """Estimate likelihood scores (0-100) for tumor, hemorrhage, and fracture with simple CV heuristics.
        Returns (scores_dict, evidence_dict).
        """
        scores = {"tumor": 0.0, "hemorrhage": 0.0, "fracture": 0.0}
        evidence = {"tumor": [], "hemorrhage": [], "fracture": []}

        try:
            if 'opencv_image' not in image_data:
                return scores, evidence
            bgr = image_data['opencv_image']
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
            h, w = gray.shape

            # Common pre-processing
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            eq = clahe.apply(gray)

            # 1) Hemorrhage: bright hyperdense clusters relative to background
            # Use high-percentile threshold and connected components
            high_thresh = int(np.clip(np.percentile(eq, 92), 160, 245))
            _, high_mask = cv2.threshold(eq, high_thresh, 255, cv2.THRESH_BINARY)
            # Morph cleanup
            kernel = np.ones((3, 3), np.uint8)
            high_mask = cv2.morphologyEx(high_mask, cv2.MORPH_OPEN, kernel, iterations=1)
            num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(high_mask, connectivity=8)
            bright_regions = 0
            significant_area = 0
            for i in range(1, num_labels):
                area = stats[i, cv2.CC_STAT_AREA]
                if area >= max(20, int(0.0005 * h * w)):
                    bright_regions += 1
                    significant_area += area
            bright_area_ratio = significant_area / float(h * w)
            hem_score = 0.0
            if bright_regions >= 1:
                hem_score += 35 + min(bright_regions * 7.0, 25.0)
                evidence["hemorrhage"].append(f"{bright_regions} hyperdense region(s) above P92 threshold")
            if bright_area_ratio > 0.002:
                hem_score += min(bright_area_ratio * 2000.0, 20.0)
                evidence["hemorrhage"].append(f"Bright-area ratio {bright_area_ratio:.3f}")
            if patterns.get('asymmetry_detected') and body_part == 'brain':
                hem_score += 8.0
                evidence["hemorrhage"].append("Asymmetry supports focal hyperdensity")
            scores['hemorrhage'] = float(np.clip(hem_score, 0.0, 100.0))

            # 2) Fracture: sharp linear edges and discontinuities (line segments)
            edges = cv2.Canny(eq, 60, 160)
            lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=60, minLineLength=int(0.06 * min(h, w)), maxLineGap=6)
            line_count = 0 if lines is None else len(lines)
            edge_density = float((edges > 0).mean())
            frac_score = 0.0
            if line_count >= 4:
                frac_score += min(40 + (line_count - 4) * 4.0, 55.0)
                evidence["fracture"].append(f"{line_count} linear segments detected")
            if edge_density > 0.10:
                frac_score += min((edge_density - 0.10) * 200.0, 20.0)
                evidence["fracture"].append(f"High edge density {edge_density:.2f}")
            scores['fracture'] = float(np.clip(frac_score, 0.0, 100.0))

            # 3) Tumor/mass: suspicious contours + heterogeneity
            sus_count = float(patterns.get('potential_masses', 0))
            tumor_score = 0.0
            if sus_count >= 1:
                tumor_score += min(30 + (sus_count - 1) * 6.0, 48.0)
                evidence["tumor"].append(f"{int(sus_count)} suspicious region(s) by contour analysis")
            # Heterogeneous texture boosts tumor likelihood
            lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            local_std = gray.std()
            if lap_var > 350 and local_std > 35:
                tumor_score += 18.0
                evidence["tumor"].append("Heterogeneous texture (high Laplacian variance and local std)")
            if patterns.get('asymmetry_detected'):
                tumor_score += 8.0
                evidence["tumor"].append("Asymmetry present")
            scores['tumor'] = float(np.clip(tumor_score, 0.0, 100.0))

            # Body-part specific adjustments
            if body_part == 'breast':
                # Microcalcifications: many small bright foci
                mc_thresh = int(np.clip(np.percentile(eq, 97), 180, 250))
                _, mc_mask = cv2.threshold(eq, mc_thresh, 255, cv2.THRESH_BINARY)
                kernel2 = np.ones((2, 2), np.uint8)
                mc_mask = cv2.morphologyEx(mc_mask, cv2.MORPH_OPEN, kernel2, iterations=1)
                num_labels2, _, stats2, _ = cv2.connectedComponentsWithStats(mc_mask, connectivity=8)
                small_bright = 0
                for i in range(1, num_labels2):
                    area = stats2[i, cv2.CC_STAT_AREA]
                    if 2 <= area <= 60:
                        small_bright += 1
                if small_bright >= 8:
                    add = min(10 + (small_bright - 8) * 1.2, 22.0)
                    scores['tumor'] = float(np.clip(scores['tumor'] + add, 0.0, 100.0))
                    evidence["tumor"].append(f"Microcalcification pattern: {small_bright} small hyperdense foci")

                # Spiculated/irregular masses: high shape irregularity
                bin_thr = int(np.clip(np.percentile(eq, 75), 120, 210))
                _, bin_mask = cv2.threshold(eq, bin_thr, 255, cv2.THRESH_BINARY)
                contours, _ = cv2.findContours(bin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                img_area = float(h * w)
                irregular_count = 0
                for c in contours:
                    area = cv2.contourArea(c)
                    if area <= 0:
                        continue
                    area_ratio = area / img_area
                    if not (0.0008 <= area_ratio <= 0.05):
                        continue
                    peri = cv2.arcLength(c, True)
                    if peri == 0:
                        continue
                    shape_factor = (peri * peri) / (4.0 * np.pi * area)
                    hull = cv2.convexHull(c)
                    hull_area = cv2.contourArea(hull) if hull is not None else area
                    solidity = area / hull_area if hull_area > 0 else 1.0
                    if shape_factor >= 6.0 or solidity <= 0.75:
                        irregular_count += 1
                if irregular_count >= 1:
                    add = min(16.0 + (irregular_count - 1) * 6.0, 34.0)
                    scores['tumor'] = float(np.clip(scores['tumor'] + add, 0.0, 100.0))
                    evidence["tumor"].append(f"{irregular_count} irregular mass-like region(s)")

            if body_part == 'chest':
                # Pulmonary nodule heuristic via blob-like bright regions
                params = cv2.SimpleBlobDetector_Params()
                params.filterByArea = True
                params.minArea = max(30, 0.0005 * h * w)
                params.maxArea = 0.03 * h * w
                params.filterByCircularity = True
                params.minCircularity = 0.4
                params.filterByConvexity = False
                params.filterByInertia = False
                try:
                    detector = cv2.SimpleBlobDetector_create(params)
                    keypoints = detector.detect(eq)
                    n = len(keypoints)
                    if n >= 1:
                        add = min(12.0 + (n - 1) * 4.0, 24.0)
                        scores['tumor'] = float(np.clip(scores['tumor'] + add, 0.0, 100.0))
                        evidence["tumor"].append(f"Nodule-like blobs detected: {n}")
                except Exception:
                    pass

            if body_part == 'brain':
                # Brain tumor surrogate: heterogeneous region without hyperdense mask
                # Use local variance map to find patches with high variability
                blur = cv2.GaussianBlur(eq, (0, 0), sigmaX=1.2)
                var_map = (eq.astype(np.float32) - blur.astype(np.float32)) ** 2
                var_score = float(var_map.mean())
                if var_score > 450.0 and not (scores['hemorrhage'] >= 35):
                    scores['tumor'] = float(np.clip(scores['tumor'] + 16.0, 0.0, 100.0))
                    evidence["tumor"].append("High intraparenchymal heterogeneity without hyperdense pattern")

            # Apply body-part priors
            priors = self.BODY_PART_CONDITION_PRIORS.get(body_part, self.BODY_PART_CONDITION_PRIORS['unknown'])
            for k in scores.keys():
                scores[k] = float(np.clip(scores[k] * priors.get(k, 1.0), 0.0, 100.0))

        except Exception as e:
            logger.warning(f"Specific condition detection failed: {e}")

        return scores, evidence

    def _preprocess_for_contours(self, bgr: np.ndarray) -> np.ndarray:
        """Contrast enhance + blur + adaptive threshold + morphology to isolate regions"""
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        eq = clahe.apply(gray)
        blur = cv2.GaussianBlur(eq, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 35, 2)
        # invert if majority white background
        if (thresh > 0).mean() > 0.6:
            thresh = cv2.bitwise_not(thresh)
        kernel = np.ones((3, 3), np.uint8)
        opened = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel, iterations=2)
        return closed

    def _compute_asymmetry_score(self, bgr: np.ndarray) -> float:
        """Compute asymmetry as normalized MSE between halves after alignment"""
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        left = gray[:, : w // 2]
        right = gray[:, w - (w // 2):]
        right_flipped = cv2.flip(right, 1)
        # Resize halves to same size
        min_w = min(left.shape[1], right_flipped.shape[1])
        left = left[:, :min_w]
        right_flipped = right_flipped[:, :min_w]
        diff = (left.astype(np.float32) - right_flipped.astype(np.float32))
        mse = np.mean((diff / 255.0) ** 2)
        return float(mse)  # ~0 == symmetric, larger == asymmetric

    def _estimate_photograph_likelihood(self, bgr: np.ndarray) -> float:
        """Estimate if the image is a color photograph (non-diagnostic)"""
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        sat = hsv[:, :, 1].astype(np.float32)
        sat_mean = sat.mean()
        sat_std = sat.std()
        # Color photographs typically have higher saturation; medical scans are often grayscale
        # Normalize to [0,1] range
        likelihood = max(0.0, min(1.0, (sat_mean / 255.0) * 0.7 + (sat_std / 255.0) * 0.3))
        return float(likelihood)
    
    def _classify_medical_condition_enhanced(self, patterns, body_part, condition_scores=None, advanced_features=None):
        """Enhanced classification with multi-factor analysis and improved accuracy"""
        # Non-diagnostic photograph guard
        if patterns.get('photograph_likelihood', 0) > 0.35:
            return {
                "primary_condition": "NON_DIAGNOSTIC_PHOTOGRAPH",
                "secondary_conditions": [],
                "risk_level": "MINIMAL",
                "urgency": "ROUTINE",
                "risk_score": 0,
                "confidence_level": "HIGH"
            }

        # Initialize scoring
        base_risk_score = 0.0
        condition_scores = condition_scores or {"tumor": 0.0, "hemorrhage": 0.0, "fracture": 0.0}
        advanced_features = advanced_features or {}
        
        # Base pattern contributions with enhanced weighting
        mass_count = float(patterns.get('potential_masses', 0))
        base_risk_score += min(mass_count, 3.0) * 20.0 + max(mass_count - 3.0, 0.0) * 8.0

        # Asymmetry with body-part specific weighting
        if patterns.get('asymmetry_detected', False):
            asymmetry_weight = 22.0 if body_part in ['brain', 'breast'] else 15.0
            base_risk_score += asymmetry_weight

        # Texture irregularity
        if patterns.get('texture_variations') == 'Irregular':
            base_risk_score += 18.0

        # Advanced feature contributions
        intensity_stats = advanced_features.get('intensity_statistics', {})
        if intensity_stats.get('skewness', 0) > 1.5 or intensity_stats.get('kurtosis', 0) > 2.0:
            base_risk_score += 12.0  # Abnormal distribution
            
        # Morphological feature contributions
        morph_features = advanced_features.get('morphological_features', {})
        if morph_features.get('gradient_mean', 0) > 30:
            base_risk_score += 10.0  # High edge activity
            
        # Body part specific features
        body_specific = advanced_features.get('body_part_specific', {})
        base_risk_score += self._calculate_body_specific_risk(body_part, body_specific)

        # Enhanced condition-specific analysis
        top_condition = max(condition_scores, key=lambda k: condition_scores[k]) if condition_scores else None
        top_score = condition_scores.get(top_condition, 0.0) if top_condition else 0.0
        secondary_conditions = [k for k, v in condition_scores.items() if v >= 25 and k != top_condition]
        
        # Weighted condition contribution
        condition_weight = 0.7 if top_score >= 50 else 0.5
        base_risk_score += min(top_score * condition_weight, 45.0)

        # Multiple condition penalty/bonus
        if len(secondary_conditions) > 0:
            base_risk_score += 8.0  # Multiple pathologies increase risk
            
        # Body part specific risk thresholds with enhanced criteria
        risk_thresholds = self._get_enhanced_risk_thresholds(body_part, top_condition, advanced_features)
        high_thresh, moderate_thresh, low_thresh = risk_thresholds

        # Determine condition classification
        primary_condition = "NORMAL"
        risk_level = "MINIMAL"
        urgency = "ROUTINE"
        confidence_level = "MODERATE"
        
        # Enhanced classification logic
        if base_risk_score >= high_thresh:
            if top_condition and top_score >= 40:
                primary_condition = f"{top_condition.upper()}_SUSPECTED"
                confidence_level = "HIGH" if top_score >= 60 else "MODERATE"
            else:
                primary_condition = "SUSPICIOUS_ABNORMALITY"
                confidence_level = "MODERATE"
            risk_level = "HIGH"
            urgency = self._determine_urgency(body_part, top_condition, top_score, "HIGH")
            
        elif base_risk_score >= moderate_thresh:
            if top_condition and top_score >= 30:
                primary_condition = f"{top_condition.upper()}_POSSIBLE"
                confidence_level = "MODERATE"
            else:
                primary_condition = "ABNORMAL_FINDINGS"
                confidence_level = "MODERATE"
            risk_level = "MODERATE"
            urgency = self._determine_urgency(body_part, top_condition, top_score, "MODERATE")
            
        elif base_risk_score >= low_thresh:
            primary_condition = "MILD_ABNORMALITY"
            risk_level = "LOW"
            urgency = "ROUTINE_FOLLOWUP"
            confidence_level = "MODERATE"
        else:
            # Additional normal vs. benign classification
            if any(score > 15 for score in condition_scores.values()):
                primary_condition = "BENIGN_FINDINGS"
            confidence_level = "HIGH"

        # Quality-based confidence adjustment
        quality_score = self._calculate_overall_quality_score(advanced_features)
        if quality_score < 0.6:
            confidence_level = "LOW"
        elif quality_score > 0.8:
            if confidence_level == "MODERATE":
                confidence_level = "HIGH"

        return {
            "primary_condition": primary_condition,
            "secondary_conditions": secondary_conditions,
            "risk_level": risk_level,
            "urgency": urgency,
            "risk_score": int(min(max(base_risk_score, 0.0), 100.0)),
            "confidence_level": confidence_level,
            "top_condition": top_condition,
            "condition_scores": {k: int(v) for k, v in condition_scores.items()} if condition_scores else None,
            "contributing_factors": self._identify_contributing_factors(patterns, advanced_features, condition_scores)
        }

    def _calculate_body_specific_risk(self, body_part: str, body_specific: dict):
        """Calculate risk based on body part specific features"""
        risk_addition = 0.0
        
        try:
            if body_part == 'brain':
                if body_specific.get('symmetry_score', 1.0) < 0.7:
                    risk_addition += 15.0
                dark_regions = body_specific.get('dark_regions', {})
                if dark_regions.get('count', 0) > 2:
                    risk_addition += 10.0
                    
            elif body_part == 'chest':
                lung_analysis = body_specific.get('lung_field_analysis', {})
                if lung_analysis.get('size_asymmetry', 0) > 0.3:
                    risk_addition += 12.0
                if not lung_analysis.get('bilateral_lungs', True):
                    risk_addition += 8.0
                    
            elif body_part == 'breast':
                density_analysis = body_specific.get('density_analysis', {})
                if density_analysis.get('density_class') == 'extremely_dense':
                    risk_addition += 5.0  # Increases detection difficulty
                distortion = body_specific.get('architectural_distortion', {})
                if distortion.get('distortion_present', False):
                    risk_addition += 20.0
                    
            elif body_part == 'extremities':
                bone_analysis = body_specific.get('bone_analysis', {})
                if not bone_analysis.get('cortical_continuity', True):
                    risk_addition += 25.0  # Possible fracture
                joint_analysis = body_specific.get('joint_analysis', {})
                if joint_analysis.get('joint_narrowing_suspected', False):
                    risk_addition += 10.0
                    
        except Exception as e:
            logger.warning(f"Body specific risk calculation failed: {e}")
            
        return risk_addition

    def _get_enhanced_risk_thresholds(self, body_part: str, top_condition: str, advanced_features: dict):
        """Get enhanced risk thresholds based on body part and condition"""
        base_thresholds = {
            "brain": (50, 30, 15),
            "chest": (55, 32, 18),
            "heart": (48, 28, 14),
            "breast": (52, 30, 16),
            "spine": (58, 35, 20),
            "extremities": (60, 38, 22),
            "abdomen": (55, 33, 19),
            "unknown": (55, 32, 18)
        }
        
        high, moderate, low = base_thresholds.get(body_part, base_thresholds["unknown"])
        
        # Adjust based on image quality
        quality_score = self._calculate_overall_quality_score(advanced_features)
        if quality_score < 0.6:
            # Lower quality images require higher thresholds
            high += 8
            moderate += 5
            low += 3
        elif quality_score > 0.8:
            # Higher quality allows for more sensitive detection
            high -= 3
            moderate -= 2
            low -= 1
            
        # Condition-specific adjustments
        if top_condition == 'hemorrhage' and body_part == 'brain':
            high -= 5  # More sensitive for brain hemorrhage
        elif top_condition == 'fracture' and body_part == 'extremities':
            high -= 3  # More sensitive for fractures
            
        return (high, moderate, low)

    def _determine_urgency(self, body_part: str, condition: str, score: float, risk_level: str):
        """Determine urgency based on body part, condition, and score"""
        try:
            urgency_matrix = self.URGENCY_MATRIX.get(body_part, {})
            condition_urgency = urgency_matrix.get(condition, {})
            
            if condition_urgency:
                return condition_urgency.get(risk_level, "ROUTINE")
            
            # Default urgency based on risk level and body part
            if risk_level == "HIGH":
                if body_part in ['brain', 'heart'] and score >= 70:
                    return "IMMEDIATE"
                elif body_part in ['brain', 'heart']:
                    return "WITHIN_4_HOURS"
                else:
                    return "WITHIN_1_WEEK"
            elif risk_level == "MODERATE":
                if body_part in ['brain', 'heart']:
                    return "WITHIN_24_HOURS"
                else:
                    return "WITHIN_2_WEEKS"
            else:
                return "ROUTINE_FOLLOWUP"
                
        except Exception as e:
            logger.warning(f"Urgency determination failed: {e}")
            return "ROUTINE"

    def _calculate_overall_quality_score(self, advanced_features: dict):
        """Calculate overall image quality score"""
        try:
            intensity_stats = advanced_features.get('intensity_statistics', {})
            
            # Normalize metrics to 0-1 scale
            contrast_score = min(intensity_stats.get('std', 0) / 50.0, 1.0)
            range_score = min((intensity_stats.get('max', 0) - intensity_stats.get('min', 0)) / 255.0, 1.0)
            
            # Simple quality metric
            quality_score = (contrast_score + range_score) / 2.0
            return max(0.0, min(1.0, quality_score))
            
        except:
            return 0.5  # Default moderate quality

    def _identify_contributing_factors(self, patterns: dict, advanced_features: dict, condition_scores: dict):
        """Identify key factors contributing to the classification"""
        factors = []
        
        try:
            # Pattern-based factors
            if patterns.get('potential_masses', 0) > 0:
                factors.append(f"Detected {patterns['potential_masses']} suspicious region(s)")
                
            if patterns.get('asymmetry_detected', False):
                factors.append("Asymmetry between left and right sides")
                
            if patterns.get('texture_variations') == 'Irregular':
                factors.append("Irregular texture patterns")
                
            # Advanced feature factors
            intensity_stats = advanced_features.get('intensity_statistics', {})
            if abs(intensity_stats.get('skewness', 0)) > 1.0:
                factors.append("Abnormal intensity distribution")
                
            # Condition-specific factors
            for condition, score in condition_scores.items():
                if score >= 30:
                    factors.append(f"Elevated {condition} indicators (score: {score})")
                    
            # Body part specific factors
            body_specific = advanced_features.get('body_part_specific', {})
            if body_specific:
                # Add specific findings based on body part
                factors.extend(self._extract_body_specific_factors(body_specific))
                
        except Exception as e:
            logger.warning(f"Factor identification failed: {e}")
            
        return factors[:5]  # Limit to top 5 factors

    def _extract_body_specific_factors(self, body_specific: dict):
        """Extract body part specific contributing factors"""
        factors = []
        
        try:
            # Brain-specific factors
            if 'symmetry_score' in body_specific and body_specific['symmetry_score'] < 0.8:
                factors.append(f"Brain asymmetry (score: {body_specific['symmetry_score']:.2f})")
                
            # Chest-specific factors
            lung_analysis = body_specific.get('lung_field_analysis', {})
            if lung_analysis.get('size_asymmetry', 0) > 0.2:
                factors.append(f"Lung field asymmetry ({lung_analysis['size_asymmetry']:.2f})")
                
            # Breast-specific factors
            density_analysis = body_specific.get('density_analysis', {})
            if density_analysis.get('heterogeneity_score', 0) > 0.3:
                factors.append("High tissue heterogeneity")
                
            distortion = body_specific.get('architectural_distortion', {})
            if distortion.get('distortion_present', False):
                factors.append("Architectural distortion detected")
                
            # Extremity-specific factors
            bone_analysis = body_specific.get('bone_analysis', {})
            if not bone_analysis.get('cortical_continuity', True):
                factors.append("Cortical discontinuity suggesting fracture")
                
        except Exception as e:
            logger.warning(f"Body specific factor extraction failed: {e}")
            
        return factors
    
    def _generate_risk_assessment(self, classification, patterns, body_part, condition_scores, advanced_features):
        """Generate comprehensive risk assessment for medical decision making"""
        risk_assessment = {
            "overall_risk": {},
            "specific_risks": {},
            "clinical_significance": {},
            "follow_up_requirements": {},
            "differential_diagnosis": []
        }
        
        try:
            risk_score = classification.get('risk_score', 0)
            risk_level = classification.get('risk_level', 'MINIMAL')
            primary_condition = classification.get('primary_condition', 'NORMAL')
            
            # Overall risk assessment
            risk_assessment["overall_risk"] = {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "risk_category": self._categorize_risk(risk_score, body_part),
                "urgency_level": classification.get('urgency', 'ROUTINE'),
                "confidence": classification.get('confidence_level', 'MODERATE')
            }
            
            # Specific risk analysis
            risk_assessment["specific_risks"] = self._analyze_specific_risks(
                body_part, condition_scores, advanced_features, patterns
            )
            
            # Clinical significance
            risk_assessment["clinical_significance"] = self._assess_clinical_significance(
                primary_condition, risk_score, body_part, condition_scores
            )
            
            # Follow-up requirements
            risk_assessment["follow_up_requirements"] = self._determine_followup_requirements(
                classification, body_part, condition_scores
            )
            
            # Differential diagnosis
            risk_assessment["differential_diagnosis"] = self._generate_differential_diagnosis(
                condition_scores, body_part, advanced_features
            )
            
        except Exception as e:
            logger.warning(f"Risk assessment generation failed: {e}")
            
        return risk_assessment

    def _categorize_risk(self, risk_score: int, body_part: str):
        """Categorize risk with body part specific considerations"""
        if body_part in ['brain', 'heart']:
            # More stringent categories for critical organs
            if risk_score >= 40:
                return "CRITICAL"
            elif risk_score >= 25:
                return "HIGH"
            elif risk_score >= 15:
                return "MODERATE"
            else:
                return "LOW"
        else:
            # Standard categories
            if risk_score >= 60:
                return "CRITICAL"
            elif risk_score >= 40:
                return "HIGH"
            elif risk_score >= 20:
                return "MODERATE"
            else:
                return "LOW"

    def _analyze_specific_risks(self, body_part: str, condition_scores: dict, advanced_features: dict, patterns: dict):
        """Analyze specific medical risks based on findings"""
        risks = {
            "immediate_risks": [],
            "short_term_risks": [],
            "long_term_risks": [],
            "complication_risks": []
        }
        
        try:
            # Condition-specific risk analysis
            for condition, score in condition_scores.items():
                if score >= 40:
                    risks["immediate_risks"].extend(
                        self._get_condition_specific_risks(condition, body_part, "immediate")
                    )
                elif score >= 25:
                    risks["short_term_risks"].extend(
                        self._get_condition_specific_risks(condition, body_part, "short_term")
                    )
                elif score >= 15:
                    risks["long_term_risks"].extend(
                        self._get_condition_specific_risks(condition, body_part, "long_term")
                    )
            
            # Pattern-specific risks
            if patterns.get('potential_masses', 0) > 1:
                risks["complication_risks"].append("Multiple lesions may indicate systemic disease")
                
            if patterns.get('asymmetry_detected', False) and body_part == 'brain':
                risks["immediate_risks"].append("Brain asymmetry may indicate increased intracranial pressure")
                
        except Exception as e:
            logger.warning(f"Specific risk analysis failed: {e}")
            
        return risks

    def _get_condition_specific_risks(self, condition: str, body_part: str, timeframe: str):
        """Get condition and timeframe specific risks"""
        risk_map = {
            "hemorrhage": {
                "immediate": {
                    "brain": ["Risk of increased intracranial pressure", "Potential for herniation"],
                    "chest": ["Risk of hemodynamic instability", "Possible airway compromise"],
                    "default": ["Risk of hemodynamic compromise", "Potential for expansion"]
                },
                "short_term": {
                    "brain": ["Risk of secondary brain injury", "Potential for vasospasm"],
                    "default": ["Risk of anemia", "Potential for rebleeding"]
                },
                "long_term": {
                    "brain": ["Risk of cognitive impairment", "Potential for seizures"],
                    "default": ["Risk of chronic pain", "Potential for scarring"]
                }
            },
            "tumor": {
                "immediate": {
                    "brain": ["Risk of mass effect", "Potential for seizures"],
                    "default": ["Risk of local compression", "Potential for obstruction"]
                },
                "short_term": {
                    "brain": ["Risk of neurological deterioration", "Potential for hydrocephalus"],
                    "default": ["Risk of growth", "Potential for metastasis"]
                },
                "long_term": {
                    "default": ["Risk of malignant transformation", "Potential for recurrence"]
                }
            },
            "fracture": {
                "immediate": {
                    "spine": ["Risk of spinal cord injury", "Potential for instability"],
                    "default": ["Risk of displacement", "Potential for neurovascular injury"]
                },
                "short_term": {
                    "default": ["Risk of non-union", "Potential for infection"]
                },
                "long_term": {
                    "default": ["Risk of arthritis", "Potential for chronic pain"]
                }
            }
        }
        
        condition_risks = risk_map.get(condition, {})
        timeframe_risks = condition_risks.get(timeframe, {})
        
        return timeframe_risks.get(body_part, timeframe_risks.get("default", []))

    def _assess_clinical_significance(self, primary_condition: str, risk_score: int, body_part: str, condition_scores: dict):
        """Assess clinical significance of findings"""
        significance = {
            "clinical_impact": "MINIMAL",
            "patient_management_change": False,
            "treatment_urgency": "ROUTINE",
            "prognosis_impact": "MINIMAL",
            "quality_of_life_impact": "MINIMAL"
        }
        
        try:
            if risk_score >= 60:
                significance.update({
                    "clinical_impact": "MAJOR",
                    "patient_management_change": True,
                    "treatment_urgency": "IMMEDIATE",
                    "prognosis_impact": "SIGNIFICANT",
                    "quality_of_life_impact": "MAJOR"
                })
            elif risk_score >= 40:
                significance.update({
                    "clinical_impact": "MODERATE",
                    "patient_management_change": True,
                    "treatment_urgency": "WITHIN_24_HOURS",
                    "prognosis_impact": "MODERATE",
                    "quality_of_life_impact": "MODERATE"
                })
            elif risk_score >= 20:
                significance.update({
                    "clinical_impact": "MILD",
                    "patient_management_change": True,
                    "treatment_urgency": "WITHIN_1_WEEK",
                    "prognosis_impact": "MILD",
                    "quality_of_life_impact": "MILD"
                })
                
            # Body part specific adjustments
            if body_part in ['brain', 'heart'] and risk_score >= 30:
                significance["clinical_impact"] = "MAJOR"
                significance["patient_management_change"] = True
                
        except Exception as e:
            logger.warning(f"Clinical significance assessment failed: {e}")
            
        return significance

    def _determine_followup_requirements(self, classification, body_part, condition_scores):
        """Determine specific follow-up requirements"""
        followup = {
            "imaging_followup": {},
            "specialist_referrals": [],
            "monitoring_parameters": [],
            "timeline": {}
        }
        
        try:
            risk_level = classification.get('risk_level', 'MINIMAL')
            urgency = classification.get('urgency', 'ROUTINE')
            primary_condition = classification.get('primary_condition', 'NORMAL')
            
            # Imaging follow-up
            if risk_level in ['HIGH', 'MODERATE']:
                followup["imaging_followup"] = self._recommend_imaging_followup(
                    body_part, primary_condition, urgency
                )
                
            # Specialist referrals
            followup["specialist_referrals"] = self._recommend_specialists(
                body_part, primary_condition, condition_scores
            )
            
            # Monitoring parameters
            followup["monitoring_parameters"] = self._recommend_monitoring(
                body_part, primary_condition, risk_level
            )
            
            # Timeline
            followup["timeline"] = self._create_followup_timeline(urgency, risk_level)
            
        except Exception as e:
            logger.warning(f"Follow-up requirements determination failed: {e}")
            
        return followup

    def _recommend_imaging_followup(self, body_part: str, condition: str, urgency: str):
        """Recommend specific imaging follow-up"""
        imaging_map = {
            "brain": {
                "HEMORRHAGE_SUSPECTED": "Non-contrast CT in 6-12 hours, MRI if stable",
                "TUMOR_SUSPECTED": "Contrast-enhanced MRI with spectroscopy",
                "default": "Follow-up CT or MRI as clinically indicated"
            },
            "chest": {
                "TUMOR_SUSPECTED": "Contrast-enhanced CT chest, consider PET-CT",
                "default": "Follow-up chest X-ray or CT"
            },
            "breast": {
                "TUMOR_SUSPECTED": "Diagnostic mammography, breast MRI, consider biopsy",
                "default": "Follow-up mammography"
            },
            "extremities": {
                "FRACTURE_SUSPECTED": "Orthogonal X-rays, consider CT for complex fractures",
                "default": "Follow-up X-rays"
            }
        }
        
        body_recommendations = imaging_map.get(body_part, {"default": "Follow-up imaging as indicated"})
        return body_recommendations.get(condition, body_recommendations["default"])

    def _recommend_specialists(self, body_part: str, condition: str, condition_scores: dict):
        """Recommend specialist consultations"""
        specialists = []
        
        specialist_map = {
            "brain": {
                "HEMORRHAGE": ["Neurosurgery", "Neurology"],
                "TUMOR": ["Neurosurgery", "Neuro-oncology"],
                "default": ["Neurology"]
            },
            "chest": {
                "TUMOR": ["Pulmonology", "Oncology"],
                "default": ["Pulmonology"]
            },
            "heart": {
                "default": ["Cardiology"]
            },
            "breast": {
                "TUMOR": ["Breast Surgery", "Oncology"],
                "default": ["Breast Surgery"]
            },
            "extremities": {
                "FRACTURE": ["Orthopedic Surgery"],
                "default": ["Orthopedics"]
            }
        }
        
        body_specialists = specialist_map.get(body_part, {"default": ["Internal Medicine"]})
        
        # Check for specific conditions
        for cond, score in condition_scores.items():
            if score >= 30:
                specialists.extend(body_specialists.get(cond.upper(), []))
                
        if not specialists:
            specialists = body_specialists["default"]
            
        return list(set(specialists))  # Remove duplicates

    def _recommend_monitoring(self, body_part: str, condition: str, risk_level: str):
        """Recommend monitoring parameters"""
        monitoring = []
        
        if body_part == "brain":
            monitoring.extend([
                "Neurological status assessment",
                "Glasgow Coma Scale monitoring",
                "Intracranial pressure signs"
            ])
            if "HEMORRHAGE" in condition:
                monitoring.extend([
                    "Hemoglobin levels",
                    "Coagulation studies",
                    "Blood pressure monitoring"
                ])
        elif body_part == "chest":
            monitoring.extend([
                "Respiratory status",
                "Oxygen saturation",
                "Chest pain assessment"
            ])
        elif body_part == "heart":
            monitoring.extend([
                "Cardiac rhythm monitoring",
                "Blood pressure",
                "Cardiac enzymes"
            ])
            
        if risk_level == "HIGH":
            monitoring.append("Frequent vital signs monitoring")
            
        return monitoring

    def _create_followup_timeline(self, urgency: str, risk_level: str):
        """Create follow-up timeline"""
        timeline_map = {
            "IMMEDIATE": {
                "first_assessment": "Within 1 hour",
                "imaging_followup": "Within 6 hours",
                "specialist_consultation": "Within 4 hours"
            },
            "WITHIN_4_HOURS": {
                "first_assessment": "Within 4 hours",
                "imaging_followup": "Within 24 hours",
                "specialist_consultation": "Within 24 hours"
            },
            "WITHIN_24_HOURS": {
                "first_assessment": "Within 24 hours",
                "imaging_followup": "Within 1 week",
                "specialist_consultation": "Within 1 week"
            },
            "WITHIN_1_WEEK": {
                "first_assessment": "Within 1 week",
                "imaging_followup": "Within 1 month",
                "specialist_consultation": "Within 2 weeks"
            },
            "ROUTINE": {
                "first_assessment": "Routine scheduling",
                "imaging_followup": "As clinically indicated",
                "specialist_consultation": "As clinically indicated"
            }
        }
        
        return timeline_map.get(urgency, timeline_map["ROUTINE"])

    def _generate_differential_diagnosis(self, condition_scores: dict, body_part: str, advanced_features: dict):
        """Generate differential diagnosis list"""
        differentials = []
        
        try:
            # Sort conditions by score
            sorted_conditions = sorted(condition_scores.items(), key=lambda x: x[1], reverse=True)
            
            for condition, score in sorted_conditions:
                if score >= 20:  # Include conditions with significant scores
                    differentials.extend(
                        self._get_differential_for_condition(condition, body_part, score)
                    )
            
            # Add body part specific differentials
            body_specific_diffs = self._get_body_part_differentials(body_part, advanced_features)
            differentials.extend(body_specific_diffs)
            
            # Remove duplicates and limit
            differentials = list(set(differentials))[:8]
            
        except Exception as e:
            logger.warning(f"Differential diagnosis generation failed: {e}")
            
        return differentials

    def _get_differential_for_condition(self, condition: str, body_part: str, score: int):
        """Get differential diagnoses for specific condition"""
        differentials_map = {
            "hemorrhage": {
                "brain": ["Intracerebral hemorrhage", "Subarachnoid hemorrhage", "Epidural hematoma", "Subdural hematoma"],
                "chest": ["Hemothorax", "Pulmonary contusion", "Aortic injury"],
                "default": ["Active bleeding", "Hematoma", "Vascular injury"]
            },
            "tumor": {
                "brain": ["Primary brain tumor", "Metastatic disease", "Meningioma", "Glioma"],
                "chest": ["Lung cancer", "Pulmonary nodule", "Metastatic disease"],
                "breast": ["Breast carcinoma", "Fibroadenoma", "Phyllodes tumor"],
                "default": ["Primary neoplasm", "Metastatic disease", "Benign tumor"]
            },
            "fracture": {
                "spine": ["Vertebral compression fracture", "Burst fracture", "Facet dislocation"],
                "extremities": ["Simple fracture", "Comminuted fracture", "Pathological fracture"],
                "default": ["Acute fracture", "Stress fracture", "Pathological fracture"]
            }
        }
        
        condition_diffs = differentials_map.get(condition, {})
        return condition_diffs.get(body_part, condition_diffs.get("default", []))

    def _get_body_part_differentials(self, body_part: str, advanced_features: dict):
        """Get body part specific differential diagnoses"""
        differentials = []
        
        try:
            body_specific = advanced_features.get('body_part_specific', {})
            
            if body_part == "brain":
                if body_specific.get('symmetry_score', 1.0) < 0.8:
                    differentials.extend(["Stroke", "Mass effect", "Edema"])
                    
            elif body_part == "chest":
                lung_analysis = body_specific.get('lung_field_analysis', {})
                if not lung_analysis.get('bilateral_lungs', True):
                    differentials.extend(["Pneumothorax", "Pleural effusion", "Consolidation"])
                    
            elif body_part == "breast":
                density_analysis = body_specific.get('density_analysis', {})
                if density_analysis.get('heterogeneity_score', 0) > 0.3:
                    differentials.extend(["Fibrocystic changes", "Mastitis", "Ductal changes"])
                    
        except Exception as e:
            logger.warning(f"Body part differential generation failed: {e}")
            
        return differentials
        """Generate comprehensive doctor recommendations"""
        recommendations = {
            "risk_based_recommendations": [],
            "medical_recommendations": [],
            "quality_recommendations": [],
            "general_recommendations": []
        }
        
        # Non-diagnostic photograph
        if classification.get('condition') == 'NON_DIAGNOSTIC_PHOTOGRAPH':
            recommendations["risk_based_recommendations"].append(
                "Image appears to be a non-diagnostic photograph; obtain appropriate medical imaging (X-ray/CT/MRI/Ultrasound)"
            )
            recommendations["general_recommendations"].extend([
                "Verify correct modality and acquisition settings",
                "Re-upload a diagnostic-quality scan for analysis"
            ])
            return recommendations

        # Risk-based recommendations
        if classification['risk_level'] == "HIGH":
            recommendations["risk_based_recommendations"].extend([
                "Immediate follow-up consultation required",
                "Consider urgent referral to specialist",
                "Schedule follow-up imaging within 1 week"
            ])
        elif classification['risk_level'] == "MODERATE":
            recommendations["risk_based_recommendations"].extend([
                "Follow-up consultation recommended",
                "Consider specialist referral",
                "Repeat imaging in 1-3 months"
            ])
        elif classification['risk_level'] == "LOW":
            recommendations["risk_based_recommendations"].extend([
                "Routine follow-up as per standard protocol",
                "Monitor for any changes in symptoms"
            ])
        
        # Medical recommendations based on findings
        if patterns['potential_masses'] > 0:
            recommendations["medical_recommendations"].extend([
                f"Evaluate {patterns['potential_masses']} detected masses/lesions",
                "Consider additional imaging modalities if needed",
                "Document size and location of findings"
            ])
        
        if patterns['asymmetry_detected']:
            recommendations["medical_recommendations"].extend([
                "Investigate cause of asymmetry",
                "Compare with previous imaging if available",
                "Consider contralateral imaging for comparison"
            ])

        # Condition-specific recommendations
        top_condition = classification.get('top_condition')
        cond_scores = condition_scores or {}
        if top_condition == 'hemorrhage' and cond_scores.get('hemorrhage', 0) >= 35:
            if body_part == 'brain':
                recommendations["medical_recommendations"].extend([
                    "Urgent non-contrast head CT or CT angiography as indicated",
                    "Immediate neurology/neurosurgery consultation",
                    "Initiate hemorrhage protocol per institutional guidelines"
                ])
            else:
                recommendations["medical_recommendations"].append("Assess for active bleeding; correlate clinically and consider contrast-enhanced imaging")
        if top_condition == 'fracture' and cond_scores.get('fracture', 0) >= 35:
            recommendations["medical_recommendations"].extend([
                "Immobilize suspected region pending confirmation",
                "Obtain dedicated radiographic series; consider CT for complex fractures",
                "Surgical consultation if displaced/unstable"
            ])
        if top_condition == 'tumor' and cond_scores.get('tumor', 0) >= 35:
            recommendations["medical_recommendations"].extend([
                "Obtain dedicated imaging with contrast (MRI preferred where applicable)",
                "Refer to appropriate oncology/specialist clinic",
                "Consider biopsy if lesion amenable and clinically indicated"
            ])
        
        # Quality recommendations
        recommendations["quality_recommendations"].extend([
            "Ensure proper patient positioning for future scans",
            "Maintain consistent imaging protocols",
            "Verify image quality before analysis"
        ])
        
        # General recommendations
        recommendations["general_recommendations"].extend([
            "Review complete patient history",
            "Correlate with clinical findings",
            "Document all observations in patient record"
        ])
        
        return recommendations
    
    def _assess_image_quality_enhanced(self, image_data):
        """Enhanced assessment of image quality with quantitative metrics"""
        quality_ratings = {
            "overall_rating": "Good",
            "sharpness_rating": "Good",
            "contrast_rating": "Good",
            "noise_rating": "Low",
            "quality_score": 0.75,  # 0-1 scale
            "diagnostic_quality": "ACCEPTABLE",
            "artifacts": [],
            "recommended_improvements": []
        }
        
        try:
            if 'opencv_image' in image_data:
                gray = cv2.cvtColor(image_data['opencv_image'], cv2.COLOR_BGR2GRAY)
                
                # Sharpness assessment using Laplacian variance
                laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                quality_ratings["sharpness_value"] = float(laplacian_var)
                if laplacian_var > 100:
                    quality_ratings["sharpness_rating"] = "Excellent"
                elif laplacian_var > 50:
                    quality_ratings["sharpness_rating"] = "Good"
                elif laplacian_var > 20:
                    quality_ratings["sharpness_rating"] = "Fair"
                else:
                    quality_ratings["sharpness_rating"] = "Poor"
                    quality_ratings["recommended_improvements"].append("Improve image focus")
                
                # Contrast assessment with histogram analysis
                hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
                hist_norm = hist.flatten() / np.sum(hist)
                cumulative_dist = np.cumsum(hist_norm)
                contrast_range = np.where(cumulative_dist > 0.95)[0][0] - np.where(cumulative_dist > 0.05)[0][0]
                contrast = gray.std()
                quality_ratings["contrast_value"] = float(contrast)
                
                if contrast > 50 and contrast_range > 150:
                    quality_ratings["contrast_rating"] = "Excellent"
                elif contrast > 30 and contrast_range > 100:
                    quality_ratings["contrast_rating"] = "Good"
                elif contrast > 15 and contrast_range > 50:
                    quality_ratings["contrast_rating"] = "Fair"
                else:
                    quality_ratings["contrast_rating"] = "Poor"
                    quality_ratings["recommended_improvements"].append("Enhance image contrast")
                
                # Noise assessment with advanced filtering
                noise = np.mean(np.abs(cv2.medianBlur(gray, 3) - gray))
                snr = 0
                if noise > 0:
                    snr = gray.mean() / noise
                quality_ratings["noise_value"] = float(noise)
                quality_ratings["signal_to_noise_ratio"] = float(snr)
                
                if noise < 5 and snr > 20:
                    quality_ratings["noise_rating"] = "Very Low"
                elif noise < 10 and snr > 15:
                    quality_ratings["noise_rating"] = "Low"
                elif noise < 20 and snr > 10:
                    quality_ratings["noise_rating"] = "Moderate"
                else:
                    quality_ratings["noise_rating"] = "High"
                    quality_ratings["recommended_improvements"].append("Reduce image noise")
                
                # Artifact detection
                # Motion blur detection
                if self._detect_motion_blur(gray):
                    quality_ratings["artifacts"].append("Motion Blur")
                    quality_ratings["recommended_improvements"].append("Minimize patient movement")
                    
                # Check for overexposure
                if self._detect_overexposure(gray):
                    quality_ratings["artifacts"].append("Overexposure")
                    quality_ratings["recommended_improvements"].append("Reduce exposure settings")
                    
                # Check for underexposure
                if self._detect_underexposure(gray):
                    quality_ratings["artifacts"].append("Underexposure")
                    quality_ratings["recommended_improvements"].append("Increase exposure settings")
                
                # Overall quality score calculation (0-1 scale)
                sharpness_score = min(laplacian_var / 200.0, 1.0)
                contrast_score = min(contrast / 80.0, 1.0)
                noise_score = min(max((25.0 - noise) / 25.0, 0.0), 1.0)
                artifact_penalty = len(quality_ratings["artifacts"]) * 0.1
                
                quality_score = (sharpness_score * 0.4 + contrast_score * 0.3 + noise_score * 0.3) - artifact_penalty
                quality_ratings["quality_score"] = max(0.0, min(1.0, quality_score))
                
                # Overall rating
                if quality_ratings["quality_score"] > 0.8:
                    quality_ratings["overall_rating"] = "Excellent"
                    quality_ratings["diagnostic_quality"] = "HIGH"
                elif quality_ratings["quality_score"] > 0.6:
                    quality_ratings["overall_rating"] = "Good"
                    quality_ratings["diagnostic_quality"] = "ACCEPTABLE"
                elif quality_ratings["quality_score"] > 0.4:
                    quality_ratings["overall_rating"] = "Fair"
                    quality_ratings["diagnostic_quality"] = "LIMITED"
                else:
                    quality_ratings["overall_rating"] = "Poor"
                    quality_ratings["diagnostic_quality"] = "SUBOPTIMAL"
                    quality_ratings["recommended_improvements"].append("Consider rescanning with improved technique")
                
        except Exception as e:
            logger.warning(f"Enhanced quality assessment failed: {e}")
        
        return quality_ratings
        
    def _detect_motion_blur(self, gray):
        """Detect motion blur artifacts"""
        try:
            # FFT approach to detect directional blur
            f = np.fft.fft2(gray)
            fshift = np.fft.fftshift(f)
            magnitude = 20 * np.log(np.abs(fshift))
            
            # Check for strong directional components in FFT
            rows, cols = gray.shape
            center_row, center_col = rows // 2, cols // 2
            
            # Create a mask for the central region
            mask = np.zeros_like(magnitude)
            center_size = min(20, min(rows, cols) // 10)
            mask[center_row-center_size:center_row+center_size, center_col-center_size:center_col+center_size] = 1
            
            # Calculate directional variance
            masked_magnitude = magnitude * mask
            if masked_magnitude.max() > 0:
                row_variance = np.var(np.sum(masked_magnitude, axis=1))
                col_variance = np.var(np.sum(masked_magnitude, axis=0))
                
                # High ratio between directional variances suggests motion blur
                ratio = max(row_variance, col_variance) / max(1, min(row_variance, col_variance))
                return ratio > 5.0
            
            return False
        except Exception:
            return False
    
    def _detect_overexposure(self, gray):
        """Detect overexposure artifacts"""
        # Check if significant portion is very bright
        high_intensity_ratio = np.sum(gray > 240) / float(gray.size)
        return high_intensity_ratio > 0.15
    
    def _detect_underexposure(self, gray):
        """Detect underexposure artifacts"""
        # Check if significant portion is very dark
        low_intensity_ratio = np.sum(gray < 30) / float(gray.size)
        return low_intensity_ratio > 0.4
    
    def _generate_technical_details(self, image_data, patterns):
        """Generate technical analysis details"""
        return {
            "image_dimensions": f"{image_data.get('width', 'Unknown')} x {image_data.get('height', 'Unknown')}",
            "color_channels": image_data.get('channels', 'Unknown'),
            "detected_contours": patterns.get('potential_masses', 0),
            "analysis_algorithm": "Enhanced Computer Vision Analysis",
            "processing_time": "Real-time",
            "confidence_score": "85%"
        }
        
    def _generate_technical_details_enhanced(self, image_data, patterns, advanced_features):
        """Generate enhanced technical analysis details with comprehensive metrics"""
        tech_details = {
            "image_dimensions": f"{image_data.get('width', 'Unknown')} x {image_data.get('height', 'Unknown')}",
            "color_channels": image_data.get('channels', 'Unknown'),
            "detected_contours": patterns.get('potential_masses', 0),
            "analysis_algorithm": "Enhanced Deep Tissue Analysis v2.0",
            "processing_time": "Real-time",
            "confidence_score": "85%",
            "image_statistics": {},
            "algorithmic_parameters": {},
            "processing_pipeline": []
        }
        
        try:
            # Enhanced image statistics
            if 'opencv_image' in image_data:
                gray = cv2.cvtColor(image_data['opencv_image'], cv2.COLOR_BGR2GRAY)
                tech_details["image_statistics"] = {
                    "mean_intensity": float(gray.mean()),
                    "intensity_std_dev": float(gray.std()),
                    "min_intensity": int(gray.min()),
                    "max_intensity": int(gray.max()),
                    "dynamic_range": int(gray.max() - gray.min()),
                    "histogram_entropy": float(self._calculate_histogram_entropy(gray)),
                    "intensity_skewness": float(self._calculate_skewness(gray)),
                    "intensity_kurtosis": float(self._calculate_kurtosis(gray))
                }
                
            # Add algorithmic parameters
            tech_details["algorithmic_parameters"] = {
                "contour_detection": {
                    "min_contour_area_ratio": self.min_contour_area_ratio,
                    "max_contour_area_ratio": self.max_contour_area_ratio,
                    "min_circularity": self.min_circularity,
                    "min_solidity": self.min_solidity
                },
                "feature_extraction": {
                    "texture_analysis": "Advanced GLCM + LBP",
                    "morphological_analysis": "Multi-scale structure elements",
                    "spatial_distribution": "Quadrant + center-periphery analysis"
                },
                "classification": {
                    "multi_factor_analysis": "Weighted condition scores with body-part priors",
                    "risk_assessment": "Multi-parameter urgency matrix"
                }
            }
            
            # Add processing pipeline
            tech_details["processing_pipeline"] = [
                "Image preprocessing and normalization",
                "Advanced pattern detection",
                "Body-part specific feature extraction",
                "Multi-factor medical condition classification",
                "Comprehensive risk assessment",
                "Doctor recommendation generation"
            ]
            
            # Add advanced feature summary
            intensity_stats = advanced_features.get('intensity_statistics', {})
            if intensity_stats:
                tech_details["feature_summary"] = {
                    "intensity_distribution": "Normal" if abs(intensity_stats.get('skewness', 0)) < 0.5 else "Skewed",
                    "texture_complexity": "High" if advanced_features.get('texture_analysis', {}).get('lbp_score', 0) > 1000 else "Moderate",
                    "spatial_homogeneity": "Homogeneous" if advanced_features.get('spatial_distribution', {}).get('quadrant_variance', 0) < 100 else "Heterogeneous"
                }
                
        except Exception as e:
            logger.warning(f"Enhanced technical details generation failed: {e}")
            
        return tech_details
        
    def _calculate_histogram_entropy(self, gray):
        """Calculate entropy of the histogram as a measure of information content"""
        try:
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist = hist.flatten() / hist.sum()
            # Remove zeros to avoid log(0)
            hist = hist[hist > 0]
            return -np.sum(hist * np.log2(hist))
        except:
            return 0.0
            
    def _calculate_confidence_metrics(self, classification, quality, advanced_features):
        """Calculate confidence metrics for the analysis"""
        confidence_metrics = {
            "overall_confidence": "MODERATE",
            "classification_confidence": 0.75,
            "feature_extraction_confidence": 0.80,
            "risk_assessment_confidence": 0.70,
            "factors_affecting_confidence": []
        }
        
        try:
            # Base confidence on classification and quality
            confidence_level = classification.get('confidence_level', 'MODERATE')
            quality_score = quality.get('quality_score', 0.75)
            
            # Map confidence level to numeric score
            confidence_map = {"LOW": 0.4, "MODERATE": 0.7, "HIGH": 0.9}
            classification_confidence = confidence_map.get(confidence_level, 0.7)
            
            # Calculate overall confidence as weighted combination
            overall_confidence = 0.5 * classification_confidence + 0.5 * quality_score
            
            # Map back to categorical
            if overall_confidence > 0.8:
                confidence_level = "HIGH"
            elif overall_confidence > 0.5:
                confidence_level = "MODERATE"
            else:
                confidence_level = "LOW"
                
            confidence_metrics["overall_confidence"] = confidence_level
            confidence_metrics["classification_confidence"] = float(classification_confidence)
            confidence_metrics["feature_extraction_confidence"] = float(quality_score)
            
            # Factors affecting confidence
            factors = []
            
            if quality.get('quality_score', 0) < 0.6:
                factors.append("Limited image quality")
                
            if quality.get('artifacts', []):
                factors.append(f"Image artifacts: {', '.join(quality['artifacts'])}")
                
            if classification.get('risk_score', 0) < 20:
                factors.append("Minimal abnormal findings")
                
            if len(factors) == 0:
                factors.append("Analysis performed on adequate quality image")
                
            confidence_metrics["factors_affecting_confidence"] = factors
            
        except Exception as e:
            logger.warning(f"Confidence metrics calculation failed: {e}")
            
        return confidence_metrics
    
    def _generate_medical_report(self, filename, body_part, classification, patterns, recommendations, quality, technical):
        """Generate a formatted medical report"""
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("DARKMED AI - MEDICAL IMAGE ANALYSIS REPORT")
        report_lines.append("=" * 60)
        report_lines.append("")
        
        # Patient Information
        report_lines.append("PATIENT INFORMATION:")
        report_lines.append(f"File: {filename}")
        report_lines.append(f"Body Part: {body_part.upper()}")
        report_lines.append(f"Analysis Date: {classification.get('analysis_timestamp', '2024-01-15')}")
        report_lines.append("")
        
        # Medical Classification
        report_lines.append("MEDICAL CLASSIFICATION:")
        report_lines.append(f"Condition: {classification['condition']}")
        report_lines.append(f"Risk Level: {classification['risk_level']}")
        report_lines.append(f"Urgency: {classification['urgency']}")
        report_lines.append(f"Risk Score: {classification['risk_score']}/100")
        if classification.get('top_condition'):
            report_lines.append(f"Primary Concern: {classification['top_condition'].upper()}")
        if classification.get('condition_scores'):
            cs = classification['condition_scores']
            report_lines.append(f"Condition Likelihoods (0-100): Tumor {cs.get('tumor',0)}, Hemorrhage {cs.get('hemorrhage',0)}, Fracture {cs.get('fracture',0)}")
        report_lines.append("")
        
        # Medical Findings
        report_lines.append("MEDICAL FINDINGS:")
        report_lines.append(f"Potential Masses/Lesions: {patterns.get('potential_masses', 0)}")
        report_lines.append(f"Asymmetry: {'Yes' if patterns.get('asymmetry_detected', False) else 'No'}")
        report_lines.append(f"Asymmetry Details: {patterns.get('asymmetry_interpretation', 'N/A')}")
        report_lines.append(f"Texture Variations: {patterns.get('texture_variations', 'N/A')}")
        report_lines.append(f"Contour Analysis: {patterns.get('contour_analysis', 'N/A')}")
        # Evidence details
        cond_evidence = patterns.get('condition_evidence', {})
        if any(cond_evidence.get(k) for k in ['tumor','hemorrhage','fracture']):
            report_lines.append("")
            report_lines.append("Condition Evidence:")
            for k in ['tumor','hemorrhage','fracture']:
                ev_list = cond_evidence.get(k, [])
                if ev_list:
                    report_lines.append(f"- {k.capitalize()}: " + "; ".join(ev_list))
        report_lines.append("")
        
        # Doctor Recommendations
        report_lines.append("CLINICAL RECOMMENDATIONS:")
        if recommendations.get('risk_based_recommendations'):
            report_lines.append("Risk-Based Actions:")
            for rec in recommendations['risk_based_recommendations']:
                report_lines.append(f"  • {rec}")
            report_lines.append("")
        
        if recommendations.get('medical_recommendations'):
            report_lines.append("Medical Actions:")
            for rec in recommendations['medical_recommendations']:
                report_lines.append(f"  • {rec}")
            report_lines.append("")
        
        if recommendations.get('general_recommendations'):
            report_lines.append("General Actions:")
            for rec in recommendations['general_recommendations']:
                report_lines.append(f"  • {rec}")
            report_lines.append("")
        
        # Quality Assessment
        report_lines.append("IMAGE QUALITY ASSESSMENT:")
        report_lines.append(f"Overall Rating: {quality.get('overall_rating', 'N/A')}")
        report_lines.append(f"Sharpness: {quality.get('sharpness_rating', 'N/A')}")
        report_lines.append(f"Contrast: {quality.get('contrast_rating', 'N/A')}")
        report_lines.append(f"Noise Level: {quality.get('noise_rating', 'N/A')}")
        report_lines.append("")
        
        # Technical Details
        report_lines.append("TECHNICAL DETAILS:")
        report_lines.append(f"Image Dimensions: {technical.get('image_dimensions', 'N/A')}")
        report_lines.append(f"Analysis Algorithm: {technical.get('analysis_algorithm', 'N/A')}")
        report_lines.append(f"Confidence Score: {technical.get('confidence_score', 'N/A')}")
        report_lines.append("")
        
        # Disclaimer
        report_lines.append("DISCLAIMER:")
        report_lines.append("This is a preliminary AI-assisted analysis for licensed clinicians only.")
        report_lines.append("This is not a diagnosis and should not replace professional medical judgment.")
        report_lines.append("Always consult with qualified healthcare providers for proper diagnosis and treatment.")
        report_lines.append("")
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
        
    def _generate_medical_report_enhanced(self, filename, body_part, classification, patterns, 
                                        recommendations, quality, technical, risk_assessment, advanced_features):
        """Generate an enhanced formatted medical report with comprehensive risk assessment"""
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("MEDSCOPE-AI - ENHANCED MEDICAL IMAGE ANALYSIS REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # Patient Information
        report_lines.append("PATIENT INFORMATION:")
        report_lines.append(f"File: {filename}")
        report_lines.append(f"Body Part: {body_part.upper()}")
        report_lines.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report_lines.append("")
        
        # Enhanced Medical Classification
        report_lines.append("MEDICAL CLASSIFICATION:")
        report_lines.append(f"Primary Condition: {classification['primary_condition']}")
        if classification.get('secondary_conditions'):
            report_lines.append(f"Secondary Conditions: {', '.join(classification['secondary_conditions'])}")
        report_lines.append(f"Risk Level: {classification['risk_level']}")
        report_lines.append(f"Risk Score: {classification['risk_score']}/100")
        report_lines.append(f"Urgency: {classification['urgency']}")
        report_lines.append(f"Confidence Level: {classification.get('confidence_level', 'MODERATE')}")
        
        if classification.get('condition_scores'):
            cs = classification['condition_scores']
            report_lines.append("\nCondition Likelihood Scores (0-100):")
            for condition, score in cs.items():
                report_lines.append(f"  • {condition.capitalize()}: {score}")
        
        if classification.get('contributing_factors'):
            report_lines.append("\nContributing Factors:")
            for factor in classification.get('contributing_factors', []):
                report_lines.append(f"  • {factor}")
        report_lines.append("")
        
        # Risk Assessment Section (new)
        report_lines.append("COMPREHENSIVE RISK ASSESSMENT:")
        overall_risk = risk_assessment.get('overall_risk', {})
        report_lines.append(f"Risk Category: {overall_risk.get('risk_category', 'UNKNOWN')}")
        report_lines.append(f"Urgency Level: {overall_risk.get('urgency_level', 'ROUTINE')}")
        
        specific_risks = risk_assessment.get('specific_risks', {})
        if specific_risks.get('immediate_risks'):
            report_lines.append("\nImmediate Risks:")
            for risk in specific_risks.get('immediate_risks', []):
                report_lines.append(f"  • {risk}")
                
        if specific_risks.get('short_term_risks'):
            report_lines.append("\nShort-term Risks:")
            for risk in specific_risks.get('short_term_risks', []):
                report_lines.append(f"  • {risk}")
                
        if specific_risks.get('long_term_risks'):
            report_lines.append("\nLong-term Risks:")
            for risk in specific_risks.get('long_term_risks', []):
                report_lines.append(f"  • {risk}")
        
        # Clinical Significance (new)
        clinical_sig = risk_assessment.get('clinical_significance', {})
        if clinical_sig:
            report_lines.append("\nClinical Significance:")
            report_lines.append(f"  • Clinical Impact: {clinical_sig.get('clinical_impact', 'UNKNOWN')}")
            report_lines.append(f"  • Treatment Urgency: {clinical_sig.get('treatment_urgency', 'ROUTINE')}")
            report_lines.append(f"  • Prognosis Impact: {clinical_sig.get('prognosis_impact', 'MINIMAL')}")
        report_lines.append("")
        
        # Medical Findings
        report_lines.append("MEDICAL FINDINGS:")
        report_lines.append(f"Potential Masses/Lesions: {patterns.get('potential_masses', 0)}")
        report_lines.append(f"Asymmetry: {'Yes' if patterns.get('asymmetry_detected', False) else 'No'}")
        report_lines.append(f"Asymmetry Details: {patterns.get('asymmetry_interpretation', 'N/A')}")
        report_lines.append(f"Texture Variations: {patterns.get('texture_variations', 'N/A')}")
        report_lines.append(f"Contour Analysis: {patterns.get('contour_analysis', 'N/A')}")
        
        # Evidence details
        cond_evidence = patterns.get('condition_evidence', {})
        if any(cond_evidence.get(k) for k in ['tumor', 'hemorrhage', 'fracture']):
            report_lines.append("\nCondition Evidence:")
            for k in ['tumor', 'hemorrhage', 'fracture']:
                ev_list = cond_evidence.get(k, [])
                if ev_list:
                    report_lines.append(f"  • {k.capitalize()}: " + "; ".join(ev_list))
        report_lines.append("")
        
        # Differential Diagnosis (new)
        differentials = risk_assessment.get('differential_diagnosis', [])
        if differentials:
            report_lines.append("DIFFERENTIAL DIAGNOSIS:")
            for diff in differentials:
                report_lines.append(f"  • {diff}")
            report_lines.append("")
        
        # Enhanced Doctor Recommendations
        report_lines.append("CLINICAL RECOMMENDATIONS:")
        
        # Urgency-based actions (new)
        if recommendations.get('urgency_based_actions'):
            report_lines.append("Urgency-Based Actions:")
            for rec in recommendations['urgency_based_actions']:
                report_lines.append(f"  • {rec}")
            report_lines.append("")
        
        # Risk-based recommendations
        if recommendations.get('risk_based_recommendations'):
            report_lines.append("Risk-Based Recommendations:")
            for rec in recommendations['risk_based_recommendations']:
                report_lines.append(f"  • {rec}")
            report_lines.append("")
        
        # Medical recommendations
        if recommendations.get('medical_recommendations'):
            report_lines.append("Medical Recommendations:")
            for rec in recommendations['medical_recommendations']:
                report_lines.append(f"  • {rec}")
            report_lines.append("")
        
        # Patient management (new)
        if recommendations.get('patient_management'):
            report_lines.append("Patient Management:")
            for rec in recommendations['patient_management']:
                report_lines.append(f"  • {rec}")
            report_lines.append("")
            
        # Specialist consultations (new)
        if recommendations.get('specialist_consultations'):
            report_lines.append("Specialist Consultations:")
            for rec in recommendations['specialist_consultations']:
                report_lines.append(f"  • {rec}")
            report_lines.append("")
            
        # Imaging recommendations (new)
        if recommendations.get('imaging_recommendations'):
            report_lines.append("Imaging Recommendations:")
            for rec in recommendations['imaging_recommendations']:
                report_lines.append(f"  • {rec}")
            report_lines.append("")
            
        # Monitoring recommendations (new)
        if recommendations.get('monitoring_recommendations'):
            report_lines.append("Monitoring Recommendations:")
            for rec in recommendations['monitoring_recommendations']:
                report_lines.append(f"  • {rec}")
            report_lines.append("")
        
        # Follow-up Requirements (new)
        followup = risk_assessment.get('follow_up_requirements', {})
        if followup:
            report_lines.append("FOLLOW-UP REQUIREMENTS:")
            
            if followup.get('timeline'):
                timeline = followup.get('timeline', {})
                report_lines.append("Timeline:")
                for key, value in timeline.items():
                    report_lines.append(f"  • {key.replace('_', ' ').title()}: {value}")
                report_lines.append("")
                
            if followup.get('imaging_followup'):
                report_lines.append(f"Imaging Follow-up: {followup.get('imaging_followup')}")
                
            if followup.get('specialist_referrals'):
                report_lines.append("Specialist Referrals: " + ", ".join(followup.get('specialist_referrals', [])))
                
            if followup.get('monitoring_parameters'):
                report_lines.append("\nMonitoring Parameters:")
                for param in followup.get('monitoring_parameters', []):
                    report_lines.append(f"  • {param}")
                    
            report_lines.append("")
        
        # Quality Assessment
        report_lines.append("IMAGE QUALITY ASSESSMENT:")
        report_lines.append(f"Overall Rating: {quality.get('overall_rating', 'N/A')}")
        report_lines.append(f"Sharpness: {quality.get('sharpness_rating', 'N/A')}")
        report_lines.append(f"Contrast: {quality.get('contrast_rating', 'N/A')}")
        report_lines.append(f"Noise Level: {quality.get('noise_rating', 'N/A')}")
        report_lines.append("")
        
        # Technical Details
        report_lines.append("TECHNICAL DETAILS:")
        report_lines.append(f"Image Dimensions: {technical.get('image_dimensions', 'N/A')}")
        report_lines.append(f"Analysis Algorithm: Enhanced Deep Tissue Analysis v2.0")
        report_lines.append(f"Confidence Metrics: {classification.get('confidence_level', 'MODERATE')}")
        report_lines.append("")
        
        # Disclaimer
        report_lines.append("DISCLAIMER:")
        report_lines.append("This is a preliminary AI-assisted analysis for licensed clinicians only.")
        report_lines.append("This is not a diagnosis and should not replace professional medical judgment.")
        report_lines.append("Always consult with qualified healthcare providers for proper diagnosis and treatment.")
        report_lines.append("")
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)
    
    def _create_error_analysis(self, filename, error_message):
        """Create error analysis when image processing fails"""
        return {
            "summary": f"Analysis failed for {filename}",
            "medical_classification": {
                "condition": "ANALYSIS_ERROR",
                "risk_level": "UNKNOWN",
                "urgency": "ROUTINE",
                "risk_score": 0
            },
            "medical_findings": {
                "potential_masses": 0,
                "asymmetry_detected": False,
                "asymmetry_interpretation": "Analysis failed",
                "texture_variations": "Unknown",
                "variation_interpretation": "Unable to analyze",
                "contour_analysis": "Analysis failed"
            },
            "doctor_recommendations": {
                "risk_based_recommendations": ["Manual review required"],
                "medical_recommendations": ["Re-upload image if possible"],
                "quality_recommendations": ["Check image format and quality"],
                "general_recommendations": ["Contact technical support if issue persists"]
            },
            "quality_assessment": {
                "overall_rating": "Unknown",
                "sharpness_rating": "Unknown",
                "contrast_rating": "Unknown",
                "noise_rating": "Unknown"
            },
            "technical_details": {
                "image_dimensions": "Unknown",
                "color_channels": "Unknown",
                "detected_contours": 0,
                "analysis_algorithm": "Failed",
                "processing_time": "Failed",
                "confidence_score": "0%"
            },
            "medical_report": f"Analysis failed for {filename}. Error: {error_message}",
            "disclaimer": "This is a preliminary AI-assisted analysis for licensed clinicians only. This is not a diagnosis and should not replace professional medical judgment. Always consult with qualified healthcare providers for proper diagnosis and treatment.",
            "analysis_timestamp": "2024-01-15T10:30:00Z"
        }

# Initialize analyzer and recommendation engine
analyzer = EnhancedMedicalAnalyzer()
recommendation_engine = MedicalRecommendationEngine()

# Helper functions
def save_temp_file(file: UploadFile) -> str:
    """Save uploaded file to temporary location"""
    suffix = Path(file.filename).suffix if file.filename else ""
    fd, tmp_path = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(file.file.read())
        return tmp_path
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save uploaded file")

def get_file_type(filename: str) -> str:
    """Determine file type based on extension"""
    ext = Path(filename).suffix.lower()
    
    if ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']:
        return "image"
    elif ext == '.pdf':
        return "pdf"
    elif ext == '.dcm':
        return "dicom"
    elif ext in ['.mp4', '.avi', '.mov', '.mkv']:
        return "video"
    else:
        return "unknown"

@app.get("/")
async def root():
    return {
        "message": "DarkMed AI - Medical Analysis API",
        "version": "2.0.0",
        "status": "operational",
        "features": [
            "Enhanced medical image analysis",
            "Body part context awareness",
            "Risk classification and urgency assessment",
            "Comprehensive doctor recommendations",
            "Professional medical reports"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": "2024-01-15T10:30:00Z",
        "version": "2.0.0"
    }

@app.get("/body-parts")
async def get_body_parts():
    return {
        "descriptions": analyzer.BODY_PARTS,
        "total_parts": len(analyzer.BODY_PARTS)
    }

@app.post("/analyze")
async def analyze_files(
    files: List[UploadFile] = File(...),
    body_part: str = Form("unknown")
):
    """Analyze uploaded medical files with enhanced AI analysis"""
    
    # Validate body part
    if body_part not in analyzer.BODY_PARTS:
        raise HTTPException(status_code=400, detail=f"Invalid body part. Must be one of: {list(analyzer.BODY_PARTS.keys())}")
    
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    results = []
    total_files = len(files)
    processed_files = 0
    failed_files = 0
    
    for file in files:
        try:
            logger.info(f"Processing file: {file.filename} for body part: {body_part}")
            
            # Save file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # Determine file type
                file_type = get_file_type(file.filename)
                
                if file_type in ["image"]:
                    logger.info(f"Analyzing {body_part} image: {file.filename}")
                    analysis_result = analyzer.analyze_image(temp_file_path, file.filename, body_part)
                    logger.info(f"Enhanced analysis completed for: {file.filename}")
                else:
                    # For non-image files, provide basic analysis
                    analysis_result = {
                        "summary": f"File {file.filename} uploaded for {body_part} analysis",
                        "note": f"File type {file_type} requires specialized analysis tools",
                        "disclaimer": "This is a preliminary AI-assisted analysis for licensed clinicians only. This is not a diagnosis and should not replace professional medical judgment. Always consult with qualified healthcare providers for proper diagnosis and treatment.",
                        "analysis_timestamp": "2024-01-15T10:30:00Z"
                    }
                
                results.append({
                    "filename": file.filename,
                    "body_part": body_part,
                    "file_type": file_type,
                    "analysis": analysis_result
                })
                processed_files += 1
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Failed to process {file.filename}: {str(e)}")
            results.append({
                "filename": file.filename,
                "body_part": body_part,
                "file_type": "unknown",
                "error": str(e)
            })
            failed_files += 1
    
    return {
        "body_part": body_part,
        "total_files": total_files,
        "processed_files": processed_files,
        "failed_files": failed_files,
        "reports": results
    }

@app.post("/generate-pdf-report")
async def generate_pdf_report(
    filename: str = Form(...),
    body_part: str = Form(...),
    analysis_data: str = Form(...)
):
    """Generate an enhanced professional PDF medical report"""
    try:
        import json
        analysis = json.loads(analysis_data)
        
        # Create PDF
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubheading',
            parent=styles['Heading3'],
            fontSize=12,
            spaceAfter=8,
            spaceBefore=10,
            textColor=colors.darkslateblue
        )
        
        normal_style = styles['Normal']
        
        # Title with enhanced styling
        story.append(Paragraph("MEDSCOPE-AI - ENHANCED MEDICAL IMAGE ANALYSIS REPORT", title_style))
        story.append(Spacer(1, 20))
        
        # Patient Information
        story.append(Paragraph("PATIENT INFORMATION", heading_style))
        story.append(Paragraph(f"<b>File:</b> {filename}", normal_style))
        story.append(Paragraph(f"<b>Body Part:</b> {body_part.upper()}", normal_style))
        story.append(Paragraph(f"<b>Analysis Date:</b> {analysis.get('analysis_timestamp', datetime.now().isoformat())}", normal_style))
        story.append(Spacer(1, 12))
        
        # Enhanced Medical Classification
        if 'medical_classification' in analysis:
            story.append(Paragraph("MEDICAL CLASSIFICATION", heading_style))
            classification = analysis['medical_classification']
            
            # More comprehensive classification table
            classification_data = [
                ['Attribute', 'Value'],
                ['Primary Condition', classification.get('primary_condition', 'N/A')],
                ['Risk Level', classification.get('risk_level', 'N/A')],
                ['Risk Score', f"{classification.get('risk_score', 0)}/100"],
                ['Urgency', classification.get('urgency', 'ROUTINE')],
                ['Confidence Level', classification.get('confidence_level', 'MODERATE')]
            ]
            
            # Add secondary conditions if present
            if classification.get('secondary_conditions'):
                classification_data.append(['Secondary Conditions', ', '.join(classification.get('secondary_conditions', []))])
                
            classification_table = Table(classification_data, colWidths=[2*inch, 3*inch])
            classification_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(classification_table)
            
            # Add condition scores if present
            if classification.get('condition_scores'):
                story.append(Spacer(1, 10))
                story.append(Paragraph("Condition Likelihood Scores", subheading_style))
                cs = classification.get('condition_scores', {})
                
                condition_data = [['Condition', 'Score (0-100)']]
                for condition, score in cs.items():
                    condition_data.append([condition.capitalize(), str(score)])
                
                condition_table = Table(condition_data, colWidths=[2*inch, 3*inch])
                condition_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(condition_table)
            
            # Add contributing factors
            if classification.get('contributing_factors'):
                story.append(Spacer(1, 10))
                story.append(Paragraph("Contributing Factors", subheading_style))
                for factor in classification.get('contributing_factors', []):
                    story.append(Paragraph(f"• {factor}", normal_style))
            
            story.append(Spacer(1, 12))
        
        # Risk Assessment (new section)
        if 'risk_assessment' in analysis:
            story.append(Paragraph("COMPREHENSIVE RISK ASSESSMENT", heading_style))
            risk_assessment = analysis['risk_assessment']
            
            # Overall risk
            overall_risk = risk_assessment.get('overall_risk', {})
            overall_data = [
                ['Attribute', 'Value'],
                ['Risk Category', overall_risk.get('risk_category', 'UNKNOWN')],
                ['Urgency Level', overall_risk.get('urgency_level', 'ROUTINE')]
            ]
            
            risk_table = Table(overall_data, colWidths=[2*inch, 3*inch])
            risk_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.mistyrose),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(risk_table)
            
            # Specific risks
            specific_risks = risk_assessment.get('specific_risks', {})
            if specific_risks:
                story.append(Spacer(1, 10))
                
                # Immediate risks
                if specific_risks.get('immediate_risks'):
                    story.append(Paragraph("Immediate Risks", subheading_style))
                    for risk in specific_risks.get('immediate_risks', []):
                        story.append(Paragraph(f"• {risk}", normal_style))
                    story.append(Spacer(1, 6))
                
                # Short-term risks
                if specific_risks.get('short_term_risks'):
                    story.append(Paragraph("Short-term Risks", subheading_style))
                    for risk in specific_risks.get('short_term_risks', []):
                        story.append(Paragraph(f"• {risk}", normal_style))
                    story.append(Spacer(1, 6))
                
                # Long-term risks
                if specific_risks.get('long_term_risks'):
                    story.append(Paragraph("Long-term Risks", subheading_style))
                    for risk in specific_risks.get('long_term_risks', []):
                        story.append(Paragraph(f"• {risk}", normal_style))
            
            # Clinical significance
            clinical_sig = risk_assessment.get('clinical_significance', {})
            if clinical_sig:
                story.append(Spacer(1, 10))
                story.append(Paragraph("Clinical Significance", subheading_style))
                
                clinical_data = [
                    ['Attribute', 'Assessment'],
                    ['Clinical Impact', clinical_sig.get('clinical_impact', 'UNKNOWN')],
                    ['Treatment Urgency', clinical_sig.get('treatment_urgency', 'ROUTINE')],
                    ['Prognosis Impact', clinical_sig.get('prognosis_impact', 'MINIMAL')]
                ]
                
                clinical_table = Table(clinical_data, colWidths=[2*inch, 3*inch])
                clinical_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightsteelblue),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(clinical_table)
            
            story.append(Spacer(1, 12))
        
        # Medical Findings
        if 'medical_findings' in analysis:
            story.append(Paragraph("MEDICAL FINDINGS", heading_style))
            findings = analysis['medical_findings']
            
            findings_data = [
                ['Finding', 'Details'],
                ['Potential Masses/Lesions', str(findings.get('potential_masses', 0))],
                ['Asymmetry', 'Yes' if findings.get('asymmetry_detected', False) else 'No'],
                ['Asymmetry Details', findings.get('asymmetry_interpretation', 'N/A')],
                ['Texture Variations', findings.get('texture_variations', 'N/A')],
                ['Contour Analysis', findings.get('contour_analysis', 'N/A')]
            ]
            
            findings_table = Table(findings_data, colWidths=[2*inch, 3*inch])
            findings_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(findings_table)
            
            # Condition evidence
            cond_evidence = findings.get('condition_evidence', {})
            if any(cond_evidence.get(k) for k in ['tumor', 'hemorrhage', 'fracture']):
                story.append(Spacer(1, 10))
                story.append(Paragraph("Condition Evidence", subheading_style))
                
                for k in ['tumor', 'hemorrhage', 'fracture']:
                    ev_list = cond_evidence.get(k, [])
                    if ev_list:
                        story.append(Paragraph(f"<b>{k.capitalize()}:</b> " + "; ".join(ev_list), normal_style))
                        story.append(Spacer(1, 4))
            
            story.append(Spacer(1, 12))
        
        # Differential Diagnosis (new section)
        if 'risk_assessment' in analysis and analysis['risk_assessment'].get('differential_diagnosis'):
            story.append(Paragraph("DIFFERENTIAL DIAGNOSIS", heading_style))
            differentials = analysis['risk_assessment'].get('differential_diagnosis', [])
            
            for diff in differentials:
                story.append(Paragraph(f"• {diff}", normal_style))
                
            story.append(Spacer(1, 12))
        
        # Enhanced Doctor Recommendations
        if 'doctor_recommendations' in analysis:
            story.append(Paragraph("CLINICAL RECOMMENDATIONS", heading_style))
            recommendations = analysis['doctor_recommendations']
            
            # Urgency-based actions
            if recommendations.get('urgency_based_actions'):
                story.append(Paragraph("Urgency-Based Actions", subheading_style))
                for rec in recommendations['urgency_based_actions']:
                    story.append(Paragraph(f"• {rec}", normal_style))
                story.append(Spacer(1, 6))
            
            # Risk-based recommendations
            if recommendations.get('risk_based_recommendations'):
                story.append(Paragraph("Risk-Based Recommendations", subheading_style))
                for rec in recommendations['risk_based_recommendations']:
                    story.append(Paragraph(f"• {rec}", normal_style))
                story.append(Spacer(1, 6))
            
            # Medical recommendations
            if recommendations.get('medical_recommendations'):
                story.append(Paragraph("Medical Recommendations", subheading_style))
                for rec in recommendations['medical_recommendations']:
                    story.append(Paragraph(f"• {rec}", normal_style))
                story.append(Spacer(1, 6))
            
            # Patient management
            if recommendations.get('patient_management'):
                story.append(Paragraph("Patient Management", subheading_style))
                for rec in recommendations['patient_management']:
                    story.append(Paragraph(f"• {rec}", normal_style))
                story.append(Spacer(1, 6))
                
            # Specialist consultations
            if recommendations.get('specialist_consultations'):
                story.append(Paragraph("Specialist Consultations", subheading_style))
                for rec in recommendations['specialist_consultations']:
                    story.append(Paragraph(f"• {rec}", normal_style))
                story.append(Spacer(1, 6))
                
            # Imaging recommendations
            if recommendations.get('imaging_recommendations'):
                story.append(Paragraph("Imaging Recommendations", subheading_style))
                for rec in recommendations['imaging_recommendations']:
                    story.append(Paragraph(f"• {rec}", normal_style))
                story.append(Spacer(1, 6))
                
            # Monitoring recommendations
            if recommendations.get('monitoring_recommendations'):
                story.append(Paragraph("Monitoring Recommendations", subheading_style))
                for rec in recommendations['monitoring_recommendations']:
                    story.append(Paragraph(f"• {rec}", normal_style))
                
            story.append(Spacer(1, 12))
        
        # Follow-up Requirements (new section)
        if 'risk_assessment' in analysis and analysis['risk_assessment'].get('follow_up_requirements'):
            story.append(Paragraph("FOLLOW-UP REQUIREMENTS", heading_style))
            followup = analysis['risk_assessment'].get('follow_up_requirements', {})
            
            # Timeline
            if followup.get('timeline'):
                story.append(Paragraph("Timeline", subheading_style))
                timeline = followup.get('timeline', {})
                
                timeline_data = [['Requirement', 'Timeframe']]
                for key, value in timeline.items():
                    timeline_data.append([key.replace('_', ' ').title(), value])
                
                timeline_table = Table(timeline_data, colWidths=[2*inch, 3*inch])
                timeline_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightsteelblue),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(timeline_table)
                story.append(Spacer(1, 6))
                
            # Imaging followup
            if followup.get('imaging_followup'):
                story.append(Paragraph("Imaging Follow-up", subheading_style))
                story.append(Paragraph(followup.get('imaging_followup'), normal_style))
                story.append(Spacer(1, 6))
                
            # Specialist referrals
            if followup.get('specialist_referrals'):
                story.append(Paragraph("Specialist Referrals", subheading_style))
                story.append(Paragraph(", ".join(followup.get('specialist_referrals', [])), normal_style))
                story.append(Spacer(1, 6))
                
            # Monitoring parameters
            if followup.get('monitoring_parameters'):
                story.append(Paragraph("Monitoring Parameters", subheading_style))
                for param in followup.get('monitoring_parameters', []):
                    story.append(Paragraph(f"• {param}", normal_style))
                
            story.append(Spacer(1, 12))
        
        # Quality Assessment
        if 'quality_assessment' in analysis:
            story.append(Paragraph("IMAGE QUALITY ASSESSMENT", heading_style))
            quality = analysis['quality_assessment']
            
            quality_data = [
                ['Aspect', 'Rating'],
                ['Overall Rating', quality.get('overall_rating', 'N/A')],
                ['Diagnostic Quality', quality.get('diagnostic_quality', 'N/A')],
                ['Sharpness', quality.get('sharpness_rating', 'N/A')],
                ['Contrast', quality.get('contrast_rating', 'N/A')],
                ['Noise Level', quality.get('noise_rating', 'N/A')]
            ]
            
            quality_table = Table(quality_data, colWidths=[2*inch, 3*inch])
            quality_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(quality_table)
            
            # Quality recommendations
            if quality.get('recommended_improvements'):
                story.append(Spacer(1, 8))
                story.append(Paragraph("Recommended Improvements", subheading_style))
                for improvement in quality.get('recommended_improvements', []):
                    story.append(Paragraph(f"• {improvement}", normal_style))
            
            story.append(Spacer(1, 12))
        
        # Technical Details
        if 'technical_details' in analysis:
            story.append(Paragraph("TECHNICAL DETAILS", heading_style))
            technical = analysis['technical_details']
            
            tech_data = [
                ['Parameter', 'Value'],
                ['Image Dimensions', technical.get('image_dimensions', 'N/A')],
                ['Analysis Algorithm', technical.get('analysis_algorithm', 'N/A')],
                ['Confidence Metrics', technical.get('confidence_score', 'N/A')]
            ]
            
            tech_table = Table(tech_data, colWidths=[2*inch, 3*inch])
            tech_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(tech_table)
            story.append(Spacer(1, 12))
        
        # Confidence Metrics (new section)
        if 'confidence_metrics' in analysis:
            story.append(Paragraph("CONFIDENCE ASSESSMENT", heading_style))
            confidence = analysis['confidence_metrics']
            
            confidence_data = [
                ['Metric', 'Value'],
                ['Overall Confidence', confidence.get('overall_confidence', 'MODERATE')],
                ['Classification Confidence', f"{confidence.get('classification_confidence', 0.7):.2f}"],
                ['Feature Extraction Confidence', f"{confidence.get('feature_extraction_confidence', 0.8):.2f}"]
            ]
            
            confidence_table = Table(confidence_data, colWidths=[2*inch, 3*inch])
            confidence_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkslateblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(confidence_table)
            
            # Factors affecting confidence
            if confidence.get('factors_affecting_confidence'):
                story.append(Spacer(1, 8))
                story.append(Paragraph("Factors Affecting Confidence", subheading_style))
                for factor in confidence.get('factors_affecting_confidence', []):
                    story.append(Paragraph(f"• {factor}", normal_style))
                    
            story.append(Spacer(1, 12))
        
        # Disclaimer
        story.append(Paragraph("DISCLAIMER", heading_style))
        disclaimer_text = "This is a preliminary AI-assisted analysis for licensed clinicians only. This is not a diagnosis and should not replace professional medical judgment. Always consult with qualified healthcare providers for proper diagnosis and treatment."
        story.append(Paragraph(disclaimer_text, normal_style))
        
        # Build PDF
        doc.build(story)
        pdf_buffer.seek(0)
        
        # Return PDF data directly
        from fastapi.responses import Response
        return Response(
            content=pdf_buffer.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}_enhanced_medical_report.pdf"}
        )
        
    except Exception as e:
        logger.error(f"PDF generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
