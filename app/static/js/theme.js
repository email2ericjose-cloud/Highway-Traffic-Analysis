/**
 * Theme & Appearance Manager
 * Manages Color Themes, Liquid Glass (On/Off), Motion Effects, and localStorage persistence.
 */

const ThemeManager = {
  THEMES: {
    'warm-cream': {
      name: 'Warm Cream & Beige',
      primary: '#806342',
      secondary: '#397C78',
      text: '#292820',
      textMuted: '#716B60',
      grid: 'rgba(216, 203, 182, 0.4)',
      cardBg: '#FFFDF8'
    },
    'clean-light': {
      name: 'Clean Modern Light',
      primary: '#2563EB',
      secondary: '#0D9488',
      text: '#0F172A',
      textMuted: '#64748B',
      grid: 'rgba(203, 213, 225, 0.5)',
      cardBg: '#FFFFFF'
    },
    'dark-analytics': {
      name: 'Dark Analytics',
      primary: '#F59E0B',
      secondary: '#14B8A6',
      text: '#F9FAFB',
      textMuted: '#9CA3AF',
      grid: 'rgba(55, 65, 81, 0.5)',
      cardBg: '#1F2937'
    }
  },

  init() {
    // Default per prompt: Warm Cream with Liquid Glass enabled
    const savedTheme = localStorage.getItem('uav_studio_theme') || 'warm-cream';
    const savedGlass = localStorage.getItem('uav_studio_glass') !== null ? localStorage.getItem('uav_studio_glass') : 'true';
    const savedMotion = localStorage.getItem('uav_studio_motion') !== null ? localStorage.getItem('uav_studio_motion') : 'true';

    this.setTheme(savedTheme, false);
    this.setGlass(savedGlass === 'true', false);
    this.setMotion(savedMotion === 'true', false);

    this.bindEvents();
    this.updateUIControls();
  },

  bindEvents() {
    // Quick glass toggle button in header
    const btnGlass = document.getElementById('btnQuickGlassToggle');
    if (btnGlass) {
      btnGlass.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-glass') === 'true';
        this.setGlass(!current);
      });
    }

    // Theme dropdown in header
    const selectTheme = document.getElementById('selectHeaderTheme');
    if (selectTheme) {
      selectTheme.addEventListener('change', (e) => {
        this.setTheme(e.target.value);
      });
    }
  },

  setTheme(themeName, persist = true) {
    if (!this.THEMES[themeName]) themeName = 'warm-cream';
    document.documentElement.setAttribute('data-theme', themeName);
    if (persist) localStorage.setItem('uav_studio_theme', themeName);

    this.updateUIControls();

    // Trigger Chart.js palette update if charts exist
    if (window.ChartManager && typeof window.ChartManager.updateAllCharts === 'function') {
      window.ChartManager.updateAllCharts();
    }
  },

  setGlass(enabled, persist = true) {
    const val = enabled ? 'true' : 'false';
    document.documentElement.setAttribute('data-glass', val);
    if (persist) localStorage.setItem('uav_studio_glass', val);

    const btn = document.getElementById('btnQuickGlassToggle');
    if (btn) {
      btn.innerHTML = enabled
        ? '<i class="fa-solid fa-droplet text-amber-600"></i> Glass: <b>ON</b>'
        : '<i class="fa-solid fa-square-full text-slate-400"></i> Glass: <b>OFF</b>';
    }

    const modalToggle = document.getElementById('inputSettingGlass');
    if (modalToggle) modalToggle.checked = enabled;
  },

  setMotion(enabled, persist = true) {
    const val = enabled ? 'true' : 'false';
    document.documentElement.setAttribute('data-motion', val);
    if (persist) localStorage.setItem('uav_studio_motion', val);

    const modalToggle = document.getElementById('inputSettingMotion');
    if (modalToggle) modalToggle.checked = enabled;
  },

  updateUIControls() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'warm-cream';
    const selectTheme = document.getElementById('selectHeaderTheme');
    if (selectTheme) selectTheme.value = currentTheme;

    const selectModalTheme = document.getElementById('inputSettingTheme');
    if (selectModalTheme) selectModalTheme.value = currentTheme;
  },

  getCurrentColors() {
    const theme = document.documentElement.getAttribute('data-theme') || 'warm-cream';
    return this.THEMES[theme] || this.THEMES['warm-cream'];
  }
};

window.ThemeManager = ThemeManager;
