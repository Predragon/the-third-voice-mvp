// src/app/api/proxy/[...path]/route.ts
import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'edge';

// Backends
const PRIMARY = 'https://api.thethirdvoice.ai'; // Pi (via Cloudflare Tunnel)
const SECONDARY = 'https://the-third-voice-mvp.onrender.com'; // Render backup

// Configuration
const HEALTH_CHECK_INTERVAL = 30 * 1000; // 30s
const REQUEST_TIMEOUT = 30 * 1000; // 30s
const HEALTH_CHECK_TIMEOUT = 5 * 1000; // 5s
const MAX_RETRIES = 2;

// Headers that should not be forwarded
const BLOCKED_HEADERS = new Set([
  'host', 'connection', 'keep-alive', 'proxy-authenticate', 
  'proxy-authorization', 'te', 'trailer', 'upgrade'
]);

// Shared state (edge runtime: cached per Vercel region)
let isPrimaryHealthy = true;
let lastChecked = 0;
let backendSince = Date.now();
let consecutiveFailures = 0;

/**
 * Create timeout controller with cleanup
 */
function createTimeoutController(timeoutMs: number) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => {
    controller.abort();
  }, timeoutMs);
  
  return {
    controller,
    cleanup: () => clearTimeout(timeoutId)
  };
}

/**
 * Robust health check for Pi server only.
 */
async function checkPrimaryHealth(req?: NextRequest): Promise<boolean> {
  const now = Date.now();

  // Manual failover testing with ?simulateDown=true
  if (req?.url.includes('simulateDown=true')) {
    if (isPrimaryHealthy) {
      isPrimaryHealthy = false;
      backendSince = now;
      consecutiveFailures = 1;
    }
    lastChecked = now;
    return isPrimaryHealthy;
  }

  // Cache health check result for CHECK_INTERVAL
  if (now - lastChecked < HEALTH_CHECK_INTERVAL) {
    return isPrimaryHealthy;
  }

  lastChecked = now;
  const { controller, cleanup } = createTimeoutController(HEALTH_CHECK_TIMEOUT);

  try {
    const response = await fetch(`${PRIMARY}/health`, {
      method: 'GET',
      cache: 'no-store',
      signal: controller.signal,
      headers: {
        'User-Agent': 'NextJS-Proxy-HealthCheck'
      }
    });

    cleanup();
    const newStatus = response.ok && response.status < 400;

    if (newStatus !== isPrimaryHealthy) {
      backendSince = now;
      consecutiveFailures = newStatus ? 0 : consecutiveFailures + 1;
      console.log(`[Health Check] Primary backend ${newStatus ? 'recovered' : 'failed'}. Consecutive failures: ${consecutiveFailures}`);
    }

    isPrimaryHealthy = newStatus;
    if (newStatus) consecutiveFailures = 0;

  } catch (error) {
    cleanup();
    consecutiveFailures++;
    
    if (isPrimaryHealthy) {
      backendSince = now;
      console.log(`[Health Check] Primary backend failed: ${error instanceof Error ? error.message : 'Unknown error'}. Consecutive failures: ${consecutiveFailures}`);
    }
    
    isPrimaryHealthy = false;
  }

  return isPrimaryHealthy;
}

/**
 * Clean and filter headers for forwarding
 */
function createForwardHeaders(originalHeaders: Headers): Headers {
  const headers = new Headers();
  
  originalHeaders.forEach((value, key) => {
    const lowerKey = key.toLowerCase();
    if (!BLOCKED_HEADERS.has(lowerKey)) {
      headers.set(key, value);
    }
  });

  // Always set proxy User-Agent
  headers.set('User-Agent', 'NextJS-Proxy');
  
  return headers;
}

/**
 * Handle request body safely
 */
