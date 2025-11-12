from groq import Groq
from typing import List, Dict
from src.utils.logger import Logger
from src.constants.environment_constants import EnvironmentConstants


class LLMService:
    def __init__(self):
        self.client = Groq(api_key=EnvironmentConstants.GROQ_API_KEY.value)
        self.receptionist_model = EnvironmentConstants.RECEPTIONIST_MODEL.value
        self.clinical_model = EnvironmentConstants.CLINICAL_MODEL.value
        Logger.log_info_message(f"LLMService initialized with Groq API")
        Logger.log_info_message(f"Receptionist Model: {self.receptionist_model}")
        Logger.log_info_message(f"Clinical Model: {self.clinical_model}")
    
    def generate_receptionist_response(
        self, 
        system_prompt: str, 
        user_message: str,
        temperature: float = 0.7
    ) -> str:
      
        try:
            response = self.client.chat.completions.create(
                model=self.receptionist_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature,
                max_tokens=500
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            Logger.log_error_message(e, "Error in receptionist LLM generation")
            return "I apologize, I'm having trouble processing your request right now. Please try again."
    
    def generate_clinical_response(
        self, 
        system_prompt: str, 
        user_message: str,
        temperature: float = 0.3
    ) -> str:
       
        try:
            response = self.client.chat.completions.create(
                model=self.clinical_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            Logger.log_error_message(e, "Error in clinical LLM generation")
            return "I apologize, I'm having trouble generating a medical response right now. Please consult your healthcare provider."
    
    def generate_with_context(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        model_type: str = "receptionist",
        temperature: float = 0.7
    ) -> str:
       
        model = self.receptionist_model if model_type == "receptionist" else self.clinical_model
        max_tokens = 500 if model_type == "receptionist" else 1500
        
        try:
            formatted_messages = [{"role": "system", "content": system_prompt}]
            formatted_messages.extend(messages)
            
            response = self.client.chat.completions.create(
                model=model,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            Logger.log_error_message(e, f"Error in {model_type} LLM generation with context")
            return "I apologize, I'm having trouble processing your request."