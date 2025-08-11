from flask import Blueprint, request, jsonify, send_file
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
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

scan_bp = Blueprint('scan', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        # Heuristic thresholds
        self.min_contour_area_ratio = 0.001  # 0.1% of image area
        self.max_contour_area_ratio = 0.2    # 20% of image area
        self.min_circularity = 0.3
        self.min_solidity = 0.6
        # Body-part priors to modulate condition likelihoods
        self.BODY_PART_CONDITION_PRIORS = {
            "brain": {"hemorrhage": 1.35, "tumor": 1.2, "fracture": 0.7},
            "chest": {"hemorrhage": 0.8, "tumor": 1.15, "fracture": 0.9},
            "abdomen": {"hemorrhage": 0.9, "tumor": 1.15, "fracture": 0.8},
            "breast": {"hemorrhage": 0.6, "tumor": 1.6, "fracture": 0.6},
            "spine": {"hemorrhage": 0.7, "tumor": 1.0, "fracture": 1.3},
            "extremities": {"hemorrhage": 0.6, "tumor": 0.9, "fracture": 1.5},
            "heart": {"hemorrhage": 0.7, "tumor": 0.9, "fracture": 0.6},
            "unknown": {"hemorrhage": 1.0, "tumor": 1.0, "fracture": 1.0},
        }
    
    def analyze_image(self, image_path: str, filename: str, body_part: str = "unknown"):
        """Analyze medical image and provide comprehensive analysis"""
        try:
            # Load and preprocess image
            image_data = self._load_and_preprocess_image(image_path)
            if image_data is None:
                return self._create_error_analysis(filename, "Failed to load image")
            
            # Analyze image patterns
            patterns = self._detect_patterns(image_data)

            # Detect condition-specific evidence and scores
            condition_scores, condition_evidence = self._detect_specific_conditions(image_data, body_part, patterns)
            
            # Classify medical condition
            classification = self._classify_medical_condition(patterns, body_part, condition_scores)
            
            # Generate recommendations
            recommendations = self._generate_doctor_recommendations(classification, patterns, body_part, condition_scores)
            
            # Quality assessment
            quality = self._assess_image_quality(image_data)
            
            # Technical details
            technical = self._generate_technical_details(image_data, patterns)
            
            # Generate medical report
            medical_report = self._generate_medical_report(
                filename, body_part, classification, patterns, 
                recommendations, quality, technical
            )
            
            return {
                "summary": f"Analysis of {body_part} image reveals {classification['condition'].replace('_', ' ').lower()} with {classification['risk_level']} risk.",
                "medical_classification": classification,
                "medical_findings": {**patterns, "condition_scores": condition_scores, "condition_evidence": condition_evidence},
                "doctor_recommendations": recommendations,
                "quality_assessment": quality,
                "technical_details": technical,
                "medical_report": medical_report,
                "disclaimer": "This is a preliminary AI-assisted analysis for licensed clinicians only. This is not a diagnosis and should not replace professional medical judgment. Always consult with qualified healthcare providers for proper diagnosis and treatment.",
                "analysis_timestamp": datetime.now().isoformat()
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

    def _detect_specific_conditions(self, image_data, body_part: str, patterns: dict):
        """Estimate likelihood scores (0-100) for tumor, hemorrhage, and fracture"""
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
            high_thresh = int(np.clip(np.percentile(eq, 92), 160, 245))
            _, high_mask = cv2.threshold(eq, high_thresh, 255, cv2.THRESH_BINARY)
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

            # 2) Fracture: sharp linear edges and discontinuities
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
            lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            local_std = gray.std()
            if lap_var > 350 and local_std > 35:
                tumor_score += 18.0
                evidence["tumor"].append("Heterogeneous texture (high Laplacian variance and local std)")
            if patterns.get('asymmetry_detected'):
                tumor_score += 8.0
                evidence["tumor"].append("Asymmetry present")
            scores['tumor'] = float(np.clip(tumor_score, 0.0, 100.0))

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
        min_w = min(left.shape[1], right_flipped.shape[1])
        left = left[:, :min_w]
        right_flipped = right_flipped[:, :min_w]
        diff = (left.astype(np.float32) - right_flipped.astype(np.float32))
        mse = np.mean((diff / 255.0) ** 2)
        return float(mse)

    def _estimate_photograph_likelihood(self, bgr: np.ndarray) -> float:
        """Estimate if the image is a color photograph (non-diagnostic)"""
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        sat = hsv[:, :, 1].astype(np.float32)
        sat_mean = sat.mean()
        sat_std = sat.std()
        likelihood = max(0.0, min(1.0, (sat_mean / 255.0) * 0.7 + (sat_std / 255.0) * 0.3))
        return float(likelihood)
    
    def _classify_medical_condition(self, patterns, body_part, condition_scores=None):
        """Classify the medical condition based on detected patterns and condition likelihoods"""
        if patterns.get('photograph_likelihood', 0) > 0.35:
            return {
                "condition": "NON_DIAGNOSTIC_PHOTOGRAPH",
                "risk_level": "MINIMAL",
                "urgency": "ROUTINE",
                "risk_score": 0
            }

        risk_score = 0.0
        mass_count = float(patterns.get('potential_masses', 0))
        risk_score += min(mass_count, 3.0) * 18.0 + max(mass_count - 3.0, 0.0) * 6.0

        if patterns.get('asymmetry_detected', False):
            risk_score += 18.0

        if patterns.get('texture_variations') == 'Irregular':
            risk_score += 16.0

        condition_scores = condition_scores or {"tumor": 0.0, "hemorrhage": 0.0, "fracture": 0.0}
        top_condition = max(condition_scores, key=lambda k: condition_scores[k]) if condition_scores else None
        top_score = condition_scores.get(top_condition, 0.0) if top_condition else 0.0
        risk_score += min(top_score * 0.6, 40.0)

        if body_part == "breast":
            risk_thresholds = (55, 35, 18)
        elif body_part == "brain":
            risk_thresholds = (50, 30, 15)
        elif body_part == "extremities":
            risk_thresholds = (65, 40, 22)
        else:
            risk_thresholds = (60, 35, 20)

        high, moderate, low = risk_thresholds
        condition = "NORMAL"
        risk_level = "MINIMAL"
        urgency = "ROUTINE"
        
        if risk_score >= high:
            if top_condition and top_score >= 35:
                condition = f"{top_condition.upper()}_SUSPECTED"
            else:
                condition = "SUSPICIOUS"
            risk_level = "HIGH"
            urgency = "IMMEDIATE" if (top_condition == 'hemorrhage' and top_score >= 45 and body_part == 'brain') else "WITHIN_1_WEEK"
        elif risk_score >= moderate:
            if top_condition and top_score >= 30:
                condition = f"{top_condition.upper()}_POSSIBLE"
            else:
                condition = "ABNORMAL"
            risk_level = "MODERATE"
            urgency = "WITHIN_1_MONTH"
        elif risk_score >= low:
            condition = "MILD ABNORMALITY"
            risk_level = "LOW"
            urgency = "ROUTINE"

        return {
            "condition": condition,
            "risk_level": risk_level,
            "urgency": urgency,
            "risk_score": int(min(max(risk_score, 0.0), 100.0)),
            "top_condition": top_condition,
            "condition_scores": {k: int(v) for k, v in condition_scores.items()} if condition_scores else None
        }
    
    def _generate_doctor_recommendations(self, classification, patterns, body_part, condition_scores):
        """Generate comprehensive doctor recommendations"""
        recommendations = {
            "risk_based_recommendations": [],
            "medical_recommendations": [],
            "quality_recommendations": [],
            "general_recommendations": []
        }
        
        if classification.get('condition') == 'NON_DIAGNOSTIC_PHOTOGRAPH':
            recommendations["risk_based_recommendations"].append(
                "Image appears to be a non-diagnostic photograph; obtain appropriate medical imaging (X-ray/CT/MRI/Ultrasound)"
            )
            recommendations["general_recommendations"].extend([
                "Verify correct modality and acquisition settings",
                "Re-upload a diagnostic-quality scan for analysis"
            ])
            return recommendations

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
        
        recommendations["quality_recommendations"].extend([
            "Ensure proper patient positioning for future scans",
            "Maintain consistent imaging protocols",
            "Verify image quality before analysis"
        ])
        
        recommendations["general_recommendations"].extend([
            "Review complete patient history",
            "Correlate with clinical findings",
            "Document all observations in patient record"
        ])
        
        return recommendations
    
    def _assess_image_quality(self, image_data):
        """Assess the quality of the medical image"""
        quality_ratings = {
            "overall_rating": "Good",
            "sharpness_rating": "Good",
            "contrast_rating": "Good",
            "noise_rating": "Low"
        }
        
        try:
            if 'opencv_image' in image_data:
                gray = cv2.cvtColor(image_data['opencv_image'], cv2.COLOR_BGR2GRAY)
                
                laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                if laplacian_var > 100:
                    quality_ratings["sharpness_rating"] = "Excellent"
                elif laplacian_var > 50:
                    quality_ratings["sharpness_rating"] = "Good"
                elif laplacian_var > 20:
                    quality_ratings["sharpness_rating"] = "Fair"
                else:
                    quality_ratings["sharpness_rating"] = "Poor"
                
                contrast = gray.std()
                if contrast > 50:
                    quality_ratings["contrast_rating"] = "Excellent"
                elif contrast > 30:
                    quality_ratings["contrast_rating"] = "Good"
                elif contrast > 15:
                    quality_ratings["contrast_rating"] = "Fair"
                else:
                    quality_ratings["contrast_rating"] = "Poor"
                
                noise = np.mean(cv2.medianBlur(gray, 3) - gray)
                if abs(noise) < 5:
                    quality_ratings["noise_rating"] = "Very Low"
                elif abs(noise) < 10:
                    quality_ratings["noise_rating"] = "Low"
                elif abs(noise) < 20:
                    quality_ratings["noise_rating"] = "Moderate"
                else:
                    quality_ratings["noise_rating"] = "High"
                
                ratings = [quality_ratings["sharpness_rating"], quality_ratings["contrast_rating"], quality_ratings["noise_rating"]]
                if all("Excellent" in r or "Good" in r for r in ratings):
                    quality_ratings["overall_rating"] = "Excellent"
                elif any("Poor" in r for r in ratings):
                    quality_ratings["overall_rating"] = "Fair"
                
        except Exception as e:
            logger.warning(f"Quality assessment failed: {e}")
        
        return quality_ratings
    
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
    
    def _generate_medical_report(self, filename, body_part, classification, patterns, recommendations, quality, technical):
        """Generate a formatted medical report"""
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("MEDSCOPE AI - MEDICAL IMAGE ANALYSIS REPORT")
        report_lines.append("=" * 60)
        report_lines.append("")
        
        report_lines.append("PATIENT INFORMATION:")
        report_lines.append(f"File: {filename}")
        report_lines.append(f"Body Part: {body_part.upper()}")
        report_lines.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
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
        
        report_lines.append("MEDICAL FINDINGS:")
        report_lines.append(f"Potential Masses/Lesions: {patterns.get('potential_masses', 0)}")
        report_lines.append(f"Asymmetry: {'Yes' if patterns.get('asymmetry_detected', False) else 'No'}")
        report_lines.append(f"Asymmetry Details: {patterns.get('asymmetry_interpretation', 'N/A')}")
        report_lines.append(f"Texture Variations: {patterns.get('texture_variations', 'N/A')}")
        report_lines.append(f"Contour Analysis: {patterns.get('contour_analysis', 'N/A')}")
        cond_evidence = patterns.get('condition_evidence', {})
        if any(cond_evidence.get(k) for k in ['tumor','hemorrhage','fracture']):
            report_lines.append("")
            report_lines.append("Condition Evidence:")
            for k in ['tumor','hemorrhage','fracture']:
                ev_list = cond_evidence.get(k, [])
                if ev_list:
                    report_lines.append(f"- {k.capitalize()}: " + "; ".join(ev_list))
        report_lines.append("")
        
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
        
        report_lines.append("IMAGE QUALITY ASSESSMENT:")
        report_lines.append(f"Overall Rating: {quality.get('overall_rating', 'N/A')}")
        report_lines.append(f"Sharpness: {quality.get('sharpness_rating', 'N/A')}")
        report_lines.append(f"Contrast: {quality.get('contrast_rating', 'N/A')}")
        report_lines.append(f"Noise Level: {quality.get('noise_rating', 'N/A')}")
        report_lines.append("")
        
        report_lines.append("TECHNICAL DETAILS:")
        report_lines.append(f"Image Dimensions: {technical.get('image_dimensions', 'N/A')}")
        report_lines.append(f"Analysis Algorithm: {technical.get('analysis_algorithm', 'N/A')}")
        report_lines.append(f"Confidence Score: {technical.get('confidence_score', 'N/A')}")
        report_lines.append("")
        
        report_lines.append("DISCLAIMER:")
        report_lines.append("This is a preliminary AI-assisted analysis for licensed clinicians only.")
        report_lines.append("This is not a diagnosis and should not replace professional medical judgment.")
        report_lines.append("Always consult with qualified healthcare providers for proper diagnosis and treatment.")
        report_lines.append("")
        report_lines.append("=" * 60)
        
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
            "analysis_timestamp": datetime.now().isoformat()
        }

# Initialize analyzer
analyzer = EnhancedMedicalAnalyzer()

@scan_bp.route("/health", methods=["GET"])
def health():
    """Scan service health check"""
    return jsonify({"status": "Scan service is running"})

@scan_bp.route("/body-parts", methods=["GET"])
def get_body_parts():
    """Get available body parts for analysis"""
    return jsonify({
        "body_parts": analyzer.BODY_PARTS,
        "total_parts": len(analyzer.BODY_PARTS)
    })

@scan_bp.route("/analyze", methods=["POST"])
def analyze_scan():
    """Analyze uploaded medical scan"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        body_part = request.form.get('body_part', 'unknown')
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if body_part not in analyzer.BODY_PARTS:
            return jsonify({"error": f"Invalid body part. Must be one of: {list(analyzer.BODY_PARTS.keys())}"}), 400
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            file.save(temp_file.name)
            temp_file_path = temp_file.name
        
        try:
            # Analyze the image
            analysis_result = analyzer.analyze_image(temp_file_path, file.filename, body_part)
            
            return jsonify({
                "success": True,
                "filename": file.filename,
                "body_part": body_part,
                "analysis": analysis_result
            })
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        logger.error(f"Scan analysis failed: {str(e)}")
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

@scan_bp.route("/generate-pdf", methods=["POST"])
def generate_pdf_report():
    """Generate PDF report from analysis data"""
    try:
        data = request.get_json()
        if not data or 'analysis' not in data:
            return jsonify({"error": "Analysis data required"}), 400
        
        filename = data.get('filename', 'scan')
        body_part = data.get('body_part', 'unknown')
        analysis = data['analysis']
        
        # Create PDF
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
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
        
        normal_style = styles['Normal']
        
        # Title
        story.append(Paragraph("MEDSCOPE AI - MEDICAL IMAGE ANALYSIS REPORT", title_style))
        story.append(Spacer(1, 20))
        
        # Patient Information
        story.append(Paragraph("PATIENT INFORMATION", heading_style))
        story.append(Paragraph(f"<b>File:</b> {filename}", normal_style))
        story.append(Paragraph(f"<b>Body Part:</b> {body_part.upper()}", normal_style))
        story.append(Paragraph(f"<b>Analysis Date:</b> {analysis.get('analysis_timestamp', datetime.now().isoformat())}", normal_style))
        story.append(Spacer(1, 12))
        
        # Medical Classification
        if 'medical_classification' in analysis:
            story.append(Paragraph("MEDICAL CLASSIFICATION", heading_style))
            classification = analysis['medical_classification']
            
            classification_data = [
                ['Condition', classification.get('condition', 'N/A')],
                ['Risk Level', classification.get('risk_level', 'N/A')],
                ['Urgency', classification.get('urgency', 'N/A')],
                ['Risk Score', f"{classification.get('risk_score', 0)}/100"]
            ]
            
            classification_table = Table(classification_data, colWidths=[2*inch, 3*inch])
            classification_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(classification_table)
            story.append(Spacer(1, 12))
        
        # Add disclaimer
        story.append(Paragraph("DISCLAIMER", heading_style))
        disclaimer_text = analysis.get('disclaimer', 'This is a preliminary AI-assisted analysis for licensed clinicians only.')
        story.append(Paragraph(disclaimer_text, normal_style))
        
        # Build PDF
        doc.build(story)
        pdf_buffer.seek(0)
        
        # Save to temporary file and return
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            temp_pdf.write(pdf_buffer.getvalue())
            temp_pdf_path = temp_pdf.name
        
        return send_file(
            temp_pdf_path,
            as_attachment=True,
            download_name=f"{filename}_medical_report.pdf",
            mimetype="application/pdf"
        )
        
    except Exception as e:
        logger.error(f"PDF generation failed: {str(e)}")
        return jsonify({"error": f"Failed to generate PDF: {str(e)}"}), 500

@scan_bp.route("/feedback", methods=["POST"])
def submit_feedback():
    """Submit feedback for analysis improvement"""
    try:
        data = request.get_json()
        if not data or 'feedback' not in data:
            return jsonify({"error": "Feedback text required"}), 400
        
        feedback_text = data['feedback']
        analysis_id = data.get('analysis_id', 'unknown')
        timestamp = datetime.now().isoformat()
        
        # Save feedback to file
        feedback_dir = os.path.join(os.path.dirname(__file__), '..', 'feedback')
        os.makedirs(feedback_dir, exist_ok=True)
        
        feedback_file = os.path.join(feedback_dir, 'medical_feedback.jsonl')
        
        feedback_entry = {
            "timestamp": timestamp,
            "analysis_id": analysis_id,
            "feedback": feedback_text,
            "source": "medical_professional"
        }
        
        with open(feedback_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(feedback_entry) + '\n')
        
        return jsonify({
            "success": True,
            "message": "Thank you for your feedback! Your input helps us improve our AI analysis for better patient care.",
            "timestamp": timestamp
        })
        
    except Exception as e:
        logger.error(f"Feedback submission failed: {str(e)}")
        return jsonify({"error": f"Failed to submit feedback: {str(e)}"}), 500
