import streamlit as st
from app.orchestrator import ProtocolOrchestrator
from config import Config
from app.utils.pdf_parser import PDFParser

st.set_page_config(page_title="ProtocolLens", page_icon="🔬", layout="wide")
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

# Input method
input_method = st.radio("Choose input method:", ["Paste Text", "Upload PDF"])

protocol_text = None

if input_method == "Paste Text":
    protocol_text = st.text_area("Paste protocol text:", height=300)
elif input_method == "Upload PDF":
    uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])
    if uploaded_file:
        parser = PDFParser()
        try:
            protocol_text = parser.parse_uploaded_file(uploaded_file)
        except Exception as e:
            st.error(f"❌ Error parsing PDF: {str(e)}")

# Trigger analysis
if protocol_text and st.button("🔍 Analyze Protocol"):
    with st.spinner("Analyzing protocol..."):
        try:
            result = orchestrator.run(protocol_text)

            st.success("✅ Analysis complete!")
            
            # Minimal output
            if result.get("criteria"):
                st.markdown("### 📋 Inclusion Criteria")
                for i, c in enumerate(result["criteria"], 1):
                    st.markdown(f"{i}. {c['text']} (confidence: {c.get('confidence', 0):.2f})")
            
            # Show raw JSON
            with st.expander("🔧 Raw JSON"):
                st.json(result)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