async function handleRequestBody(req: NextRequest, method: string, headers: Headers): Promise<BodyInit | null> {
  if (!['POST', 'PUT', 'PATCH'].includes(method)) {
    return null;
  }

  try {
    const contentType = req.headers.get('content-type')?.toLowerCase() || '';
    
    if (contentType.includes('application/json')) {
      const jsonData = await req.json();
      headers.set('Content-Type', 'application/json');
      return JSON.stringify(jsonData);
    } else if (contentType.includes('text/')) {
      const textData = await req.text();
      headers.set('Content-Type', contentType);
      return textData;
    } else if (contentType.includes('multipart/form-data') || contentType.includes('application/x-www-form-urlencoded')) {
      // For form data, pass through as-is
      const formData = await req.arrayBuffer();
      if (contentType) headers.set('Content-Type', contentType);
      return formData;
    } else {
      // Default: try to read as array buffer
      const buffer = await req.arrayBuffer();
      if (contentType) headers.set('Content-Type', contentType);
      return buffer;
    }
  } catch (error) {
    console.error('[Body Parse Error]:', error);
    throw new Error(`Invalid request body: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Make request with retries and circuit breaker logic
 */
async function makeRequestWithRetries(url: string, init: RequestInit, retries = MAX_RETRIES): Promise<Response> {
  let lastError: Error | null = null;
  
  for (let attempt = 0; attempt <= retries; attempt++) {
    const { controller, cleanup } = createTimeoutController(REQUEST_TIMEOUT);
    
    try {
      const response = await fetch(url, {
        ...init,
        signal: controller.signal
      });
      
      cleanup();
      
      // Don't retry on client errors (4xx), only server errors (5xx) and network issues
      if (response.status < 500) {
        return response;
      }
      
      if (attempt < retries) {
        const delay = Math.min(1000 * Math.pow(2, attempt), 5000); // Exponential backoff, max 5s
        console.log(`[Retry] Attempt ${attempt + 1} failed with ${response.status}. Retrying in ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
        continue;
      }
      
      return response;
      
    } catch (error) {
      cleanup();
      lastError = error as Error;
      
      if (attempt < retries) {
        const delay = Math.min(1000 * Math.pow(2, attempt), 5000);
        console.log(`[Retry] Attempt ${attempt + 1} failed: ${lastError.message}. Retrying in ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
        continue;
      }
      
      throw lastError;
    }
  }
  
  throw lastError || new Error('Max retries exceeded');
}

/**
 * Build target URL with query parameters
 */
function buildTargetUrl(baseUrl: string, resolvedParams: { path: string[] }, originalUrl: string): string {
  let targetPath = resolvedParams.path.join('/').replace(/\/+$/, '');
  
  // Shortcut for docs (optional)
  if (resolvedParams.path[0] === 'docs') {
    targetPath = 'docs';
  }
  
  const targetUrl = new URL(`${baseUrl}/${targetPath}`);
  
  // Copy query parameters from original request
  try {
    const originalUrlObj = new URL(originalUrl);
    originalUrlObj.searchParams.forEach((value, key) => {
      // Skip proxy-specific parameters
      if (!['simulateDown'].includes(key)) {
        targetUrl.searchParams.set(key, value);
      }
    });
  } catch (error) {
    console.warn('[URL Parse Warning]:', error);
  }
  
  return targetUrl.toString();
}

/**
 * Handle response with proper content type detection
 */
async function handleResponse(response: Response): Promise<NextResponse> {
  const responseHeaders = new Headers();
  
  // Copy response headers
  response.headers.forEach((value, key) => {
    responseHeaders.set(key, value);
  });
  
  // Set CORS headers
  responseHeaders.set('Access-Control-Allow-Origin', '*');
  responseHeaders.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS');
  responseHeaders.set('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With');
  responseHeaders.set('Access-Control-Expose-Headers', 'Content-Type, Content-Length');

  const contentType = response.headers.get('content-type')?.toLowerCase() || '';

  try {
    if (contentType.includes('application/json')) {
      const jsonData = await response.json();
      return NextResponse.json(jsonData, {
        status: response.status,
        statusText: response.statusText,
        headers: responseHeaders,
      });
    } else if (contentType.includes('text/')) {
      const textData = await response.text();
      return new NextResponse(textData, {
        status: response.status,
        statusText: response.statusText,
        headers: responseHeaders,
      });
    } else {
      const binaryData = await response.arrayBuffer();
      return new NextResponse(binaryData, {
        status: response.status,
        statusText: response.statusText,
        headers: responseHeaders,
      });
    }
  } catch (error) {
    console.error('[Response Parse Error]:', error);
    // Fallback: return response as-is
    const fallbackData = await response.arrayBuffer();
    return new NextResponse(fallbackData, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
    });
  }
}

/**
 * Core proxy logic with full error handling
 */
async function handleRequest(
  req: NextRequest,
  method: string,
  params: Promise<{ path: string[] }>
): Promise<NextResponse> {
  try {
    const resolvedParams = await params;
    
    // Pick backend with health check
    const usePrimary = await checkPrimaryHealth(req);
    const baseUrl = usePrimary ? PRIMARY : SECONDARY;
    const url = buildTargetUrl(baseUrl, resolvedParams, req.url);

    console.log(`[Proxy] ${method} ${req.url} → ${url} (${usePrimary ? 'Primary' : 'Secondary'})`);

    // Prepare headers
    const headers = createForwardHeaders(req.headers);
    
    // Handle request body
    const body = await handleRequestBody(req, method, headers);

    const init: RequestInit = {
      method,
      headers,
      cache: 'no-store',
      body
    };

    // Make request with retries
    const response = await makeRequestWithRetries(url, init);
    
    // Handle response
    return await handleResponse(response);

  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    const errorDetails = {
      error: 'Proxy request failed',
      message: errorMessage,
      method,
      timestamp: new Date().toISOString(),
      backend: isPrimaryHealthy ? 'Primary' : 'Secondary',
      consecutiveFailures
    };

    console.error(`[Proxy Error] ${method} ${req.url}:`, error);
    
    return NextResponse.json(errorDetails, {
      status: 500,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
      }
    });
  }
}

// Handlers with proper error boundaries
export async function GET(
  req: NextRequest,
  ctx: { params: Promise<{ path: string[] }> }
) {
  try {
    const resolvedParams = await ctx.params;

    // Custom proxy status endpoint
    if (resolvedParams.path.length === 1 && resolvedParams.path[0] === 'status') {
      const now = Date.now();
      const uptimeMs = now - backendSince;
      const uptime = {
        days: Math.floor(uptimeMs / (1000 * 60 * 60 * 24)),
        hours: Math.floor((uptimeMs / (1000 * 60 * 60)) % 24),
        minutes: Math.floor((uptimeMs / (1000 * 60)) % 60),
        seconds: Math.floor((uptimeMs / 1000) % 60)
      };

      return NextResponse.json({
        status: 'healthy',
        primaryHealthy: isPrimaryHealthy,
        currentBackend: isPrimaryHealthy ? 'Pi Server (Primary)' : 'Render (Secondary)',
        backendUrl: isPrimaryHealthy ? PRIMARY : SECONDARY,
        lastHealthCheck: new Date(lastChecked).toISOString(),
        backendSince: new Date(backendSince).toISOString(),
        uptime,
        consecutiveFailures,
        checkIntervalSeconds: HEALTH_CHECK_INTERVAL / 1000,
        requestTimeoutSeconds: REQUEST_TIMEOUT / 1000,
        maxRetries: MAX_RETRIES,
        timestamp: new Date().toISOString()
      });
    }

    return await handleRequest(req, 'GET', ctx.params);
  } catch (error) {
    console.error('[GET Handler Error]:', error);
    return NextResponse.json(
      { error: 'Handler error', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500, headers: { 'Access-Control-Allow-Origin': '*' } }
    );
  }
}

export async function POST(
  req: NextRequest,
  ctx: { params: Promise<{ path: string[] }> }
) {
  try {
    return await handleRequest(req, 'POST', ctx.params);
  } catch (error) {
    console.error('[POST Handler Error]:', error);
    return NextResponse.json(
      { error: 'Handler error', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500, headers: { 'Access-Control-Allow-Origin': '*' } }
    );
  }
}

export async function PUT(
  req: NextRequest,
  ctx: { params: Promise<{ path: string[] }> }
) {
  try {
    return await handleRequest(req, 'PUT', ctx.params);
  } catch (error) {
    console.error('[PUT Handler Error]:', error);
    return NextResponse.json(
      { error: 'Handler error', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500, headers: { 'Access-Control-Allow-Origin': '*' } }
    );
  }
}

export async function PATCH(
  req: NextRequest,
  ctx: { params: Promise<{ path: string[] }> }
) {
  try {
    return await handleRequest(req, 'PATCH', ctx.params);
  } catch (error) {
    console.error('[PATCH Handler Error]:', error);
    return NextResponse.json(
      { error: 'Handler error', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500, headers: { 'Access-Control-Allow-Origin': '*' } }
    );
  }
}

export async function DELETE(
  req: NextRequest,
  ctx: { params: Promise<{ path: string[] }> }
) {
  try {
    return await handleRequest(req, 'DELETE', ctx.params);
  } catch (error) {
    console.error('[DELETE Handler Error]:', error);
    return NextResponse.json(
      { error: 'Handler error', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500, headers: { 'Access-Control-Allow-Origin': '*' } }
    );
  }
}

// Enhanced preflight requests
export async function OPTIONS(req: NextRequest) {
  const origin = req.headers.get('origin');
  const requestedMethod = req.headers.get('access-control-request-method');
  const requestedHeaders = req.headers.get('access-control-request-headers');

  const responseHeaders = new Headers();
  responseHeaders.set('Access-Control-Allow-Origin', origin || '*');
  responseHeaders.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS');
  responseHeaders.set('Access-Control-Allow-Headers', requestedHeaders || 'Content-Type, Authorization, X-Requested-With');
  responseHeaders.set('Access-Control-Expose-Headers', 'Content-Type, Content-Length');
  responseHeaders.set('Access-Control-Max-Age', '86400');
  responseHeaders.set('Access-Control-Allow-Credentials', 'false');

  return new NextResponse(null, {
    status: 200,
    headers: responseHeaders,
  });
  }
