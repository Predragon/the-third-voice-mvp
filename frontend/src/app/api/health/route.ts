import { NextResponse } from "next/server";

export const runtime = "edge";

export async function GET() {
  return NextResponse.json(
    {
      ok: true,
      service: "The Third Voice",
      timestamp: new Date().toISOString(),
    },
    { status: 200, headers: { "Access-Control-Allow-Origin": "*" } }
  );
}
