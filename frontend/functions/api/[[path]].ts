export async function onRequest({ request, env }: { request: Request, env: any }) {
  const url = new URL(request.url);

  // Default to local backend if LOCAL_API_URL is set (via .dev.vars)
  const backendBase = env.LOCAL_API_URL || "https://your-backend-domain.com";

  const backendUrl = `${backendBase}${url.pathname.replace("/api", "")}`;

  return fetch(backendUrl, {
    method: request.method,
    headers: request.headers,
    body: request.method !== "GET" ? await request.text() : undefined,
  });
}