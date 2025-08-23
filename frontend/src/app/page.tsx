"use client";

import { useState } from "react";

export default function MainInterface() {
  const [messageText, setMessageText] = useState("");

  const handleSendMessage = () => {
    if (!messageText.trim()) return;
    console.log("Sending message:", messageText);
    setMessageText("");
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      {/* Header */}
      <header className="p-4 bg-white shadow-md sticky top-0 z-10">
        <h1 className="text-xl font-bold text-gray-800">The Third Voice</h1>
      </header>

      {/* Content Area */}
      <main className="flex-1 p-4 overflow-y-auto">
        <div className="space-y-4">
          <div className="bg-white rounded-2xl shadow-sm p-4">
            <p className="text-gray-700">Welcome to the app. Start typing below!</p>
          </div>
        </div>
      </main>

      {/* Input Area */}
      <div className="p-4 bg-white border-t">
        <textarea
          value={messageText}
          onChange={(e) => setMessageText(e.target.value)}
          placeholder="Type your message..."
          className="w-full p-4 border rounded-xl focus:ring-2 focus:ring-purple-500"
          rows={4}
        />

        <button
          onClick={handleSendMessage}
          className="mt-2 w-full bg-purple-600 text-white py-2 rounded-xl hover:bg-purple-700 disabled:opacity-50"
          disabled={!messageText.trim()}
        >
          Send
        </button>
      </div>
    </div>
  );
}
