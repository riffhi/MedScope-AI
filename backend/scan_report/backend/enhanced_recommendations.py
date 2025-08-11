"""
Enhanced Medical Image Analysis and Recommendations Module
Provides advanced functionality for risk assessment, doctor recommendations, and urgency-based actions
"""

import logging

logger = logging.getLogger(__name__)

class MedicalRecommendationEngine:
    """Engine for generating enhanced medical recommendations and risk assessments"""
    
    def __init__(self):
        # Urgency matrix based on findings and body parts
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
        
        # Risk scoring criteria
        self.RISK_SCORING_CRITERIA = {
            "size_factor": {"large": 25, "medium": 15, "small": 8},
            "location_factor": {"critical": 30, "important": 20, "routine": 10},
            "pattern_factor": {"irregular": 20, "suspicious": 15, "regular": 5},
            "multiplicity_factor": {"multiple": 15, "bilateral": 20, "single": 5}
        }
    
    def generate_doctor_recommendations_enhanced(self, classification, patterns, body_part, condition_scores, risk_assessment):
        """Generate enhanced doctor recommendations with urgency-based actions"""
        recommendations = {
            "risk_based_recommendations": [],
            "medical_recommendations": [],
            "urgency_based_actions": [],
            "patient_management": [],
            "specialist_consultations": [],
            "imaging_recommendations": [],
            "monitoring_recommendations": [],
            "quality_recommendations": [],
            "general_recommendations": []
        }
        
        # Non-diagnostic photograph
        if classification.get('primary_condition') == 'NON_DIAGNOSTIC_PHOTOGRAPH':
            recommendations["risk_based_recommendations"].append(
                "Image appears to be a non-diagnostic photograph; obtain appropriate medical imaging (X-ray/CT/MRI/Ultrasound)"
            )
            recommendations["general_recommendations"].extend([
                "Verify correct modality and acquisition settings",
                "Re-upload a diagnostic-quality scan for analysis"
            ])
            return recommendations

        # Risk-based recommendations with enhanced urgency
        risk_level = classification.get('risk_level', 'MINIMAL')
        urgency = classification.get('urgency', 'ROUTINE')
        risk_score = classification.get('risk_score', 0)
        primary_condition = classification.get('primary_condition', 'NORMAL')
        
        # Enhanced urgency-based actions (new section)
        recommendations["urgency_based_actions"] = self._get_urgency_based_actions(urgency, risk_level, body_part, primary_condition)
        
        # Risk-based recommendations (enhanced)
        if risk_level == "HIGH":
            recommendations["risk_based_recommendations"].extend([
                f"HIGH RISK (Score: {risk_score}/100) - Requires prompt clinical attention",
                "Immediate follow-up consultation required",
                "Urgent specialist referral advised",
                f"Schedule follow-up imaging within {self._get_followup_timeframe(risk_level, body_part)}"
            ])
        elif risk_level == "MODERATE":
            recommendations["risk_based_recommendations"].extend([
                f"MODERATE RISK (Score: {risk_score}/100) - Requires clinical attention",
                "Follow-up consultation recommended",
                "Consider specialist referral",
                f"Repeat imaging in {self._get_followup_timeframe(risk_level, body_part)}"
            ])
        elif risk_level == "LOW":
            recommendations["risk_based_recommendations"].extend([
                f"LOW RISK (Score: {risk_score}/100) - Routine clinical attention",
                "Routine follow-up as per standard protocol",
                "Monitor for any changes in symptoms",
                f"Consider follow-up imaging in {self._get_followup_timeframe(risk_level, body_part)} if clinically indicated"
            ])
        
        # Medical recommendations based on findings (enhanced)
        if patterns.get('potential_masses', 0) > 0:
            mass_count = patterns['potential_masses']
            recommendations["medical_recommendations"].extend([
                f"Evaluate {mass_count} detected {'mass' if mass_count == 1 else 'masses'}/lesion{'s' if mass_count > 1 else ''}",
                "Consider additional imaging modalities if needed",
                "Document size and location of findings"
            ])
        
        if patterns.get('asymmetry_detected'):
            recommendations["medical_recommendations"].extend([
                "Investigate cause of asymmetry",
                "Compare with previous imaging if available",
                "Consider contralateral imaging for comparison"
            ])

        # Patient management recommendations (new section)
        recommendations["patient_management"] = self._get_patient_management_recommendations(
            risk_level, primary_condition, body_part, risk_assessment
        )
        
        # Specialist consultations (new section with enhanced specificity)
        recommendations["specialist_consultations"] = self._get_specialist_recommendations(
            body_part, primary_condition, risk_level, condition_scores
        )
        
        # Imaging recommendations (new section with enhanced specificity)
        recommendations["imaging_recommendations"] = self._get_imaging_recommendations(
            body_part, primary_condition, risk_level, condition_scores
        )
        
        # Monitoring recommendations (new section)
        recommendations["monitoring_recommendations"] = self._get_monitoring_recommendations(
            body_part, primary_condition, risk_level
        )

        # Quality recommendations (enhanced)
        recommendations["quality_recommendations"] = self._get_quality_recommendations(patterns, body_part)
        
        # General recommendations (enhanced)
        recommendations["general_recommendations"].extend([
            "Review complete patient history and correlate with clinical findings",
            "Document all observations in patient record",
            "Consider patient's risk factors and comorbidities",
            "Establish clear follow-up protocol with timeline"
        ])
        
        return recommendations
        
    def _get_urgency_based_actions(self, urgency, risk_level, body_part, condition):
        """Get specific actions based on urgency level"""
        actions = []
        
        urgency_map = {
            "IMMEDIATE": [
                "URGENT: Immediate clinical attention required",
                "Initiate emergency protocols appropriate for findings",
                "Direct communication with referring physician required",
                "Document time-sensitive findings were communicated"
            ],
            "WITHIN_1_HOUR": [
                "VERY URGENT: Clinical attention required within 1 hour",
                "Notify on-call specialist immediately",
                "Prepare for potential emergency intervention",
                "Close monitoring required"
            ],
            "WITHIN_4_HOURS": [
                "URGENT: Clinical attention required within 4 hours",
                "Schedule same-day specialist consultation",
                "Arrange for appropriate urgent imaging if needed",
                "Monitor for clinical deterioration"
            ],
            "WITHIN_24_HOURS": [
                "SEMI-URGENT: Clinical attention required within 24 hours",
                "Next-day follow-up required",
                "Schedule specialist consultation within 24 hours",
                "Provide clear instructions on warning signs requiring immediate return"
            ],
            "WITHIN_1_WEEK": [
                "PRIORITY: Clinical attention required within 1 week",
                "Schedule follow-up appointment within 7 days",
                "Arrange appropriate consultations within available timeframe",
                "Provide detailed patient instructions"
            ],
            "ROUTINE_FOLLOWUP": [
                "ROUTINE: Standard follow-up protocols",
                "Schedule routine follow-up as clinically appropriate",
                "No urgent intervention required based on imaging alone"
            ]
        }
        
        # Get standard urgency actions
        actions.extend(urgency_map.get(urgency, urgency_map["ROUTINE_FOLLOWUP"]))
        
        # Add body part and condition specific urgent actions
        if urgency in ["IMMEDIATE", "WITHIN_1_HOUR", "WITHIN_4_HOURS"]:
            if body_part == "brain":
                if "HEMORRHAGE" in condition:
                    actions.append("Urgent neurosurgical evaluation required")
                    actions.append("Monitor neurological status every 1-2 hours")
                elif "TUMOR" in condition:
                    actions.append("Evaluate for signs of increased intracranial pressure")
            elif body_part == "chest":
                actions.append("Monitor vital signs including oxygen saturation")
                if "PNEUMONIA" in condition:
                    actions.append("Assess need for respiratory support")
            elif body_part == "heart":
                actions.append("Continuous cardiac monitoring advised")
                actions.append("Serial cardiac enzyme assessment if indicated")
                
        return actions

    def _get_followup_timeframe(self, risk_level, body_part):
        """Get appropriate follow-up timeframe"""
        if risk_level == "HIGH":
            if body_part in ["brain", "heart"]:
                return "24-48 hours"
            else:
                return "3-7 days"
        elif risk_level == "MODERATE":
            if body_part in ["brain", "heart"]:
                return "1-2 weeks"
            else:
                return "2-4 weeks"
        else:
            if body_part in ["brain", "heart"]:
                return "4-6 weeks"
            else:
                return "3-6 months"

    def _get_patient_management_recommendations(self, risk_level, condition, body_part, risk_assessment):
        """Get specific patient management recommendations"""
        recommendations = []
        
        # Common recommendations based on risk level
        if risk_level == "HIGH":
            recommendations.extend([
                "Consider admission for observation and management",
                "Develop comprehensive treatment plan with specialist input",
                "Close clinical monitoring with defined parameters"
            ])
        elif risk_level == "MODERATE":
            recommendations.extend([
                "Consider observation versus outpatient management",
                "Ensure prompt follow-up scheduling",
                "Provide clear return precautions"
            ])
        else:
            recommendations.extend([
                "Outpatient management appropriate",
                "Routine follow-up scheduling",
                "Patient education on condition"
            ])
            
        # Condition-specific management
        if "HEMORRHAGE" in condition:
            if body_part == "brain":
                recommendations.extend([
                    "Monitor neurological status closely",
                    "Consider neurosurgical intervention based on clinical status",
                    "Control blood pressure within target parameters",
                    "Avoid anticoagulants and antiplatelet agents"
                ])
        elif "FRACTURE" in condition:
            recommendations.extend([
                "Appropriate immobilization",
                "Pain management",
                "Orthopedic consultation for definitive management",
                "Evaluate need for surgical intervention"
            ])
        elif "TUMOR" in condition:
            recommendations.extend([
                "Complete staging workup",
                "Multidisciplinary tumor board discussion",
                "Biopsy planning if indicated",
                "Assess need for additional studies"
            ])
            
        return recommendations

    def _get_specialist_recommendations(self, body_part, condition, risk_level, condition_scores):
        """Get enhanced specialist consultation recommendations"""
        recommendations = []
        
        # Body part specific specialist recommendations
        body_specialists = {
            "brain": ["Neurology", "Neurosurgery"],
            "heart": ["Cardiology", "Cardiothoracic Surgery"],
            "chest": ["Pulmonology", "Thoracic Surgery"],
            "abdomen": ["Gastroenterology", "General Surgery"],
            "spine": ["Neurosurgery", "Orthopedic Spine Surgery"],
            "extremities": ["Orthopedic Surgery", "Sports Medicine"],
            "breast": ["Breast Surgery", "Oncology"]
        }
        
        # Get appropriate specialists
        specialists = body_specialists.get(body_part, ["Internal Medicine"])
        
        # Add urgency based on risk level
        if risk_level == "HIGH":
            urgency = "urgent (within 24-48 hours)"
        elif risk_level == "MODERATE":
            urgency = "prompt (within 1-2 weeks)"
        else:
            urgency = "routine"
            
        # Create recommendations
        if len(specialists) > 0:
            recommendations.append(f"{specialists[0]} consultation recommended - {urgency}")
            
        # Add condition-specific specialist recommendations
        if "TUMOR" in condition and condition_scores.get("tumor", 0) >= 40:
            if "Oncology" not in specialists:
                recommendations.append("Oncology consultation recommended")
            recommendations.append("Consider multidisciplinary tumor board review")
            
        elif "HEMORRHAGE" in condition and condition_scores.get("hemorrhage", 0) >= 40:
            if body_part == "brain" and "Neurosurgery" not in specialists:
                recommendations.append("Neurosurgical consultation - urgent")
                
        elif "FRACTURE" in condition and condition_scores.get("fracture", 0) >= 40:
            if "Orthopedic" not in " ".join(specialists):
                recommendations.append("Orthopedic consultation recommended")
                
        return recommendations

    def _get_imaging_recommendations(self, body_part, condition, risk_level, condition_scores):
        """Get enhanced imaging recommendations"""
        recommendations = []
        
        # Default follow-up imaging based on body part
        followup_imaging = {
            "brain": "MRI with and without contrast",
            "heart": "Cardiac MRI or CT angiography",
            "chest": "Contrast-enhanced chest CT",
            "abdomen": "Contrast-enhanced abdominal CT",
            "spine": "MRI of the affected region",
            "extremities": "Follow-up radiographs",
            "breast": "Diagnostic mammography and ultrasound"
        }
        
        # Initial recommendation
        recommendations.append(f"Recommended follow-up imaging: {followup_imaging.get(body_part, 'Appropriate imaging')}")
        
        # Condition-specific imaging recommendations
        if "TUMOR" in condition and condition_scores.get("tumor", 0) >= 35:
            if body_part == "brain":
                recommendations.extend([
                    "MRI brain with and without contrast with perfusion",
                    "Consider MR spectroscopy for lesion characterization",
                    "Complete neuro-axis imaging if primary CNS malignancy suspected"
                ])
            elif body_part == "chest":
                recommendations.extend([
                    "Chest CT with contrast",
                    "Consider PET-CT for staging if malignancy suspected",
                    "Guided biopsy planning"
                ])
            elif body_part == "breast":
                recommendations.extend([
                    "Diagnostic mammography with spot compression views",
                    "Targeted ultrasound",
                    "Consider MRI breast with contrast",
                    "Plan for image-guided biopsy"
                ])
                
        elif "HEMORRHAGE" in condition and condition_scores.get("hemorrhage", 0) >= 35:
            if body_part == "brain":
                recommendations.extend([
                    "Non-contrast head CT within 6-24 hours",
                    "Consider CT angiography to evaluate for vascular abnormalities",
                    "MRI brain with SWI sequence for microhemorrhage detection"
                ])
                
        elif "FRACTURE" in condition and condition_scores.get("fracture", 0) >= 35:
            if body_part == "spine":
                recommendations.extend([
                    "CT spine for detailed fracture characterization",
                    "MRI to evaluate for spinal cord or nerve root involvement",
                    "Consider flexion/extension views once stable"
                ])
            elif body_part == "extremities":
                recommendations.extend([
                    "Dedicated radiographs with appropriate views",
                    "Consider CT for complex fracture patterns",
                    "MRI if soft tissue injury suspected"
                ])
                
        return recommendations

    def _get_monitoring_recommendations(self, body_part, condition, risk_level):
        """Get specific monitoring recommendations"""
        recommendations = []
        
        # Base monitoring on risk level
        if risk_level == "HIGH":
            recommendations.append("Frequent monitoring of vital signs and clinical status")
        
        # Body part specific monitoring
        if body_part == "brain":
            recommendations.extend([
                "Regular neurological assessments",
                "Monitor for signs of increased intracranial pressure",
                "Track Glasgow Coma Scale if applicable"
            ])
            if "HEMORRHAGE" in condition:
                recommendations.extend([
                    "Monitor coagulation parameters",
                    "Strict blood pressure management",
                    "Serial neurological examinations every 1-2 hours initially"
                ])
                
        elif body_part == "chest":
            recommendations.extend([
                "Monitor respiratory rate and oxygen saturation",
                "Track work of breathing and use of accessory muscles",
                "Serial chest examinations"
            ])
            
        elif body_part == "heart":
            recommendations.extend([
                "Cardiac monitoring with telemetry if indicated",
                "Regular blood pressure checks",
                "Monitor for signs of heart failure or cardiogenic shock"
            ])
            
        elif body_part == "extremities" and "FRACTURE" in condition:
            recommendations.extend([
                "Neurovascular checks distal to injury",
                "Monitor for compartment syndrome if applicable",
                "Pain assessment and management"
            ])
            
        return recommendations

    def _get_quality_recommendations(self, patterns, body_part):
        """Get enhanced quality recommendations"""
        recommendations = [
            "Ensure proper patient positioning for future scans",
            "Maintain consistent imaging protocols",
            "Verify image quality before analysis"
        ]
        
        # Additional recommendations based on findings
        if patterns.get('photograph_likelihood', 0) > 0.2:
            recommendations.append("Ensure diagnostic-quality medical imaging is used rather than photographs")
            
        if patterns.get('texture_variations') != 'Normal':
            recommendations.append("Consider optimizing acquisition parameters for better tissue contrast")
            
        # Body part specific quality recommendations
        if body_part == "brain":
            recommendations.append("Minimize patient motion with appropriate instructions and immobilization")
            
        elif body_part == "chest":
            recommendations.append("Obtain images at appropriate inspiration for optimal lung visualization")
            
        elif body_part == "breast":
            recommendations.append("Ensure proper compression and positioning for mammographic studies")
            
        return recommendations

    def generate_risk_assessment(self, classification, patterns, body_part, condition_scores, advanced_features):
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
