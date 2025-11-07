import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  // Required for Lobe UI (ESM-only package)
  transpilePackages: ['@lobehub/ui', '@lobehub/icons', 'antd-style'],
  experimental: {
    // Enable if needed
  },
};

export default nextConfig;
