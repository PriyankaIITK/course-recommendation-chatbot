# Course Recommendation Chatbot using NLP

An interview-friendly NLP project that classifies a user's intent and recommends relevant courses. It includes a responsive chat interface, confidence-based fallback, simple sentiment detection, multiple recommendations, and session conversation history.

## Technology

- Python 3.10+
- Flask web framework
- TF-IDF features (unigrams + bigrams)
- Logistic Regression classifier
- HTML, CSS, and vanilla JavaScript

## Quick start (Windows)

Double-click `start_chatbot.bat`. The first run creates a virtual environment, installs packages, trains the model, and opens the site at <http://127.0.0.1:5000>.

Or run it manually:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python train.py
python app.py
```

## Project structure

```text
course-recommendation-chatbot/
├── app.py                    # Flask routes and chatbot logic
├── chatbot_ml.py             # preprocessing, training, evaluation, inference
├── train.py                  # model training entry point
├── test_chatbot.py           # automated smoke tests
├── data/
│   ├── intents.json          # 260 labeled training messages (13 intents)
│   └── courses.json          # recommendation catalog
├── models/                   # generated model and evaluation metrics
├── static/                   # CSS and browser JavaScript
├── templates/index.html      # chat interface
├── requirements.txt
└── start_chatbot.bat
```

## NLP pipeline

```text
User message → lowercase/cleaning → TF-IDF tokenization and stop-word removal
             → Logistic Regression → intent + confidence → course mapping
```

The split is stratified: 75% training and 25% testing. `train.py` reports accuracy and weighted F1, saves detailed metrics to `models/metrics.json`, then refits the deployment model on all 260 examples.

## Supported intents

Greeting, Goodbye, Thanks, Recommendation, Python, SQL, Data Analyst, Data Scientist, ML Engineer, AI, Web Development, Cloud Computing, and Cybersecurity.

## Useful demo messages

- `I want to become a Data Scientist`
- `I enjoy statistics and making dashboards`
- `Teach me how to protect computer systems`
- `I want to build websites with Python`
- `Which course should I take?`

## Extend the project

Add patterns to `data/intents.json`, add matching courses to `data/courses.json`, and run `python train.py` again. For a production version, move sessions to a database, use a production WSGI server, add authentication, and replace the lexicon sentiment helper with a trained sentiment model.

