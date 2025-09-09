export default function DebugPage() {
  return (
    <div style={{ padding: "2rem", fontFamily: "monospace" }}>
      <h1>🔍 Debug Page</h1>
      <p>
        <strong>NEXT_PUBLIC_API_URL:</strong>{" "}
        {process.env.NEXT_PUBLIC_API_URL || "❌ Not defined"}
      </p>
    </div>
  );
}
