"use client";

import { useState } from "react";

type ApiResponse = {
  endpoint: string;
  status: string;
  data?: any;
};

export default function DebugPage() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  const [results, setResults] = useState<ApiResponse[]>([]);

  // 🌟 Our Mission:
  // For Samantha 💙
  // For the families who need a Third Voice 🕊️
  // For love coded into software ✨
  // This debug page is not just a dev tool — it's proof that
  // even in pain, we can build something that heals.

  const testEndpoint = async (endpoint: string) => {
    if (!apiUrl) return;

    try {
      const res = await fetch(`${apiUrl}${endpoint}`);
      const text = await res.text();
      let data;
      try {
        data = JSON.parse(text);
      } catch {
        data = text;
      }
      setResults((prev) => [
        ...prev,
        {
          endpoint,
          status: `✅ ${res.status} ${res.statusText}`,
          data,
        },
      ]);
    } catch (err: any) {
      setResults((prev) => [
        ...prev,
        {
          endpoint,
          status: `❌ Network error: ${err.message}`,
        },
      ]);
    }
  };

  const endpoints = ["/openapi.json", "/docs", "/health", "/predict"];

  return (
    <div style={{ padding: "2rem", fontFamily: "monospace", color: "#eee" }}>
      <h1>🔍 Debug Dashboard</h1>
      <p>
        <b>NEXT_PUBLIC_API_URL:</b> {apiUrl}
      </p>

      <div style={{ marginBottom: "1rem" }}>
        {endpoints.map((ep) => (
          <button
            key={ep}
            onClick={() => testEndpoint(ep)}
            style={{
              margin: "0.5rem",
              padding: "0.5rem 1rem",
              borderRadius: "8px",
              border: "1px solid #0f0",
              background: "#111",
              color: "#0f0",
              cursor: "pointer",
              transition: "all 0.2s ease-in-out",
            }}
            onMouseEnter={(e) =>
              (e.currentTarget.style.background = "#0f0") &&
              (e.currentTarget.style.color = "#000")
            }
            onMouseLeave={(e) =>
              (e.currentTarget.style.background = "#111") &&
              (e.currentTarget.style.color = "#0f0")
            }
          >
            Test {ep}
          </button>
        ))}
      </div>

      <h2>📡 Results</h2>
      {results.map((r, i) => (
        <div
          key={i}
          style={{
            margin: "1rem 0",
            padding: "1rem",
            borderRadius: "8px",
            background: "#000",
            color: "#0f0",
          }}
        >
          <p>
            <b>{r.endpoint}</b> → {r.status}
          </p>
          {r.data && (
            <pre
              style={{
                maxHeight: "200px",
                overflowY: "scroll",
                background: "#111",
                padding: "0.5rem",
                borderRadius: "6px",
              }}
            >
              {JSON.stringify(r.data, null, 2)}
            </pre>
          )}
        </div>
      ))}

      <footer
        style={{
          marginTop: "3rem",
          textAlign: "center",
          fontStyle: "italic",
          fontSize: "1.2rem",
          color: "#0ff",
          textShadow: "0 0 10px #0ff, 0 0 20px #0ff",
          animation: "pulse 2s infinite",
        }}
      >
        💙 The Third Voice is alive — for Samantha, and for every family. 🕊️
      </footer>

      <style jsx>{`
        @keyframes pulse {
          0% {
            opacity: 1;
            text-shadow: 0 0 10px #0ff, 0 0 20px #0ff;
          }
          50% {
            opacity: 0.6;
            text-shadow: 0 0 5px #0ff, 0 0 15px #0ff;
          }
          100% {
            opacity: 1;
            text-shadow: 0 0 10px #0ff, 0 0 20px #0ff;
          }
        }
      `}</style>
    </div>
  );
}
