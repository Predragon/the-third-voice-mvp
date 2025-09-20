// src/app/api/proxy/[...path]/route.ts
import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'edge';

// Primary = Pi via Cloudflare Tunnel
// Secondary = Render backup
const PRIMARY = 'https://api.thethirdvoice.ai';
const SECONDARY = 'https://the-third-voice-mvp.onrender.com';

// Shared edge-region-cached state (not globally persisted)
let isPrimaryHealthy = true;
let lastChecked = 0; // timestamp of last health check
let backendSince = Date.now(); // when the active backend last changed
const CHECK_INTERVAL = 30 * 1000; // 30s cache for health checks

// Retry / timeout config
const REQUEST_TIMEOUT_MS = 30_000; // 30s each proxied request
const MAX_RETRIES = 2;
const RETRY_BACKOFF_BASE_MS = 250; // exponential backoff base

// Headers we should strip before forwarding (host, connection, content-length are problematic)
const FORWARD_REMOVE_HEADERS = new Set([
  'host',
  'connection',
  'content-length',
  'transfer-encoding',
  'x-forwarded-for',
  'x-real-ip',
]);

/**
 * Do a cached health check of the PRIMARY (Pi) server.
 * Optionally you can pass the incoming request so query `?simulateDown=true` forces fallback.
 */
async function checkPrimaryHealth(req?: NextRequest) {
  const now = Date.now();

  // Testing override: ?simulateDown=true
  try {
    if (req?.url && req.url.includes('simulateDown=true')) {
      console.log('[proxy] simulateDown=true -> forcing primary down');
      isPrimaryHealthy = false;
      backendSince = now;
      lastChecked = now;
      return isPrimaryHealthy;
    }
  } catch (e) {
    // ignore
  }

  // Use cached value if within CHECK_INTERVAL
  if (now - lastChecked < CHECK_INTERVAL) return isPrimaryHealthy;

  lastChecked = now;
  try {
    // call primary health endpoint
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), 5000); // short health-check timeout (5s)
    const res = await fetch(`${PRIMARY}/api/health`, { method: 'GET', cache: 'no-store', signal: controller.signal });
    clearTimeout(id);

    const ok = res.ok;
    if (ok !== isPrimaryHealthy) {
      backendSince = now; // record switch time
      console.log(`[proxy] primary health changed: ${isPrimaryHealthy} -> ${ok}`);
    }
    isPrimaryHealthy = ok;
  } catch (err) {
    // network / timeout -> primary considered down
    if (isPrimaryHealthy) backendSince = now;
    isPrimaryHealthy = false;
    console.warn('[proxy] primary health check failed:', (err as Error).message);
  }

  return isPrimaryHealthy;
}

/**
 * Build headers for outgoing proxied request by copying incoming request headers
 * and removing problematic ones. Also set a safe User-Agent.
 */
function buildForwardHeaders(inHeaders: Headers) {
  const headers = new Headers();

  // copy allowed headers
  inHeaders.forEach((value, key) => {
    if (!FORWARD_REMOVE_HEADERS.has(key.toLowerCase())) {
      headers.set(key, value);
    }
  });

  // ensure sensible defaults
  if (!headers.get('accept')) headers.set('accept', 'application/json, text/*, */*');
  headers.set('user-agent', 'NextJS-Proxy'); // override User-Agent

  return headers;
}

/**
 * Fetch with timeout + retries + exponential backoff
 */
async function fetchWithRetries(url: string, init: RequestInit, timeoutMs = REQUEST_TIMEOUT_MS) {
  let attempt = 0;
  let lastErr: any = null;

  while (attempt <= MAX_RETRIES) {
    const controller = new AbortController();
    const signal = controller.signal;
    const timer = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const mergedInit: RequestInit = { ...init, signal };
      const res = await fetch(url, mergedInit);
      clearTimeout(timer);

      // treat HTTP 502/503/504 as retryable network errors
      if ([502, 503, 504].includes(res.status) && attempt < MAX_RETRIES) {
        attempt++;
        const delay = RETRY_BACKOFF_BASE_MS * 2 ** (attempt - 1);
        await new Promise(r => setTimeout(r, delay));
        continue;
      }

      // success (may be non-200 but it's a valid response)
      return res;
    } catch (err) {
      lastErr = err;
      clearTimeout(timer);

      // abort / network error -> retry if attempts left
      if (attempt < MAX_RETRIES) {
        const delay = RETRY_BACKOFF_BASE_MS * 2 ** attempt;
        await new Promise(r => setTimeout(r, delay));
        attempt++;
        continue;
      }

      // no attempts left -> throw
      throw err;
    }
  }

  // should never reach, but throw last error
  throw lastErr;
}

/**
 * Proxy handler: forwards request to selected backend and returns response back to client.
 */
