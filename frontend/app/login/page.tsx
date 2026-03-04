"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";  // ← Added this!

export default function Login() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const savedEmail = localStorage.getItem("userEmail");
    const savedPassword = localStorage.getItem("userPassword");

    if (email === savedEmail && password === savedPassword) {
      localStorage.setItem("isLoggedIn", "true");
      router.push("/game");
    } else {
      setError("Invalid email or password");
    }
  };

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center bg-gradient-to-br from-blue-950 via-indigo-950 to-cyan-950 text-white">
      <div 
        className="glass-card p-5 p-md-5 rounded-4 shadow-2xl position-relative overflow-hidden"
        style={{ 
          maxWidth: "480px", 
          width: "90%",
          background: "rgba(30, 40, 70, 0.45)",
          backdropFilter: "blur(16px)",
          border: "1px solid rgba(100, 150, 255, 0.25)",
        }}
      >
        <h2 className="text-center fw-bold mb-5 fs-2 text-gradient">
          Welcome Back
        </h2>

        <form onSubmit={handleLogin} className="d-flex flex-column gap-4">
          <div className="form-floating">
            <input
              type="email"
              className="form-control bg-white/5 border-white/20 text-white shadow-sm"
              id="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoFocus
            />
            <label htmlFor="email" className="text-white-75">Email address</label>
          </div>

          <div className="form-floating">
            <input
              type="password"
              className="form-control bg-white/5 border-white/20 text-white shadow-sm"
              id="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <label htmlFor="password" className="text-white-75">Password</label>
          </div>

          {error && <div className="alert alert-danger text-center py-2 mb-0">{error}</div>}

          <button 
            type="submit" 
            className="btn btn-gradient btn-lg w-100 rounded-pill shadow-lg mt-2 py-3 fw-bold"
          >
            Login to Sorting Quest
          </button>
        </form>

        <p className="mt-4 text-center text-white-75">
          Don't have an account?{" "}
          <Link href="/register" className="text-info fw-semibold text-decoration-underline">
            Register now
          </Link>
        </p>
      </div>

      <style jsx global>{`
        .text-gradient {
          background: linear-gradient(90deg, #60a5fa, #a5b4fc, #c084fc);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }
        .btn-gradient {
          background: linear-gradient(135deg, #3b82f6, #6366f1, #8b5cf6);
          border: none;
          transition: all 0.3s ease;
        }
        .btn-gradient:hover {
          background: linear-gradient(135deg, #2563eb, #4f46e5, #7c3aed);
          transform: translateY(-3px);
          box-shadow: 0 15px 30px rgba(59, 130, 246, 0.4);
        }
        .glass-card {
          transition: all 0.4s ease;
        }
        .glass-card:hover {
          transform: translateY(-8px);
          box-shadow: 0 25px 60px rgba(0, 0, 0, 0.4);
        }
        .form-control {
          background: rgba(255,255,255,0.08) !important;
          border: 1px solid rgba(255,255,255,0.18) !important;
          color: white !important;
          transition: all 0.3s;
        }
        .form-control:focus {
          background: rgba(255,255,255,0.12) !important;
          border-color: #60a5fa !important;
          box-shadow: 0 0 0 0.25rem rgba(96, 165, 250, 0.25) !important;
        }
        .form-floating > label {
          color: rgba(255,255,255,0.75) !important;
        }
        .form-floating > .form-control:focus ~ label,
        .form-floating > .form-control:not(:placeholder-shown) ~ label {
          color: #60a5fa !important;
        }
      `}</style>
    </div>
  );
}