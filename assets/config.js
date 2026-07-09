/**
 * Toolify Site Configuration
 * Replace all YOUR_* placeholders with your actual credentials.
 *
 * SETUP GUIDE:
 * 1. Google: https://console.cloud.google.com/ → APIs & Services → Credentials → Create OAuth 2.0 Client ID (Web)
 * 2. Apple:  https://developer.apple.com/ → Certificates, IDs & Profiles → Identifiers → Create Services ID → enable Sign in with Apple
 *    (Requires Apple Developer Program membership, $99/year)
 * 3. Lemon Squeezy: https://app.lemonsqueezy.com/ → Create products, copy checkout URLs
 * 4. Google Analytics: https://analytics.google.com/ → Create property, copy Measurement ID
 */
const CONFIG = {
  // ---- Google OAuth (Google Identity Services) ----
  GOOGLE_CLIENT_ID: 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com',

  // ---- Sign in with Apple ----
  APPLE_CLIENT_ID: 'YOUR_APPLE_CLIENT_ID',  // Services ID (e.g. com.toolify.web)

  // ---- Lemon Squeezy Checkout ----
  // Create two products in Lemon Squeezy: one in USD, one in JPY
  LEMON_SQUEEZY_USD_URL: 'https://toolify.lemonsqueezy.com/checkout/buy-PRODUCT-USD',
  LEMON_SQUEEZY_JPY_URL: 'https://toolify.lemonsqueezy.com/checkout/buy-PRODUCT-JPY',
  LEMON_SQUEEZY_USD_YEARLY_URL: 'https://toolify.lemonsqueezy.com/checkout/buy-PRODUCT-USD-YEARLY',
  LEMON_SQUEEZY_JPY_YEARLY_URL: 'https://toolify.lemonsqueezy.com/checkout/buy-PRODUCT-JPY-YEARLY',

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
  PRICE_USD_YEARLY: '$99.90',
  PRICE_JPY_YEARLY: '¥15,000',
  PRICE_JPY: '\u00a51,500',
};

// Expose globally
window.CONFIG = CONFIG;
