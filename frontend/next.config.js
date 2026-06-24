/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['images.unsplash.com', 'res.cloudinary.com', 'localhost'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8000/api/:path*', // proxy API requests to FastAPI backend
      },
      {
        source: '/webhook',
        destination: 'http://127.0.0.1:8000/webhook', // proxy webhook calls
      },
      {
        source: '/static/:path*',
        destination: 'http://127.0.0.1:8000/static/:path*', // proxy static assets (audio/images)
      }
    ];
  }
};

module.exports = nextConfig;
