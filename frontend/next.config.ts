import { NextConfig } from 'next';
import withPWA from 'next-pwa';

const isDev = process.env.NODE_ENV === 'development';
const isCloudflare = Boolean(process.env.CF_PAGES);

const nextConfig: NextConfig = {
  // Proxy rewrites - Works on Vercel, handled by API routes on Cloudflare
  async rewrites() {
    // Only use rewrites on Vercel, not on Cloudflare (use API routes instead)
    if (!isCloudflare) {
      return [
        {
          source: '/api/proxy/:path*',
          destination: 'https://api.thethirdvoice.ai/:path*',
        },
      ];
    }
    return [];
  },

  // Next.js core config
  reactStrictMode: true,
  poweredByHeader: false,
  compress: true,
  
  // Conditional image optimization - optimized on Vercel, unoptimized on Cloudflare
  images: { 
    unoptimized: isCloudflare,
    domains: ['localhost', 'api.thethirdvoice.ai'],
  },

  env: {
    NEXT_PUBLIC_API_URL: 'https://api.thethirdvoice.ai',
    NEXT_PUBLIC_PLATFORM: isCloudflare ? 'cloudflare' : 'vercel',
  },

  eslint: {
    ignoreDuringBuilds: true,
  },

  webpack: (config, { isServer }) => {
    // Disable cache on Cloudflare Pages for stability
    if (isCloudflare) {
      config.cache = false;
    }

    // Client-side fallbacks for Node.js modules
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
  disable: isDev || isCloudflare, // Disable PWA on Cloudflare for now
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
          maxAgeSeconds: 24 * 60 * 60, // 24 hours
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
          maxAgeSeconds: 30 * 24 * 60 * 60, // 30 days
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
          maxAgeSeconds: 30 * 24 * 60 * 60, // 30 days
        },
      },
    },
  ],
})(nextConfig);