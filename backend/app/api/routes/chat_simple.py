from flask import Blueprint, request, jsonify
from datetime import datetime

chat_bp = Blueprint('chat', __name__)

@chat_bp.route("/health", methods=["GET"])
def health():
    """Chat service health check"""
    return jsonify({"status": "Chat service is running"})

@chat_bp.route("/message-anonymous", methods=["POST"])
def send_anonymous_message():
    """Send a message without authentication (for popup chatbot)"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
            
        message_text = data['message']
        
        # Generate AI response
        ai_response = generate_ai_response(message_text)
        
        return jsonify({
            "message": message_text,
            "response": ai_response,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to process message: {str(e)}"}), 500

def generate_ai_response(message: str) -> str:
    """Generate AI response based on user message"""
    message_lower = message.lower()
    
    # Medical imaging responses
    if any(word in message_lower for word in ['mri', 'magnetic resonance', 'scan']):
        return "For MRI analysis, I can help interpret various sequences including T1, T2, FLAIR, and DWI. MRI provides excellent soft tissue contrast and is particularly useful for brain, spine, and joint imaging. What specific MRI findings would you like me to explain?"
    
    elif any(word in message_lower for word in ['ct', 'computed tomography', 'cat scan']):
        return "CT scans provide excellent bone detail and are great for trauma, chest, and abdominal imaging. They're faster than MRI and useful in emergency situations. Would you like me to explain specific CT findings or help interpret a report?"
    
    elif any(word in message_lower for word in ['x-ray', 'radiograph', 'chest x-ray']):
        return "X-rays are the most common imaging study, excellent for bone fractures, chest pathology, and basic screening. They use ionizing radiation but provide quick, cost-effective imaging. What X-ray findings are you interested in discussing?"
    
    elif any(word in message_lower for word in ['ultrasound', 'sonogram', 'echo']):
        return "Ultrasound uses sound waves to create real-time images, making it safe during pregnancy and useful for cardiac, abdominal, and vascular studies. It's operator-dependent but provides dynamic imaging. What ultrasound application interests you?"
    
    # Medical conditions and findings
    elif any(word in message_lower for word in ['brain', 'neurological', 'stroke', 'tumor']):
        return "Brain imaging typically involves MRI for detailed soft tissue evaluation or CT for acute conditions. Common findings include strokes, tumors, hemorrhages, and degenerative changes. I can help interpret neuroimaging findings and explain their clinical significance."
    
    elif any(word in message_lower for word in ['chest', 'lung', 'pneumonia', 'covid']):
        return "Chest imaging often starts with X-rays for basic evaluation, with CT providing more detail for complex cases. Common findings include pneumonia, COVID-19 changes, lung nodules, and cardiac abnormalities. What chest imaging findings would you like me to explain?"
    
    elif any(word in message_lower for word in ['bone', 'fracture', 'orthopedic', 'joint']):
        return "Musculoskeletal imaging includes X-rays for initial evaluation, MRI for soft tissue detail, and CT for complex fractures. I can help explain fracture patterns, joint pathology, and bone lesions. What orthopedic imaging question do you have?"
    
    # Report interpretation
    elif any(word in message_lower for word in ['report', 'interpret', 'findings', 'results']):
        return "I can help interpret medical imaging reports by explaining medical terminology, discussing clinical significance, and putting findings in context. Please share the specific findings you'd like me to explain, and I'll break them down in understandable terms."
    
    elif any(word in message_lower for word in ['normal', 'abnormal', 'pathology']):
        return "When evaluating imaging studies, I assess anatomy, tissue characteristics, symmetry, and enhancement patterns. Normal variants can sometimes appear concerning, while subtle abnormalities might be significant. What specific findings would you like me to help clarify?"
    
    # Contrast and advanced imaging
    elif any(word in message_lower for word in ['contrast', 'gadolinium', 'iodine', 'enhancement']):
        return "Contrast agents help highlight blood vessels, inflammation, and tumors. Gadolinium is used in MRI while iodinated contrast is used in CT. Enhancement patterns provide crucial diagnostic information. Are you asking about contrast safety, indications, or interpretation of enhanced studies?"
    
    # General medical questions
    elif any(word in message_lower for word in ['diagnosis', 'differential', 'treatment']):
        return "Medical imaging is crucial for diagnosis, helping narrow differential diagnoses and guide treatment decisions. Different imaging modalities provide complementary information. I can help explain how imaging findings relate to clinical symptoms and guide next steps."
    
    elif any(word in message_lower for word in ['radiation', 'safety', 'risk']):
        return "Radiation safety is important in medical imaging. X-rays and CT scans use ionizing radiation, while MRI and ultrasound don't. The benefits typically outweigh risks when imaging is medically indicated. Would you like me to explain radiation doses or safety considerations for specific exams?"
    
    # Greetings and general
    elif any(word in message_lower for word in ['hello', 'hi', 'help', 'start']):
        return "Hello! I'm your AI medical imaging assistant. I can help with interpreting medical images, explaining reports, discussing imaging techniques, and answering clinical questions. What specific imaging topic would you like to explore today?"
    
    elif any(word in message_lower for word in ['thank', 'thanks']):
        return "You're welcome! I'm here to help with any medical imaging questions you have. Feel free to ask about specific findings, imaging techniques, or report interpretations anytime."
    
    # Default response
    else:
        return "That's an interesting question! As a medical imaging AI assistant, I can help with MRI, CT, X-ray, and ultrasound interpretation, explain medical reports, discuss imaging techniques, and provide clinical insights. Could you provide more specific details about what you'd like to know?"
