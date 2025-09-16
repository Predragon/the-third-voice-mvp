// next.config.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.thethirdvoice.ai";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/proxy/:path*",
        destination: `${API_URL}/:path*`, // always defined
      },
    ];
  },
  // ... rest of config
};

export default nextConfig;