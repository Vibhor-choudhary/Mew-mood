from pathlib import Path
import numpy as np
from PIL import Image

import torch
import torch.nn as nn
from torchvision import models, transforms

import librosa
from joblib import load
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Image model paths
IMG_MODEL_DIR = PROJECT_ROOT / "backend" / "trained_modelimages" / "image_model"
IMG_MODEL_PATH = IMG_MODEL_DIR / "model.pth"
IMG_CLASSES_PATH = IMG_MODEL_DIR / "classes.txt"

# Audio model paths
AUD_MODEL_DIR = PROJECT_ROOT / "backend" / "trained_modelimages" / "audio_model"
AUD_CLF_PATH = AUD_MODEL_DIR / "audio_classifier.pkl"
AUD_SCALER_PATH = AUD_MODEL_DIR / "scaler.pkl"
AUD_ENCODER_PATH = AUD_MODEL_DIR / "label_encoder.pkl"

IMAGE_SIZE = (224, 224)
SAMPLE_RATE = 22050
DURATION = 3.0  # seconds


# -------- IMAGE MODEL --------

_image_model = None
_image_classes = None
_image_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(IMAGE_SIZE),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225]
    ),
])


def load_image_model():
    global _image_model, _image_classes
    if _image_model is not None:
        return _image_model, _image_classes

    with open(IMG_CLASSES_PATH, "r") as f:
        classes = [line.strip() for line in f if line.strip()]

    num_classes = len(classes)
    
    # Initialize correct ResNet18 architecture for new weights
    model = models.resnet18(weights=None)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, num_classes)

    # Load new trained state_dict map
    state_dict = torch.load(IMG_MODEL_PATH, map_location=torch.device('cpu'))
    
    # Check if there are strict dimension mismatches
    model.load_state_dict(state_dict, strict=True)
    model.eval()

    _image_model = model
    _image_classes = classes
    return _image_model, _image_classes


def predict_image_from_path(image_path: Path):
    model, classes = load_image_model()
    img = Image.open(image_path).convert("RGB")
    x = _image_transform(img).unsqueeze(0)

    with torch.no_grad():
        logits = model(x)
        probs = torch.softmax(logits, dim=1).numpy()[0]

    idx = int(np.argmax(probs))
    pred_class = classes[idx]
    pred_prob = float(probs[idx])
    return pred_class, pred_prob


# -------- AUDIO MODEL --------

_audio_clf = None
_audio_scaler = None
_audio_encoder = None


def load_audio_model():
    global _audio_clf, _audio_scaler, _audio_encoder
    if _audio_clf is not None:
        return _audio_clf, _audio_scaler, _audio_encoder

    clf = load(AUD_CLF_PATH)
    scaler: StandardScaler = load(AUD_SCALER_PATH)
    encoder = load(AUD_ENCODER_PATH)

    _audio_clf = clf
    _audio_scaler = scaler
    _audio_encoder = encoder
    return _audio_clf, _audio_scaler, _audio_encoder


def _extract_audio_features(file_path: Path):
    y, sr = librosa.load(file_path, sr=SAMPLE_RATE, duration=DURATION)
    if len(y) < int(SAMPLE_RATE * DURATION):
        pad_len = int(SAMPLE_RATE * DURATION) - len(y)
        y = np.pad(y, (0, pad_len))

    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
    mfcc_mean = np.mean(mfcc, axis=1)

    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)

    mel = librosa.feature.melspectrogram(y=y, sr=sr)
    mel_mean = np.mean(mel, axis=1)

    contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    contrast_mean = np.mean(contrast, axis=1)

    tonnetz = librosa.feature.tonnetz(y=librosa.effects.harmonic(y), sr=sr)
    tonnetz_mean = np.mean(tonnetz, axis=1)

    feats = np.concatenate(
        [mfcc_mean, chroma_mean, mel_mean, contrast_mean, tonnetz_mean]
    )
    return feats.reshape(1, -1)


def predict_audio_from_path(audio_path: Path):
    clf, scaler, encoder = load_audio_model()
    X = _extract_audio_features(audio_path)
    X_scaled = scaler.transform(X)

    probs = clf.predict_proba(X_scaled)[0]
    idx = int(np.argmax(probs))
    pred_class = encoder.inverse_transform([idx])[0]
    pred_prob = float(probs[idx])
    return pred_class, pred_prob
