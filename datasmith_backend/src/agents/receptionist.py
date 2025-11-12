from typing import Dict
from src.tools.patient_db import PatientDatabase
from src.services.llm_service import LLMService
from src.utils.logger import Logger


class ReceptionistAgent:
    def __init__(self, patient_db: PatientDatabase):
        self.patient_db = patient_db
        self.llm = LLMService()
        Logger.log_info_message("Receptionist Agent initialized")
    
    def greet_patient(self) -> str:
       
        return """Hello! Welcome to the Post-Discharge Medical Assistant. 

I'm here to help you with any questions about your discharge instructions and recovery.

May I have your full name please?"""
    
    def process_patient_name(self, message: str, session_id: str) -> Dict:
        """Process patient name and retrieve their information"""
        Logger.log_info_message(f"Processing patient name: {message}")
        
        
        patient = self.patient_db.find_patient_by_name(message)
        
        if patient:
            response = f"""Thank you, {patient['patient_name']}! I've found your discharge record.

{self.patient_db.format_patient_info(patient)}

How are you feeling today? Do you have any questions about your discharge instructions or recovery?"""
            
            return {
                "found": True,
                "response": response,
                "patient_data": patient
            }
        else:
            
            system_prompt = """You are a receptionist. Extract the patient name from the message.
If you can extract a name, respond with just the name.
If no name is found, respond with 'NO_NAME_FOUND'."""
            
            extracted = self.llm.generate_receptionist_response(
                system_prompt,
                message
            ).strip()
            
            if extracted != "NO_NAME_FOUND":
                patient = self.patient_db.find_patient_by_name(extracted)
                if patient:
                    response = f"""Thank you, {patient['patient_name']}! I've found your discharge record.

{self.patient_db.format_patient_info(patient)}

How are you feeling today? Do you have any questions about your discharge instructions or recovery?"""
                    
                    return {
                        "found": True,
                        "response": response,
                        "patient_data": patient
                    }
            
            return {
                "found": False,
                "response": """I'm sorry, I couldn't find your record. Could you please provide your full name as it appears on your discharge papers?

Here are some test patients you can try:
- John Smith
- Sarah Johnson
- Michael Chen
- Emily Davis"""
            }
    
    def handle_general_query(self, message: str, session_id: str) -> Dict:
        """Handle general queries and route medical questions to clinical agent"""
        
        
        medical_keywords = [
            'pain', 'medication', 'symptom', 'doctor', 'treatment',
            'side effect', 'dosage', 'kidney', 'blood', 'pressure',
            'swelling', 'diet', 'exercise', 'headache', 'nausea'
        ]
        
        message_lower = message.lower()
        is_medical = any(keyword in message_lower for keyword in medical_keywords)
        
        if is_medical:
            return {
                "route_to_clinical": True,
                "response": "Let me connect you with our clinical specialist who can better answer your medical question..."
            }
        
        
        system_prompt = """You are a friendly receptionist at a medical facility.
Respond warmly and professionally to general queries.
For medical questions, indicate that the patient should speak with a clinical specialist.
Keep responses brief and conversational."""
        
        response = self.llm.generate_receptionist_response(
            system_prompt,
            message
        )
        
        return {
            "route_to_clinical": False,
            "response": response
        }