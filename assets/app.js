/**
 * Toolify Auth & Common App Logic
 * Handles: Google login (GIS), LINE login (implicit flow), user state,
 * premium status, usage tracking, and UI updates.
 */
(function() {
  'use strict';

  const STORAGE_KEY = 'toolify_user';
  const USAGE_KEY = 'toolify_usage';

  // ---- User State ----
  function getUser() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY)); } catch { return null; }
  }

  function setUser(user) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
  }

  function clearUser() {
    localStorage.removeItem(STORAGE_KEY);
  }

  function isLoggedIn() {
    return !!getUser();
  }

  function isPremium() {
    const u = getUser();
    return u && u.premium === true;
  }

  // ---- Usage Tracking (free tier) ----
  function getUsage() {
    try {
      const data = JSON.parse(localStorage.getItem(USAGE_KEY));
      if (data && data.date === new Date().toDateString()) return data;
    } catch {}
    return { date: new Date().toDateString(), merges: 0, conversions: 0 };
  }

  function incrementUsage(type) {
    const usage = getUsage();
    usage[type] = (usage[type] || 0) + 1;
    localStorage.setItem(USAGE_KEY, JSON.stringify(usage));
    return usage;
  }

  function canUse(type) {
    if (isPremium()) return true;
    const usage = getUsage();
    const limit = CONFIG.FREE_LIMIT[type + 'sPerDay'] || Infinity;
    return (usage[type] || 0) < limit;
  }

  function getMaxFileSize() {
    return isPremium() ? CONFIG.PREMIUM_LIMIT.maxFileSize : CONFIG.FREE_LIMIT.maxFileSize;
  }

  // ---- Demo Mode (active when credentials are placeholders) ----
  function isDemoMode() {
    return CONFIG.GOOGLE_CLIENT_ID.startsWith('YOUR_') ||
           CONFIG.LINE_CHANNEL_ID.startsWith('YOUR_');
  }

  function demoLogin(provider) {
    var names = {
      google: 'Demo Google User',
      line: 'Demo LINE User'
    };
    var name = names[provider] || 'Demo User';
    setUser({
      provider: provider,
      id: 'demo_' + provider + '_' + Date.now(),
      name: name,
      email: 'demo@toolify.app',
      avatar: null,
      premium: false,
      demo: true
    });
    updateAuthUI();
    closeLoginModal();
    showToast(getText('login_success') + ' ' + name + ' (Demo)');
  }

  // ---- Google Login (Google Identity Services) ----
  let googleInitialized = false;

  function initGoogleAuth() {
    if (googleInitialized || !window.google || !window.google.accounts) return;
    if (CONFIG.GOOGLE_CLIENT_ID.startsWith('YOUR_')) return;

    google.accounts.id.initialize({
      client_id: CONFIG.GOOGLE_CLIENT_ID,
      callback: handleGoogleCredential
    });
    googleInitialized = true;

    // Render button if modal is open
    const btn = document.getElementById('google-login-btn');
    if (btn) {
      google.accounts.id.renderButton(btn, {
        theme: 'outline', size: 'large', width: '100%', text: 'continue_with'
      });
    }
  }

  function handleGoogleCredential(response) {
    try {
      // Decode JWT payload
      const payload = JSON.parse(atob(response.credential.split('.')[1]));
      setUser({
        provider: 'google',
        id: payload.sub,
        name: payload.name,
        email: payload.email,
        avatar: payload.picture,
        premium: false
      });
      updateAuthUI();
      closeLoginModal();
      showToast(getText('login_success') + ' ' + payload.name);
    } catch (e) {
      console.error('Google login error:', e);
      showToast(getText('login_failed'), true);
    }
  }

  // ---- LINE Login (implicit grant flow) ----
  function loginWithLINE() {
    if (CONFIG.LINE_CHANNEL_ID.startsWith('YOUR_')) {
      // Demo mode: simulate LINE login
      demoLogin('line');
      return;
    }
    const redirectUri = encodeURIComponent(window.location.origin + '/auth/line-callback.html');
    const state = Math.random().toString(36).substring(2);
    localStorage.setItem('line_auth_state', state);
    const url = 'https://access.line.me/oauth2/v2.1/authorize' +
      '?response_type=token' +
      '&client_id=' + CONFIG.LINE_CHANNEL_ID +
      '&redirect_uri=' + redirectUri +
      '&state=' + state +
      '&scope=profile%20openid';
    window.location.href = url;
  }

  // Called by line-callback.html after redirect
  window.handleLINECallback = function() {
    const hash = window.location.hash.substring(1);
    const params = new URLSearchParams(hash);
    const accessToken = params.get('access_token');
    const state = params.get('state');
    const savedState = localStorage.getItem('line_auth_state');
    localStorage.removeItem('line_auth_state');

    if (!accessToken || state !== savedState) {
      // Redirect to home with error
      window.location.href = '/?login_error=line';
      return;
    }

    fetch('https://api.line.me/v2/profile', {
      headers: { 'Authorization': 'Bearer ' + accessToken }
    })
    .then(r => r.json())
    .then(profile => {
      setUser({
        provider: 'line',
        id: profile.userId,
        name: profile.displayName,
        email: profile.email || null,
        avatar: profile.pictureUrl,
        premium: false
      });
      window.location.href = '/';
    })
    .catch(err => {
      console.error('LINE profile error:', err);
      window.location.href = '/?login_error=line';
    });
  };

  // ---- Login Modal ----
  function openLoginModal() {
    const modal = document.getElementById('loginModal');
    if (!modal) return;
    modal.classList.add('active');
    // Re-render Google button now that modal is visible
    setTimeout(initGoogleAuth, 100);
  }

  function closeLoginModal() {
    const modal = document.getElementById('loginModal');
    if (modal) modal.classList.remove('active');
  }

  // ---- Logout ----
  function logout() {
    clearUser();
    updateAuthUI();
    showToast(getText('logged_out'));
  }

  // ---- UI Updates ----
  function updateAuthUI() {
    const user = getUser();
    const loginBtn = document.getElementById('loginBtn');
    const userMenu = document.getElementById('userMenu');

    if (user) {
      if (loginBtn) loginBtn.style.display = 'none';
      if (userMenu) {
        userMenu.style.display = 'flex';
        const avatar = userMenu.querySelector('.user-avatar');
        const name = userMenu.querySelector('.user-name');
        if (avatar) {
          if (user.avatar) {
            avatar.innerHTML = '<img src="' + user.avatar + '" alt="">';
          } else {
            avatar.textContent = (user.name || 'U').charAt(0).toUpperCase();
          }
        }
        if (name) name.textContent = user.name || user.email || 'User';

        // Add premium badge
        if (isPremium()) {
          userMenu.classList.add('premium');
        } else {
          userMenu.classList.remove('premium');
        }
      }
    } else {
      if (loginBtn) loginBtn.style.display = 'inline-flex';
      if (userMenu) userMenu.style.display = 'none';
    }
  }

  // ---- User Menu Dropdown ----
  function toggleUserMenu() {
    const dropdown = document.getElementById('userDropdown');
    if (dropdown) dropdown.classList.toggle('active');
  }

  // ---- Toast ----
  function showToast(msg, isError) {
    let toast = document.getElementById('toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'toast';
      toast.className = 'toast';
      document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.className = 'toast' + (isError ? ' error' : '') + ' show';
    clearTimeout(toast._timeout);
    toast._timeout = setTimeout(function() { toast.classList.remove('show'); }, 3000);
  }

  // ---- i18n text helper ----
  function getText(key) {
    const lang = document.documentElement.lang || 'en';
    const texts = {
      en: {
        login: 'Login', signup: 'Sign Up', logout: 'Log Out',
        login_success: 'Welcome', login_failed: 'Login failed. Please try again.',
        logged_out: 'You have been logged out.',
        login_title: 'Welcome to Toolify', login_subtitle: 'Login to sync your subscriptions and unlock premium features.',
        login_with_google: 'Continue with Google', login_with_line: 'Continue with LINE',
        or_continue: 'or', no_signup: 'No signup required — just one click.',
        my_account: 'My Account', upgrade: 'Upgrade to Premium',
        premium_member: 'Premium Member', free_member: 'Free Member'
      },
      zh: {
        login: '登录', signup: '注册', logout: '退出登录',
        login_success: '欢迎', login_failed: '登录失败，请重试。',
        logged_out: '您已退出登录。',
        login_title: '欢迎来到 Toolify', login_subtitle: '登录以同步您的订阅并解锁高级功能。',
        login_with_google: '使用 Google 继续', login_with_line: '使用 LINE 继续',
        or_continue: '或', no_signup: '无需注册—一键登录。',
        my_account: '我的账户', upgrade: '升级到高级会员',
        premium_member: '高级会员', free_member: '免费用户'
      },
      ja: {
        login: 'ログイン', signup: '登録', logout: 'ログアウト',
        login_success: 'ようこそ', login_failed: 'ログインに失敗しました。もう一度お試しください。',
        logged_out: 'ログアウトしました。',
        login_title: 'Toolifyへようこそ', login_subtitle: 'ログインしてサブスクリプションを同期し、プレミアム機能のロックを解除します。',
        login_with_google: 'Googleで続行', login_with_line: 'LINEで続行',
        or_continue: 'または', no_signup: '登録不要—ワンクリックでログイン。',
        my_account: 'マイアカウント', upgrade: 'プレミアムにアップグレード',
        premium_member: 'プレミアム会員', free_member: '無料会員'
      }
    };
    return (texts[lang] && texts[lang][key]) || texts.en[key] || key;
  }

  // ---- Inject Login Modal HTML ----
  function injectLoginModal() {
    if (document.getElementById('loginModal')) return;

    var demo = isDemoMode();
    var demoBanner = demo ?
      '<div class="login-demo-banner">Demo Mode — credentials not configured yet. Click any provider to simulate login.</div>' : '';
    var googleClick = demo ? ' onclick="demoLogin(\'google\')" style="cursor:pointer"' : '';
    var lineClick = demo ? ' onclick="demoLogin(\'line\')"' : ' onclick="loginWithLINE()"';

    const modal = document.createElement('div');
    modal.id = 'loginModal';
    modal.className = 'login-modal';
    modal.innerHTML =
      '<div class="login-overlay" onclick="closeLoginModal()"></div>' +
      '<div class="login-dialog">' +
        '<button class="login-close" onclick="closeLoginModal()">&times;</button>' +
        '<h2 class="login-title">' + getText('login_title') + '</h2>' +
        '<p class="login-subtitle">' + getText('login_subtitle') + '</p>' +
        demoBanner +
        '<div class="login-buttons">' +
          '<div id="google-login-btn" class="login-provider-btn google-btn"' + googleClick + '>' +
            '<svg viewBox="0 0 24 24" width="20" height="20"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>' +
            '<span>' + getText('login_with_google') + '</span>' +
          '</div>' +
          '<div id="line-login-btn" class="login-provider-btn line-btn"' + lineClick + '>' +
            '<svg viewBox="0 0 24 24" width="20" height="20" fill="#06C755"><path d="M19.365 9.863c.349 0 .63.285.63.631 0 .345-.281.63-.63.63H17.61v1.125h1.755c.349 0 .63.283.63.63 0 .344-.281.629-.63.629h-2.386c-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.627-.63h2.386c.349 0 .63.285.63.63 0 .349-.281.63-.63.63H17.61v1.125h1.755zm-3.855 3.016c0 .344-.282.629-.631.629-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.627-.63.349 0 .631.285.631.63v4.771zm-10.781.629c-.345 0-.63-.285-.63-.629V8.108c0-.345.285-.63.63-.63.345 0 .63.285.63.63v4.771c0 .344-.285.629-.63.629zM12 1C5.926 1 1 5.926 1 12s4.926 11 11 11 11-4.926 11-11S18.074 1 12 1z"/></svg>' +
            '<span>' + getText('login_with_line') + '</span>' +
          '</div>' +
        '</div>' +
        '<p class="login-note">' + getText('no_signup') + '</p>' +
      '</div>';
    document.body.appendChild(modal);
  }

  // ---- Inject User Menu HTML ----
  function injectUserMenu() {
    if (document.getElementById('userMenu')) return;

    const header = document.querySelector('.header-inner');
    if (!header) return;

    // Create login button
    const loginBtn = document.createElement('button');
    loginBtn.id = 'loginBtn';
    loginBtn.className = 'btn-login';
    loginBtn.innerHTML =
      '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h4a2 2 0 012 2v14a2 2 0 01-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>' +
      '<span>' + getText('login') + '</span>';
    loginBtn.onclick = openLoginModal;

    // Create user menu (hidden by default)
    const userMenu = document.createElement('div');
    userMenu.id = 'userMenu';
    userMenu.className = 'user-menu';
    userMenu.style.display = 'none';
    userMenu.innerHTML =
      '<button class="user-trigger" onclick="toggleUserMenu()">' +
        '<span class="user-avatar"></span>' +
        '<span class="user-name"></span>' +
        '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>' +
      '</button>' +
      '<div class="user-dropdown" id="userDropdown">' +
        '<div class="user-dropdown-header">' +
          '<span class="user-status"></span>' +
        '</div>' +
        '<a href="/pricing/" class="user-dropdown-item upgrade-link">' +
          '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>' +
          '<span>' + getText('upgrade') + '</span>' +
        '</a>' +
        '<a href="/support/" class="user-dropdown-item">' +
          '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>' +
          '<span>Support</span>' +
        '</a>' +
        '<button class="user-dropdown-item" onclick="logout()">' +
          '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>' +
          '<span>' + getText('logout') + '</span>' +
        '</button>' +
      '</div>';

    // Update dropdown status text
    const status = userMenu.querySelector('.user-status');
    if (status) {
      status.textContent = isPremium() ? getText('premium_member') : getText('free_member');
    }

    // Insert into header (after nav, before lang-switcher or at end)
    const nav = header.querySelector('.nav');
    if (nav) {
      nav.appendChild(loginBtn);
      nav.appendChild(userMenu);
    } else {
      header.appendChild(loginBtn);
      header.appendChild(userMenu);
    }
  }

  // ---- Check URL for login errors ----
  function checkLoginErrors() {
    const params = new URLSearchParams(window.location.search);
    if (params.get('login_error') === 'line') {
      showToast(getText('login_failed'), true);
      history.replaceState(null, '', window.location.pathname);
    }
  }

  // ---- Close dropdown on outside click ----
  document.addEventListener('click', function(e) {
    const dropdown = document.getElementById('userDropdown');
    const trigger = document.querySelector('.user-trigger');
    if (dropdown && dropdown.classList.contains('active') &&
        !dropdown.contains(e.target) && !trigger?.contains(e.target)) {
      dropdown.classList.remove('active');
    }
  });

  // ---- Public API ----
  window.ToolifyAuth = {
    getUser, setUser, isLoggedIn, isPremium, logout,
    canUse, incrementUsage, getMaxFileSize,
    openLoginModal, closeLoginModal, updateAuthUI,
    loginWithLINE, initGoogleAuth
  };

  // Expose simple functions globally for onclick handlers
  window.openLoginModal = openLoginModal;
  window.closeLoginModal = closeLoginModal;
  window.loginWithLINE = loginWithLINE;
  window.demoLogin = demoLogin;
  window.logout = logout;
  window.toggleUserMenu = toggleUserMenu;
  window.showToast = showToast;

  // ---- Initialize on DOM ready ----
  function init() {
    injectLoginModal();
    injectUserMenu();
    updateAuthUI();
    initGoogleAuth();
    checkLoginErrors();

    // Load Google GIS script
    if (!document.getElementById('google-gis-script') && !CONFIG.GOOGLE_CLIENT_ID.startsWith('YOUR_')) {
      const script = document.createElement('script');
      script.id = 'google-gis-script';
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      script.onload = initGoogleAuth;
      document.head.appendChild(script);
    }

    // Update user dropdown status
    const status = document.querySelector('.user-status');
    if (status) {
      status.textContent = isPremium() ? getText('premium_member') : getText('free_member');
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
