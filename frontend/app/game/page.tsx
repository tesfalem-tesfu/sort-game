"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import confetti from "canvas-confetti";
import { Howl } from "howler";
import { useTheme } from "next-themes";

const sounds = {
  correct: new Howl({ src: ["/sounds/correct.mp3"], volume: 0.8 }),
  wrong: new Howl({ src: ["/sounds/wrong.mp3"], volume: 0.7 }),
  gameover: new Howl({ src: ["/sounds/gameover.mp3"], volume: 0.9 }),
};

type Question = {
  id: number;
  question: string;
  items: string[];
};

export default function Game() {
  const router = useRouter();
  const { theme, setTheme } = useTheme();

  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [items, setItems] = useState<string[]>([]);
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [feedback, setFeedback] = useState<"correct" | "wrong" | null>(null);
  const [correctOrder, setCorrectOrder] = useState<string[]>([]);
  const [showReveal, setShowReveal] = useState(false);
  const [score, setScore] = useState(0);
  const [lives, setLives] = useState(3);
  const [timeLeft, setTimeLeft] = useState(60);
  const [streak, setStreak] = useState(0);
  const [highScore, setHighScore] = useState(0);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [gameOver, setGameOver] = useState(false);

  // Persist sound toggle
  useEffect(() => {
    const saved = localStorage.getItem("soundEnabled");
    if (saved !== null) setSoundEnabled(saved === "true");
  }, []);

  useEffect(() => {
    localStorage.setItem("soundEnabled", String(soundEnabled));
  }, [soundEnabled]);

  // Streak & high score from localStorage
  useEffect(() => {
    const savedStreak = localStorage.getItem("streak") || "0";
    const savedHigh = localStorage.getItem("highScore") || "0";
    setStreak(Number(savedStreak));
    setHighScore(Number(savedHigh));
  }, []);

  // Login protection
  useEffect(() => {
    if (localStorage.getItem("isLoggedIn") !== "true") {
      router.replace("/login");
    }
  }, [router]);

  // Fetch questions
  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        const res = await fetch("http://127.0.0.1:5000/api/game/questions", {
          cache: "no-store",
        });
        const data = await res.json();
        setQuestions(data.questions || []);
        if (data.questions?.length) {
          setItems([...data.questions[0].items]);
        }
      } catch {
        setError("Cannot connect to backend.");
      } finally {
        setLoading(false);
      }
    };
    fetchQuestions();
  }, []);

  // Timer
  useEffect(() => {
    if (timeLeft > 0 && !feedback && !gameOver) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [timeLeft, feedback, gameOver]);

  // Reset question
  useEffect(() => {
    if (questions[currentIndex]) {
      setItems([...questions[currentIndex].items]);
      setFeedback(null);
      setCorrectOrder([]);
      setShowReveal(false);
      setTimeLeft(60);
      setSelectedIndex(null);
    }
  }, [currentIndex, questions]);

  const playSound = (type: "correct" | "wrong" | "gameover") => {
    if (!soundEnabled) return;
    sounds[type].play();
  };

  const handleItemClick = (index: number) => {
    if (feedback) return;
    if (selectedIndex === null) {
      setSelectedIndex(index);
    } else {
      const newItems = [...items];
      [newItems[selectedIndex], newItems[index]] = [newItems[index], newItems[selectedIndex]];
      setItems(newItems);
      setSelectedIndex(null);
    }
  };

  const submit = () => {
    const current = questions[currentIndex];
    if (!current) return;

    fetch("http://127.0.0.1:5000/api/game/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: current.id, answer: items }),
    })
      .then((res) => res.json())
      .then((data) => {
        const isCorrect = data.correct;
        setFeedback(isCorrect ? "correct" : "wrong");
        setCorrectOrder(data.correct_order || []);

        if (isCorrect) {
          const newScore = score + 10;
          setScore(newScore);
          setStreak((prev) => {
            const newStreak = prev + 1;
            localStorage.setItem("streak", String(newStreak));
            return newStreak;
          });
          confetti({ particleCount: 220, spread: 110, origin: { y: 0.6 } });
          playSound("correct");
        } else {
          setLives((prev) => prev - 1);
          setStreak(0);
          localStorage.setItem("streak", "0");
          playSound("wrong");
          setTimeout(() => setShowReveal(true), 700);
        }
      })
      .catch(() => setFeedback(null));

    setTimeout(() => {
      if (currentIndex < questions.length - 1 && lives > 0) {
        setCurrentIndex((prev) => prev + 1);
      } else {
        setGameOver(true);
        playSound("gameover");
        if (score > highScore) {
          setHighScore(score);
          localStorage.setItem("highScore", String(score));
        }
      }
    }, 3200);
  };

  const goToPrevious = () => {
    if (currentIndex > 0) setCurrentIndex(currentIndex - 1);
  };

  const goToNext = () => {
    if (currentIndex < questions.length - 1) setCurrentIndex(currentIndex + 1);
  };

  const logout = () => {
    localStorage.removeItem("isLoggedIn");
    router.replace("/login");
  };

  const shareScore = () => {
    const text = `I scored ${score} on Sorting Quest! Can you beat me? 🔥`;
    navigator.clipboard.writeText(text);
    alert("Score copied to clipboard! Paste it anywhere.");
  };

  if (loading) return <div className="min-vh-100 d-flex align-items-center justify-content-center text-white">Loading...</div>;

  if (error || !questions.length) {
    return <div className="text-center p-5 text-white">Error: {error || "No questions found"}</div>;
  }

  if (gameOver) {
    return (
      <div className="min-vh-100 d-flex flex-column align-items-center justify-content-center text-white p-5">
        <motion.h2
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-danger mb-4"
        >
          Game Over
        </motion.h2>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-center bg-dark bg-opacity-70 p-5 rounded shadow-lg"
        >
          <h3>Final Score: <span className="text-success">{score}</span></h3>
          <h5 className="mt-3">High Score: <span className="text-warning">{highScore}</span></h5>
          <p className="mt-2">Questions attempted: {questions.length}</p>
          <div className="d-flex gap-3 justify-content-center mt-4">
            <button className="btn btn-primary px-5" onClick={() => window.location.reload()}>
              Play Again
            </button>
            <button className="btn btn-outline-info px-4" onClick={shareScore}>
              Share Score
            </button>
          </div>
        </motion.div>
      </div>
    );
  }

  const currentQuestion = questions[currentIndex];
  const isFirst = currentIndex === 0;
  const isLast = currentIndex === questions.length - 1;
  const isLocked = !!feedback;

  return (
    <div
      className={`min-vh-100 text-white d-flex flex-column ${theme === "dark" ? "bg-dark" : "bg-light text-dark"}`}
      style={{
        backgroundImage: "url('/images/back.jpg')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
      }}
    >
      {/* Header */}
      <header className="d-flex flex-column flex-sm-row justify-content-between align-items-center p-3 bg-dark bg-opacity-80 gap-3">
        <h3>Sorting Quest</h3>
        <div className="d-flex flex-wrap gap-3 align-items-center">
          <span>Score: {score}</span>
          <span>Streak: <span className="text-warning">{streak} 🔥</span></span>
          <span>Lives: {lives}</span>
          <span>Time: {timeLeft}s</span>
          <button
            className="btn btn-sm btn-outline-secondary"
            onClick={() => setSoundEnabled(!soundEnabled)}
          >
            Sound: {soundEnabled ? "ON" : "OFF"}
          </button>
          <button
            className="btn btn-sm btn-outline-light"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            {theme === "dark" ? "☀️ Light" : "🌙 Dark"}
          </button>
          <button className="btn btn-sm btn-outline-danger" onClick={logout}>
            Logout
          </button>
        </div>
      </header>

      {/* Progress bar */}
      <div className="px-4 pt-2">
        <div className="progress bg-secondary" style={{ height: "8px" }}>
          <div
            className="progress-bar bg-info"
            style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
          />
        </div>
        <p className="text-center mt-1 small">
          Question {currentIndex + 1} / {questions.length}
        </p>
      </div>

      {/* Question with fade-in */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center p-4"
      >
        <h4 className="bg-dark bg-opacity-60 d-inline-block px-4 py-3 rounded shadow">
          {currentQuestion.question}
        </h4>
      </motion.div>

      {/* Items */}
      <motion.div
        className="d-flex flex-wrap justify-content-center gap-3 gap-sm-4 p-3 p-sm-4"
        animate={feedback === "wrong" && !showReveal ? { x: [0, -10, 10, -8, 0] } : {}}
        transition={{ duration: 0.5 }}
      >
        <AnimatePresence mode="popLayout">
          {items.map((item, index) => {
            const isCorrect = feedback === "correct";
            const isShake = feedback === "wrong" && !showReveal;
            const isReveal = feedback === "wrong" && showReveal;

            let bgClass = "bg-secondary bg-opacity-75 hover:bg-opacity-90";
            if (selectedIndex === index) bgClass = "bg-warning text-dark shadow-lg scale-110";
            if (isCorrect) bgClass = "bg-success text-white shadow-2xl scale-105";
            if (isShake) bgClass = "bg-danger text-white animate-pulse shadow-lg";
            if (isReveal) bgClass = "bg-info text-white shadow-2xl";

            return (
              <motion.div
                key={isReveal ? correctOrder[index] || item : item}
                layout
                initial={{ opacity: 0, y: 40, scale: 0.9 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, scale: 0.85, rotate: -5 }}
                transition={{ duration: 0.45, delay: index * 0.08 }}
                onClick={() => handleItemClick(index)}
                className={`px-4 py-3 rounded-xl shadow-md cursor-pointer text-base sm:text-lg font-medium text-center min-w-[110px] sm:min-w-[140px] md:min-w-[160px] ${bgClass}`}
                style={{ pointerEvents: isLocked ? "none" : "auto" }}
                whileHover={!isLocked ? { scale: 1.08, rotate: 2 } : {}}
                whileTap={!isLocked ? { scale: 0.95 } : {}}
              >
                {isReveal ? (correctOrder[index] ?? item) : item}
              </motion.div>
            );
          })}
        </AnimatePresence>
      </motion.div>

      {/* Controls */}
      <div className="d-flex flex-wrap justify-content-center gap-3 gap-sm-4 mb-4 px-3">
        <button
          className={`btn px-4 ${isFirst || isLocked ? "btn-outline-secondary opacity-50" : "btn-outline-primary"}`}
          onClick={goToPrevious}
          disabled={isFirst || isLocked}
        >
          ← Previous
        </button>

        <button
          className="btn btn-success px-5 py-2 shadow"
          onClick={submit}
          disabled={isLocked}
        >
          Submit
        </button>

        <button
          className={`btn px-4 ${isLast || isLocked ? "btn-outline-secondary opacity-50" : "btn-outline-info"}`}
          onClick={goToNext}
          disabled={isLast || isLocked}
        >
          Next →
        </button>
      </div>

      {/* Feedback */}
      <AnimatePresence>
        {feedback && (
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            className={`mx-4 mx-sm-5 mt-3 p-4 rounded shadow-lg text-center fw-bold fs-5
              ${feedback === "correct" ? "bg-success text-white" : "bg-danger text-white"}`}
          >
            {feedback === "correct" ? "Correct! +10 points 🎉" : "Wrong — correct order shown above"}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}