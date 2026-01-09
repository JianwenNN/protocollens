# protocolLens
> AI-powered Clinical Trial Protocol Analyzer using Gemini API
ProtocolLens is an AI-powered system for structuring and reasoning over clinical trial protocols, designed for downstream use in trial feasibility, patient pre-screening, and operational tooling.

## 🎯 Features

- ✅ **Inclusion Criteria Extraction**: Automatically identifies patient eligibility requirements
- 🚧 **Exclusion Criteria Analysis** (Coming Soon)
- 🚧 **Patient Matching** (Coming Soon)
- 🚧 **Multi-Protocol Comparison** (Coming Soon)

## 🏆 Built For

[Gemini 3 API Developer Competition](https://gemini3.devpost.com/)

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API key ([Get one here](https://aistudio.google.com/))

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/protocollens.git
cd protocollens

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Run the App
```bash
streamlit run app/main.py
```

Open your browser at `http://localhost:8501`

## 🧪 Demo

Try with this sample protocol text:
```
4.1 Inclusion Criteria
Patients must meet ALL of the following criteria:
1. Age ≥ 18 years at the time of informed consent
2. Histologically confirmed non-small cell lung cancer
3. ECOG performance status of 0 or 1
```

## 🏗️ Architecture
```
Protocol PDF/Text
    ↓
Section Segmentation (Gemini Flash)
    ↓
┌────────────────┬─────────────────┐
Inclusion       Exclusion        Endpoints
Extractor       Extractor        Parser
(Flash)         (Flash)          (Flash)
    ↓               ↓                ↓
        Structured JSON
            ↓
    Patient Matching (Gemini Pro)
            ↓
        User Interface
```
## 🤖 Why Gemini 3?

ProtocolLens is designed specifically to leverage Gemini 3's strengths:

- **Long Context Reasoning**: Protocols often exceed 100 pages. Gemini 3 Pro processes entire protocols holistically instead of chunk-based retrieval.
- **Structured Output Control**: Schema-constrained extraction ensures outputs are machine-readable and safe for downstream systems.
- **Model Orchestration**: Flash is used for fast section classification, while Pro is reserved for high-precision reasoning tasks.

This project is not a prompt wrapper, but a multi-stage AI pipeline orchestrated around Gemini 3’s capabilities.

## 🛠️ Tech Stack

- **AI Model**: Google Gemini 1.5 Pro & Flash
- **Backend**: Python
- **Frontend**: Streamlit
- **PDF Processing**: PyPDF2

## 📊 Why ProtocolLens?

Clinical trial protocols are typically 50-200 pages of dense medical text. Reading and understanding them takes hours. ProtocolLens:

- ⚡ **Saves Time**: Extract key info in seconds vs. hours
- 🎯 **Improves Accuracy**: Structured extraction reduces human error
- 🌍 **Increases Access**: Helps patients understand trial eligibility

## 🗺️ Roadmap

- [x] Inclusion criteria extraction
- [ ] Exclusion criteria extraction
- [ ] Endpoint identification
- [ ] Patient matching algorithm
- [ ] Multi-protocol comparison
- [ ] PDF upload support
- [ ] Export to structured formats

## 👨‍💻 Author

Built by Jianwen Xu — Pharmaceutical Industry Professional with domain expertise in clinical trials and a focus on AI-powered systems engineering.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Google Gemini API Team
- Clinical trial research community