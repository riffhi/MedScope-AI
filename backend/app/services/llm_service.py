"""
LLM Service using Google Gemini API for medical assistance
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

class LLMService:
    def __init__(self):
        """Initialize the LLM service with Gemini API"""
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def is_medical_question(self, message: str) -> bool:
        """Check if the message is related to medical topics"""
        message_lower = message.lower()
        
        # Medical keywords and terms
        medical_keywords = [
            # Imaging terms
            'mri', 'ct', 'x-ray', 'xray', 'ultrasound', 'scan', 'imaging', 'radiograph',
            'mammogram', 'pet scan', 'nuclear medicine', 'fluoroscopy', 'angiogram',
            
            # Body parts and systems
            'brain', 'heart', 'lung', 'liver', 'kidney', 'spine', 'bone', 'joint',
            'chest', 'abdomen', 'pelvis', 'head', 'neck', 'extremity', 'blood vessel',
            
            # Medical conditions
            'cancer', 'tumor', 'pneumonia', 'fracture', 'stroke', 'infection',
            'inflammation', 'disease', 'syndrome', 'disorder', 'lesion', 'mass',
            'nodule', 'cyst', 'fluid', 'swelling', 'pain', 'symptoms',
            
            # Medical terms
            'diagnosis', 'treatment', 'therapy', 'medicine', 'medication', 'surgery',
            'procedure', 'examination', 'test', 'lab', 'blood', 'biopsy',
            'pathology', 'histology', 'radiology', 'oncology', 'cardiology',
            
            # Medical report terms
            'report', 'findings', 'impression', 'recommendation', 'follow-up',
            'contrast', 'enhancement', 'abnormal', 'normal', 'negative', 'positive',
            
            # Common medical phrases
            'medical', 'clinical', 'patient', 'doctor', 'physician', 'hospital',
            'clinic', 'health', 'healthcare', 'medical history', 'family history'
        ]
        
        # Check for medical keywords
        for keyword in medical_keywords:
            if keyword in message_lower:
                return True
        
        # Check for common medical question patterns
        medical_patterns = [
            r'what (is|are|does|do).*(mean|indicate|suggest)',
            r'(interpret|explain|analyze).*(report|result|finding)',
            r'(should i|do i need).*(worry|see|consult)',
            r'(is|are) (this|these).*(normal|abnormal|concerning)',
            r'(what|how).*(treatment|medication|therapy)'
        ]
        
        for pattern in medical_patterns:
            if re.search(pattern, message_lower):
                return True
        
        return False
    
    async def chat_response(self, user_message: str, context: str = "") -> str:
        """Generate a medical AI response using Gemini"""
        try:
            # Check if the question is medical-related
            if not self.is_medical_question(user_message):
                return "I'm a medical AI assistant specialized in medical imaging, radiology, and clinical questions. I can only help with medical-related inquiries such as interpreting medical reports, explaining imaging findings, discussing symptoms, or providing general medical information. Please ask me a medical question."
            
            # Build the medical prompt with context
            medical_prompt = f"""
You are a highly knowledgeable medical AI assistant specializing in medical imaging, radiology, and clinical medicine. Your role is to:

1. Provide accurate, evidence-based medical information
2. Explain medical imaging findings and reports in understandable terms
3. Discuss medical conditions, symptoms, and diagnostic procedures
4. Offer general medical guidance while emphasizing the importance of professional medical consultation
5. Be empathetic and supportive while maintaining clinical accuracy

Important guidelines:
- Always remind users that AI advice doesn't replace professional medical consultation
- Be precise with medical terminology while explaining it in layman's terms
- If discussing serious conditions, encourage seeking immediate medical attention when appropriate
- Focus on education and understanding rather than diagnosis
- Acknowledge limitations and uncertainty when appropriate

{f"Context from previous conversation and reports: {context}" if context else ""}

User question: {user_message}

Please provide a helpful, accurate, and compassionate response focused on medical education and understanding.
"""
            
            # Generate response using Gemini
            response = self.model.generate_content(medical_prompt)
            
            if response and response.text:
                ai_response = response.text.strip()
                
                # Add medical disclaimer if not already present
                if "medical professional" not in ai_response.lower() and "doctor" not in ai_response.lower():
                    ai_response += "\n\n⚠️ **Important**: This information is for educational purposes only and should not replace professional medical advice. Always consult with a qualified healthcare provider for proper diagnosis and treatment."
                
                return ai_response
            else:
                return "I apologize, but I'm having trouble generating a response right now. Please try asking your medical question again, or consult with a healthcare professional for immediate assistance."
                
        except Exception as e:
            print(f"Error generating Gemini response: {str(e)}")
            return "I'm experiencing technical difficulties right now. For medical questions and concerns, I recommend consulting with a qualified healthcare professional who can provide proper guidance based on your specific situation."
