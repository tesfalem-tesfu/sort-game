"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000";

export default function Login() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await fetch(`${API}/api/login`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.msg || "Login failed");
        return;
      }
      // Store JWT token
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("userEmail", data.email);

      router.push("/select");
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
          Welcome Back
        </h2>

        <form onSubmit={handleLogin} className="d-flex flex-column gap-4">
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
              placeholder="Your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <label htmlFor="password">Password</label>
          </div>

          {error && <div className="alert alert-danger text-center py-2 mb-0">{error}</div>}

          <button
            type="submit"
            className="btn btn-gradient btn-lg w-100 rounded-pill mt-2 py-3 fw-bold"
            disabled={loading}
          >
            {loading ? "Logging in..." : "Login to Sorting Quest"}
          </button>

          <div className="text-center mt-3">
            <Link href="/reset-password" className="text-info text-decoration-none">
              Forgot your password?
            </Link>
          </div>
        </form>

        <p className="mt-4 text-center text-white-50">
          Don&apos;t have an account?{" "}
          <Link href="/register" className="text-info fw-semibold">
            Register now
          </Link>
        </p>
      </div>
    </div>
  );
}
