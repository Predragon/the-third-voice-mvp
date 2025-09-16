// src/api/proxy/[...path]/route.ts
import { NextRequest, NextResponse } from 'next/server';

// Required for Cloudflare Pages compatibility
export const runtime = 'edge';

// Base API URL from env (falls back to production if not set)
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://api.thethirdvoice.ai';

async function handleRequest(
  req: NextRequest,
  method: string,
  params: Promise<{ path: string[] }>
) {
  const resolvedParams = await params;
  const pathSegments = resolvedParams.path;
  let targetPath = pathSegments.join('/');

  // Special handling for docs
  if (pathSegments[0] === 'docs') {
    targetPath = 'docs';
  }

  const url = `${API_BASE}/${targetPath}`;
  console.log(`Proxying ${method} request to: ${url}`);

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

    // Prepare headers with CORS
    const responseHeaders = new Headers();
    response.headers.forEach((value, key) => {
      responseHeaders.set(key, value);
    });
    responseHeaders.set('Access-Control-Allow-Origin', '*');
    responseHeaders.set(
      'Access-Control-Allow-Methods',
      'GET, POST, PUT, DELETE, PATCH, OPTIONS'
    );
    responseHeaders.set(
      'Access-Control-Allow-Headers',
      'Content-Type, Authorization'
    );

    // Handle content type
    const contentType = response.headers.get('content-type');
    if (contentType?.includes('application/json')) {
      const data = await response.json();
      return NextResponse.json(data, { status: response.status, headers: responseHeaders });
    } else if (contentType?.includes('text/')) {
      const text = await response.text();
      return new NextResponse(text, { status: response.status, headers: responseHeaders });
    } else {
      const buffer = await response.arrayBuffer();
      return new NextResponse(buffer, { status: response.status, headers: responseHeaders });
    }
  } catch (error) {
    console.error(`${method} Proxy error for ${url}:`, error);
    return NextResponse.json(
      { error: 'Proxy request failed', message: (error as Error).message, url },
      {
        status: 500,
        headers: { 'Access-Control-Allow-Origin': '*' },
      }
    );
  }
}

// Handlers
export async function GET(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
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