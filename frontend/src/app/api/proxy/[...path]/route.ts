// src/api/proxy/[...path]/route.ts
import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'edge';

// Define your backends
const PRIMARY = 'https://api.thethirdvoice.ai'; // Pi (via Cloudflare Tunnel)
const SECONDARY = 'https://the-third-voice-mvp.onrender.com'; // Render backup

// Shared state (edge runtime: cached per region, not persisted globally)
let isPrimaryHealthy = true;
let lastChecked = 0;
let backendSince = Date.now(); // <-- tracks when backend last switched
const CHECK_INTERVAL = 30 * 1000; // 30s

async function checkPrimaryHealth() {
  const now = Date.now();
  if (now - lastChecked < CHECK_INTERVAL) return isPrimaryHealthy; // cached

  lastChecked = now;
  try {
    const res = await fetch(`${PRIMARY}/api/health`, { cache: 'no-store', method: 'GET' });
    const newStatus = res.ok;

    // If backend health changes, update since time
    if (newStatus !== isPrimaryHealthy) {
      backendSince = now;
    }

    isPrimaryHealthy = newStatus;
  } catch {
    if (isPrimaryHealthy) {
      backendSince = now;
    }
    isPrimaryHealthy = false;
  }
  return isPrimaryHealthy;
}

async function handleRequest(
  req: NextRequest,
  method: string,
  params: Promise<{ path: string[] }>
) {
  const resolvedParams = await params;
  let targetPath = resolvedParams.path.join('/').replace(/\/+$/, '');

  if (resolvedParams.path[0] === 'docs') {
    targetPath = 'docs';
  }

  // Pick backend based on health
  const usePrimary = await checkPrimaryHealth();
  const baseUrl = usePrimary ? PRIMARY : SECONDARY;
  const url = `${baseUrl}/${targetPath}`;

  console.log(`Proxying ${method} to: ${url}`);

  try {
    const init: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': req.headers.get('user-agent') || 'NextJS-Proxy',
      },
      cache: 'no-store',
    };

    if (['POST', 'PUT', 'PATCH'].includes(method)) {
      init.body = JSON.stringify(await req.json());
    }

    const response = await fetch(url, init);

    const responseHeaders = new Headers();
    response.headers.forEach((value, key) => responseHeaders.set(key, value));
    responseHeaders.set('Access-Control-Allow-Origin', '*');
    responseHeaders.set(
      'Access-Control-Allow-Methods',
      'GET, POST, PUT, DELETE, PATCH, OPTIONS'
    );
    responseHeaders.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');

    const contentType = response.headers.get('content-type');
    if (contentType?.includes('application/json')) {
      return NextResponse.json(await response.json(), { status: response.status, headers: responseHeaders });
    } else if (contentType?.includes('text/')) {
      return new NextResponse(await response.text(), { status: response.status, headers: responseHeaders });
    } else {
      return new NextResponse(await response.arrayBuffer(), { status: response.status, headers: responseHeaders });
    }
  } catch (error) {
    console.error(`${method} Proxy error for ${url}:`, error);
    return NextResponse.json(
      { error: 'Proxy request failed', message: (error as Error).message, url },
      { status: 500, headers: { 'Access-Control-Allow-Origin': '*' } }
    );
  }
}

// Handlers
export async function GET(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  const resolvedParams = await ctx.params;

  // Handle /api/proxy/status
  if (resolvedParams.path.length === 1 && resolvedParams.path[0] === 'status') {
    const now = Date.now();
    const uptimeMs = now - backendSince;
    const uptime = {
      days: Math.floor(uptimeMs / (1000 * 60 * 60 * 24)),
      hours: Math.floor((uptimeMs / (1000 * 60 * 60)) % 24),
      minutes: Math.floor((uptimeMs / (1000 * 60)) % 60),
    };

    return NextResponse.json({
      domain: "thethirdvoice.ai",
      primaryHealthy: isPrimaryHealthy,
      currentBackend: isPrimaryHealthy ? "Pi Server" : "Render",
      lastChecked: new Date(lastChecked).toISOString(),
      since: new Date(backendSince).toISOString(),
      uptime,
      checkIntervalSeconds: CHECK_INTERVAL / 1000,
    });
  }

  return handleRequest(req, 'GET', ctx.params);
}

export async function POST(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  return handleRequest(req, 'POST', ctx.params);
}
export async function PUT(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  return handleRequest(req, 'PUT', ctx.params);
}
export async function DELETE(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  return handleRequest(req, 'DELETE', ctx.params);
}

// Preflight requests
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Max-Age': '86400',
    },
  });
}