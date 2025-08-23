"use client";

import React from 'react';

export default function TestPage() {
  return (
    <div className="min-h-screen bg-blue-50 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          🚀 Build Test Success!
        </h1>
        <p className="text-gray-600 mb-4">
          If you can see this page, your Next.js build is working correctly.
        </p>
        <div className="bg-green-100 p-4 rounded-lg">
          <p className="text-green-800 font-medium">
            ✅ No TypeScript errors<br/>
            ✅ No ESLint warnings<br/>
            ✅ Build completed successfully
          </p>
        </div>
        <p className="text-sm text-gray-500 mt-4">
          Replace this file with your actual app when ready.
        </p>
      </div>
    </div>
  );
}
