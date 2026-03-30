import os
from pathlib import Path
from collections import Counter

from flask import (
    Flask,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
    jsonify,
)
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

# Local modules
from database.database_logic import db, init_db, User, Prediction
from backend.inference.predictor import (
    predict_image_from_path,
    predict_audio_from_path,
)

# ==========================================
# APP CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / 'front_end'),
    static_folder=str(BASE_DIR / 'front_end'),
    static_url_path='/static'
)

FRONT_END_DIR = str(BASE_DIR / 'front_end')

app.config["SECRET_KEY"] = "your_secret_key_here_change_in_production"

# Database (SQLite)
DB_PATH = BASE_DIR / "database" / "cat_emotion.db"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# File uploads
UPLOAD_FOLDER = BASE_DIR / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp3", "wav"}

# ==========================================
# INITIALIZE EXTENSIONS
# ==========================================

init_db(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ==========================================
# HELPER: User stats
# ==========================================

def get_user_stats(user_id: int):
    preds = Prediction.query.filter_by(user_id=user_id).all()
    total = len(preds)
    image_count = sum(1 for p in preds if p.file_type == "image")
    audio_count = sum(1 for p in preds if p.file_type == "audio")

    emotion_counts = Counter(p.prediction_result for p in preds)
    unique_emotions = len(emotion_counts)

    recent = (
        Prediction.query.filter_by(user_id=user_id)
        .order_by(Prediction.timestamp.desc())
        .limit(10)
        .all()
    )

    return {
        "total_predictions": total,
        "image_count": image_count,
        "audio_count": audio_count,
        "unique_emotions": unique_emotions,
        "emotion_distribution": dict(emotion_counts),
        "recent_predictions": recent,
    }


# ==========================================
# PUBLIC ROUTES
# ==========================================

@app.route("/")
def home():
    return redirect(url_for("landing"))


@app.route("/landing")
def landing():
    return send_from_directory(FRONT_END_DIR, "index.html")


@app.route("/ppt")
def ppt():
    ppt_dir = BASE_DIR / "ppt_like_work"
    return send_from_directory(str(ppt_dir), "index.html")


# ==========================================
# AUTH ROUTES
# ==========================================

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_pass = request.form.get("confirm_password", "")

        if not email or not password:
            flash("Email and password are required.", "danger")
            return redirect(url_for("login") + "?tab=register")

        if "@" not in email:
            flash("Please enter a valid email address.", "danger")
            return redirect(url_for("login") + "?tab=register")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return redirect(url_for("login") + "?tab=register")

        if password != confirm_pass:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("login") + "?tab=register")

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "warning")
            return redirect(url_for("login") + "?tab=register")

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(
            name=full_name if full_name else "Cat Lover",
            email=email,
            password_hash=hashed_password,
        )
        db.session.add(user)
        db.session.commit()

        flash("Account created successfully! You can now login. 🎉", "success")
        return redirect(url_for("login"))

    return send_from_directory(FRONT_END_DIR, "login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter email and password.", "danger")
            return redirect(url_for("login"))

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Login successful! Welcome back! 🐾", "success")
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("dashboard"))

        flash("Login unsuccessful. Please check email and password.", "danger")

    return send_from_directory(FRONT_END_DIR, "login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out. See you soon! 👋", "info")
    return redirect(url_for("login"))


# ==========================================
# AUTHENTICATED ROUTES
# ==========================================

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    prediction_text = None
    confidence_value = None

    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part in request.", "danger")
            return redirect(request.url)

        file = request.files["file"]
        file_type = request.form.get("file_type", "image")  # 'image' or 'audio'

        if file.filename == "":
            flash("No file selected.", "danger")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            try:
                # Default fallbacks
                emotion = None
                confidence = None

                if file_type == "image":
                    result = predict_image_from_path(filepath)
                elif file_type == "audio":
                    result = predict_audio_from_path(filepath)
                else:
                    raise ValueError("Unsupported file_type")

                # Handle both (emotion, conf) and plain string
                if isinstance(result, tuple) and len(result) == 2:
                    emotion, confidence = result
                else:
                    emotion = str(result)
                    confidence = None

                prediction_text = (
                    f"{emotion} ({confidence*100:.1f}%)"
                    if confidence is not None
                    else emotion
                )
                confidence_value = confidence

                pred_entry = Prediction(
                    user_id=current_user.id,
                    file_type=file_type,
                    filename=filename,
                    prediction_result=emotion,
                    confidence=confidence,
                )
                db.session.add(pred_entry)
                db.session.commit()

                if confidence is not None:
                    flash(
                        f"File processed successfully! Emotion: {emotion} "
                        f"({confidence*100:.1f}%) 🎉",
                        "success",
                    )
                else:
                    flash(
                        f"File processed successfully! Emotion detected: {emotion} 🎉",
                        "success",
                    )

            except Exception as e:
                flash(f"Error processing file: {e}", "danger")
        else:
            flash("Invalid file type. Allowed: PNG, JPG, JPEG, GIF, MP3, WAV", "warning")

    stats = get_user_stats(current_user.id)

    return send_from_directory(FRONT_END_DIR, "dashboard.html")


@app.route("/profile")
@login_required
def profile():
    return send_from_directory(FRONT_END_DIR, "profile.html")


