import streamlit as st
import requests
import uuid
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="Post-Discharge Medical AI Assistant",
    page_icon="🏥",
    layout="wide"
)

# API endpoint - FIXED to match FastAPI routes
API_BASE = "http://localhost:8000/api/v1/chat"

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "patient_data" not in st.session_state:
    st.session_state.patient_data = None
if "conversation_started" not in st.session_state:
    st.session_state.conversation_started = False

# Title and header
st.title("🏥 Post-Discharge Medical AI Assistant")
st.markdown("---")

# Sidebar with information
with st.sidebar:
    st.header("ℹ️ System Information")
    
    st.info("""
    **Disclaimer:**  
    This is an AI assistant for educational purposes only.  
    Always consult healthcare professionals for medical advice.
    """)
    
    st.markdown("### 🤖 Multi-Agent System")
    st.markdown("""
    - **Receptionist Agent**: Handles patient identification and general queries
    - **Clinical AI Agent**: Provides medical information using RAG and web search
    """)
    
    if st.session_state.patient_data:
        st.success("✅ Patient Identified")
        st.markdown(f"**Name:** {st.session_state.patient_data['patient_name']}")
        st.markdown(f"**Diagnosis:** {st.session_state.patient_data['primary_diagnosis']}")
    
    st.markdown("---")
    
    # Reset button
    if st.button("🔄 Start New Conversation"):
        try:
            requests.post(f"{API_BASE}/session/{st.session_state.session_id}/reset")
        except:
            pass
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.patient_data = None
        st.session_state.conversation_started = False
        st.rerun()
    
    # Test patients
    with st.expander("📋 Test Patients"):
        st.markdown("""
        Try these names:
        - John Smith
        - Mary Johnson
        - Robert Williams
        - Patricia Brown
        - Michael Davis
        """)

# Main chat interface
st.markdown("### 💬 Chat Interface")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show patient info if available
        if message.get("patient_data") and message["role"] == "assistant":
            with st.expander("📄 Patient Discharge Information"):
                data = message["patient_data"]
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Discharge Date:** {data['discharge_date']}")
                    st.markdown(f"**Diagnosis:** {data['primary_diagnosis']}")
                    st.markdown(f"**Follow-up:** {data['follow_up']}")
                with col2:
                    st.markdown(f"**Medications:**")
                    for med in data['medications']:
                        st.markdown(f"- {med}")
        
        # Show sources if available
        if message.get("sources"):
            sources = message["sources"]
            if sources.get("rag") or sources.get("web"):
                with st.expander("📚 Sources"):
                    if sources.get("rag"):
                        st.markdown("**Medical Knowledge Base:**")
                        for source in sources["rag"][:2]:
                            st.markdown(f"- {source}")
                    if sources.get("web"):
                        st.markdown("**Web Search Results:**")
                        for result in sources["web"][:2]:
                            st.markdown(f"- [{result['title']}]({result['url']})")

# Start conversation automatically
if not st.session_state.conversation_started:
    try:
        response = requests.post(
            f"{API_BASE}/message",
            json={
                "message": "start",
                "session_id": st.session_state.session_id
            }
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.messages.append({
                "role": "assistant",
                "content": data["response"]
            })
            st.session_state.conversation_started = True
            st.rerun()
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
        st.info(f"Make sure the backend server is running on {API_BASE}")

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response from API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_BASE}/message",
                    json={
                        "message": prompt,
                        "session_id": st.session_state.session_id
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Display response
                    st.markdown(data["response"])
                    
                    # Store patient data if received
                    if data.get("patient_data"):
                        st.session_state.patient_data = data["patient_data"]
                    
                    # Add assistant message to chat
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": data["response"],
                        "agent": data.get("agent"),
                        "patient_data": data.get("patient_data"),
                        "sources": data.get("sources")
                    })
                    
                    # Show patient info if just identified
                    if data.get("patient_data") and data.get("agent") == "receptionist":
                        with st.expander("📄 Patient Discharge Information", expanded=True):
                            pdata = data["patient_data"]
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"**Discharge Date:** {pdata['discharge_date']}")
                                st.markdown(f"**Diagnosis:** {pdata['primary_diagnosis']}")
                                st.markdown(f"**Follow-up:** {pdata['follow_up']}")
                            with col2:
                                st.markdown(f"**Medications:**")
                                for med in pdata['medications']:
                                    st.markdown(f"- {med}")
                    
                    # Show sources if available
                    if data.get("sources"):
                        sources = data["sources"]
                        if sources.get("rag") or sources.get("web"):
                            with st.expander("📚 Sources"):
                                if sources.get("rag"):
                                    st.markdown("**Medical Knowledge Base:**")
                                    for source in sources["rag"][:2]:
                                        st.markdown(f"- {source}")
                                if sources.get("web"):
                                    st.markdown("**Web Search Results:**")
                                    for result in sources["web"][:2]:
                                        st.markdown(f"- [{result['title']}]({result['url']})")
                    
                    st.rerun()
                else:
                    st.error(f"Error: {response.status_code}")
                    st.error(f"Response: {response.text}")
            
            except requests.exceptions.ConnectionError:
                st.error(f"❌ Cannot connect to backend server")
                st.info(f"Make sure the FastAPI server is running on http://localhost:8000")
            except Exception as e:
                st.error(f"Error communicating with backend: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>Post-Discharge Medical AI Assistant POC | Built with FastAPI, LangChain & Streamlit</small>
</div>
""", unsafe_allow_html=True)