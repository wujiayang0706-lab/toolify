/**
 * Toolify Site Configuration
 * Replace all YOUR_* placeholders with your actual credentials.
 *
 * SETUP GUIDE:
 * 1. Google: https://console.cloud.google.com/ → APIs & Services → Credentials → Create OAuth 2.0 Client ID (Web)
 * 2. LINE:   https://developers.line.biz/console/ → Create a LINE Login channel (Web app)
 * 3. Lemon Squeezy: https://app.lemonsqueezy.com/ → Create products, copy checkout URLs
 * 4. Google Analytics: https://analytics.google.com/ → Create property, copy Measurement ID
 */
const CONFIG = {
  // ---- Google OAuth (Google Identity Services) ----
  GOOGLE_CLIENT_ID: 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com',

  // ---- LINE Login ----
  LINE_CHANNEL_ID: 'YOUR_LINE_CHANNEL_ID',

  // ---- Lemon Squeezy Checkout ----
  // Create two products in Lemon Squeezy: one in USD, one in JPY
  LEMON_SQUEEZY_USD_URL: 'https://toolify.lemonsqueezy.com/checkout/buy-PRODUCT-USD',
  LEMON_SQUEEZY_JPY_URL: 'https://toolify.lemonsqueezy.com/checkout/buy-PRODUCT-JPY',

  // ---- Support ----
  SUPPORT_EMAIL: 'support@toolify.com',

  // ---- Google Analytics ----
  GA_TRACKING_ID: '',  // e.g. 'G-XXXXXXXXXX' — leave empty to disable

  // ---- Free vs Premium limits ----
  FREE_LIMIT: {
    mergesPerDay: 3,
    conversionsPerDay: 3,
    maxFileSize: 10   // MB
  },
  PREMIUM_LIMIT: {
    mergesPerDay: Infinity,
    conversionsPerDay: Infinity,
    maxFileSize: 50   // MB
  },

  // ---- Pricing ----
  PRICE_USD: '$9.99',
  PRICE_JPY: '\u00a51,500',
};

// Expose globally
window.CONFIG = CONFIG;
