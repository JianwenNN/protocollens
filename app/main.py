import streamlit as st
from app.orchestrator import ProtocolOrchestrator
from config import Config
from app.utils.pdf_parser import PDFParser
from app.eligibility_checker import EligibilityChecker, format_eligibility_result
from app.prompts.role_specific_qa import get_role_specific_qa_prompt
from app.prompts.boundary_detection import is_unsupported_question, get_unsupported_message
import json

# Page configuration
st.set_page_config(
    page_title="ProtocolLens - Clinical Trial Protocol Interpreter",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
    }
    .supported-questions {
        background-color: #e7f3ff;
        border-left: 4px solid #2196F3;
        padding: 1rem;
        margin: 1rem 0;
    }
    .unsupported-questions {
        background-color: #fff3cd;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ========== Display Helper Functions ==========

def display_eligibility(result):
    """Display eligibility criteria section"""
    st.markdown("### 📋 Eligibility Criteria")
    
    eligibility = result.get("eligibility", {})
    
    # Inclusion Criteria
    st.markdown("#### ✅ Inclusion Criteria")
    inclusion = eligibility.get("inclusion", {})
    
    if isinstance(inclusion, dict):
        criteria_list = inclusion.get("criteria", [])
        confidence = inclusion.get("confidence", 0.0)
        
        if criteria_list:
            st.caption(f"Found {len(criteria_list)} criteria (confidence: {confidence:.2f})")
            
            for i, criterion in enumerate(criteria_list, 1):
                with st.expander(f"**{criterion.get('id', f'INC_{i:02d}')}**: {criterion.get('text', 'N/A')[:100]}..."):
                    st.markdown(f"**Full Text:** {criterion.get('text', 'N/A')}")
                    st.markdown(f"**Category:** `{criterion.get('category', 'N/A')}`")
                    st.markdown(f"**Operator:** `{criterion.get('operator', 'N/A')}`")
                    st.markdown(f"**Value:** `{criterion.get('value', 'N/A')}`")
                    st.markdown(f"**Confidence:** {criterion.get('confidence', 0.0):.2f}")
                    
                    # Display source evidence
                    source_evidence = criterion.get('source_evidence', [])
                    if source_evidence:
                        st.markdown("---")
                        st.markdown("**📄 Source Evidence:**")
                        for source in source_evidence:
                            with st.container():
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.caption(f"📍 Section: {source.get('section', 'N/A')}")
                                with col2:
                                    if source.get('page'):
                                        st.caption(f"📄 Page {source.get('page')}")
                                st.info(f'"{source.get("quote", "N/A")}"')
        else:
            st.info("No inclusion criteria found")
    else:
        st.info("Inclusion criteria data not available")
    
    st.markdown("---")
    
    # Exclusion Criteria
    st.markdown("#### ❌ Exclusion Criteria")
    exclusion = eligibility.get("exclusion", {})
    
    if isinstance(exclusion, dict):
        criteria_list = exclusion.get("criteria", [])
        confidence = exclusion.get("confidence", 0.0)
        
        if criteria_list:
            st.caption(f"Found {len(criteria_list)} criteria (confidence: {confidence:.2f})")
            
            for i, criterion in enumerate(criteria_list, 1):
                with st.expander(f"**{criterion.get('id', f'EXC_{i:02d}')}**: {criterion.get('text', 'N/A')[:100]}..."):
                    st.markdown(f"**Full Text:** {criterion.get('text', 'N/A')}")
                    st.markdown(f"**Category:** `{criterion.get('category', 'N/A')}`")
                    st.markdown(f"**Operator:** `{criterion.get('operator', 'N/A')}`")
                    st.markdown(f"**Value:** `{criterion.get('value', 'N/A')}`")
                    st.markdown(f"**Confidence:** {criterion.get('confidence', 0.0):.2f}")
                    
                    # Display source evidence
                    source_evidence = criterion.get('source_evidence', [])
                    if source_evidence:
                        st.markdown("---")
                        st.markdown("**📄 Source Evidence:**")
                        for source in source_evidence:
                            with st.container():
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.caption(f"📍 Section: {source.get('section', 'N/A')}")
                                with col2:
                                    if source.get('page'):
                                        st.caption(f"📄 Page {source.get('page')}")
                                st.info(f'"{source.get("quote", "N/A")}"')
        else:
            st.info("No exclusion criteria found")
    else:
        st.info("Exclusion criteria data not available")


def display_study_design(result):
    """Display study design section"""
    st.markdown("### 🎯 Study Design")
    
    metadata = result.get("trial_metadata", {})
    design = result.get("study_design", {})
    population = result.get("population", {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Trial Metadata")
        st.markdown(f"**Title:** {metadata.get('title', 'Not specified')}")
        st.markdown(f"**Phase:** {metadata.get('phase', 'Not specified')}")
        st.markdown(f"**Status:** {metadata.get('status', 'Not specified')}")
        
        st.markdown("#### Design Characteristics")
        st.markdown(f"**Type:** {design.get('type', 'Not specified')}")
        st.markdown(f"**Randomization:** {design.get('randomization', 'Not specified')}")
        st.markdown(f"**Blinding:** {design.get('blinding', 'Not specified')}")
        st.markdown(f"**Control:** {design.get('control', 'Not specified')}")
    
    with col2:
        st.markdown("#### Target Population")
        st.markdown(f"**Indication:** {population.get('indication', 'Not specified')}")
        st.markdown(f"**Disease Stage:** {population.get('disease_stage', 'Not specified')}")
        st.markdown(f"**Age Range:** {population.get('age_range', 'Not specified')}")
        
        biomarkers = population.get('biomarkers', [])
        if biomarkers:
            st.markdown("**Biomarkers:**")
            for bm in biomarkers:
                st.markdown(f"- {bm}")
        else:
            st.markdown("**Biomarkers:** None specified")


def display_interventions(result):
    """Display interventions section"""
    st.markdown("### 💊 Interventions")
    
    interventions = result.get("interventions", [])
    
    if interventions:
        for i, intervention in enumerate(interventions, 1):
            with st.expander(f"**Arm {i}:** {intervention.get('arm_name', 'Unnamed Arm')}"):
                st.markdown(f"**Treatment:** {intervention.get('treatment', 'Not specified')}")
                st.markdown(f"**Dose:** {intervention.get('dose', 'Not specified')}")
                st.markdown(f"**Route:** {intervention.get('route', 'Not specified')}")
                st.markdown(f"**Schedule:** {intervention.get('schedule', 'Not specified')}")
    else:
        st.info("No intervention information found")


def display_endpoints(result):
    """Display endpoints section"""
    st.markdown("### 📍 Study Endpoints")
    
    endpoints = result.get("endpoints", {})
    
    # Primary Endpoints
    st.markdown("#### 🎯 Primary Endpoints")
    primary = endpoints.get("primary", [])
    if primary:
        for i, ep in enumerate(primary, 1):
            st.markdown(f"{i}. {ep}")
    else:
        st.info("No primary endpoints specified")
    
    # Secondary Endpoints
    st.markdown("#### 📊 Secondary Endpoints")
    secondary = endpoints.get("secondary", [])
    if secondary:
        for i, ep in enumerate(secondary, 1):
            st.markdown(f"{i}. {ep}")
    else:
        st.info("No secondary endpoints specified")
    
    # Exploratory Endpoints
    exploratory = endpoints.get("exploratory", [])
    if exploratory:
        st.markdown("#### 🔬 Exploratory Endpoints")
        for i, ep in enumerate(exploratory, 1):
            st.markdown(f"{i}. {ep}")


def display_timeline(result):
    """Display study timeline section"""
    st.markdown("### 📅 Study Timeline")
    
    timeline = result.get("study_timeline", {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Treatment Duration:**")
        st.info(timeline.get("treatment_duration", "Not specified"))
    
    with col2:
        st.markdown("**Follow-up Duration:**")
        st.info(timeline.get("follow_up_duration", "Not specified"))
    
    visit_schedule = timeline.get("visit_schedule", [])
    if visit_schedule:
        st.markdown("**Visit Schedule:**")
        for i, visit in enumerate(visit_schedule, 1):
            st.markdown(f"{i}. {visit}")
    else:
        st.info("No visit schedule specified")

# ========== END OF HELPER FUNCTIONS ==========

# Initialize session state
if 'trial_result' not in st.session_state:
    st.session_state.trial_result = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = "researcher"  # Default to researcher
if 'patient_profile' not in st.session_state:
    st.session_state.patient_profile = {}

# Header
st.markdown('<div class="main-header">🔬 ProtocolLens</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Clinical Trial Protocol Interpretation Tool</div>', unsafe_allow_html=True)

# Product positioning
with st.expander("ℹ️ What ProtocolLens Does (and Doesn't Do)", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="supported-questions">
        <h4>✅ What ProtocolLens DOES</h4>
        <ul>
        <li>Extract structured information from protocols</li>
        <li>Parse eligibility criteria into atomic rules</li>
        <li>Map patient info to protocol requirements</li>
        <li>Identify missing information</li>
        <li>Answer protocol-based questions</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="unsupported-questions">
        <h4>🚫 What ProtocolLens DOES NOT Do</h4>
        <ul>
        <li>Determine patient eligibility (investigator's role)</li>
        <li>Provide medical advice</li>
        <li>Replace physician judgment</li>
        <li>Infer missing clinical information</li>
        <li>Make treatment recommendations</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.info("**Design Philosophy:** ProtocolLens helps users *read the protocol correctly*, not make clinical decisions.")

# Check API key
if not Config.GEMINI_API_KEY:
    st.error("⚠️ **GEMINI_API_KEY not found**")
    st.info("Please create a `.env` file in the project root with:\n```\nGEMINI_API_KEY=your_api_key_here\n```")
    st.stop()

# Initialize components
@st.cache_resource
def get_orchestrator():
    return ProtocolOrchestrator()

@st.cache_resource
def get_eligibility_checker():
    return EligibilityChecker(model=Config.FLASH_MODEL)

try:
    orchestrator = get_orchestrator()
    eligibility_checker = get_eligibility_checker()
except Exception as e:
    st.error(f"❌ Failed to initialize: {str(e)}")
    st.stop()

# Sidebar with role selection
with st.sidebar:
    st.markdown("### 👤 Your Role")
    
    user_role = st.selectbox(
        "I am using this as a:",
        ["researcher", "physician", "patient"],
        format_func=lambda x: {
            "researcher": "🔬 Clinical Researcher",
            "physician": "⚕️ Physician / Coordinator",
            "patient": "👤 Patient / Advocate"
        }[x],
        index=["researcher", "physician", "patient"].index(st.session_state.user_role),
        key="role_selector",
        help="Your role determines the language and context of responses"
    )
    st.session_state.user_role = user_role
    
    st.markdown("---")
    
    # Role-specific guidance
    if user_role == "researcher":
        st.markdown("### 📊 Research Focus")
        st.caption("""
        **You can ask:**
        - Protocol design questions
        - Criteria logic analysis
        - Comparative assessments
        - Protocol ambiguities
        """)
    
    elif user_role == "physician":
        st.markdown("### 🏥 Clinical Focus")
        st.caption("""
        **You can ask:**
        - Specific eligibility criteria
        - Required assessments
        - Protocol-specified procedures
        - Washout requirements
        """)
    
    else:  # patient
        st.markdown("### 💡 Patient Focus")
        st.caption("""
        **You can ask:**
        - Basic eligibility requirements
        - What tests are needed
        - Study procedures
        - Time commitments
        """)
    
    st.markdown("---")
    
    # Optional patient profile for eligibility checking
    if user_role in ["patient", "physician"]:
        st.markdown("### 📋 Patient Information (Optional)")
        st.caption("For eligibility screening only")
        
        age = st.number_input("Age", min_value=0, max_value=120, value=0, key="profile_age")
        sex = st.selectbox("Sex", ["", "Male", "Female"], key="profile_sex")
        diagnosis = st.text_input("Diagnosis", key="profile_diagnosis")
        
        st.session_state.patient_profile = {
            "Age": age if age > 0 else "",
            "Sex": sex,
            "Diagnosis": diagnosis
        }
    
    st.markdown("---")
    
    st.markdown("### ℹ️ About")
    st.markdown("""
    **ProtocolLens** is a protocol interpretation tool, not a clinical decision system.
    
    Built with Google Gemini 3 API.
    """)

# ========== Protocol Input Section ==========
st.markdown("### 📄 Protocol Input")

# Initialize uploaded_file in session state
if 'uploaded_pdf' not in st.session_state:
    st.session_state.uploaded_pdf = None

# PDF Upload (Primary method - recommended!)
uploaded_file = st.file_uploader(
    "📎 Upload Protocol PDF",
    type=['pdf'],
    help="Upload a clinical trial protocol in PDF format. Gemini will read it directly for better accuracy."
)

# Store uploaded file in session state
if uploaded_file is not None:
    st.session_state.uploaded_pdf = uploaded_file
    st.success(f"✅ PDF uploaded: {uploaded_file.name}")
    
    # Show file info
    file_size_mb = uploaded_file.size / (1024 * 1024)
    st.caption(f"📊 File size: {file_size_mb:.2f} MB")

# Optional: Text input (fallback method)
with st.expander("📝 Or paste protocol text (legacy method - less accurate)", expanded=False):
    st.warning("⚠️ Text input uses legacy parsing. PDF upload is recommended for better accuracy.")
    protocol_text_input = st.text_area(
        "Paste protocol text:",
        height=150,
        placeholder="Paste full protocol text here...",
        help="This method is less accurate than PDF upload. Results may miss some criteria."
    )

# ========== Analyze Button ==========
st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_button = st.button("🔍 Analyze Protocol", use_container_width=True, type="primary")

if analyze_button:
    # Check what input we have
    has_pdf = st.session_state.uploaded_pdf is not None
    has_text = 'protocol_text_input' in locals() and protocol_text_input and protocol_text_input.strip()
    
    if not has_pdf and not has_text:
        st.warning("⚠️ Please upload a PDF or paste protocol text")
    else:
        with st.spinner("🤖 Analyzing protocol..."):
            try:
                # Prefer PDF method (better accuracy!)
                if has_pdf:
                    st.info("📄 Using Gemini Direct PDF reading (recommended method)")
                    result = orchestrator.run_from_pdf_direct(st.session_state.uploaded_pdf)
                else:
                    st.warning("⚠️ Using text parsing (legacy method - may miss some criteria)")
                    result = orchestrator.run(protocol_text_input, prefer_fallback=False)
                
                st.session_state.trial_result = result
                
                extraction_method = result.get("extraction_method", "unknown")
                
                # Show success message with method info
                if extraction_method == "gemini_pdf_direct":
                    st.markdown(
                        '<div class="success-box">✅ <b>Analysis complete!</b> '
                        '(Method: Gemini Direct PDF - Highest Accuracy)</div>', 
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div class="success-box">✅ <b>Analysis complete!</b> '
                        f'(Method: {extraction_method} - Consider using PDF upload for better accuracy)</div>', 
                        unsafe_allow_html=True
                    )
                
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                with st.expander("🐛 Debug Info"):
                    st.exception(e)
                    st.write("**Tip:** Try uploading the PDF instead of pasting text for better results")

# ========== Display Results ==========

# Display results
if st.session_state.trial_result is not None:
    st.markdown("---")
    st.markdown("## 📊 Protocol Analysis")
    
    result = st.session_state.trial_result
    
    # Collapsible analysis results
    with st.expander("📋 View Detailed Extraction Results", expanded=False):
        st.caption("Expand to see eligibility criteria, study design, interventions, endpoints, and timeline")
        
        tabs = st.tabs([
            "📋 Eligibility", 
            "🎯 Study Design", 
            "💊 Interventions",
            "📍 Endpoints",
            "📅 Timeline",
            "🔬 Full JSON"
        ])
        
        with tabs[0]:
            display_eligibility(result)
        
        with tabs[1]:
            display_study_design(result)
        
        with tabs[2]:
            display_interventions(result)
        
        with tabs[3]:
            display_endpoints(result)
        
        with tabs[4]:
            display_timeline(result)
        
        with tabs[5]:
            st.json(result)
    
    # Patient-Protocol Matching (for patients/physicians)
    if st.session_state.user_role in ["patient", "physician"]:
        has_profile = any(v for v in st.session_state.patient_profile.values() if v)
        
        if has_profile:
            st.markdown("---")
            st.markdown("## ✅ Patient-Protocol Matching")
            
            with st.expander("📋 Provided Information", expanded=False):
                for key, value in st.session_state.patient_profile.items():
                    if value:
                        st.markdown(f"**{key}:** {value}")
            
            if st.button("🔍 Match to Protocol", type="primary", use_container_width=True):
                with st.spinner("Analyzing match..."):
                    try:
                        eligibility_result = eligibility_checker.check_eligibility(
                            trial_data=result,
                            patient_profile=st.session_state.patient_profile,
                            user_role=st.session_state.user_role
                        )
                        
                        formatted_result = format_eligibility_result(
                            eligibility_result,
                            st.session_state.user_role
                        )
                        
                        st.markdown(formatted_result)
                        
                        st.info("⚠️ **Important:** This analysis identifies which protocol criteria can be assessed with the provided information. Final eligibility determination is made by the study investigator.")
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    # Protocol Q&A (role-aware)
    st.markdown("---")
    st.markdown("## ❓ Ask About This Protocol")
    
    # Show supported questions based on role
    with st.expander("💡 What questions can I ask?", expanded=False):
        if st.session_state.user_role == "researcher":
            st.markdown("""
            **✅ Supported Questions:**
            - "Is this inclusion/exclusion too restrictive compared to standard trials?"
            - "Which criteria allow investigator discretion?"
            - "What biomarkers define eligibility?"
            - "Are there any unusual protocol requirements?"
            
            **❌ Unsupported Questions:**
            - "Should patient X be enrolled?" (investigator decision)
            - "What's the expected outcome?" (speculative)
            """)
        
        elif st.session_state.user_role == "physician":
            st.markdown("""
            **✅ Supported Questions:**
            - "What lab values are required at screening?"
            - "Is ECOG 2 allowed?"
            - "What is the washout period for prior therapy?"
            - "Are there exceptions to HBV exclusion?"
            
            **❌ Unsupported Questions:**
            - "Is this patient eligible?" (investigator judgment)
            - "Is this safe for my patient?" (clinical decision)
            """)
        
        else:  # patient
            st.markdown("""
            **✅ Supported Questions:**
            - "What are the basic eligibility requirements?"
            - "What tests will I need?"
            - "How long is the treatment?"
            - "How often are visits?"
            
            **❌ Unsupported Questions:**
            - "Am I eligible?" (requires full medical evaluation)
            - "Should I join this trial?" (personal decision with doctor)
            """)
    
    question = st.text_input(
        "Your question about the protocol:",
        placeholder=f"e.g., {'What are the washout requirements?' if st.session_state.user_role == 'physician' else 'What is the study phase?' if st.session_state.user_role == 'researcher' else 'What tests are needed?'}",
        help="Ask protocol-based questions only. Clinical decisions require professional consultation."
    )
    
    if st.button("Get Answer", use_container_width=True):
        if question:
            # Check for unsupported question patterns (clinical judgment)
            unsupported, reason = is_unsupported_question(question)
            
            if unsupported:
                st.warning("⚠️ **This question requires clinical judgment**")
                st.info(get_unsupported_message(reason))
            else:
                with st.spinner("Analyzing protocol..."):
                    try:
                        # Use role-specific prompt
                        role_prompt = get_role_specific_qa_prompt(
                            question, 
                            result, 
                            st.session_state.user_role
                        )
                        
                        answer = orchestrator.ask_question(result, question)
                        
                        st.markdown("**Answer:**")
                        st.info(answer)
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a question")

# Footer disclaimer
st.markdown("---")
st.caption("""
**Disclaimer:** ProtocolLens is a protocol interpretation tool. It does not provide medical advice, 
determine patient eligibility, or replace professional clinical judgment. All clinical decisions 
should be made by qualified healthcare professionals.
""")
