import { NextResponse } from "next/server";

export const runtime = "edge";

export async function GET() {
  return NextResponse.json(
    {
      success: true,
      message: "API test endpoint is working 🚀",
      timestamp: new Date().toISOString(),
    },
    { status: 200, headers: { "Access-Control-Allow-Origin": "*" } }
  );
}
