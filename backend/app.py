from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os
import random
import string

# ────────────────────────────────────────────────
# INIT
# ────────────────────────────────────────────────

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY") or "super-secret-change-this"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600

CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

db = SQLAlchemy(app)
jwt = JWTManager(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# ────────────────────────────────────────────────
# MODELS
# ────────────────────────────────────────────────


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    verified = db.Column(db.Boolean, default=True)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(300), nullable=False)
    items = db.Column(db.String(1000), nullable=False)
    answer = db.Column(db.String(1000), nullable=False)
    category = db.Column(db.String(50), default="general")


# ────────────────────────────────────────────────
# DATABASE + SEEDING
# ────────────────────────────────────────────────

with app.app_context():
    db.create_all()

    if not User.query.filter_by(email="test@example.com").first():
        db.session.add(
            User(
                email="test@example.com",
                password=generate_password_hash("test123"),
                verified=True,
            )
        )

    if Question.query.count() < 100:
        print("Seeding 1000+ questions...")

        # Numbers ascending
        for _ in range(400):
            size = random.randint(4, 10)
            nums = random.sample(range(1, 1001), size)
            shuffled = nums[:]
            random.shuffle(shuffled)

            db.session.add(
                Question(
                    question="Sort these numbers in ascending order",
                    items=",".join(map(str, shuffled)),
                    answer=",".join(map(str, sorted(nums))),
                    category="numbers_asc",
                )
            )

        # Numbers descending
        for _ in range(300):
            size = random.randint(4, 10)
            nums = random.sample(range(1, 1001), size)
            shuffled = nums[:]
            random.shuffle(shuffled)

            db.session.add(
                Question(
                    question="Sort these numbers in descending order",
                    items=",".join(map(str, shuffled)),
                    answer=",".join(map(str, sorted(nums, reverse=True))),
                    category="numbers_desc",
                )
            )

        # Letters ascending
        for _ in range(200):
            size = random.randint(5, 12)
            letters = random.sample(string.ascii_lowercase, size)
            shuffled = letters[:]
            random.shuffle(shuffled)

            db.session.add(
                Question(
                    question="Sort these letters alphabetically",
                    items=",".join(shuffled),
                    answer=",".join(sorted(letters)),
                    category="letters_asc",
                )
            )

        # Letters descending
        for _ in range(150):
            size = random.randint(5, 12)
            letters = random.sample(string.ascii_lowercase, size)
            shuffled = letters[:]
            random.shuffle(shuffled)

            db.session.add(
                Question(
                    question="Sort these letters in reverse alphabetical order",
                    items=",".join(shuffled),
                    answer=",".join(sorted(letters, reverse=True)),
                    category="letters_desc",
                )
            )

        # Days of week
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        for _ in range(50):
            shuffled = days[:]
            random.shuffle(shuffled)

            db.session.add(
                Question(
                    question="Sort the days of the week correctly (start Monday)",
                    items=",".join(shuffled),
                    answer=",".join(days),
                    category="days",
                )
            )

        db.session.commit()
        print("Seeding complete:", Question.query.count())

# ────────────────────────────────────────────────
# SECURITY HEADERS
# ────────────────────────────────────────────────


@app.after_request
def security_headers(response):
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    return response


# ────────────────────────────────────────────────
# ROUTES
# ────────────────────────────────────────────────


@app.route("/api/health")
def health():
    return jsonify({"status": "healthy", "question_count": Question.query.count()})


@app.route("/api/register", methods=["POST"])
@limiter.limit("5 per minute")
def register():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"msg": "Email and password required"}), 400

    if len(password) < 8:
        return jsonify({"msg": "Password must be at least 8 characters"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already exists"}), 409

    user = User(
        email=email,
        password=generate_password_hash(password),
        verified=True,
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=email)
    return jsonify({"access_token": token})


@app.route("/api/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Invalid credentials"}), 401

    token = create_access_token(identity=email)
    return jsonify({"access_token": token})


# ✅ FIXED DYNAMIC QUESTIONS ROUTE
@app.route("/api/game/questions", methods=["GET"])
@jwt_required(optional=True)
def get_questions():
    limit = request.args.get("limit", type=int)
    category = request.args.get("category")

    query = Question.query

    if category:
        query = query.filter(Question.category == category)

    total_available = query.count()

    query = query.order_by(db.func.random())

    if limit and limit > 0:
        limit = min(limit, 2000)
        questions = query.limit(limit).all()
    else:
        questions = query.all()

    return jsonify(
        {
            "questions": [
                {
                    "id": q.id,
                    "question": q.question,
                    "items": q.items.split(","),
                    "category": q.category,
                }
                for q in questions
            ],
            "count": len(questions),
            "total_available": total_available,
        }
    )


@app.route("/api/game/submit", methods=["POST"])
@limiter.limit("20 per minute")
def submit():
    data = request.get_json(silent=True) or {}
    qid = data.get("id")
    user_answer_list = data.get("answer", [])

    if not qid:
        return jsonify({"msg": "Question ID required"}), 400

    question = Question.query.get(qid)
    if not question:
        return jsonify({"msg": "Question not found"}), 404

    user_answer = ",".join(str(x).strip() for x in user_answer_list)
    correct = user_answer == question.answer.strip()

    return jsonify(
        {
            "correct": correct,
            "correct_order": question.answer.split(","),
            "user_submitted": user_answer,
        }
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
