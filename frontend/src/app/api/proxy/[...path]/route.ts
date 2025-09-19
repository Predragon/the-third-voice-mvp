// src/app/api/proxy/[...path]/route.ts
import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'edge';

// Backends
const PRIMARY = 'https://api.thethirdvoice.ai'; // Pi (via Cloudflare Tunnel)
const SECONDARY = 'https://the-third-voice-mvp.onrender.com'; // Render backup

// Shared state (edge runtime: cached per Vercel region)
let isPrimaryHealthy = true;
let lastChecked = 0;
let backendSince = Date.now();
const CHECK_INTERVAL = 30 * 1000; // 30s

/**
 * Health check for Pi server only.
 * - If Pi healthy → route traffic there.
 * - If Pi fails → fallback to Render.
 * Render is not actively checked here, because:
 *   - keep-alive.yml keeps Render warm.
 *   - health-monitor.yml separately alerts you if Render is down.
 */
async function checkPrimaryHealth(req?: NextRequest) {
  const now = Date.now();

  // Manual failover testing with ?simulateDown=true
  if (req?.url.includes('simulateDown=true')) {
    isPrimaryHealthy = false;
    backendSince = now;
    lastChecked = now;
    return isPrimaryHealthy;
  }

  // Cache health check result for CHECK_INTERVAL
  if (now - lastChecked < CHECK_INTERVAL) return isPrimaryHealthy;

  lastChecked = now;
  try {
    const res = await fetch(`${PRIMARY}/health`, {
      cache: 'no-store',
      method: 'GET',
    });
    const newStatus = res.ok;

    if (newStatus !== isPrimaryHealthy) backendSince = now;
    isPrimaryHealthy = newStatus;
  } catch {
    if (isPrimaryHealthy) backendSince = now;
    isPrimaryHealthy = false;
  }
  return isPrimaryHealthy;
}

/**
 * Core proxy logic
 */
async function handleRequest(
  req: NextRequest,
  method: string,
  params: Promise<{ path: string[] }>
) {
  const resolvedParams = await params;
  let targetPath = resolvedParams.path.join('/').replace(/\/+$/, '');

  // Shortcut for docs (optional)
  if (resolvedParams.path[0] === 'docs') targetPath = 'docs';

  // Pick backend
  const usePrimary = await checkPrimaryHealth(req);
  const baseUrl = usePrimary ? PRIMARY : SECONDARY;
  const url = `${baseUrl}/${targetPath}`;

  console.log(`[Proxy] ${method} → ${url}`);

  try {
    const init: RequestInit = {
      method,
      headers: new Headers(req.headers),
      cache: 'no-store',
    };
    init.headers.set('User-Agent', 'NextJS-Proxy');

    if (['POST', 'PUT', 'PATCH'].includes(method)) {
      init.body = JSON.stringify(await req.json());
    }

    const response = await fetch(url, init);

    const responseHeaders = new Headers();
    response.headers.forEach((value, key) =>
      responseHeaders.set(key, value)
    );
    responseHeaders.set('Access-Control-Allow-Origin', '*');
    responseHeaders.set(
      'Access-Control-Allow-Methods',
      'GET, POST, PUT, DELETE, PATCH, OPTIONS'
    );
    responseHeaders.set(
      'Access-Control-Allow-Headers',
      'Content-Type, Authorization'
    );

    const contentType = response.headers.get('content-type');
    if (contentType?.includes('application/json')) {
      return NextResponse.json(await response.json(), {
        status: response.status,
        headers: responseHeaders,
      });
    } else if (contentType?.includes('text/')) {
      return new NextResponse(await response.text(), {
        status: response.status,
        headers: responseHeaders,
      });
    } else {
      return new NextResponse(await response.arrayBuffer(), {
        status: response.status,
        headers: responseHeaders,
      });
    }
  } catch (error) {
    console.error(`[Proxy Error] ${method} ${url}:`, error);
    return NextResponse.json(
      {
        error: 'Proxy request failed',
        message: (error as Error).message,
        url,
      },
      { status: 500, headers: { 'Access-Control-Allow-Origin': '*' } }
    );
  }
}

// Handlers
export async function GET(
  req: NextRequest,
  ctx: { params: Promise<{ path: string[] }> }
) {
  const resolvedParams = await ctx.params;

  // Custom proxy status endpoint
  if (resolvedParams.path.length === 1 && resolvedParams.path[0] === 'status') {
    const now = Date.now();
    const uptimeMs = now - backendSince;
    const uptime = {
      days: Math.floor(uptimeMs / (1000 * 60 * 60 * 24)),
      hours: Math.floor((uptimeMs / (1000 * 60 * 60)) % 24),
      minutes: Math.floor((uptimeMs / (1000 * 60)) % 60),
    };

    return NextResponse.json({
      primaryHealthy: isPrimaryHealthy,
      currentBackend: isPrimaryHealthy ? 'Pi Server' : 'Render',
      lastChecked: new Date(lastChecked).toISOString(),
      since: new Date(backendSince).toISOString(),
      uptime,
      checkIntervalSeconds: CHECK_INTERVAL / 1000,
    });
  }

  return handleRequest(req, 'GET', ctx.params);
}

export async function POST(
  req: NextRequest,
  ctx: { params: Promise<{ path: string[] }> }
) {
  return handleRequest(req, 'POST', ctx.params);
}

export async function PUT(
  req: NextRequest,
  ctx: { params: Promise<{ path: string[] }> }
) {
  return handleRequest(req, 'PUT', ctx.params);
}

export async function DELETE(
  req: NextRequest,
  ctx: { params: Promise<{ path: string[] }> }
) {
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
