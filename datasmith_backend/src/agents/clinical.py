from typing import Dict, List
from src.tools.rag_tool import RAGTool
from src.tools.web_search import WebSearchTool
from src.services.llm_service import LLMService
from src.utils.logger import Logger


class ClinicalAgent:
    def __init__(self, rag_tool: RAGTool, web_search_tool: WebSearchTool):
        self.rag_tool = rag_tool
        self.web_search_tool = web_search_tool
        self.llm = LLMService()
        Logger.log_info_message("Clinical Agent initialized")
    
    def handle_medical_query(self, query: str, patient_data: Dict) -> Dict:
        
        Logger.log_info_message(f"Handling medical query for patient: {patient_data['patient_name']}")
        
        
        rag_results = self.rag_tool.search(query)
        
        
        web_keywords = ['latest', 'recent', 'new', 'current', '2024', '2025', 'research']
        needs_web_search = any(keyword in query.lower() for keyword in web_keywords)
        
        web_results = []
        if needs_web_search:
            web_results = self.web_search_tool.search(query)
        
       
        context_parts = []
        
        
        context_parts.append(f"""Patient Information:
- Name: {patient_data['patient_name']}
- Diagnosis: {patient_data['primary_diagnosis']}
- Medications: {', '.join(patient_data['medications'])}
- Dietary Restrictions: {patient_data['dietary_restrictions']}
""")
        
        
        if rag_results:
            context_parts.append("\n**Medical Reference Information:**")
            for i, result in enumerate(rag_results, 1):
                context_parts.append(f"\n[Source {i} - Chunk {result['chunk_index']}]")
                context_parts.append(result['content'][:500])
        
        
        if web_results:
            context_parts.append("\n**Recent Web Information:**")
            for i, result in enumerate(web_results, 1):
                context_parts.append(f"\n[Web Source {i}]")
                context_parts.append(f"Title: {result['title']}")
                context_parts.append(f"Summary: {result['snippet'][:300]}")
        
        full_context = "\n".join(context_parts)
        
        
        system_prompt = f"""You are a clinical medical AI assistant specializing in post-discharge care.

Use the provided context to answer the patient's question accurately and professionally.

IMPORTANT:
- Always cite sources when using information from the reference material or web
- Format citations as [Source: Reference Book, Page X] or [Source: Web]
- Prioritize patient safety - recommend consulting healthcare providers for serious concerns
- Be empathetic and clear in your explanations
- If information is not in the context, say so clearly

{full_context}"""
        
        response_text = self.llm.generate_clinical_response(
            system_prompt,
            f"Patient Question: {query}"
        )
        
     
        response_text += "\n\n**Disclaimer:** This information is for educational purposes only. Always consult your healthcare provider for medical advice specific to your situation."
        
       
        sources = {
            "rag": [f"Chunk {r['chunk_index']}" for r in rag_results] if rag_results else [],
            "web": [{"title": r['title'], "url": r['url']} for r in web_results] if web_results else []
        }
        
        return {
            "response": response_text,
            "sources": sources
        }
    
    def log_interaction(self, query: str, response: str, patient_name: str):
       
        Logger.log_info_message(f"Clinical interaction logged for patient: {patient_name}")