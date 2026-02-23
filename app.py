import streamlit as st
import os
import spacy
import pandas as pd
from groq import Groq
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import re

try:
    import PyPDF2
    PDF_AVAILABLE = True
except:
    PDF_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except:
    DOCX_AVAILABLE = False

# ------------------------
# CONFIG
# ------------------------
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        st.error("⚠️ GROQ_API_KEY not found! Please add it in Streamlit secrets.")
        st.stop()
        
client = Groq(api_key=GROQ_API_KEY)
nlp = spacy.load("en_core_web_sm")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

chroma_client = chromadb.Client(Settings(persist_directory="vectordb", anonymized_telemetry=False))
collection = chroma_client.get_or_create_collection(name="docs")

# ------------------------
# MINIMAL PRO CSS
# ------------------------
MINIMAL_PRO_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Inter', sans-serif !important;
}

/* Hide Streamlit default elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Main background */
.stApp {
    background: #f8fafc;
}

/* Main header */
.main-header {
    text-align: center;
    padding: 2.5rem 0 1rem 0;
}
.main-header h1 {
    font-size: 2.4rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.5px;
    margin-bottom: 0.3rem;
}
.main-header p {
    font-size: 1rem;
    color: #64748b;
    font-weight: 400;
}

/* Upload area */
.upload-section {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
    margin-bottom: 1.5rem;
    border: 1px solid #e2e8f0;
}

/* Cards */
.card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
    border: 1px solid #e2e8f0;
    margin-bottom: 1rem;
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}
.card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1), 0 8px 32px rgba(0,0,0,0.06);
    transform: translateY(-1px);
}

/* Metric cards */
.metric-card {
    background: white;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    border: 1px solid #e2e8f0;
    text-align: center;
    transition: all 0.2s ease;
}
.metric-card:hover {
    border-color: #6366f1;
    box-shadow: 0 4px 12px rgba(99,102,241,0.1);
}
.metric-card .metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #0f172a;
    line-height: 1;
}
.metric-card .metric-label {
    font-size: 0.78rem;
    color: #64748b;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 0.3rem;
}
.metric-card .metric-icon {
    font-size: 1.4rem;
    margin-bottom: 0.5rem;
}

/* Doc type badge */
.doc-type-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: white;
    padding: 0.6rem 1.4rem;
    border-radius: 50px;
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: 0.2px;
    box-shadow: 0 4px 12px rgba(99,102,241,0.3);
}

/* Section headers */
.section-header {
    font-size: 1.1rem;
    font-weight: 600;
    color: #0f172a;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #f1f5f9;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Answer card */
.answer-card {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    border-left: 4px solid #0ea5e9;
    margin-top: 1rem;
    color: #0c4a6e;
    font-size: 0.95rem;
    line-height: 1.6;
}

/* Risk cards */
.risk-card-high {
    background: white;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    border-left: 5px solid #ef4444;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 0 0 1px #fee2e2;
    margin-bottom: 0.8rem;
    transition: all 0.2s ease;
}
.risk-card-high:hover {
    box-shadow: 0 4px 12px rgba(239,68,68,0.15), 0 0 0 1px #fecaca;
    transform: translateX(3px);
}
.risk-card-medium {
    background: white;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    border-left: 5px solid #f59e0b;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 0 0 1px #fef3c7;
    margin-bottom: 0.8rem;
    transition: all 0.2s ease;
}
.risk-card-medium:hover {
    box-shadow: 0 4px 12px rgba(245,158,11,0.15), 0 0 0 1px #fde68a;
    transform: translateX(3px);
}
.risk-card-low {
    background: white;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    border-left: 5px solid #22c55e;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 0 0 1px #dcfce7;
    margin-bottom: 0.8rem;
    transition: all 0.2s ease;
}
.risk-card-low:hover {
    box-shadow: 0 4px 12px rgba(34,197,94,0.15), 0 0 0 1px #bbf7d0;
    transform: translateX(3px);
}
.risk-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.4rem;
}
.risk-clause {
    font-size: 0.95rem;
    font-weight: 600;
    color: #0f172a;
    margin-bottom: 0.4rem;
}
.risk-detail {
    font-size: 0.85rem;
    color: #475569;
    line-height: 1.5;
}
.risk-suggestion {
    font-size: 0.85rem;
    color: #0f172a;
    background: #f8fafc;
    padding: 0.5rem 0.8rem;
    border-radius: 6px;
    margin-top: 0.5rem;
    font-weight: 500;
}

