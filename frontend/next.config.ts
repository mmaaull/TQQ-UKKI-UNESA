import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  async rewrites() {
    // Jalur same-origin tetap tersedia untuk localhost dan tunnel ngrok,
    // termasuk ketika NEXT_PUBLIC_API_URL pernah disetel ke localhost.
    const backendUrl = (process.env.BACKEND_API_URL?.trim() || "http://127.0.0.1:8000").replace(/\/$/, "");
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
