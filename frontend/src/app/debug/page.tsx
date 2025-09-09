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
    <div
      style={{
        minHeight: "100vh",
        padding: "2rem",
        fontFamily: "monospace",
        background: "#000",   // 🌑 dark background
        color: "#0f0",        // 🟢 green terminal-style text
      }}
    >
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
            }}
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
            background: "#111",
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
                background: "#000",
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
