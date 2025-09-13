import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  req: NextRequest, 
  { params }: { params: Promise<{ path: string[] }> }
) {
  const resolvedParams = await params;
  const pathSegments = resolvedParams.path;
  
  // Construct the target URL
  let targetPath = pathSegments.join('/');
  
  // Handle special cases for docs endpoint
  if (pathSegments[0] === 'docs') {
    // For docs, we want to return JSON, not HTML
    targetPath = 'docs';
  }
  
  const url = `https://api.thethirdvoice.ai/${targetPath}`;
  
  console.log(`Proxying GET request to: ${url}`);

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        // Forward user agent and other relevant headers
        'User-Agent': req.headers.get('user-agent') || 'NextJS-Proxy',
      },
      cache: 'no-store',
    });

    console.log(`Response status: ${response.status}`);
    console.log(`Response headers:`, Object.fromEntries(response.headers.entries()));

    // Handle different content types
    const contentType = response.headers.get('content-type');
    
    if (contentType?.includes('application/json')) {
      const data = await response.json();
      return NextResponse.json(data, { status: response.status });
    } else if (contentType?.includes('text/')) {
      const text = await response.text();
      return new NextResponse(text, { 
        status: response.status,
        headers: { 'Content-Type': contentType }
      });
    } else {
      // For binary or other content types
      const buffer = await response.arrayBuffer();
      return new NextResponse(buffer, { 
        status: response.status,
        headers: { 'Content-Type': contentType || 'application/octet-stream' }
      });
    }
  } catch (error) {
    console.error(`Proxy error for ${url}:`, error);
    return NextResponse.json(
      { 
        error: 'Proxy request failed',
        message: (error as Error).message,
        url: url
      },
      { status: 500 }
    );
  }
}

export async function POST(
  req: NextRequest, 
  { params }: { params: Promise<{ path: string[] }> }
) {
  const resolvedParams = await params;
  const url = `https://api.thethirdvoice.ai/${resolvedParams.path.join('/')}`;
  
  console.log(`Proxying POST request to: ${url}`);

  try {
    const body = await req.json();

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': req.headers.get('user-agent') || 'NextJS-Proxy',
      },
      body: JSON.stringify(body),
      cache: 'no-store',
    });

    console.log(`POST Response status: ${response.status}`);

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error(`POST Proxy error for ${url}:`, error);
    return NextResponse.json(
      { 
        error: 'Proxy request failed',
        message: (error as Error).message,
        url: url
      },
      { status: 500 }
    );
  }
}