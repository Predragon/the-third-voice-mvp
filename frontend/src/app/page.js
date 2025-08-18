'use client';

import { useEffect, useState } from 'react';

export default function Home() {
  const [messages, setMessages] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/messages')
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          setError(data.error);
        } else {
          setMessages(data);
        }
      })
      .catch(err => setError(err.message));
  }, []);

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div>
      <h1>The Third Voice AI</h1>
      {messages.map(msg => (
        <div key={msg.id}>
          <p><strong>Message:</strong> {msg.content}</p>
          <p><strong>AI Response:</strong> {msg.ai_response ? msg.ai_response.ai_response : 'No AI response'}</p>
          <hr />
        </div>
      ))}
    </div>
  );
}
