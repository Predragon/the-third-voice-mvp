// app/not-found.tsx (cloudflare branch)
'use client'

export const dynamic = 'force-static';

export default function NotFound() {
  return (
    <div>
      <h2>Not Found</h2>
      <p>Could not find requested resource</p>
    </div>
  )
}
