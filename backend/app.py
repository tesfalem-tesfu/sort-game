from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os, random, string, re, logging, bleach

# ────────────────────────────────────────────────
# INIT
# ────────────────────────────────────────────────

load_dotenv()

# ── Validate critical env vars ────────────────────────────────────────────────
JWT_SECRET = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET or JWT_SECRET == "change-this-to-a-long-random-string":
    raise RuntimeError("JWT_SECRET_KEY is not set or is using the default value. Set it in .env!")

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("security.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ── Database ──────────────────────────────────────────────────────────────────
# Render provides DATABASE_URL for PostgreSQL — use it if available, else fall back to MySQL locally
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Render gives postgres:// but SQLAlchemy needs postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
else:
    # Local MySQL (XAMPP)
    MYSQL_USER     = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_HOST     = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT     = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DB       = os.getenv("MYSQL_DB", "sorting_quiz")
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ── JWT — short-lived access + long-lived refresh ─────────────────────────────
app.config["JWT_SECRET_KEY"]                  = JWT_SECRET
app.config["JWT_ACCESS_TOKEN_EXPIRES"]        = timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"]       = timedelta(days=30)
app.config["JWT_TOKEN_LOCATION"]              = ["headers", "cookies"]
app.config["JWT_COOKIE_SECURE"]               = False   # True in production (HTTPS)
app.config["JWT_COOKIE_SAMESITE"]             = "Lax"
app.config["JWT_ACCESS_COOKIE_NAME"]          = "access_token"
app.config["JWT_REFRESH_COOKIE_NAME"]         = "refresh_token"
app.config["JWT_COOKIE_CSRF_PROTECT"]         = False   # Enable in production

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "")

CORS(app, resources={r"/api/*": {"origins": [
    "http://localhost:3000", "http://localhost:3001", "http://localhost:3002",
    "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://127.0.0.1:3002",
    FRONTEND_ORIGIN,
]}}, supports_credentials=True)

db  = SQLAlchemy(app)
jwt = JWTManager(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["2000 per day", "500 per hour"],
    storage_uri="memory://",
)

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES     = 15

# ────────────────────────────────────────────────
# MODELS
# ────────────────────────────────────────────────

class User(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    email           = db.Column(db.String(120), unique=True, nullable=False)
    password        = db.Column(db.String(255), nullable=False)
    username        = db.Column(db.String(50), nullable=True)
    high_score      = db.Column(db.Integer, default=0)
    total_games     = db.Column(db.Integer, default=0)
    email_verified  = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(255), nullable=True)
    reset_token     = db.Column(db.String(255), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    failed_attempts = db.Column(db.Integer, default=0)
    locked_until    = db.Column(db.DateTime, nullable=True)

# ────────────────────────────────────────────────
# HELPERS
# ────────────────────────────────────────────────

def sanitize(value: str) -> str:
    """Strip HTML/JS from any string input."""
    return bleach.clean(str(value).strip(), tags=[], strip=True)


def validate_password(password: str):
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-]", password):
        return False, "Password must contain at least one special character"
    return True, ""


def is_locked(user: User) -> bool:
    return bool(user.locked_until and datetime.utcnow() < user.locked_until)


def record_failed_login(user: User, ip: str):
    user.failed_attempts += 1
    logger.warning(f"Failed login for {user.email} from {ip} — attempt {user.failed_attempts}")
    if user.failed_attempts >= MAX_FAILED_ATTEMPTS:
        user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)
        user.failed_attempts = 0
        logger.warning(f"Account {user.email} locked until {user.locked_until}")
    db.session.commit()


def reset_failed_login(user: User):
    user.failed_attempts = 0
    user.locked_until    = None
    db.session.commit()


def _fake_id(items: list) -> int:
    return abs(hash(tuple(items))) % (10 ** 9)

# ────────────────────────────────────────────────
# DATABASE INIT
# ────────────────────────────────────────────────

with app.app_context():
    db.create_all()

# ────────────────────────────────────────────────
# SECURITY HEADERS (on every response)
# ────────────────────────────────────────────────

@app.after_request
def security_headers(response):
    response.headers["X-Frame-Options"]           = "DENY"
    response.headers["X-Content-Type-Options"]    = "nosniff"
    response.headers["X-XSS-Protection"]          = "1; mode=block"
    response.headers["Referrer-Policy"]           = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"]   = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self' https://fonts.gstatic.com; "
        "connect-src 'self' http://localhost:* https://*.onrender.com;"
    )
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response

# ────────────────────────────────────────────────
# JWT ERROR HANDLERS
# ────────────────────────────────────────────────

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"msg": "Token expired", "error": "token_expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"msg": "Invalid token", "error": "invalid_token"}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"msg": "Authorization required", "error": "authorization_required"}), 401

