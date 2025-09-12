declare module 'next-pwa/cache' {
  const runtimeCaching: any[];
  export = runtimeCaching;
}

declare module 'next-pwa' {
  import { NextConfig } from 'next';
  
  interface PWAConfig {
    dest?: string;
    disable?: boolean;
    register?: boolean;
    skipWaiting?: boolean;
    buildExcludes?: RegExp[];
    runtimeCaching?: any[];
    [key: string]: any;
  }
  
  function withPWA(config: PWAConfig): (nextConfig: NextConfig) => NextConfig;
  export default withPWA;
}