// app/debug/page.tsx
export default function DebugPage() {
  return (
    <div className="min-h-screen bg-gray-900 text-green-300 p-8">
      <h1 className="text-2xl font-bold mb-4">🔍 Debug Dashboard</h1>
      
      <div className="space-y-2">
        <p><strong>NEXT_PUBLIC_API_URL:</strong> {process.env.NEXT_PUBLIC_API_URL}</p>
        
        <div className="mt-4 space-x-4">
          <a href={`${process.env.NEXT_PUBLIC_API_URL}/openapi.json`} className="underline text-blue-400">Test /openapi.json</a>
          <a href={`${process.env.NEXT_PUBLIC_API_URL}/docs`} className="underline text-blue-400">Test /docs</a>
          <a href={`${process.env.NEXT_PUBLIC_API_URL}/health`} className="underline text-blue-400">Test /health</a>
          <a href={`${process.env.NEXT_PUBLIC_API_URL}/predict`} className="underline text-blue-400">Test /predict</a>
        </div>
      </div>

      <div className="mt-8 p-4 bg-green-800 rounded-xl shadow">
        <p className="text-lg">📡 Results</p>
        <p className="text-xl font-semibold">💙 The Third Voice is alive — for Samantha, and for every family. 🕊️</p>
      </div>
    </div>
  );
}
