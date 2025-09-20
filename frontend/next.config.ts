import { NextConfig } from 'next';
import withPWA from 'next-pwa';

const isDev = process.env.NODE_ENV === 'development';
const isCloudflare = Boolean(process.env.CF_PAGES);
const isVercel = Boolean(process.env.VERCEL);
const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.thethirdvoice.ai";

const nextConfig: NextConfig = {
  async rewrites() {
    // Only use rewrites for local development, not on Vercel or Cloudflare
    // This allows route.ts to handle intelligent failover on production
    if (!isCloudflare && !isVercel) {
      return [
        {
          source: '/api/proxy/:path*',
          destination: `${API_URL}/:path*`,
        },
      ];
    }
    return [];
  },

  reactStrictMode: true,
  poweredByHeader: false,
  compress: true,

  images: {
    unoptimized: isCloudflare,
    domains: ['localhost', 'api.thethirdvoice.ai'],
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