/* Progress bar custom */
.progress-container {
    background: #f1f5f9;
    border-radius: 50px;
    height: 12px;
    overflow: hidden;
    margin: 0.5rem 0;
}
.progress-bar-high {
    height: 100%;
    border-radius: 50px;
    background: linear-gradient(90deg, #ef4444, #dc2626);
    transition: width 1s ease;
}
.progress-bar-medium {
    height: 100%;
    border-radius: 50px;
    background: linear-gradient(90deg, #f59e0b, #d97706);
    transition: width 1s ease;
}
.progress-bar-low {
    height: 100%;
    border-radius: 50px;
    background: linear-gradient(90deg, #22c55e, #16a34a);
    transition: width 1s ease;
}

/* Success/info banners */
.success-banner {
    background: linear-gradient(135deg, #f0fdf4, #dcfce7);
    border: 1px solid #86efac;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    color: #166534;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.info-banner {
    background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
    border: 1px solid #7dd3fc;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    color: #075985;
    font-weight: 500;
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    background: white;
    border-radius: 12px;
    padding: 0.3rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    border: 1px solid #e2e8f0;
    gap: 0.2rem;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 0.5rem 1.2rem;
    font-weight: 500;
    font-size: 0.9rem;
    color: #64748b;
    transition: all 0.2s ease;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
}

/* Sidebar */
.css-1d391kg, [data-testid="stSidebar"] {
    background: white !important;
    border-right: 1px solid #e2e8f0 !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.5rem;
    font-weight: 600;
    font-size: 0.9rem;
    transition: all 0.2s ease;
    box-shadow: 0 4px 12px rgba(99,102,241,0.25);
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(99,102,241,0.35);
}

/* Input fields */
.stTextInput > div > div > input {
    border-radius: 10px;
    border: 1.5px solid #e2e8f0;
    padding: 0.7rem 1rem;
    font-size: 0.95rem;
    transition: border-color 0.2s ease;
}
.stTextInput > div > div > input:focus {
    border-color: #6366f1;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.1);
}

/* Dataframe */
.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #e2e8f0;
}

/* Divider */
hr {
    border: none;
    border-top: 1px solid #f1f5f9;
    margin: 1.5rem 0;
}

/* Fade in animation */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(12px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
.fade-in {
    animation: fadeInUp 0.4s ease forwards;
}

/* Spinner */
@keyframes spin {
    to { transform: rotate(360deg); }
}
</style>
"""

# ------------------------
# HELPER FUNCTIONS
# ------------------------
def extract_text(file):
    try:
        if file.name.endswith(".pdf"):
            if not PDF_AVAILABLE:
                st.error("PyPDF2 not installed. Run: pip install PyPDF2")
                return None
            reader = PyPDF2.PdfReader(file)
            return "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
        elif file.name.endswith(".docx"):
            if not DOCX_AVAILABLE:
                st.error("python-docx not installed. Run: pip install python-docx")
                return None
            doc = docx.Document(file)
            return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        else:
            return file.read().decode("utf-8")
    except Exception as e:
        st.error(f"❌ Error extracting text: {e}")
        return None

def split_text(text, chunk_size=500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def build_vector_db(text):
    try:
        collection.delete(where={"source": "doc"})
        chunks = split_text(text)
        embeddings = embedder.encode(chunks)
        for i, chunk in enumerate(chunks):
            collection.add(
                documents=[chunk],
                embeddings=[embeddings[i].tolist()],
                ids=[str(i)],
                metadatas=[{"source": "doc"}]
            )
        return True
    except Exception as e:
        st.error(f"Error building vector DB: {e}")
        return False

def ask_rag(question):
    try:
        q_emb = embedder.encode([question])[0].tolist()
        results = collection.query(query_embeddings=[q_emb], n_results=3)
        context = "\n".join(results["documents"][0])
        prompt = f"""Answer the question using ONLY the information from this document context.
If the answer is not in the context, say "I cannot find this information in the document."

Context:
{context}

Question: {question}
Answer:"""
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=300
        )
        return chat.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

def ask_llm(prompt):
    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        return chat.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

def classify_document_type(text):
    sample_text = text[:1500]
    prompt = f"""Classify this document into ONE of these categories:
- Resume/CV
- Invoice
- Contract/Agreement
- Legal Document
- Business Letter
- Research Paper/Article
- Report
- Medical Record
- Financial Statement
- Receipt
- Transcript
- Application Form
- Other

Return ONLY the category name, nothing else.
Document: {sample_text}
Category:"""
    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=30
        )
        return chat.choices[0].message.content.strip() or "Unknown"
    except:
        return "Unknown"

def get_entity_description(label):
    descriptions = {
        "PERSON": "👤 Person name", "ORG": "🏢 Organization",
        "GPE": "📍 Location", "DATE": "📅 Date",
        "MONEY": "💰 Monetary value", "PERCENT": "📊 Percentage",
        "TIME": "⏰ Time", "CARDINAL": "🔢 Number",
        "EMAIL": "📧 Email", "PHONE": "📞 Phone",
        "URL": "🔗 URL", "SKILL": "💡 Skill",
        "INVOICE_NUMBER": "🧾 Invoice No.", "QUANTITY": "📏 Quantity"
    }
    return descriptions.get(label, label)

def extract_emails(text):
    return list(set(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)))

def extract_phones(text):
    patterns = [r'\b\d{5}\s*\d{5}\b', r'\b\d{10}\b',
                r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
                r'\b\(\d{3}\)\s*\d{3}[-.\s]?\d{4}\b',
                r'\b\+91[-.\s]?\d{10}\b']
    phones = []
    for p in patterns:
        phones.extend(re.findall(p, text))
    return list(set([' '.join(ph.split()) for ph in phones]))

def extract_urls(text):
    return list(set(re.findall(r'https?://[^\s]+|www\.[^\s]+', text)))

def extract_skills_with_llm(text):
    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": f"Extract professional skills from this resume as comma-separated list only:\n{text[:2000]}"}],
            temperature=0.1, max_tokens=200
        )
        return [s.strip() for s in chat.choices[0].message.content.split(',') if s.strip()][:10]
    except:
        return []

def extract_enhanced_entities(text, doc_type):
    doc = nlp(text)
    entities = []
    seen = set()

    for email in extract_emails(text):
        if email not in seen:
            entities.append({"Entity": email, "Type": "EMAIL", "Description": get_entity_description("EMAIL"), "Context": "Contact info"})
            seen.add(email)

    for phone in extract_phones(text):
        if phone not in seen:
            entities.append({"Entity": phone, "Type": "PHONE", "Description": get_entity_description("PHONE"), "Context": "Contact info"})
            seen.add(phone)

    for url in extract_urls(text):
        if url not in seen:
            entities.append({"Entity": url[:50], "Type": "URL", "Description": get_entity_description("URL"), "Context": "Web reference"})
            seen.add(url)

    for ent in doc.ents:
        t = ent.text.strip()
        if not t or t in seen or len(t) <= 1:
            continue
        if ent.label_ == "DATE" and re.match(r'^[\d\s\-\.()]+$', t):
            continue
        etype = ent.label_
        if etype == "GPE" and t.isupper() and len(t) > 3:
            etype = "PERSON"
        if etype == "ORG" and ("resume" in doc_type.lower() or "cv" in doc_type.lower()):
            if any(k in t.lower() for k in ["management", "planning", "service", "operations", "strategic", "excellence"]):
                etype = "SKILL"
        entities.append({"Entity": t, "Type": etype, "Description": get_entity_description(etype),
                        "Context": ent.sent.text[:80] + "..." if len(ent.sent.text) > 80 else ent.sent.text})
        seen.add(t)

    if "resume" in doc_type.lower() or "cv" in doc_type.lower():
        for skill in extract_skills_with_llm(text):
            if skill not in seen:
                entities.append({"Entity": skill, "Type": "SKILL", "Description": get_entity_description("SKILL"), "Context": "Professional skill"})
                seen.add(skill)

    return entities

def detect_risks(text, doc_type):
    prompt = f"""You are a legal risk analyst. Analyze this document and identify risky clauses.

For each risk, return EXACTLY:
RISK_START
Level: High/Medium/Low
Clause: [risky text]
Reason: [why risky]
Suggestion: [what to do]
RISK_END

Document Type: {doc_type}
Document: {text[:3000]}"""
    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2, max_tokens=1000
        )
        return chat.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

def parse_risks(risk_text):
    risks = []
    for block in re.findall(r'RISK_START(.*?)RISK_END', risk_text, re.DOTALL):
        risk = {}
        for field, key in [('Level', 'Level'), ('Clause', 'Clause'), ('Reason', 'Reason'), ('Suggestion', 'Suggestion')]:
            m = re.search(rf'{field}:\s*(.*?)(?:\n|$)', block)
            if m:
                risk[key] = m.group(1).strip()
        if risk:
            risks.append(risk)
    return risks

def get_risk_score(risks):
    if not risks:
        return 0, "Safe ✅", "low"
    score = min(sum({"High": 30, "Medium": 15, "Low": 5}.get(r.get("Level", "Low"), 5) for r in risks), 100)
    if score >= 60:
        return score, "High Risk", "high"
    elif score >= 30:
        return score, "Medium Risk", "medium"
    return score, "Low Risk", "low"

# ------------------------
# PAGE SETUP
# ------------------------
st.set_page_config(page_title="DocuSense AI", page_icon="📄", layout="wide")
st.markdown(MINIMAL_PRO_CSS, unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header fade-in">
    <h1>📄 DocuSense AI</h1>
    <p>Intelligent document analysis powered by AI — Extract, Analyze, and Understand any document</p>
</div>
""", unsafe_allow_html=True)

# Session state
for key in ['document_text', 'document_type', 'filename']:
    if key not in st.session_state:
        st.session_state[key] = None

# Upload Section
st.markdown('<div class="upload-section fade-in">', unsafe_allow_html=True)
uploaded = st.file_uploader("📤 Drop your document here — PDF, DOCX, or TXT", type=["pdf", "docx", "txt"])
st.markdown('</div>', unsafe_allow_html=True)

if uploaded:
    if st.session_state.filename != uploaded.name:
        with st.spinner("⚡ Processing your document..."):
            document_text = extract_text(uploaded)
            if document_text:
                st.session_state.document_text = document_text
                st.session_state.filename = uploaded.name
                if build_vector_db(document_text):
                    st.session_state.document_type = classify_document_type(document_text)
                    st.markdown(f"""
                    <div class="success-banner fade-in">
                        ✅ Document processed successfully! &nbsp;|&nbsp; 
                        Detected as: <strong>{st.session_state.document_type}</strong> &nbsp;|&nbsp;
                        {len(document_text.split()):,} words
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("❌ Failed to extract text from document")

st.markdown("<br>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["💬  Ask Questions", "🏷  Entity Extraction", "📊  Document Intelligence", "⚠️  Risk Detector"])

# ─────────────────────────────────────────────
# TAB 1 — ASK QUESTIONS
# ─────────────────────────────────────────────
with tab1:
    if st.session_state.document_text:
        st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">💬 Ask anything about your document</div>', unsafe_allow_html=True)
        q = st.text_input("", placeholder="e.g. What are the payment terms? Who are the parties involved?", label_visibility="collapsed")

        if q:
            with st.spinner("Thinking..."):
                ans = ask_rag(q)
            st.markdown(f'<div class="answer-card fade-in">💡 <strong>Answer:</strong><br><br>{ans}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Example questions card
        if st.session_state.document_type:
            st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
            st.markdown('<div class="section-header">💭 Example Questions</div>', unsafe_allow_html=True)
            if "resume" in st.session_state.document_type.lower():
                cols = st.columns(3)
                for i, q_ex in enumerate(["What are the key skills?", "What is the work experience?", "What education does the candidate have?"]):
                    with cols[i]:
                        st.markdown(f'<div class="info-banner">📌 {q_ex}</div>', unsafe_allow_html=True)
            elif "invoice" in st.session_state.document_type.lower():
                cols = st.columns(3)
                for i, q_ex in enumerate(["What is the total amount?", "Who is the vendor?", "What is the due date?"]):
                    with cols[i]:
                        st.markdown(f'<div class="info-banner">📌 {q_ex}</div>', unsafe_allow_html=True)
            elif "contract" in st.session_state.document_type.lower():
                cols = st.columns(3)
                for i, q_ex in enumerate(["What are the terms?", "Who are the parties?", "What is the duration?"]):
                    with cols[i]:
                        st.markdown(f'<div class="info-banner">📌 {q_ex}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-banner fade-in">📤 Please upload a document to start asking questions</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TAB 2 — ENTITY EXTRACTION
# ─────────────────────────────────────────────
with tab2:
    if st.session_state.document_text and st.session_state.document_type:

        # Doc type badge
        st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">📋 Document Classification</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center; padding: 0.5rem 0;"><span class="doc-type-badge">📄 {st.session_state.document_type}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Extract entities
        with st.spinner("🔍 Extracting entities..."):
            entities = extract_enhanced_entities(st.session_state.document_text, st.session_state.document_type)

        if entities:
            df = pd.DataFrame(entities)

            # Metric cards
            st.markdown('<div class="fade-in">', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            metrics = [
                ("📊", len(entities), "Total Entities"),
                ("🎯", df["Type"].nunique(), "Entity Types"),
                ("👤", len(df[df["Type"] == "PERSON"]), "People Found"),
                ("🏢", len(df[df["Type"] == "ORG"]), "Organizations"),
            ]
            for col, (icon, val, label) in zip([col1, col2, col3, col4], metrics):
                with col:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-icon">{icon}</div>
                        <div class="metric-value">{val}</div>
                        <div class="metric-label">{label}</div>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Filter + Table
            st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
            st.markdown('<div class="section-header">🏷️ Contains the Following Entities</div>', unsafe_allow_html=True)
            col1, col2 = st.columns([1, 3])
            with col1:
                entity_types = ["All"] + sorted(df["Type"].unique().tolist())
                selected_type = st.selectbox("Filter by type", entity_types)
            filtered_df = df[df["Type"] == selected_type] if selected_type != "All" else df
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)

            csv = df.to_csv(index=False)
            st.download_button("📥 Download CSV", data=csv, file_name=f"entities_{st.session_state.filename}.csv", mime="text/csv")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-banner fade-in">📤 Please upload a document to extract entities</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TAB 3 — DOCUMENT INTELLIGENCE
# ─────────────────────────────────────────────
with tab3:
    if st.session_state.document_text:
        st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">📊 AI Document Analysis</div>', unsafe_allow_html=True)
        st.markdown("Get a comprehensive AI-powered breakdown of your document's content, key insights, and recommendations.")

        if st.button("🚀 Generate Analysis", type="primary"):
            prompt = f"""Analyze this document comprehensively.
Document Type: {st.session_state.document_type}

Provide:
1. **Key Information:** Names, Organizations, Dates, Money, Locations
2. **Summary:** 4-5 clear lines
3. **Key Insights:** 3-4 important observations
4. **Recommendations:** 2-3 action items

Document: {st.session_state.document_text[:3000]}"""

            with st.spinner("🤖 AI is analyzing your document..."):
                result = ask_llm(prompt)

            st.markdown(f'<div class="answer-card fade-in">{result}</div>', unsafe_allow_html=True)
            st.download_button("📥 Download Analysis", data=result, file_name=f"analysis_{st.session_state.filename}.txt", mime="text/plain")

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-banner fade-in">📤 Please upload a document first</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TAB 4 — RISK DETECTOR
# ─────────────────────────────────────────────
with tab4:
    if st.session_state.document_text:
        st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">⚠️ Document Risk Analysis</div>', unsafe_allow_html=True)
        st.markdown("Scan your document for risky clauses, suspicious terms, and legal red flags.")

        if st.button("🔍 Scan for Risks", type="primary"):
            with st.spinner("🔍 Scanning for risks..."):
                raw_risks = detect_risks(st.session_state.document_text, st.session_state.document_type)
                risks = parse_risks(raw_risks)

            if risks:
                score, label, level = get_risk_score(risks)
                high_risks = [r for r in risks if r.get("Level") == "High"]
                med_risks  = [r for r in risks if r.get("Level") == "Medium"]
                low_risks  = [r for r in risks if r.get("Level") == "Low"]

                # Overall score card
                bar_class = f"progress-bar-{level}"
                score_color = {"high": "#ef4444", "medium": "#f59e0b", "low": "#22c55e"}[level]

                st.markdown(f"""
                <div class="card fade-in" style="border-top: 4px solid {score_color};">
                    <div class="section-header">📊 Overall Risk Score</div>
                    <div style="display:flex; align-items:center; gap:1rem; margin-bottom:0.8rem;">
                        <span style="font-size:2.5rem; font-weight:700; color:{score_color};">{score}</span>
                        <span style="font-size:1rem; color:#64748b;">/ 100 &nbsp;—&nbsp; <strong style="color:{score_color};">{label}</strong></span>
                    </div>
                    <div class="progress-container">
                        <div class="{bar_class}" style="width:{score}%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Risk breakdown metrics
                col1, col2, col3, col4 = st.columns(4)
                for col, icon, val, lbl, color in zip(
                    [col1, col2, col3, col4],
                    ["🔍", "🔴", "🟡", "🟢"],
                    [len(risks), len(high_risks), len(med_risks), len(low_risks)],
                    ["Total Issues", "High Risk", "Medium Risk", "Low Risk"],
                    ["#6366f1", "#ef4444", "#f59e0b", "#22c55e"]
                ):
                    with col:
                        st.markdown(f"""
                        <div class="metric-card" style="border-top: 3px solid {color};">
                            <div class="metric-icon">{icon}</div>
                            <div class="metric-value" style="color:{color};">{val}</div>
                            <div class="metric-label">{lbl}</div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Detailed risks
                st.markdown('<div class="section-header">🔍 Detailed Risk Breakdown</div>', unsafe_allow_html=True)

                if high_risks:
                    st.markdown("#### 🔴 High Risk")
                    for r in high_risks:
                        st.markdown(f"""
                        <div class="risk-card-high fade-in">
                            <div class="risk-label" style="color:#ef4444;">⚠ HIGH RISK</div>
                            <div class="risk-clause">{r.get('Clause','N/A')}</div>
                            <div class="risk-detail">❓ <strong>Why:</strong> {r.get('Reason','N/A')}</div>
                            <div class="risk-suggestion">✅ <strong>Suggestion:</strong> {r.get('Suggestion','N/A')}</div>
                        </div>
                        """, unsafe_allow_html=True)

                if med_risks:
                    st.markdown("#### 🟡 Medium Risk")
                    for r in med_risks:
                        st.markdown(f"""
                        <div class="risk-card-medium fade-in">
                            <div class="risk-label" style="color:#f59e0b;">⚠ MEDIUM RISK</div>
                            <div class="risk-clause">{r.get('Clause','N/A')}</div>
                            <div class="risk-detail">❓ <strong>Why:</strong> {r.get('Reason','N/A')}</div>
                            <div class="risk-suggestion">✅ <strong>Suggestion:</strong> {r.get('Suggestion','N/A')}</div>
                        </div>
                        """, unsafe_allow_html=True)

                if low_risks:
                    st.markdown("#### 🟢 Low Risk")
                    for r in low_risks:
                        st.markdown(f"""
                        <div class="risk-card-low fade-in">
                            <div class="risk-label" style="color:#22c55e;">ℹ LOW RISK</div>
                            <div class="risk-clause">{r.get('Clause','N/A')}</div>
                            <div class="risk-detail">❓ <strong>Why:</strong> {r.get('Reason','N/A')}</div>
                            <div class="risk-suggestion">✅ <strong>Suggestion:</strong> {r.get('Suggestion','N/A')}</div>
                        </div>
                        """, unsafe_allow_html=True)

                # Download report
                report = f"RISK REPORT — {st.session_state.filename}\n{'='*50}\n"
                report += f"Score: {score}/100 — {label}\nIssues: {len(risks)}\n\n"
                for i, r in enumerate(risks, 1):
                    report += f"{i}. [{r.get('Level','')}] {r.get('Clause','')}\n   Why: {r.get('Reason','')}\n   Fix: {r.get('Suggestion','')}\n\n"
                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button("📥 Download Risk Report", data=report, file_name=f"risk_{st.session_state.filename}.txt", mime="text/plain")

            else:
                st.markdown('<div class="success-banner fade-in">✅ No major risks detected! This document appears safe.</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-banner fade-in">📤 Please upload a document to scan for risks</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 0.5rem 0;">
        <div style="font-size:2rem;">📄</div>
        <div style="font-size:1.1rem; font-weight:700; color:#0f172a;">DocuSense AI</div>
        <div style="font-size:0.78rem; color:#64748b; margin-top:0.2rem;">Document Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div style="font-size:0.85rem; color:#475569; line-height:2;">
        <div>💬 &nbsp;<strong>Ask Questions</strong> — RAG powered Q&A</div>
        <div>🏷️ &nbsp;<strong>Entity Extraction</strong> — Smart NER</div>
        <div>📊 &nbsp;<strong>Doc Intelligence</strong> — AI analysis</div>
        <div>⚠️ &nbsp;<strong>Risk Detector</strong> — Clause scanner</div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.document_text:
        st.markdown("---")
        st.markdown('<div style="font-size:0.8rem; font-weight:600; color:#0f172a; text-transform:uppercase; letter-spacing:0.5px;">📈 Document Stats</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        stats = [
            ("📁", "File", st.session_state.filename[:20] + "..." if len(st.session_state.filename) > 20 else st.session_state.filename),
            ("🔍", "Type", st.session_state.document_type),
            ("📝", "Words", f"{len(st.session_state.document_text.split()):,}"),
            ("📄", "Est. Pages", str(max(1, len(st.session_state.document_text) // 3000))),
        ]
        for icon, label, value in stats:
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center;
                        padding:0.5rem 0.8rem; background:#f8fafc; border-radius:8px;
                        margin-bottom:0.4rem; border:1px solid #e2e8f0;">
                <span style="font-size:0.82rem; color:#64748b;">{icon} {label}</span>
                <span style="font-size:0.82rem; font-weight:600; color:#0f172a;">{value}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div style="font-size:0.75rem; color:#94a3b8; text-align:center;">Groq LLM · spaCy · ChromaDB · Streamlit</div>', unsafe_allow_html=True)