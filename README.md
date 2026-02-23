# 📄 DocuSense AI - Intelligent Document Analysis Platform

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![AI](https://img.shields.io/badge/AI-Powered-brightgreen?style=for-the-badge)

An AI-powered document intelligence platform that helps you extract, analyze, and understand any document using advanced NLP and LLM technology.

## 🌟 Features

### 💬 **Ask Questions (RAG-based Q&A)**
- Ask natural language questions about your documents
- Get accurate answers using Retrieval Augmented Generation
- Powered by vector search and Llama 3.1 LLM

### 🏷️ **Smart Entity Extraction**
- Automatically detect and extract:
  - 👤 Person names
  - 🏢 Organizations
  - 📍 Locations
  - 📅 Dates & times
  - 💰 Monetary values
  - 📧 Emails & 📞 Phone numbers
  - 💡 Skills & competencies
  - 🧾 Invoice numbers
- Context-aware extraction based on document type
- Export entities as CSV

### 📊 **Document Intelligence**
- AI-powered comprehensive analysis
- Key information extraction
- Automatic summarization
- Actionable insights and recommendations

### ⚠️ **Risk Detector**
- Scan contracts and legal documents for risks
- Identify suspicious clauses and unfair terms
- Risk scoring (High/Medium/Low)
- Detailed suggestions for each risk
- Perfect for contracts, agreements, and legal documents

### 🔍 **Auto Document Classification**
- Automatically detects document type:
  - Resume/CV
  - Invoice
  - Contract/Agreement
  - Legal Document
  - Business Letter
  - Research Paper
  - And more...

## 🚀 Live Demo

**Try it here:** [Your Streamlit App URL]

## 📸 Screenshots

### Document Upload & Classification
![Upload](screenshots/upload.png)

### Entity Extraction
![Entities](screenshots/entities.png)

### Risk Detection
![Risk](screenshots/risk.png)

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **Streamlit** | Web interface |
| **Groq API** | LLM (Llama 3.1 8B) |
| **spaCy** | Named Entity Recognition |
| **ChromaDB** | Vector database for RAG |
| **Sentence Transformers** | Document embeddings |
| **Python-docx** | Word document processing |
| **PyPDF2** | PDF processing |

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip package manager
- Groq API key ([Get one here](https://console.groq.com))

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/YOUR-USERNAME/AI-DOC.git
cd AI-DOC
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up API key**

Create a `.streamlit/secrets.toml` file:
```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

Or set as environment variable:
```bash
export GROQ_API_KEY="your_groq_api_key_here"
```

4. **Run the app**
```bash
streamlit run app.py
```

5. **Open in browser**
```
http://localhost:8501
```

## 🌐 Deployment

This app is deployed on **Streamlit Cloud**.

### Deploy Your Own

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repository
5. Add your `GROQ_API_KEY` in Secrets
6. Deploy!

## 📁 Project Structure

```
AI-DOC/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
├── README.md              # This file
├── data/                  # Training datasets
│   ├── bbc/              # BBC news dataset
│   └── ner/              # NER training data
├── models/               # Trained ML models
│   └── doc_classifier.pkl
├── rag/                  # RAG system files
│   ├── ask.py           # RAG query script
│   ├── build_index.py   # Index builder
│   └── chroma_db/       # Vector database storage
├── train_classifier.py  # Train document classifier
├── train_ner.py        # Train NER model
├── test_classifier.py  # Test classifier
└── test_ner.py         # Test NER

```

## 🎯 Supported File Types

- 📄 PDF (.pdf)
- 📝 Word Documents (.docx)
- 📃 Text Files (.txt)

## 🧠 How It Works

### Document Upload
1. User uploads document (PDF/DOCX/TXT)
2. Text is extracted and processed
3. Document is classified using LLM
4. Vector embeddings are created and stored

### Entity Extraction
1. spaCy NER extracts standard entities
2. Regex patterns extract emails, phones, URLs
3. Document-type-specific extraction (skills for resumes, invoice numbers, etc.)
4. LLM-powered skill extraction for resumes
5. Results displayed in interactive table

### Q&A System (RAG)
1. User asks a question
2. Question is converted to embedding
3. Similar document chunks retrieved from vector DB
4. LLM generates answer using retrieved context
5. Answer displayed to user

### Risk Detection
1. Document analyzed by LLM for risky clauses
2. Risks categorized as High/Medium/Low
3. Each risk includes:
   - The problematic clause
   - Why it's risky
   - Suggested action
4. Overall risk score calculated

## 📊 Model Details

### Document Classification
- **Current:** LLM-based (Llama 3.1 via Groq)
- **Alternative:** TF-IDF + Logistic Regression (trained model available)

### Entity Extraction
- **Primary:** spaCy `en_core_web_sm` (v3.7)
- **Enhancement:** Regex patterns + LLM extraction

### RAG System
- **Embeddings:** `all-MiniLM-L6-v2` (Sentence Transformers)
- **Vector DB:** ChromaDB
- **LLM:** Llama 3.1 8B Instant (Groq)

## 🔐 Security & Privacy

- ⚠️ **API Key:** Never commit your API key to Git. Use `.streamlit/secrets.toml` or environment variables
- 🔒 Documents are processed locally and not stored permanently
- 🚫 No user data is collected or shared

## 🐛 Known Limitations

- Vector database resets between sessions (documents need re-upload)
- Maximum file size: 200MB (Streamlit limit)
- LLM rate limits apply (Groq free tier)
- Entity extraction accuracy depends on document quality

## 🚧 Future Enhancements

- [ ] Multi-document comparison
- [ ] Chat history persistence
- [ ] Batch document processing
- [ ] Custom entity types
- [ ] Multi-language support
- [ ] PDF report generation
- [ ] Document templates library

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Your Name**
- GitHub: [@your-username](https://github.com/your-username)
- LinkedIn: [Your Name](https://linkedin.com/in/your-profile)

## 🙏 Acknowledgments

- **Groq** for lightning-fast LLM inference
- **spaCy** for NER capabilities
- **Streamlit** for the amazing framework
- **Anthropic** for Claude (used in development)
- BBC News dataset for classification training

## 📧 Contact

For questions or feedback, please open an issue or reach out via [your-email@example.com](mailto:your-email@example.com)

---

⭐ If you found this project useful, please give it a star!
