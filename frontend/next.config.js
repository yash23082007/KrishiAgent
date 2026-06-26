let BACKEND_URL = process.env.NEXT_PUBLIC_API_URL;
if (!BACKEND_URL) {
  if (process.env.VERCEL_URL) {
    BACKEND_URL = `https://${process.env.VERCEL_URL}/_/backend`;
  } else {
    BACKEND_URL = 'http://127.0.0.1:8000';
  }
}

const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['images.unsplash.com', 'res.cloudinary.com', 'localhost'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${BACKEND_URL}/api/:path*`, // proxy API requests to FastAPI backend
      },
      {
        source: '/webhook',
        destination: `${BACKEND_URL}/webhook`, // proxy webhook calls
      },
      {
        source: '/static/:path*',
        destination: `${BACKEND_URL}/static/:path*`, // proxy static assets (audio/images)
      }
    ];
  }
};

module.exports = nextConfig;
