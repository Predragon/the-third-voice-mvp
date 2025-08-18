import { useState } from 'react';

export default function Home() {
  const [message, setMessage] = useState('');
  const [context, setContext] = useState('romantic');
  const [result, setResult] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await fetch('/api/coach', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, context }),
    });
    const data = await res.json();
    setResult(data.refined);
  };

  return (
    <div>
      <h1>🎙️ The Third Voice</h1>
      <form onSubmit={handleSubmit}>
        <textarea value={message} onChange={(e) => setMessage(e.target.value)} />
        <select value={context} onChange={(e) => setContext(e.target.value)}>
          {Object.keys(prompts).map((ctx) => <option key={ctx} value={ctx}>{ctx}</option>)}
        </select>
        <button type="submit">Refine</button>
      </form>
      {result && <p>{result}</p>}
    </div>
  );
}
