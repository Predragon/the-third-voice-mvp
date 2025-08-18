import { NextResponse } from 'next/server';

export async function GET() {
    try {
        const response = await fetch('http://100.71.78.118:8000/messages', {
            headers: { 'Content-Type': 'application/json' },
        });
        const data = await response.json();
        return NextResponse.json(data);
    } catch (error) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
