import streamlit as st
from app.orchestrator import ProtocolOrchestrator
from config import Config

st.set_page_config(
    page_title="ProtocolLens",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 ProtocolLens")
st.markdown("*AI-powered Clinical Trial Protocol Analyzer*")

# Check API key
if not Config.GEMINI_API_KEY:
    st.error("⚠️ Please set GEMINI_API_KEY in your .env file")
    st.stop()

# Initialize orchestrator
@st.cache_resource
def get_orchestrator():
    return ProtocolOrchestrator()

orchestrator = get_orchestrator()

# Main interface
st.markdown("### 📄 Upload or Paste Protocol")

input_method = st.radio(
    "Choose input method:",
    ["Paste Text", "Upload PDF (Coming Soon)"]
)

if input_method == "Paste Text":
    protocol_text = st.text_area(
        "Paste clinical trial protocol text:",
        height=300,
        placeholder="Paste the protocol content here..."
    )
    
    if st.button("🔍 Analyze Protocol", type="primary"):
        if not protocol_text:
            st.warning("Please paste protocol text first")
        else:
            with st.spinner("Analyzing protocol..."):
                try:
                    # Extract inclusion criteria
                    result = orchestrator.extract_inclusion_criteria(protocol_text)
                    
                    st.success("✅ Analysis complete!")
                    
                    # Display results
                    st.markdown("### 📋 Inclusion Criteria")
                    
                    if result['criteria']:
                        for i, criterion in enumerate(result['criteria'], 1):
                            confidence = criterion.get('confidence', 0)
                            
                            # Color coding by confidence
                            if confidence > 0.8:
                                emoji = "🟢"
                            elif confidence > 0.5:
                                emoji = "🟡"
                            else:
                                emoji = "🔴"
                            
                            st.markdown(f"{emoji} **{i}.** {criterion['text']}")
                            st.caption(f"Confidence: {confidence:.2f}")
                    else:
                        st.info("No inclusion criteria found")
                    
                    # Show raw JSON in expander
                    with st.expander("🔧 View Raw JSON"):
                        st.json(result)
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# Sidebar info
with st.sidebar:
    st.markdown("### ℹ️ About")
    st.markdown("""
    ProtocolLens uses Google's Gemini API to automatically extract and analyze 
    key information from clinical trial protocols.
    
    **Current Features:**
    - ✅ Inclusion criteria extraction
    - 🚧 Exclusion criteria (coming soon)
    - 🚧 Patient matching (coming soon)
    """)
    
    st.markdown("### 🔗 Resources")
    st.markdown("[GitHub Repo](https://github.com/yourusername/protocollens)")
    st.markdown("[Gemini 3 Hackathon](https://gemini3.devpost.com/)")