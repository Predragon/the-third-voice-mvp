// app/api/not-found/route.ts (cloudflare branch)

export async function GET() {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/not-found`);
    if (!response.ok) throw new Error('Primary API failed');
    const data = await response.json();
    return new Response(JSON.stringify(data), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    const fallback = await fetch('https://fallback.thethirdvoice.ai/not-found');
    const data = await fallback.json();
    return new Response(JSON.stringify(data), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}
