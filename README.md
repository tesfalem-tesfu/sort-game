# Sorting Quiz Game

A fun, interactive sorting game where players arrange items (numbers, letters, days) in the correct order. Built with Flask (Python) backend and Next.js (TypeScript) frontend.

## Features

- **JWT Authentication** — Secure user registration and login
- **Multiple Question Types** — Numbers (ascending/descending), letters, days of the week 
- **Real-time Scoring** — Track score, streak, and high score
- **Lives System** — 3 lives per game
- **Timer** — 30 seconds per question (auto-submits at 0)
- **Sound Effects** — Web Audio API tones (no files needed)
- **Dark/Light Mode** — Theme toggle
- **Responsive Design** — Works on mobile and desktop
- **Smooth Animations** — Framer Motion for polished UX

## Tech Stack

**Backend:**
- Flask (Python web framework)
- MySQL (database)
- Flask-JWT-Extended (authentication)
- Flask-CORS (cross-origin support)
- Flask-Limiter (rate limiting)
- SQLAlchemy (ORM)

**Frontend:**
- Next.js 14 (React framework)
- TypeScript
- Bootstrap 5 (styling)
- Framer Motion (animations)
- Canvas Confetti (celebration effects)
- next-themes (dark mode)

## Prerequisites

- Python 3.8+
- Node.js 18+
- MySQL 8.0+

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd sorting-quiz-game
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. MySQL Database Setup

```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE sorting_quiz;
EXIT;
```

### 4. Configure Backend Environment

Edit `backend/.env`:

```env
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=sorting_quiz
JWT_SECRET_KEY=your-super-secret-key-change-this
FRONTEND_ORIGIN=http://localhost:3000
```

### 5. Run Backend

```bash
# Make sure you're in backend/ with venv activated
python app.py
```

Backend will run on `http://127.0.0.1:5000`

The database tables and 1100+ questions will be auto-seeded on first run.

### 6. Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install
```

### 7. Configure Frontend Environment

The file `frontend/.env.local` is already created with:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:5000
```

### 8. Run Frontend

```bash
npm run dev
```

Frontend will run on `http://localhost:3000`

## How to Play

1. **Home Page** — Solve a simple math CAPTCHA or click "Register Now"
2. **Register** — Create an account (email + password, min 8 chars)
3. **Login** — Sign in with your credentials
4. **Game** — 
   - Click an item to select it
   - Click another item to swap positions
   - Click "Submit Answer" when ready
   - You have 30 seconds per question
   - 3 lives total
   - +10 points per correct answer
   - Build streaks for bragging rights!

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/health` | No | Health check |
| POST | `/api/register` | No | Create account |
| POST | `/api/login` | No | Login |
| GET | `/api/game/questions` | Yes | Get questions |
| POST | `/api/game/submit` | Yes | Submit answer |

## Project Structure

```
sorting-quiz-game/
├── backend/
│   ├── app.py              # Main Flask app
│   ├── requirements.txt    # Python dependencies
│   ├── .env               # Environment config
│   └── instance/          # SQLite (not used, MySQL instead)
├── frontend/
│   ├── app/
│   │   ├── page.tsx       # Home (CAPTCHA)
│   │   ├── layout.tsx     # Root layout
│   │   ├── login/         # Login page
│   │   ├── register/      # Register page
│   │   └── game/          # Game page
│   ├── public/
│   │   └── images/        # Background images
│   ├── package.json
│   └── .env.local         # Frontend config
└── README.md
```

## Security Features

- Password hashing (Werkzeug)
- JWT tokens (1-hour expiry)
- Rate limiting (5 register/min, 10 login/min, 60 submit/min)
- CORS protection
- Security headers (X-Frame-Options, HSTS, etc.)
- SQL injection protection (SQLAlchemy ORM)

## Known Limitations

- No email verification (users are auto-verified)
- No password reset
- No user profile page
- Leaderboard not implemented
- Sound effects are basic Web Audio tones

## Future Improvements

- Add drag-and-drop sorting
- Add difficulty levels
- Add global leaderboard
- Add daily challenges
- Add more question categories (colors, countries, etc.)
- Add power-ups (skip, extra time, hints)
- Add user statistics dashboard
- Add social sharing with images

## Deployment Guide

### 1. Database Setup (MySQL)

**Local Development:**
```bash
# Install MySQL
sudo apt install mysql-server  # Ubuntu/Debian
brew install mysql             # macOS
# Download from mysql.com      # Windows

