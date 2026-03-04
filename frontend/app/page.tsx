"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link"; // ← Added only this import for navigation

export default function Home() {
  const router = useRouter();

  const [num1, setNum1] = useState(0);
  const [num2, setNum2] = useState(0);
  const [answer, setAnswer] = useState("");
  const [error, setError] = useState("");

  // Generate random numbers ONLY on client after mount
  useEffect(() => {
    setNum1(Math.floor(Math.random() * 20) + 1);
    setNum2(Math.floor(Math.random() * 20) + 1);
  }, []);

  const correctAnswer = num1 + num2;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (parseInt(answer.trim()) === correctAnswer) {
      router.push("/register");
    } else {
      setError("Incorrect – are you human? Try again.");
      setAnswer("");
    }
  };

  // Show loading until numbers are generated
  if (num1 === 0 || num2 === 0) {
    return (
      <div className="min-vh-100 d-flex align-items-center justify-content-center bg-gradient-to-br from-indigo-950 via-purple-950 to-fuchsia-950">
        <div className="spinner-border text-light" style={{ width: "4rem", height: "4rem" }} />
      </div>
    );
  }

  return (
    <div 
      className="min-vh-100 d-flex align-items-center justify-content-center text-white"
      style={{
        backgroundImage: "url('/images/home.jpg')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        backgroundAttachment: "fixed",
      }}
    >
      <div className="glass-card p-5 p-md-5 rounded-4 shadow-2xl text-center" style={{ maxWidth: "600px", width: "90%", background: "rgba(30, 30, 60, 0.75)" }}>
        <h1 className="display-4 fw-bold mb-4 text-gradient">Enjoy Sorting Daily</h1>

        <p className="lead mb-5">
          Prove you're human to continue
        </p>

        <div className="mb-4 p-4 bg-white/10 rounded-3 border border-white/20">
          <h4 className="mb-3">Human or Machine?</h4>
          <p className="fs-3 fw-bold">
            {num1} + {num2} = ?
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <input
            type="number"
            className="form-control form-control-lg bg-white/10 border-white/30 text-white mb-4 text-center fs-4"
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Your answer"
            required
            autoFocus
          />

          {error && <p className="text-danger mb-4 fs-5">{error}</p>}

          <button type="submit" className="btn btn-gradient btn-lg w-100 rounded-pill shadow-lg">
            I'm Human – Continue
          </button>
        </form>

        {/* Added Register button */}
        <Link href="/register">
          <button className="btn btn-outline-light btn-lg w-100 rounded-pill shadow-lg mt-3 py-3 fw-bold">
            Register Now
          </button>
        </Link>

        <p className="mt-4 text-white-50">
          Already registered? <a href="/login" className="text-info">Login here</a>
        </p>
      </div>

      <style jsx global>{`
        .text-gradient {
          background: linear-gradient(90deg, #a78bfa, #ec4899, #22d3ee);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }
        .btn-gradient {
          background: linear-gradient(135deg, #6366f1, #ec4899);
          border: none;
        }
        .btn-gradient:hover {
          background: linear-gradient(135deg, #4f46e5, #db2777);
          transform: translateY(-4px);
          box-shadow: 0 20px 40px rgba(99, 102, 241, 0.5);
        }
        .glass-card {
          background: rgba(30, 30, 60, 0.75);
          backdrop-filter: blur(20px);
          border: 1px solid rgba(255, 255, 255, 0.08);
        }
      `}</style>
    </div>
  );
}