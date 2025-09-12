import { NextConfig } from 'next';
import withPWA from 'next-pwa';
import runtimeCaching from 'next-pwa/cache';

const isDev = process.env.NODE_ENV === 'development';

const nextConfig: NextConfig = {
  // PWA Configuration
  ...withPWA({
    dest: 'public',
    disable: isDev,
    register: true,
    skipWaiting: true,
    buildExcludes: [/middleware-manifest\.json$/],
    runtimeCaching, // Use default runtimeCaching from next-pwa/cache
  }),

  // Proxy rewrites (top-level Next.js config)
  async rewrites() {
    return [
      {
        source: '/api/proxy/:path*',
        destination: 'https://api.thethirdvoice.ai/:path*',
      },
    ];
  },

  // Next.js core config
  trailingSlash: true,
  reactStrictMode: true,
  poweredByHeader: false,
  compress: true,
  images: { unoptimized: true },

  env: {
    NEXT_PUBLIC_API_URL: 'https://api.thethirdvoice.ai',
  },

  eslint: {
    ignoreDuringBuilds: true,
  },

  webpack: (config, { isServer }) => {
    if (process.env.CF_PAGES) {
      config.cache = false;
    }

    if (!isServer) {
      config.resolve = config.resolve || {};
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };
    }

    return config;
  },
};

export default nextConfig;
