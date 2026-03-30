<div align="center">

# 🐱 MeowMood

### *Because your cat is trying to tell you something.*

**An AI-powered cat emotion recognition system that decodes both facial expressions and vocalizations — bridging the communication gap between cats and their humans.**

<br>

[![Live Demo](https://img.shields.io/badge/🤗%20Live%20Demo-MewMood-FF9D00?style=for-the-badge)](https://vibhor-choudhary95-mewmood.hf.space)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/spaces/vibhor-choudhary95/MewMood)

<br>

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-ResNet18-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-RandomForest-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Git LFS](https://img.shields.io/badge/Git%20LFS-F64935?style=for-the-badge&logo=git&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Deployed-2496ED?style=for-the-badge&logo=docker&logoColor=white)

</div>

---

## 🌐 Live Demo

> **Try it right now — no installation needed:**
> ### 👉 [vibhor-choudhary95-mewmood.hf.space](https://vibhor-choudhary95-mewmood.hf.space)

> ⚠️ The Space may take **1–2 minutes to wake up** if it hasn't been visited recently (free tier sleep). Just wait and refresh — it'll boot up fully.

---

## 📖 What is MeowMood?

MeowMood is an AI-powered web application that analyzes cat emotions through two independent machine learning pipelines — one for **facial expressions** (images) and one for **vocalizations** (audio). Upload a photo or sound clip of your cat, and MeowMood returns a data-driven prediction of their emotional state.

Built as an Infosys internship project, MeowMood features a full-stack architecture with user authentication, prediction history tracking, and a glassmorphism-inspired UI — deployed live on Hugging Face Spaces via Docker.

---

## ✨ Features

- 🖼️ **Image Emotion Detection** — ResNet18 (PyTorch) analyzes cat facial expressions across 5 emotion classes
- 🔊 **Audio Emotion Detection** — Scikit-learn classifier with librosa feature extraction for 3 vocal emotion classes
- 🔐 **Secure Authentication** — Gmail-only registration, bcrypt password hashing, Flask-Login session management
- 📊 **Personal Analytics** — Emotion frequency stats, full prediction history, and user metrics
- 🗂️ **History Tracking** — Every prediction is stored and viewable per user
- 💻 **Modern UI** — Custom glassmorphism design with smooth animations, no external UI framework needed
- 🚀 **Live Deployment** — Fully deployed on Hugging Face Spaces via Docker

---

## 🎭 Emotion Classes

| Modality | Detectable Emotions |
|----------|-------------------|
| 🖼️ **Image (Facial)** | Angry · Happy · Sad · Scared · Surprised |
| 🔊 **Audio (Vocal)** | Angry · Happy · Scared |

---

## 🧠 ML Architecture

### Image Model
- **Architecture**: ResNet18 with transfer learning (ImageNet weights)
- **Framework**: PyTorch
- **Input**: Cat face images (JPG, PNG, GIF)
- **Model file**: `backend/trained_modelimages/image_model/model.pth` *(stored via Git LFS)*

### Audio Model
- **Architecture**: Random Forest Classifier (Scikit-learn)
- **Feature Extraction**: Librosa — MFCCs, Chroma, Mel Spectrogram, Spectral Contrast, Tonnetz
- **Framework**: Scikit-learn + Joblib
- **Input**: Cat audio recordings (MP3, WAV)
- **Model files**: `audio_classifier.pkl`, `scaler.pkl`, `label_encoder.pkl`

> The two models are fully independent pipelines — image analysis uses deep learning (CNN), while audio analysis uses classical ML with DSP feature extraction.

---

## 🗂️ Project Structure

```
MeowMood/
│
├── app.py                              # Central Flask application server
├── setup.py                            # One-click environment setup script
├── requirements.txt                    # Master Python dependencies list
├── Dockerfile                          # HF Spaces Docker deployment config
├── .dockerignore                       # Excludes heavy dirs from Docker build
│
├── backend/
│   ├── inference/
│   │   ├── model_loader.py             # Singleton model loader (lazy init)
│   │   └── predictor.py               # Prediction logic for both models
│   ├── models_training/
│   │   ├── image_model.py             # ResNet18 training script
│   │   ├── audio_model.py             # Random Forest training script
│   │   └── requirements.txt           # Training-only dependencies
│   └── trained_modelimages/
│       ├── image_model/               # model.pth (via Git LFS)
│       └── audio_model/               # audio_classifier.pkl, scaler.pkl, label_encoder.pkl
│
├── database/
│   ├── database_logic.py              # SQLAlchemy models & DB schema
│   └── cat_emotion.db                 # SQLite DB (auto-created on first run)
│
├── front_end/
│   ├── index.html                     # Landing page
│   ├── login.html                     # Login page
│   ├── dashboard.html                 # Main analysis interface
│   ├── profile.html                   # User profile
│   ├── history.html                   # Prediction history
│   ├── metrics.html                   # Emotion analytics
│   ├── emotions/                      # Emotion result images
│   ├── frames/                        # UI frame assets
│   └── video/                         # Background video assets
│
└── uploads/                           # Temporary file processing directory
```

---

## 🚀 Quick Setup (Local)

### Prerequisites

- Python 3.12+
- Git with **Git LFS** installed ([git-lfs.com](https://git-lfs.com))
- 4GB+ RAM recommended
- Works on macOS, Windows, and Linux

### Option A — Automatic Setup (Recommended)

Clone the repo and run the setup script. It handles Git LFS, model downloads, and dependency installation automatically.

```bash
git clone https://github.com/Vibhor-choudhary/Mew-mood.git
cd Mew-mood
python setup.py
```

The `setup.py` script will:
1. Install and initialize Git LFS
2. Pull `model.pth` and all binary model files from LFS storage
3. Install all Python dependencies from `requirements.txt`
4. Create the `uploads/` directory

Then start the app:
```bash
python app.py
```

Open your browser at: **`http://127.0.0.1:7860`**

### Option B — Manual Setup

```bash
# 1. Clone (LFS files download automatically if Git LFS is installed)
git clone https://github.com/Vibhor-choudhary/Mew-mood.git
cd Mew-mood

# 2. Create a virtual environment
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create uploads folder
mkdir uploads

# 5. Start the server
python app.py
```

Open your browser at: **`http://127.0.0.1:7860`**

---

## 🧭 How to Use

1. **Register** — Create an account using a Gmail address
2. **Login** — Sign in with your credentials
3. **Upload** — Go to the Dashboard and upload a cat image or audio file
4. **Predict** — Get an instant AI emotion prediction
5. **Track** — View your full prediction history and emotion stats on the History and Metrics pages

---

## 📡 API Reference

### User Routes

| Route | Method | Description | Auth |
|-------|--------|-------------|------|
| `/` | GET | Landing / redirect | No |
| `/register` | GET, POST | User registration | No |
| `/login` | GET, POST | User login | No |
| `/logout` | GET | Logout & clear session | Yes |
| `/dashboard` | GET | Main analysis interface | Yes |
| `/history` | GET | Prediction history page | Yes |
| `/profile` | GET | User profile page | Yes |
| `/metrics` | GET | Emotion analytics page | Yes |

### API Endpoints

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/predict` | POST | Submit image or audio, returns emotion prediction | Yes |
| `/api/history` | GET | Returns all past predictions as JSON | Yes |
| `/api/stats` | GET | Returns emotion frequency data for charts | Yes |
| `/api/update_profile` | POST | Update user info | Yes |
| `/api/delete_account` | POST | Permanently delete account and data | Yes |

#### Example — `/api/predict`

**Request:**
```
POST /api/predict
Content-Type: multipart/form-data

file: <your cat image or audio file>
type: "image" | "audio"
```

**Response:**
```json
{
  "emotion": "Happy",
  "confidence": 0.91,
  "model_used": "image"
}
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root for production use:

```env
SECRET_KEY=your_very_secret_key_here
```

The app uses `python-dotenv` to load this automatically. If no `.env` is present, a default key is used (fine for local development, **not recommended for production**).

### Flask Settings (`app.py`)

| Setting | Description |
|---------|-------------|
| `SECRET_KEY` | Session signing key — change for production |
| `UPLOAD_FOLDER` | Directory for temporary file processing |
| `ALLOWED_EXTENSIONS` | Permitted file types for upload |

---

## 🏋️ Retraining Models (Optional)

The trained models are included — you don't need to retrain. But if you want to:

**Retrain the audio model (~2–5 min):**
```bash
python backend/models_training/audio_model.py
```
Input: `data_analysis/test_traindeddata/audio_data/train_data`
Output: `backend/trained_modelimages/audio_model/`

**Retrain the image model (~10–20 min on CPU, ~2–5 min on GPU):**
```bash
python backend/models_training/image_model.py
```
Input: `data_analysis/test_traindeddata/image_data/imagetraindata`
Output: `backend/trained_modelimages/image_model/`

---

## 🛡️ Security

- **Passwords**: bcrypt hashing with salt (Flask-Bcrypt)
- **Sessions**: Flask-Login with server-side session management
- **SQL Injection**: Prevented via SQLAlchemy ORM (no raw queries)
- **File uploads**: Sanitized with `secure_filename()` from Werkzeug
- **Email validation**: Restricted to Gmail addresses only

---

## 🐛 Troubleshooting

**Models not loading:**
```
Warning: Image model not found
Warning: Audio model not found
```
→ Run `python setup.py` to pull model files via Git LFS, or run `git lfs pull` manually.

**Missing module errors:**
```
ModuleNotFoundError: No module named 'flask_bcrypt'
```
→ Run `pip install -r requirements.txt`

**Database errors:**
→ Delete `database/cat_emotion.db` and restart — it will be auto-recreated fresh.

**Port already in use:**
→ Kill the existing process or change the port in `app.py`: `app.run(port=5001)`

---

## ⚠️ Known Limitations

- Image model accuracy is best with clear, well-lit, front-facing cat photos
- Audio model is limited to 3 emotion classes (Angry, Happy, Scared)
- Live demo SQLite DB resets when the HF Space goes to sleep (free tier limitation)

---

## 🔮 Future Plans

- 📹 Real-time webcam emotion analysis
- 🏥 Cat Health tracker integration (mood trends over time)
- 🔊 Expanded audio recognition for 10+ vocal nuances
- 📱 Mobile-friendly PWA version

---

## 📦 Git LFS

This repository uses **Git LFS** to store all large binary files.

| File Type | Examples | Storage |
|-----------|---------|---------|
| ML model weights | `model.pth` | Git LFS |
| Audio classifiers | `*.pkl` | Git LFS |
| Videos | `*.mp4` | Git LFS |
| Images & GIFs | `*.png`, `*.jpg`, `*.gif` | Git LFS |

If you cloned without Git LFS installed, run:
```bash
git lfs install
git lfs pull
```

---

<div align="center">

*Made for cat lovers, by cat lovers.*
**🐾 MeowMood — because every meow means something.**

</div>
