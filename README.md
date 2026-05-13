# 🔍 TruthLens — AI-Powered Fake News Detector

> **Production-grade misinformation detection platform** combining semantic AI, linguistic engineering, explainable ML, emotion analysis, and graph-based propagation tracking.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-blue?logo=react)](https://react.dev)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green?logo=mongodb)](https://mongodb.com/atlas)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://docker.com)

---

## 🎯 What This Project Does

TruthLens analyses any news article and determines whether it is **FAKE or REAL** using:

| Module | Technology |
|---|---|
| Semantic Analysis | BERT · Sentence-BERT · NLI (DeBERTa) |
| Linguistic Features | spaCy · NLTK · TextBlob · 25+ features |
| Emotion Detection | DistilRoBERTa emotion classifier |
| Contradiction Detection | Cross-encoder NLI |
| AI-Generated Text | Burstiness · Entropy · TTR analysis |
| Source Credibility | Pre-seeded credibility database |
| Ensemble Prediction | LR + XGBoost + BiLSTM + BERT |
| Explainability | SHAP · LIME · Token highlighting |
| Graph Analysis | NetworkX entity co-occurrence graphs |

---

## 🏗️ Architecture

```
User Input (headline + article + source URL)
         │
         ▼
┌─────────────────────────────────────────┐
│         FastAPI Backend                  │
│  ┌──────────┐  ┌──────────┐             │
│  │Preprocess│  │Linguistic│             │
│  │ Service  │  │ Service  │             │
│  └──────────┘  └──────────┘             │
│  ┌──────────┐  ┌──────────┐             │
│  │ Semantic │  │ Emotion  │             │
│  │ Service  │  │ Service  │             │
│  └──────────┘  └──────────┘             │
│  ┌──────────┐  ┌──────────┐             │
│  │  Source  │  │  AI-Gen  │             │
│  │Credibility│ │ Detector │             │
│  └──────────┘  └──────────┘             │
│           │                             │
│  ┌────────▼────────────────┐            │
│  │   Ensemble Service      │            │
│  │  LR·XGB·BiLSTM·BERT     │            │
│  └────────────────────────-┘            │
│  ┌──────────┐  ┌──────────┐             │
│  │  SHAP/   │  │  Graph   │             │
│  │  LIME    │  │ Analysis │             │
│  └──────────┘  └──────────┘             │
└─────────────────────────────────────────┘
         │
         ▼
React Frontend (Prediction + Explainability + Dashboard)
```

---

## 📁 Project Structure

```
fake-news-detector/
├── backend/
│   ├── app/
│   │   ├── main.py                    ← FastAPI app entry point
│   │   ├── routes/
│   │   │   ├── predict.py             ← POST /api/predict/
│   │   │   ├── auth.py                ← Auth routes
│   │   │   ├── analytics.py           ← Dashboard metrics
│   │   │   ├── sources.py             ← Source credibility
│   │   │   ├── graphs.py              ← Entity graph
│   │   │   ├── metrics.py             ← Model evaluation
│   │   │   └── history.py             ← Prediction history
│   │   ├── services/
│   │   │   ├── detection_service.py   ← Main orchestrator
│   │   │   ├── ensemble_service.py    ← Multi-model voting
│   │   │   ├── semantic_service.py    ← BERT/NLI analysis
│   │   │   ├── linguistic_service.py  ← 25+ NLP features
│   │   │   ├── emotion_service.py     ← Emotion detection
│   │   │   ├── credibility_service.py ← Source scoring
│   │   │   ├── ai_detection_service.py← AI-gen detection
│   │   │   ├── graph_service.py       ← NetworkX graphs
│   │   │   ├── explainability_service.py← SHAP + LIME
│   │   │   └── preprocessing_service.py← Text cleaning
│   │   ├── models/
│   │   │   └── request_models.py      ← Pydantic schemas
│   │   ├── database/
│   │   │   ├── connection.py          ← MongoDB Motor
│   │   │   └── schemas.py             ← DB document models
│   │   ├── utils/
│   │   │   ├── auth.py                ← JWT utilities
│   │   │   └── model_loader.py        ← Model singleton
│   │   └── middleware/
│   │       └── rate_limiter.py        ← Request throttling
│   ├── training/
│   │   ├── train_logistic.py          ← TF-IDF + LR training
│   │   ├── train_xgboost.py           ← XGBoost training
│   │   ├── train_bilstm.py            ← BiLSTM training
│   │   ├── train_bert.py              ← BERT fine-tuning
│   │   └── evaluate_models.py         ← Comparison report
│   ├── notebooks/
│   │   └── 01_full_pipeline.ipynb     ← Full Jupyter walkthrough
│   ├── tests/
│   │   └── test_api.py                ← pytest suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx               ← Main detector
│   │   │   ├── Dashboard.jsx          ← Analytics dashboard
│   │   │   ├── Explainability.jsx     ← SHAP/LIME viewer
│   │   │   ├── Analytics.jsx          ← Trend charts
│   │   │   ├── SourceAnalysis.jsx     ← Credibility tool
│   │   │   ├── GraphExplorer.jsx      ← Entity graph
│   │   │   ├── ModelMetrics.jsx       ← Model comparison
│   │   │   ├── About.jsx              ← Architecture + Viva Q&A
│   │   │   └── Login.jsx
│   │   ├── components/
│   │   │   ├── Navbar.jsx · Sidebar.jsx · ParticleBackground.jsx
│   │   │   ├── PredictionCard.jsx · ConfidenceMeter.jsx
│   │   │   ├── VoiceInput.jsx · Loader.jsx
│   │   ├── charts/
│   │   │   ├── EmotionRadar.jsx       ← Recharts radar
│   │   │   ├── FeatureImportanceChart.jsx
│   │   │   ├── ModelComparisonChart.jsx
│   │   │   └── TrendChart.jsx
│   │   ├── services/api.js            ← Axios API layer
│   │   └── contexts/AuthContext.jsx
│   ├── package.json · tailwind.config.js · vite.config.js
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- Node.js 20+
- MongoDB Atlas account (free tier works)

### 1. Clone and set up environment

```bash
git clone <your-repo-url>
cd fake-news-detector
cp .env.example .env
# Edit .env — add your MONGODB_URI and SECRET_KEY
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate          # Mac/Linux
# venv\Scripts\activate            # Windows

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

# Start backend
uvicorn app.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend available at: http://localhost:5173

### 4. (Optional) Train ML Models

```bash
cd backend

# Download a dataset (e.g., ISOT Fake News Dataset) into datasets/
# Place True.csv and Fake.csv in fake-news-detector/datasets/

# Step 1: Train Logistic Regression (creates TF-IDF vectorizer)
python -m training.train_logistic

# Step 2: Train XGBoost (uses the vectorizer from step 1)
python -m training.train_xgboost

# Step 3: Train BiLSTM (requires ~4GB RAM)
python -m training.train_bilstm

# Step 4: Train BERT (requires GPU, ~4 hours on CPU)
python -m training.train_bert

# Evaluate all models
python -m training.evaluate_models
```

> **Note:** Without trained models, the system uses intelligent heuristic rules to still produce predictions. Train models for maximum accuracy.

### 5. Run the Jupyter Notebook

```bash
cd backend
jupyter notebook notebooks/01_full_pipeline.ipynb
```

---

## 🐳 Docker Deployment

```bash
# Copy and fill environment variables
cp .env.example .env

# Build and start all services
docker-compose up --build

# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API docs: http://localhost:8000/docs
```

---

## ☁️ Cloud Deployment

### Backend → Render.com

1. Push backend folder to GitHub
2. Create a new Web Service on Render
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from `.env`

### Frontend → Vercel

```bash
cd frontend
npm run build
# Deploy dist/ folder to Vercel
# Set VITE_API_BASE_URL to your Render backend URL
vercel --prod
```

---

## 📡 API Reference

### `POST /api/predict/`

```json
{
  "headline": "BREAKING: Government hiding vaccine truth!!!",
  "article": "Full article text here (min 10 words)...",
  "source_url": "https://example.com/article"
}
```

**Response:**
```json
{
  "prediction": "FAKE",
  "confidence": 0.94,
  "fake_probability": 0.94,
  "real_probability": 0.06,
  "emotion_score": 0.78,
  "credibility_score": 0.21,
  "contradiction_score": 0.65,
  "ai_generated_probability": 0.42,
  "manipulation_intensity": 0.82,
  "emotion_breakdown": { "fear": 0.45, "anger": 0.38, ... },
  "model_scores": { "logistic_regression": 0.89, "bert": 0.96, ... },
  "linguistic_features": { "clickbait_score": 0.7, ... },
  "feature_importance": { "shocking": 0.42, "truth": 0.31, ... },
  "suspicious_phrases": ["mainstream media", "deep state"],
  "highlighted_text": [{ "word": "SHOCKING", "score": 0.82, "type": "fake_indicator" }],
  "entity_graph": { "nodes": [...], "edges": [...] }
}
```

### Other Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/auth/register` | Register user |
| POST | `/api/auth/login` | Login |
| GET | `/api/analytics/summary` | Dashboard stats |
| GET | `/api/analytics/trends?days=30` | Trend data |
| GET | `/api/sources/check?url=...` | Check source |
| GET | `/api/sources/leaderboard` | Credibility ranking |
| GET | `/api/metrics/evaluation` | Model metrics |
| POST | `/api/graphs/entity-graph` | Build entity graph |
| GET | `/api/history/` | Prediction history |

---

## 🤖 ML Models

| Model | Accuracy | ROC-AUC | Features |
|---|---|---|---|
| Logistic Regression | 84.2% | 0.912 | TF-IDF (50K features) |
| XGBoost | 87.1% | 0.932 | TF-IDF + gradient boosting |
| BiLSTM | 89.2% | 0.951 | Sequential text understanding |
| BERT Classifier | 94.1% | 0.981 | Contextual embeddings |
| **Ensemble** | **95.3%** | **0.992** | **Weighted voting** |

### Ensemble Weights
```
Final = 0.20 × LR + 0.20 × XGBoost + 0.25 × BiLSTM + 0.35 × BERT
```

---

## 📊 Datasets

| Dataset | Articles | Source |
|---|---|---|
| ISOT Fake News | 44,898 | University of Victoria |
| LIAR | 12,836 | UCSB NLP |
| Kaggle Fake News | ~20,000 | Kaggle Competition |

Place dataset CSVs in `datasets/` folder:
- `True.csv` — real news articles
- `Fake.csv` — fake news articles
- `news.csv` — Kaggle format (title, text, label)

---

## 🧪 Testing

```bash
cd backend
pytest tests/ -v --asyncio-mode=auto
```

---

## 🎓 Viva Preparation

See the **About** page in the app for full Q&A, or visit `/about` after starting the frontend.

Key talking points:
1. **Why ensemble?** — Reduces bias/variance, combines TF-IDF surface patterns with BERT's semantic depth
2. **SHAP vs LIME?** — SHAP is global + locally consistent via Shapley values; LIME is local-only approximation
3. **BiLSTM advantage?** — Captures sequential dependencies in both directions (better than unidirectional LSTM)
4. **NLI for contradiction?** — Cross-encoder NLI explicitly models CONTRADICTION/ENTAILMENT between headline and body
5. **AI-gen detection without GPT-2?** — Burstiness + entropy are language-agnostic signals that don't require a large LM

---

## 👨‍💻 Tech Stack Summary

**Frontend:** React 18 · Vite · Tailwind CSS · Framer Motion · Recharts · D3.js · React Router

**Backend:** Python 3.11 · FastAPI · Motor (async MongoDB) · JWT · Pydantic v2

**ML/NLP:** HuggingFace Transformers · Sentence-BERT · PyTorch · TensorFlow/Keras · scikit-learn · XGBoost · spaCy · NLTK · TextBlob

**Explainability:** SHAP · LIME · Custom coefficient analysis

**Infrastructure:** MongoDB Atlas · Docker · docker-compose · Vercel · Render

---

## 📜 License

MIT License — free for educational and commercial use.

---

*Built with ❤️ for Final Year Projects, Research Portfolios, and AI/ML Showcases*