async function handleRequest(req: NextRequest, method: string, params: Promise<{ path: string[] }>) {
  const resolved = await params;
  const pathSegments = resolved.path ?? [];
  // join path segments into path, remove trailing slashes
  const targetPath = pathSegments.join('/').replace(/\/+$/, '');

  // decide backend according to primary health
  const usePrimary = await checkPrimaryHealth(req);
  const baseUrl = usePrimary ? PRIMARY : SECONDARY;
  const url = `${baseUrl}/${targetPath}`;

  // keep query string
  const urlObj = new URL(url);
  try {
    const originalUrl = new URL(req.url);
    originalUrl.searchParams.forEach((v, k) => {
      // forward all query params except our simulateDown test param
      if (k !== 'simulateDown') urlObj.searchParams.set(k, v);
    });
  } catch {
    // ignore if parsing fails
  }

  const forwardUrl = urlObj.toString();
  console.log(`[proxy] ${method} -> ${forwardUrl} (primaryHealthy=${isPrimaryHealthy})`);

  // build headers
  const headers = buildForwardHeaders(req.headers);

  // body handling: we'll always attempt to forward body if present
  let body: BodyInit | undefined = undefined;
  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
    try {
      // try JSON first (works for common APIs)
      const contentType = req.headers.get('content-type') || '';
      if (contentType.includes('application/json')) {
        const json = await req.json();
        body = JSON.stringify(json);
        if (!headers.get('content-type')) headers.set('content-type', 'application/json');
      } else if (contentType.includes('application/x-www-form-urlencoded')) {
        const text = await req.text();
        body = text;
        if (!headers.get('content-type')) headers.set('content-type', contentType);
      } else {
        // fallback to arrayBuffer for binary / unknown
        const ab = await req.arrayBuffer();
        if (ab && ab.byteLength) {
          body = ab;
          if (!headers.get('content-type') && contentType) headers.set('content-type', contentType);
        }
      }
    } catch (e) {
      // If parsing fails, leave body undefined (backend will handle)
      console.warn('[proxy] body parse failed, forwarding without body:', (e as Error).message);
    }
  }

  const init: RequestInit = {
    method,
    headers,
    body,
    // no-store to avoid edge caches interfering with failover checks
    cache: 'no-store',
  };

  // perform fetch with retries/timeouts
  let response;
  try {
    response = await fetchWithRetries(forwardUrl, init, REQUEST_TIMEOUT_MS);
  } catch (err) {
    console.error('[proxy] final fetch failure:', (err as Error).message);
    return NextResponse.json(
      { error: 'Proxy fetch failed', message: (err as Error).message, attemptedUrl: forwardUrl },
      { status: 502, headers: { 'Access-Control-Allow-Origin': '*' } }
    );
  }

  // prepare headers to return to the client (copy backend response headers)
  const outHeaders = new Headers();
  response.headers.forEach((value, key) => {
    // strip hop-by-hop headers if present
    if (!FORWARD_REMOVE_HEADERS.has(key.toLowerCase())) outHeaders.set(key, value);
  });

  // Always include permissive CORS for browser clients (adjust if needed)
  outHeaders.set('Access-Control-Allow-Origin', '*');
  outHeaders.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS');
  outHeaders.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  outHeaders.set('Access-Control-Expose-Headers', 'Content-Type, Content-Length');

  // return body according to content-type
  const contentType = response.headers.get('content-type') || '';

  if (contentType.includes('application/json')) {
    const data = await response.json();
    return NextResponse.json(data, { status: response.status, headers: outHeaders });
  } else if (contentType.startsWith('text/') || contentType === '') {
    // text or no content-type => return as text
    const text = await response.text();
    return new NextResponse(text, { status: response.status, headers: outHeaders });
  } else {
    // binary (images, etc.)
    const buffer = await response.arrayBuffer();
    return new NextResponse(buffer, { status: response.status, headers: outHeaders });
  }
}

/**
 * App Router handlers
 */
export async function GET(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  const resolved = await ctx.params;

  // status endpoint: /api/proxy/status
  if (resolved.path.length === 1 && resolved.path[0] === 'status') {
    const now = Date.now();
    const uptimeMs = now - backendSince;
    const uptime = {
      days: Math.floor(uptimeMs / (1000 * 60 * 60 * 24)),
      hours: Math.floor((uptimeMs / (1000 * 60 * 60)) % 24),
      minutes: Math.floor((uptimeMs / (1000 * 60)) % 60),
    };

    return NextResponse.json({
      domain: 'thethirdvoice.ai',
      primaryHealthy: isPrimaryHealthy,
      currentBackend: isPrimaryHealthy ? 'Pi Server (primary)' : 'Render (secondary)',
      lastChecked: new Date(lastChecked).toISOString(),
      since: new Date(backendSince).toISOString(),
      uptime,
      checkIntervalSeconds: CHECK_INTERVAL / 1000,
      note: 'Use ?simulateDown=true to force primary down (for testing).',
    }, { status: 200, headers: { 'Access-Control-Allow-Origin': '*' } });
  }

  // otherwise proxy
  return handleRequest(req, 'GET', ctx.params);
}

export async function POST(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  return handleRequest(req, 'POST', ctx.params);
}
export async function PUT(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  return handleRequest(req, 'PUT', ctx.params);
}
export async function PATCH(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  return handleRequest(req, 'PATCH', ctx.params);
}
export async function DELETE(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  return handleRequest(req, 'DELETE', ctx.params);
}

// Preflight
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Max-Age': '86400',
    },
  });
}