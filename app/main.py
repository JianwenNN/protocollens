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

    st.markdown("### 📄 Upload Protocol")

uploaded_file = st.file_uploader(
    "Choose a PDF file", 
    type=['pdf'],
    help="Upload a clinical trial protocol PDF"
)

if uploaded_file is not None:
    with st.spinner("📖 Parsing PDF..."):
        try:
            # Parse PDF
            parser = PDFParser()
            protocol_text = parser.parse_uploaded_file(uploaded_file)
            
            # Show metadata
            metadata = parser.get_metadata_summary()
            
            with st.expander("📊 PDF Information"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Pages", metadata['page_count'])
                    st.metric("Words", parser.estimate_word_count())
                with col2:
                    if metadata['title'] != 'Unknown':
                        st.write(f"**Title:** {metadata['title']}")
                    if metadata['author'] != 'Unknown':
                        st.write(f"**Author:** {metadata['author']}")
            
            # Clean text
            clean_text = parser.clean_text(protocol_text)
            
            # Show preview
            with st.expander("📝 Text Preview"):
                st.text_area(
                    "Extracted Text (first 2000 characters)",
                    clean_text[:2000] + "...",
                    height=200
                )
            
            # Analyze button
            if st.button("🔍 Analyze Protocol", type="primary"):
                with st.spinner("Analyzing..."):
                    # Use orchestrator
                    orchestrator = ProtocolOrchestrator()
                    result = orchestrator.extract_inclusion(clean_text)
                    
                    # Display results
                    st.success("✅ Analysis complete!")
                    # ... rest of your display code ...
                    
        except Exception as e:
            st.error(f"❌ Error parsing PDF: {str(e)}")