import streamlit as st
from app.orchestrator import ProtocolOrchestrator
from config import Config
from app.utils.pdf_parser import PDFParser

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

# Sidebar info
with st.sidebar:
    st.markdown("### ℹ️ About")
    st.markdown("""
    ProtocolLens uses Google's Gemini API to automatically extract and analyze 
    key information from clinical trial protocols.
    
    **Current Features:**
    - ✅ Inclusion criteria extraction
    - ✅ Exclusion criteria extraction
    - 🚧 Objectives and Endpoints (coming soon)
    """)
    
    st.markdown("### 🔗 Resources")
    st.markdown("[GitHub Repo](https://github.com/yourusername/protocollens)")
    st.markdown("[Gemini 3 Hackathon](https://gemini3.devpost.com/)")

# Main interface
st.markdown("### 📄 Upload or Paste Protocol")
input_method = st.radio(
    "Choose input method:",
    ["Paste Text", "Upload PDF"]
)

protocol_text = ""
if input_method == "Paste Text":
    protocol_text = st.text_area(
        "Paste clinical trial protocol text:",
        height=300,
        placeholder="Paste the protocol content here..."
    )

elif input_method == "Upload PDF":
    uploaded_file = st.file_uploader(
        "Choose a PDF file", 
        type=['pdf'],
        help="Upload a clinical trial protocol PDF"
    )
    if uploaded_file:
        parser = PDFParser()
        try:
            protocol_text = parser.parse_uploaded_file(uploaded_file)
            st.success(f"✅ PDF parsed successfully ({len(protocol_text)} characters)")
        except Exception as e:
            st.error(f"❌ Error parsing PDF: {str(e)}")

# Analyze button
if st.button("🔍 Analyze Protocol"):
    if not protocol_text:
        st.warning("Please provide protocol text or upload a PDF first")
    else:
        with st.spinner("Analyzing protocol..."):
            try:
                result = orchestrator.run(protocol_text)

                st.success("✅ Analysis complete!")

                # Display Inclusion Criteria
                inclusion = result["sections"]["inclusion_criteria"]
                st.markdown("### 📋 Inclusion Criteria")
                if inclusion["text"]:
                    st.markdown(f"**Text:** {inclusion['text']}")
                    st.markdown(f"**Confidence:** {inclusion['confidence']:.2f}")
                    st.markdown(f"**Source Sections:** {', '.join(inclusion['source_sections'])}")
                else:
                    st.info("No inclusion criteria found")

                # Display Exclusion Criteria
                exclusion = result["sections"]["exclusion_criteria"]
                st.markdown("### 📋 Exclusion Criteria")
                if exclusion["text"]:
                    st.markdown(f"**Text:** {exclusion['text']}")
                    st.markdown(f"**Confidence:** {exclusion['confidence']:.2f}")
                    st.markdown(f"**Source Sections:** {', '.join(exclusion['source_sections'])}")
                else:
                    st.info("No exclusion criteria found")

                # Optional: show full sections JSON
                with st.expander("🔧 View Full Sections JSON"):
                    st.json(result["sections"])

            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
