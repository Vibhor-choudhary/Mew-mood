from pathlib import Path
import tempfile

from flask import Flask, request, jsonify

from backend.inference.predictor import (
    predict_image_from_path,
    predict_audio_from_path,
)

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/predict/image", methods=["POST"])
def predict_image_api():
    if "file" not in request.files:
        return jsonify({"error": "No file part 'file' in request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        file.save(tmp.name)
        tmp_path = Path(tmp.name)

    try:
        emotion, confidence = predict_image_from_path(tmp_path)
        return jsonify({
            "emotion": emotion,
            "confidence": confidence
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


@app.route("/predict/audio", methods=["POST"])
def predict_audio_api():
    if "file" not in request.files:
        return jsonify({"error": "No file part 'file' in request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        file.save(tmp.name)
        tmp_path = Path(tmp.name)

    try:
        emotion, confidence = predict_audio_from_path(tmp_path)
        return jsonify({
            "emotion": emotion,
            "confidence": confidence
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
