# 🧠 NLP Based Mental Health Support & Analytics Platform

A major-project level, research-oriented AI/NLP web platform combining conversational AI support, emotion & intent detection, conversation memory, report analysis, mental health screening (PHQ-9/GAD-7), longitudinal tracking, explainable AI (XAI), safety risk detection, and model evaluation metrics.

> [!IMPORTANT]
> **Medical Safety & Non-Diagnostic Disclaimer**:
> This platform is strictly a supportive tool. It does **NOT** claim to diagnose mental illnesses, replace psychologists or psychiatrists, or prescribe/modify medications.

---

## 🌟 Core Features & Modules

1. **Authentication & Data Privacy**:
   - Secure email/password login & registration with salted password hashing (pbkdf2:sha256).
   - Google OAuth / OpenID Connect social login ("Continue with Google") storing minimum identity info without storing social passwords.
   - User data isolation and complete account & data deletion functionality.
   - Login page appears immediately upon accessing the site.

2. **Conversational AI & Empathetic Support**:
   - Natural, empathetic support system using active listening, CBT-inspired reflection, validation, and clarifying questions.
   - Never claims to be a therapist; clearly identifies as an AI supportive tool.
   - Integrates relevant conversation context memory without sending raw long histories.

3. **NLP Processing Pipeline & Explainable AI (XAI)**:
   - **Emotion Classification**: Detects 9 classes (*Anxiety, Sadness, Fear, Anger, Frustration, Stress, Loneliness, Happiness, Neutral*).
   - **Intent Detection**: Identifies 10 intents (*Academic Stress, Anxiety Concern, Sleep Difficulty, Loneliness, Relationship Concern, Sadness Support, General Emotional Support, Stress Management, Mental Health Information, Coping Support*).
   - **Sentiment Analysis**: Lexicon-based sentiment scoring (-1.0 to +1.0).
   - **AI Insights Panel**: Real-time drawer displaying detected emotion, intent, sentiment, risk level, and token feature weights.

4. **Document Processing & Medication Entity Extraction**:
   - Accepts PDF, DOCX, and scanned Image mental health reports.
   - Extracts key clinical findings, important observations, and recommendations.
   - **Medication Extraction**: Identifies drug names, dosages, and frequencies already present in the document. Prominently displays strict non-prescription disclaimers ("Do not start/stop/change medication based on this AI summary").

5. **Validated Screening & Longitudinal Analytics**:
   - Standardized **PHQ-9** (Depression) and **GAD-7** (Anxiety) screening questionnaires with validated scoring rules.
   - **Current Well-being Assessment**: Non-diagnostic synthesis of self-reported indicators, screening scores, and emotional trends (🟢 Stable, 🟡 Needs Attention, 🔴 Immediate Support Recommended).
   - Time-series **Chart.js** trends visualization for Stress, Anxiety, and Mood index.

6. **Safety & Risk Urgency Layer**:
   - 4-tier risk classification (🟢 Normal, 🟡 Concern, 🟠 High Concern, 🔴 Crisis).
   - Automatic crisis response override providing emergency hotlines (988, Tele-MANAS 14416, Crisis Text Line 741741, UK Samaritans 116 123).

7. **Research Evaluation Framework**:
   - Includes synthetic research dataset (`evaluation/dataset.json`) and evaluation module (`evaluate_models.py`).
   - Calculates Accuracy, Precision, Recall, Macro F1, and Confusion Matrices for Intent and Emotion classifiers.

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, Vanilla CSS3 (Glassmorphism design, Inter/Outfit Google typography), JavaScript (ES6+), Chart.js
- **Backend**: Python 3.x, Flask web framework
- **Database**: SQLite3 (`database/mental_health.db`)
- **NLP & Machine Learning**: scikit-learn (TF-IDF vectorizer, MultinomialNB), NLTK/regex text preprocessing, Custom Lexicon Sentiment & Severity Rules
- **Document & Image Extraction**: pypdf, python-docx, Pillow

---

## 🚀 Running the Application

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the Application
```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 📂 Project Architecture

```
mental_health_chatbot/
├── app.py                      # Flask routes & REST endpoints
├── config.py                   # App config, database paths, upload limits, crisis hotlines
├── requirements.txt            # Python requirements
├── README.md                   # Project documentation
├── database/
│   ├── schema.sql              # SQLite table schemas
│   └── db_helper.py            # Database CRUD operations & security authorization
├── auth/
│   └── auth_service.py         # Password hashing & Google OAuth authentication logic
├── nlp/
│   ├── preprocessing.py        # Tokenization & text cleaning
│   ├── emotion_classifier.py   # 9-class emotion classifier
│   ├── intent_classifier.py    # 10-class intent classifier
│   ├── sentiment_analyzer.py   # Sentiment scoring
│   ├── risk_detector.py        # 4-tier risk & urgency detector
│   └── nlp_pipeline.py         # Unified NLP orchestration
├── memory/
│   └── context_memory.py       # Context retrieval engine
├── report_processor/
│   ├── document_extractor.py   # PDF / DOCX / Image text extractor
│   ├── report_summarizer.py    # NLP key findings & summary engine
│   └── medication_extractor.py # Extracted medication parser & disclaimers
├── screening/
│   └── questionnaires.py       # PHQ-9 & GAD-7 scoring rules
├── engine/
│   ├── wellbeing_tracker.py    # Well-being score computation & trend aggregation
│   ├── recommendation_engine.py# Personalized wellness recommendations
│   └── emotional_support.py    # Empathetic response generator & crisis overrides
├── explainability/
│   └── xai_engine.py           # Explainable AI feature importance weights
├── evaluation/
│   ├── dataset.json            # Research evaluation dataset
│   └── evaluate_models.py      # Research metrics & confusion matrix generator
├── static/
│   ├── css/
│   │   ├── style.css           # Core styling & glassmorphism theme
│   │   └── dashboard.css       # Module & chat UI styling
│   └── js/
│       ├── auth.js             # Client authentication & OAuth
│       ├── main.js             # SPA router & utilities
│       ├── chat.js             # Chatbot UI & AI Insights drawer
│       ├── dashboard.js        # Dashboard gauges & cards
│       ├── reports.js          # File upload & report viewer
│       ├── assessments.js      # Screening questionnaire forms
│       ├── trends.js           # Chart.js longitudinal trends
│       └── evaluation.js       # Research evaluation viewer
└── templates/
    └── index.html              # Main SPA container (Login-first flow)
```
