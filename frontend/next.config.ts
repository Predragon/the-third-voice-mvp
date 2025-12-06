import { NextConfig } from 'next';
import withPWA from 'next-pwa';

const isDev = process.env.NODE_ENV === 'development';
const isCloudflare = Boolean(process.env.CF_PAGES);
const isVercel = Boolean(process.env.VERCEL);
const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.thethirdvoice.ai";
const LOCAL_API_URL = process.env.LOCAL_API_URL || "http://localhost:8000";

const nextConfig: NextConfig = {
  turbopack: false,   // 🔥 FIX: Force Webpack on Next 16

  async rewrites() {
    if (isDev && !isVercel && !isCloudflare) {
      return [
        {
          source: '/api/proxy/:path*',
          destination: `${LOCAL_API_URL}/:path*`,
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
    remotePatterns: [
      { protocol: 'https', hostname: 'api.thethirdvoice.ai' },
      { protocol: 'http', hostname: 'localhost' },
      { protocol: 'http', hostname: '127.0.0.1' }
    ],
  },

  // ⚠️ Removed deprecated "eslint" block — Next 16 refuses it
  // eslint: { ignoreDuringBuilds: true },

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