# ────────────────────────────────────────────────
# ROUTES
# ────────────────────────────────────────────────

@app.route("/api/health")
def health():
    return jsonify({"status": "healthy"})


@app.route("/api/register", methods=["POST"])
@limiter.limit("5 per minute")
def register():
    data     = request.get_json(silent=True) or {}
    email    = sanitize(data.get("email", "")).lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"msg": "Email and password required"}), 400

    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return jsonify({"msg": "Invalid email format"}), 400

    ok, msg = validate_password(password)
    if not ok:
        return jsonify({"msg": msg}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already exists"}), 409

    user = User(email=email, password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()

    logger.info(f"New user registered: {email} from {request.remote_addr}")

    access_token  = create_access_token(identity=email)
    refresh_token = create_refresh_token(identity=email)

    resp = make_response(jsonify({"access_token": access_token, "email": email}), 201)
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp


@app.route("/api/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    data     = request.get_json(silent=True) or {}
    email    = sanitize(data.get("email", "")).lower()
    password = data.get("password", "")

    user = User.query.filter_by(email=email).first()

    # Always same message — prevents account enumeration
    if not user:
        logger.warning(f"Login attempt for non-existent email from {request.remote_addr}")
        return jsonify({"msg": "Invalid credentials"}), 401

    if is_locked(user):
        remaining = int((user.locked_until - datetime.utcnow()).total_seconds() / 60) + 1
        return jsonify({"msg": f"Account locked. Try again in {remaining} minute(s)"}), 423

    if not check_password_hash(user.password, password):
        record_failed_login(user, request.remote_addr)
        # Same message regardless — no enumeration
        return jsonify({"msg": "Invalid credentials"}), 401

    reset_failed_login(user)
    logger.info(f"Successful login: {email} from {request.remote_addr}")

    access_token  = create_access_token(identity=email)
    refresh_token = create_refresh_token(identity=email)

    resp = make_response(jsonify({"access_token": access_token, "email": email}))
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp


@app.route("/api/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Issue a new access token using the refresh token — no re-login needed."""
    identity     = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    resp = make_response(jsonify({"access_token": access_token}))
    set_access_cookies(resp, access_token)
    logger.info(f"Token refreshed for {identity}")
    return resp


@app.route("/api/logout", methods=["POST"])
def logout():
    resp = make_response(jsonify({"msg": "Logged out"}))
    unset_jwt_cookies(resp)
    return resp


@app.route("/api/game/questions", methods=["GET"])
@jwt_required()
def get_questions():
    limit    = request.args.get("limit", 1, type=int)
    category = sanitize(request.args.get("category", "numbers_asc"))
    limit    = min(max(limit, 1), 50)
    questions = [_generate_question(category) for _ in range(limit)]
    questions = [q for q in questions if q]
    return jsonify({"questions": questions, "count": len(questions)})


@app.route("/api/game/submit", methods=["POST"])
@jwt_required()
@limiter.limit("120 per minute")
def submit():
    data             = request.get_json(silent=True) or {}
    category         = sanitize(data.get("category", "numbers_asc"))
    original_items   = [sanitize(str(x)) for x in data.get("original_items", [])]
    user_answer_list = [sanitize(str(x)) for x in data.get("answer", [])]
    score            = data.get("score", 0)

    if not original_items:
        return jsonify({"msg": "original_items required"}), 400

    q = _generate_answer(category, original_items)
    if not q:
        return jsonify({"msg": "Unknown category"}), 400

    if set(user_answer_list) != set(original_items):
        logger.warning(f"Tampered answer from {request.remote_addr} — category: {category}")
        return jsonify({"msg": "Invalid answer: items do not match question"}), 400

    user_answer = ",".join(user_answer_list)
    correct     = user_answer == q["answer"]

    # Update user stats
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    if user and correct:
        if score > user.high_score:
            user.high_score = score
        db.session.commit()

    return jsonify({
        "correct":        correct,
        "correct_order":  q["answer"].split(","),
        "user_submitted": user_answer,
    })

# ────────────────────────────────────────────────
# QUESTION GENERATORS
# ────────────────────────────────────────────────

def _generate_question(category: str) -> dict:
    if category == "numbers_asc":
        size = random.randint(4, 8)
        nums = random.sample(range(1, 201), size)
        shuffled = nums[:]; random.shuffle(shuffled)
        return {"id": _fake_id(shuffled), "question": "Sort these numbers in ascending order",
                "items": [str(n) for n in shuffled], "answer": ",".join(str(n) for n in sorted(nums)), "category": category}

    if category == "numbers_desc":
        size = random.randint(4, 8)
        nums = random.sample(range(1, 201), size)
        shuffled = nums[:]; random.shuffle(shuffled)
        return {"id": _fake_id(shuffled), "question": "Sort these numbers in descending order",
                "items": [str(n) for n in shuffled], "answer": ",".join(str(n) for n in sorted(nums, reverse=True)), "category": category}

    if category == "letters_asc":
        size = random.randint(5, 10)
        letters = random.sample(string.ascii_lowercase, size)
        shuffled = letters[:]; random.shuffle(shuffled)
        return {"id": _fake_id(shuffled), "question": "Sort these letters alphabetically",
                "items": shuffled, "answer": ",".join(sorted(letters)), "category": category}

    if category == "letters_desc":
        size = random.randint(5, 10)
        letters = random.sample(string.ascii_lowercase, size)
        shuffled = letters[:]; random.shuffle(shuffled)
        return {"id": _fake_id(shuffled), "question": "Sort these letters in reverse alphabetical order",
                "items": shuffled, "answer": ",".join(sorted(letters, reverse=True)), "category": category}

    if category == "days":
        days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        shuffled = days[:]; random.shuffle(shuffled)
        return {"id": _fake_id(shuffled), "question": "Sort the days of the week correctly (start Monday)",
                "items": shuffled, "answer": ",".join(days), "category": category}

    if category == "bubble_sort":
        size = random.randint(4, 7)
        nums = random.sample(range(1, 100), size)
        one_pass = nums[:]
        for i in range(len(one_pass) - 1):
            if one_pass[i] > one_pass[i + 1]:
                one_pass[i], one_pass[i + 1] = one_pass[i + 1], one_pass[i]
        return {"id": _fake_id(nums), "question": "Bubble Sort: arrange so the largest number bubbles to the end (one pass)",
                "items": [str(n) for n in nums], "answer": ",".join(str(n) for n in one_pass), "category": category}

    if category == "selection_sort":
        size = random.randint(4, 7)
        nums = random.sample(range(1, 100), size)
        min_val = min(nums); rest = nums[:]; rest.remove(min_val)
        return {"id": _fake_id(nums), "question": "Selection Sort: move the smallest number to the front (one pass)",
                "items": [str(n) for n in nums], "answer": ",".join(str(n) for n in [min_val] + rest), "category": category}

    if category == "insertion_sort":
        size = random.randint(4, 7)
        nums = random.sample(range(1, 100), size)
        arr = nums[:]
        for i in range(1, len(arr)):
            key = arr[i]; j = i - 1
            while j >= 0 and arr[j] > key:
                arr[j + 1] = arr[j]; j -= 1
            arr[j + 1] = key
        return {"id": _fake_id(nums), "question": "Insertion Sort: sort by inserting each element into its correct position",
                "items": [str(n) for n in nums], "answer": ",".join(str(n) for n in arr), "category": category}

    if category == "merge_sort":
        size = random.randint(4, 8)
        nums = random.sample(range(1, 100), size)
        mid = len(nums) // 2
        left = sorted(nums[:mid]); right = sorted(nums[mid:])
        merged = sorted(left + right); display = left + right
        return {"id": _fake_id(display),
                "question": f"Merge Sort: merge the two sorted halves [{','.join(map(str,left))}] and [{','.join(map(str,right))}]",
                "items": [str(n) for n in display], "answer": ",".join(str(n) for n in merged), "category": category}

    if category == "quick_sort":
        size = random.randint(4, 7)
        nums = random.sample(range(1, 100), size)
        pivot = nums[0]
        less = [x for x in nums[1:] if x <= pivot]
        greater = [x for x in nums[1:] if x > pivot]
        return {"id": _fake_id(nums), "question": f"Quick Sort: partition around pivot {pivot} (smaller left, larger right)",
                "items": [str(n) for n in nums], "answer": ",".join(str(n) for n in less + [pivot] + greater), "category": category}

    return _generate_question("numbers_asc")


def _generate_answer(category: str, items: list) -> dict | None:
    if category == "numbers_asc":
        return {"answer": ",".join(sorted(items, key=lambda x: int(x)))}
    if category == "numbers_desc":
        return {"answer": ",".join(sorted(items, key=lambda x: int(x), reverse=True))}
    if category == "letters_asc":
        return {"answer": ",".join(sorted(items))}
    if category == "letters_desc":
        return {"answer": ",".join(sorted(items, reverse=True))}
    if category == "days":
        order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        return {"answer": ",".join(sorted(items, key=lambda d: order.index(d) if d in order else 99))}
    if category == "bubble_sort":
        arr = [int(x) for x in items]
        for i in range(len(arr) - 1):
            if arr[i] > arr[i + 1]: arr[i], arr[i + 1] = arr[i + 1], arr[i]
        return {"answer": ",".join(str(n) for n in arr)}
    if category == "selection_sort":
        arr = [int(x) for x in items]; min_val = min(arr); rest = arr[:]; rest.remove(min_val)
        return {"answer": ",".join(str(n) for n in [min_val] + rest)}
    if category == "insertion_sort":
        arr = [int(x) for x in items]
        for i in range(1, len(arr)):
            key = arr[i]; j = i - 1
            while j >= 0 and arr[j] > key: arr[j + 1] = arr[j]; j -= 1
            arr[j + 1] = key
        return {"answer": ",".join(str(n) for n in arr)}
    if category == "merge_sort":
        return {"answer": ",".join(str(n) for n in sorted(int(x) for x in items))}
    if category == "quick_sort":
        arr = [int(x) for x in items]; pivot = arr[0]
        less = [x for x in arr[1:] if x <= pivot]; greater = [x for x in arr[1:] if x > pivot]
        return {"answer": ",".join(str(n) for n in less + [pivot] + greater)}
    return None


# ────────────────────────────────────────────────
# PROFILE & LEADERBOARD ENDPOINTS
# ────────────────────────────────────────────────

@app.route("/api/profile", methods=["GET", "PUT"])
@jwt_required()
def profile():
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if request.method == "GET":
        return jsonify({
            "username": user.username,
            "email": user.email,
            "high_score": user.high_score,
            "total_games": user.total_games,
            "email_verified": user.email_verified
        })
    
    if request.method == "PUT":
        data = request.get_json(silent=True) or {}
        username = sanitize(data.get("username", ""))
        
        if username and len(username) >= 3:
            user.username = username
        
        db.session.commit()
        return jsonify({"msg": "Profile updated successfully"})


@app.route("/api/leaderboard", methods=["GET"])
def leaderboard():
    limit = request.args.get("limit", 10, type=int)
    users = User.query.filter(User.high_score > 0).order_by(User.high_score.desc()).limit(limit).all()
    
    return jsonify({
        "leaderboard": [
            {
                "username": u.username or "Anonymous",
                "high_score": u.high_score,
                "total_games": u.total_games
            } for u in users
        ]
    })


# ────────────────────────────────────────────────
# PASSWORD RESET ENDPOINTS
# ────────────────────────────────────────────────

@app.route("/api/request-password-reset", methods=["POST"])
@limiter.limit("3 per minute")
def request_password_reset():
    data = request.get_json(silent=True) or {}
    email = sanitize(data.get("email", "")).lower()
    
    if not email:
        return jsonify({"error": "Email is required"}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "If email exists, reset instructions sent"}), 200
    
    # Generate reset token
    reset_token = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    db.session.commit()
    
    # In production, send email here. For now, return token for testing
    return jsonify({
        "msg": "Password reset token generated",
        "reset_token": reset_token  # Remove this in production
    }), 200


@app.route("/api/reset-password", methods=["POST"])
@limiter.limit("5 per minute")
def reset_password():
    data = request.get_json(silent=True) or {}
    token = sanitize(data.get("token", ""))
    new_password = data.get("password", "")
    
    if not token or not new_password:
        return jsonify({"error": "Token and password are required"}), 400
    
    user = User.query.filter_by(reset_token=token).first()
    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
        return jsonify({"error": "Invalid or expired reset token"}), 400
    
    # Validate new password
    valid, msg = validate_password(new_password)
    if not valid:
        return jsonify({"error": msg}), 400
    
    # Update password
    user.password = generate_password_hash(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    user.failed_attempts = 0
    user.locked_until = None
    db.session.commit()
    
    return jsonify({"msg": "Password reset successfully"}), 200


# ────────────────────────────────────────────────
# EMAIL VERIFICATION ENDPOINTS
# ────────────────────────────────────────────────

@app.route("/api/send-verification", methods=["POST"])
@jwt_required()
@limiter.limit("3 per minute")
def send_verification():
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if user.email_verified:
        return jsonify({"msg": "Email already verified"}), 200
    
    # Generate verification token
    verification_token = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
    user.verification_token = verification_token
    db.session.commit()
    
    # In production, send email here. For now, return token for testing
    return jsonify({
        "msg": "Verification email sent",
        "verification_token": verification_token  # Remove this in production
    }), 200


@app.route("/api/verify-email", methods=["POST"])
@limiter.limit("10 per minute")
def verify_email():
    data = request.get_json(silent=True) or {}
    token = sanitize(data.get("token", ""))
    
    if not token:
        return jsonify({"error": "Verification token is required"}), 400
    
    user = User.query.filter_by(verification_token=token).first()
    if not user:
        return jsonify({"error": "Invalid verification token"}), 400
    
    user.email_verified = True
    user.verification_token = None
    db.session.commit()
    
    return jsonify({"msg": "Email verified successfully"}), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)
