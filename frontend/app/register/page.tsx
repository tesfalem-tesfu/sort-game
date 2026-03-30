"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000";

export default function Register() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${API}/api/register`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.msg || "Registration failed");
        return;
      }

      // Store JWT token
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("userEmail", data.email);

      setSuccess("Registration successful! Redirecting...");
      setTimeout(() => router.push("/select"), 1500);
    } catch {
      setError("Cannot connect to server. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center text-white page-content">
      <div className="glass-card p-5" style={{ maxWidth: "480px", width: "90%" }}>
        <h2 className="text-center fw-bold mb-5 fs-2 text-gradient">
          Create Your Account
        </h2>

        <form onSubmit={handleRegister} className="d-flex flex-column gap-4">
          <div className="form-floating">
            <input
              type="email"
              className="form-control"
              id="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoFocus
            />
            <label htmlFor="email">Email address</label>
          </div>

          <div className="form-floating">
            <input
              type="password"
              className="form-control"
              id="password"
              placeholder="At least 8 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <label htmlFor="password">Password</label>
          </div>

          {/* Password strength hints */}
          {password.length > 0 && (
            <div className="d-flex flex-column gap-1 px-1" style={{ fontSize: "0.8rem" }}>
              {[
                { ok: password.length >= 8,            label: "At least 8 characters" },
                { ok: /[A-Z]/.test(password),          label: "One uppercase letter" },
                { ok: /\d/.test(password),             label: "One number" },
                { ok: /[!@#$%^&*(),.?\":{}|<>_\-]/.test(password), label: "One special character" },
              ].map(({ ok, label }) => (
                <span key={label} style={{ color: ok ? "#22c55e" : "rgba(255,255,255,0.5)" }}>
                  {ok ? "✓" : "○"} {label}
                </span>
              ))}
            </div>
          )}

          <div className="form-floating">
            <input
              type="password"
              className="form-control"
              id="confirmPassword"
              placeholder="Re-enter your password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
            <label htmlFor="confirmPassword">Confirm Password</label>
          </div>

          {error && <div className="alert alert-danger text-center py-2 mb-0">{error}</div>}
          {success && <div className="alert alert-success text-center py-2 mb-0">{success}</div>}

          <button
            type="submit"
            className="btn btn-gradient btn-lg w-100 rounded-pill mt-2 py-3 fw-bold"
            disabled={loading}
          >
            {loading ? "Registering..." : "Register Now"}
          </button>
        </form>

        <p className="mt-4 text-center text-white-50">
          Already have an account?{" "}
          <Link href="/login" className="text-info fw-semibold">
            Login here
          </Link>
        </p>
      </div>
    </div>
  );
}
