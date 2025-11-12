from fastapi import APIRouter
from src.schemas import ChatRequest, ChatResponse
from src.utils.logger import Logger
from src.tools.patient_db import PatientDatabase
from src.tools.rag_tool import RAGTool
from src.tools.web_search import WebSearchTool
from src.agents.receptionist import ReceptionistAgent
from src.agents.clinical import ClinicalAgent

router = APIRouter()

#tools init
patient_db = PatientDatabase()
rag_tool = RAGTool()
web_search_tool = WebSearchTool()


#Agent init
receptionist_agent = ReceptionistAgent(patient_db)
clinical_agent = ClinicalAgent(rag_tool, web_search_tool)

#session state management 
session_states = {}

@router.post("/message", response_model=ChatResponse)
async def chat(request: ChatRequest):
    
    Logger.log_info_message(f"Chat received - Session: {request.session_id}, Message: {request.message[:50]}")
    
    session_id = request.session_id
    message = request.message.strip()

    if session_id not in session_states:
        session_states[session_id] = {
            "stage": "greeting",
            "patient_identified": False,
            "patient_data": None,
            "current_agent": "receptionist"
        }

    session = session_states[session_id]

    if message.lower() == "start" and session["stage"] == "greeting":
        greeting = receptionist_agent.greet_patient()
        session["stage"] = "awaiting_name"
        return ChatResponse(response=greeting, agent="receptionist")


    if session["stage"] == "awaiting_name":
        result = receptionist_agent.process_patient_name(message, session_id)
        if result["found"]:
            session.update({
                "patient_identified": True,
                "patient_data": result["patient_data"],
                "stage": "conversation"
            })
        return ChatResponse(
            response=result["response"], 
            agent="receptionist", 
            patient_data=result.get("patient_data")
        )

   
    elif session["stage"] == "conversation":
       
        if session["current_agent"] == "receptionist":
            result = receptionist_agent.handle_general_query(message, session_id)
            
            
            if result["route_to_clinical"]:
                session["current_agent"] = "clinical"
               
                clinical_result = clinical_agent.handle_medical_query(
                    message, 
                    session["patient_data"]
                )
                clinical_agent.log_interaction(
                    message, 
                    clinical_result["response"], 
                    session["patient_data"]["patient_name"]
                )
                return ChatResponse(
                    response=clinical_result["response"],
                    agent="clinical",
                    patient_data=session["patient_data"],
                    sources=clinical_result["sources"]
                )
            
            return ChatResponse(
                response=result["response"], 
                agent="receptionist", 
                patient_data=session["patient_data"]
            )

        
        elif session["current_agent"] == "clinical":
            result = clinical_agent.handle_medical_query(message, session["patient_data"])
            clinical_agent.log_interaction(
                message, 
                result["response"], 
                session["patient_data"]["patient_name"]
            )
            return ChatResponse(
                response=result["response"],
                agent="clinical",
                patient_data=session["patient_data"],
                sources=result["sources"]
            )

    
    return ChatResponse(
        response="Something went wrong. Please try again.", 
        agent="system"
    )

@router.post("/session/{session_id}/reset")
async def reset_session(session_id: str):
    
    if session_id in session_states:
        del session_states[session_id]
        Logger.log_info_message(f"Session reset: {session_id}")
    return {"status": "success", "message": "Session reset successfully"}

@router.get("/session/{session_id}")
async def get_session(session_id: str):
    
    if session_id in session_states:
        return {
            "session_id": session_id,
            "session": session_states[session_id]
        }
    return {"session_id": session_id, "session": None}

@router.get("/greeting")
async def get_greeting():
   
    return {
        "greeting": receptionist_agent.greet_patient()
    }

@router.get("/patients")
async def list_patients():
  
    return {
        "patients": [
            {
                "name": p["patient_name"],
                "diagnosis": p["primary_diagnosis"],
                "discharge_date": p["discharge_date"]
            }
            for p in patient_db.patients
        ]
    }