@app.route("/update_profile", methods=["POST"])
@login_required
def update_profile():
    name = request.form.get("name", "").strip()
    password = request.form.get("password", "").strip()

    if name:
        current_user.name = name

    if password and len(password) >= 6:
        current_user.password_hash = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

    db.session.commit()
    flash("Profile updated successfully! 🎉", "success")
    return redirect(url_for("profile"))


@app.route("/metrics")
@login_required
def metrics():
    return send_from_directory(FRONT_END_DIR, "metrics.html")


@app.route("/history")
@login_required
def history():
    return send_from_directory(FRONT_END_DIR, "history.html")


# ==========================================
# API ENDPOINTS
# ==========================================

@app.route('/api/user')
def api_user():
    if not current_user.is_authenticated:
        return jsonify({'error': 'not authenticated'}), 401
    return jsonify({
        'name': current_user.display_name,
        'email': current_user.email,
        'id': current_user.id
    })


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or request.form
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({
            'error': 'Email and password required'
        }), 400

    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password_hash, password):
        login_user(user)
        return jsonify({
            'success': True,
            'name': user.display_name,
            'redirect': '/dashboard'
        })

    return jsonify({
        'error': 'Invalid email or password'
    }), 401


@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json() or request.form
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    confirm = data.get('confirm_password', '')

    if not email or not password:
        return jsonify({
            'error': 'Email and password are required'
        }), 400

    if '@' not in email or '.' not in email:
        return jsonify({
            'error': 'Please enter a valid email address'
        }), 400

    if len(password) < 6:
        return jsonify({
            'error': 'Password must be at least 6 characters'
        }), 400

    if password != confirm:
        return jsonify({
            'error': 'Passwords do not match'
        }), 400

    if User.query.filter_by(email=email).first():
        return jsonify({
            'error': 'Email already registered'
        }), 409

    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(
        name=full_name if full_name else 'Cat Lover',
        email=email,
        password_hash=hashed
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Account created! You can now log in.',
        'redirect': '/login'
    })


@app.route('/api/logout')
@login_required
def api_logout():
    logout_user()
    return jsonify({
        'success': True,
        'redirect': '/login'
    })


@app.route('/api/stats')
@login_required
def api_stats():
    stats = get_user_stats(current_user.id)
    return jsonify({
        'total_predictions': stats['total_predictions'],
        'image_count': stats['image_count'],
        'audio_count': stats['audio_count'],
        'unique_emotions': stats['unique_emotions'],
        'emotion_distribution': stats['emotion_distribution']
    })


@app.route('/api/history')
@login_required
def api_history():
    preds = Prediction.query.filter_by(
        user_id=current_user.id
    ).order_by(Prediction.timestamp.desc()).all()
    return jsonify([{
        'timestamp': p.timestamp.strftime('%d %b, %H:%M'),
        'file_type': p.file_type,
        'filename': p.filename,
        'emotion': p.prediction_result,
        'confidence': round(p.confidence * 100) if p.confidence else None
    } for p in preds])


@app.route('/api/predict', methods=['POST'])
@login_required
def api_predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400

    file = request.files['file']
    file_type = request.form.get('file_type', 'image')

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        if file_type == 'image':
            result = predict_image_from_path(filepath)
        else:
            result = predict_audio_from_path(filepath)

        if isinstance(result, tuple) and len(result) == 2:
            emotion, confidence = result
        else:
            emotion = str(result)
            confidence = None

        emotion = emotion.strip().capitalize()

        pred = Prediction(
            user_id=current_user.id,
            file_type=file_type,
            filename=filename,
            prediction_result=emotion,
            confidence=confidence
        )
        db.session.add(pred)
        db.session.commit()

        return jsonify({
            'success': True,
            'emotion': emotion,
            'confidence': round(confidence * 100) if confidence else None,
            'filename': filename
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/update_profile', methods=['POST'])
@login_required
def api_update_profile():
    data = request.get_json() or request.form
    name = data.get('name', '').strip()
    password = data.get('password', '').strip()

    if name:
        current_user.name = name
    if password and len(password) >= 6:
        current_user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    db.session.commit()
    return jsonify({
        'success': True,
        'message': 'Profile updated successfully'
    })


@app.route('/api/delete_account', methods=['POST'])
@login_required
def api_delete_account():
    user_id = current_user.id
    logout_user()
    # Delete all predictions for this user
    Prediction.query.filter_by(user_id=user_id).delete()
    # Delete the user itself
    User.query.filter_by(id=user_id).delete()
    db.session.commit()
    return jsonify({'success': True})


# ==========================================
# STATIC ASSET ROUTES
# ==========================================

@app.route("/media/<path:filename>")
def serve_media(filename):
    return send_from_directory(str(BASE_DIR / "front_end"), filename)


@app.route("/<path:filename>")
def serve_frontend_file(filename):
    file_path = BASE_DIR / "front_end" / filename
    if file_path.exists():
        return send_from_directory(str(BASE_DIR / "front_end"), filename)
    return {"error": "Not found"}, 404


# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":
    print("=" * 60)
    print("  🐱 MewConnect - Cat Emotion Recognition System")
    print("  🌐 Starting at http://0.0.0.0:5001")
    print("=" * 60)
    app.run(host='0.0.0.0', port=7860)
