
# 📘  AIResumeRefiner

Smart Resume Enhancement & Scoring with LLMs  
Analyze, improve, and tailor your resume to job descriptions using keyword matching, section scoring, and AI-driven optimization.

---

## 🚀 Features

- ✅ **Resume Parsing** (PDF/DOCX)
- 🧠 **LLM-Powered Optimization** via Perplexity API
- 🔍 **ATS Keyword Matching**
- 🧾 **Structured Section Parsing**
- 📊 **Section Scoring & Feedback**
- 📥 **Download Options:** Final, Optimized, and Score Reports (PDF & DOCX)
- ✏️ **Manual Edits Supported** within the app UI

---

## 🧰 Tech Stack

- **Python 3.9+**
- **Streamlit** – UI framework
- **spaCy** – NLP processing
- **NLTK** – Keyword & token handling
- **PyPDF2 / python-docx** – File I/O
- **ReportLab** – PDF exporting
- **Perplexity AI API** – LLM-based optimization (sonar-pro model)

---

## 🔧 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/AIResumeRefiner.git
cd AIResumeRefiner
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Download NLTK & spaCy Resources
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```
```bash
python -m spacy download en_core_web_sm
```

### 4. Add Your Perplexity API Key
Edit the config or relevant file:
```python
PERPLEXITY_API_KEY = "your-pplx-api-key-here"
```
> 🔐 It's recommended to use environment variables for production.

---

## ▶️ Run the App
```bash
streamlit run app.py
```

---

## 📂 Project Structure

```
AIResumeRefiner/
│
├── app.py                # Streamlit main app
├── backend.py            # backend functions
│
├── requirements.txt
└── README.md
```

---

## 🔌 Perplexity API Use

This app uses the [Perplexity AI](https://www.perplexity.ai/) API (`sonar-pro`) for:

- Resume parsing
- Section scoring
- Resume optimization

You’ll need a valid API key. Free-tier keys may have request limits.

---

## ✅ To-Do / Enhancements
- [ ] Save/load user sessions
- [ ] Highlight changes in optimized resume

---

## 📃 License

MIT License.  
Free to use, adapt, and contribute. Attribution appreciated.

---

## ✨ Credits

Developed using OpenAI GPT and Perplexity LLM APIs.  
Special thanks to contributors and early testers.
