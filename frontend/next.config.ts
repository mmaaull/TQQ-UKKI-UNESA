import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  async rewrites() {
    // Proxy /api/* ke backend lokal setiap kali NEXT_PUBLIC_API_URL kosong
    // (mode same-origin, dipakai misalnya saat berbagi lewat satu tunnel ngrok),
    // baik di development maupun production build.
    if (process.env.NEXT_PUBLIC_API_URL) {
      return [];
    }
    return [
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:8000/api/:path*",
      },
    ];
  },
};

export default nextConfig;