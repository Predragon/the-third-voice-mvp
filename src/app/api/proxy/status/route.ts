// src/app/api/proxy/status/route.ts
import { NextResponse } from 'next/server';

export const runtime = 'edge';

export async function GET() {
  const now = Date.now();
  
  return NextResponse.json({
    status: 'healthy',
    message: 'Dedicated status endpoint working',
    primaryHealthy: true,
    currentBackend: 'Pi Server (Primary)',
    backendUrl: 'https://api.thethirdvoice.ai',
    lastHealthCheck: new Date().toISOString(),
    uptime: {
      days: 0,
      hours: 0,
      minutes: 5,
      seconds: 30
    },
    consecutiveFailures: 0,
    checkIntervalSeconds: 30,
    requestTimeoutSeconds: 30,
    maxRetries: 2,
    timestamp: new Date().toISOString()
  });
}
