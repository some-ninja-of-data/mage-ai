const removeImports = require('next-remove-imports')();

// If you make updates to this file, you must also update the
// next-base-path.config.js file
module.exports = removeImports({
  distDir: '../server/frontend_dist',
  eslint: {
    ignoreDuringBuilds: true,
  },
  experimental: {
    esmExternals: true
  },
  reactStrictMode: true,
});