import { NextConfig } from 'next';
import withPWA from 'next-pwa';

const isDev = process.env.NODE_ENV === 'development';
const isCloudflare = Boolean(process.env.CF_PAGES);
const isVercel = Boolean(process.env.VERCEL);
const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.thethirdvoice.ai";
const LOCAL_API_URL = process.env.LOCAL_API_URL || "http://localhost:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    // Local development: use simple rewrites to local backend
    if (isDev && !isVercel && !isCloudflare) {
      return [
        {
          source: '/api/proxy/:path*',
          destination: `${LOCAL_API_URL}/:path*`,
        },
      ];
    }
    
    // Production (Vercel/Cloudflare): let route.ts handle intelligent failover
    return [];
  },

  reactStrictMode: true,
  poweredByHeader: false,
  compress: true,

  images: {
    unoptimized: isCloudflare,
    domains: ['localhost', 'api.thethirdvoice.ai', '127.0.0.1'],
  },

  eslint: {
    ignoreDuringBuilds: true,
  },

  webpack: (config, { isServer }) => {
    if (isCloudflare) {
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

export default withPWA({
  dest: 'public',
  disable: isDev || isCloudflare,
  register: true,
  skipWaiting: true,
  buildExcludes: [/middleware-manifest\.json$/],
  runtimeCaching: [
    {
      urlPattern: /^https?.*/,
      handler: 'NetworkFirst',
      options: {
        cacheName: 'offlineCache',
        expiration: {
          maxEntries: 200,
          maxAgeSeconds: 24 * 60 * 60,
        },
      },
    },
    {
      urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp)$/,
      handler: 'CacheFirst',
      options: {
        cacheName: 'images',
        expiration: {
          maxEntries: 100,
          maxAgeSeconds: 30 * 24 * 60 * 60,
        },
      },
    },
    {
      urlPattern: /\.(?:js|css|woff2?|ttf|eot)$/,
      handler: 'CacheFirst',
      options: {
        cacheName: 'static-resources',
        expiration: {
          maxEntries: 100,
          maxAgeSeconds: 30 * 24 * 60 * 60,
        },
      },
    },
  ],
})(nextConfig);