# Start MySQL service
sudo systemctl start mysql
sudo systemctl enable mysql

# Create database and user
mysql -u root -p
CREATE DATABASE sorting_quiz;
CREATE USER 'sorting_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON sorting_quiz.* TO 'sorting_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

**Production (Cloud Options):**
- **AWS RDS**: Create MySQL instance, note endpoint
- **Google Cloud SQL**: Create MySQL instance  
- **DigitalOcean**: Managed MySQL Database
- **Heroku**: ClearDB MySQL add-on

### 2. Backend Deployment

**Option A: Traditional Server (VPS/Dedicated)**
```bash
# On server
git clone <your-repo-url>
cd sorting-quz-game/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with production values:
# MYSQL_HOST=your-db-endpoint
# MYSQL_USER=sorting_user
# MYSQL_PASSWORD=secure_password
# JWT_SECRET_KEY=your-super-secret-jwt-key-256-bits

# Initialize database
python -c "from app import app, db; with app.app_context(): db.create_all()"

# Install Gunicorn for production
pip install gunicorn

# Start with Gunicorn
gunicorn --bind 0.0.0.0:5000 app:app
```

**Option B: Docker**
```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

```bash
# Build and run
docker build -t sorting-backend .
docker run -p 5000:5000 --env-file .env sorting-backend
```

**Option C: PaaS (Heroku, Railway, etc.)**
```bash
# Heroku example
heroku create your-app-name
heroku config:set JWT_SECRET_KEY=your-secret-key
heroku config:set DATABASE_URL=mysql://user:pass@host:port/db
git push heroku main
```

### 3. Frontend Deployment

**Option A: Vercel (Recommended)**
```bash
# Install Vercel CLI
npm i -g vercel

# In frontend directory
cd frontend
vercel --prod

# Set environment variable in Vercel dashboard
# NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

**Option B: Netlify**
```bash
# Build frontend
cd frontend
npm run build

# Deploy build folder to Netlify
# Or use Netlify CLI
npm i -g netlify-cli
netlify deploy --prod --dir=out
```

**Option C: Traditional Server**
```bash
# Build frontend
cd frontend
npm run build

# Serve with nginx (example config)
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        root /path/to/frontend/out;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Option D: Docker**
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
COPY --from=builder /app/out ./out
COPY package*.json ./
RUN npm ci --only=production
EXPOSE 3000
CMD ["npm", "start"]
```

### 4. Production Checklist

**Security:**
- [ ] Change default JWT secret key
- [ ] Use HTTPS (SSL certificate)
- [ ] Set up firewall rules
- [ ] Use environment variables for secrets
- [ ] Enable database backups

**Performance:**
- [ ] Use production WSGI server (Gunicorn/uWSGI)
- [ ] Enable database connection pooling
- [ ] Set up CDN for static assets
- [ ] Configure caching headers
- [ ] Monitor server resources

**Monitoring:**
- [ ] Set up error logging
- [ ] Monitor database performance
- [ ] Set up uptime monitoring
- [ ] Configure backup alerts

### 5. Environment Variables

**Backend (.env):**
```bash
# Database
MYSQL_HOST=your-db-host
MYSQL_USER=your-db-user
MYSQL_PASSWORD=your-db-password
MYSQL_DB=sorting_quiz
MYSQL_PORT=3306

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key-256-bits-minimum

# Optional
FLASK_ENV=production
```

**Frontend (.env.local):**
```bash
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
```

## Troubleshooting

**Backend won't start:**
- Check MySQL is running: `mysql -u root -p`
- Verify database exists: `SHOW DATABASES;`
- Check `.env` credentials are correct

**Frontend can't connect:**
- Verify backend is running on port 5000
- Check browser console for CORS errors
- Verify `.env.local` has correct API URL

**401 Unauthorized errors:**
- Token expired (1 hour) — logout and login again
- Token not sent — check localStorage has `token` key

## License

MIT

## Author

Built with ❤️ in Addis Ababa, Ethiopia
