/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: "export", // <- required for Next.js 14 static export
};

module.exports = nextConfig;