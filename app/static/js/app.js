/**
 * Main Application Orchestrator
 * Coordinates Navigation, API Data Hydration, Video Player, and Modal Controls.
 */

const App = {
  currentTab: 'tab-overview',

  async init() {
    console.log('[App] Initializing UAV Traffic Studio Suite...');

    // 1. Initialize Theme & Visual Preferences
    window.ThemeManager.init();

    // 2. Hydrate System Status & KPIs from REST API
    await this.fetchStatusData();

    // 3. Initialize Studios & Visuals
    window.ChartManager.init();
    await window.TrajectoryStudio.init();
    await window.SafetyStudio.init();
    window.PipelineStudio.init();

    // 4. Bind Global Navigation & Modals
    this.bindNavigation();
    this.bindModals();
    this.bindVideoControls();

    console.log('[App] Ready. Developed by Eric Jose.');
  },

  async fetchStatusData() {
    try {
      const res = await fetch('/api/status');
      if (!res.ok) return;
      const data = await res.json();

      // Hydrate KPIs
      if (data.kpi_summary) {
        const k = data.kpi_summary;
        this.setKPI('kpiFlowRate', Math.round(k.flow_rate_veh_hr).toLocaleString());
        this.setKPI('kpiDensity', k.traffic_density_veh_km.toFixed(1));
        this.setKPI('kpiTimeMeanSpeed', `${k.time_mean_speed_kmh.toFixed(1)} km/h`);
        this.setKPI('kpiSpaceMeanSpeed', `${k.space_mean_speed_kmh.toFixed(1)} km/h`);
        this.setKPI('kpiP85Speed', `${k.p85_speed_kmh.toFixed(1)} km/h`);
        this.setKPI('kpiVehicles', `${k.highway_vehicles} <span class="text-xs font-normal text-slate-500">(${k.total_tracked_vehicles} tracks)</span>`);
        this.setKPI('kpiCriticalTTC', k.critical_ttc_count.toLocaleString());
        this.setKPI('kpiConflictPairs', `${k.tier1_high_risk_pairs} <span class="text-xs font-normal text-slate-500">(${k.evaluated_conflict_pairs} total)</span>`);
      }
    } catch (e) {
      console.warn('[App] Could not fetch status data:', e);
    }
  },

  setKPI(id, html) {
    const el = document.getElementById(id);
    if (el) el.innerHTML = html;
  },

  bindNavigation() {
    document.querySelectorAll('.sidebar-nav-item').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const targetTab = btn.getAttribute('data-tab');
        if (targetTab) {
          this.switchTab(targetTab);
        }
      });
    });
  },

  switchTab(tabId) {
    this.currentTab = tabId;

    // Panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
      pane.classList.remove('active');
    });
    const activePane = document.getElementById(tabId);
    if (activePane) activePane.classList.add('active');

    // Sidebar button styles
    document.querySelectorAll('.sidebar-nav-item').forEach(btn => {
      if (btn.getAttribute('data-tab') === tabId) {
        btn.classList.add('active-nav-tab');
      } else {
        btn.classList.remove('active-nav-tab');
      }
    });

    // Special view triggers
    if (tabId === 'tab-trajectory' && window.TrajectoryStudio) {
      window.TrajectoryStudio.resizeCanvas();
      window.TrajectoryStudio.render();
    }
  },

  bindModals() {
    // Appearance Modal
    const btnOpenAppearance = document.getElementById('btnOpenAppearanceModal');
    const modalAppearance = document.getElementById('modalAppearance');
    const btnCloseAppearance = document.getElementById('btnCloseAppearanceModal');

    if (btnOpenAppearance && modalAppearance) {
      btnOpenAppearance.addEventListener('click', () => {
        modalAppearance.classList.remove('hidden');
      });
    }

    if (btnCloseAppearance && modalAppearance) {
      btnCloseAppearance.addEventListener('click', () => {
        modalAppearance.classList.add('hidden');
      });
    }

    // Modal settings inputs
    const inputTheme = document.getElementById('inputSettingTheme');
    if (inputTheme) {
      inputTheme.addEventListener('change', (e) => {
        window.ThemeManager.setTheme(e.target.value);
      });
    }

    const inputGlass = document.getElementById('inputSettingGlass');
    if (inputGlass) {
      inputGlass.addEventListener('change', (e) => {
        window.ThemeManager.setGlass(e.target.checked);
      });
    }

    const inputMotion = document.getElementById('inputSettingMotion');
    if (inputMotion) {
      inputMotion.addEventListener('change', (e) => {
        window.ThemeManager.setMotion(e.target.checked);
      });
    }
  },

  bindVideoControls() {
    const video = document.getElementById('mainVideoPlayer');
    const btnPlay = document.getElementById('btnVideoPlay');
    const timeDisplay = document.getElementById('videoTimeDisplay');
    const btnPrevFrame = document.getElementById('btnVideoPrevFrame');
    const btnNextFrame = document.getElementById('btnVideoNextFrame');

    if (!video) return;

    if (btnPlay) {
      btnPlay.addEventListener('click', () => {
        if (video.paused) {
          video.play();
          btnPlay.innerHTML = '<i class="fa-solid fa-pause"></i>';
        } else {
          video.pause();
          btnPlay.innerHTML = '<i class="fa-solid fa-play"></i>';
        }
      });
    }

    video.addEventListener('timeupdate', () => {
      if (timeDisplay) {
        const cur = video.currentTime.toFixed(2);
        const dur = (video.duration || 20.03).toFixed(2);
        const frame = Math.round(video.currentTime * 30);
        timeDisplay.textContent = `${cur}s / ${dur}s [Frame ${frame}]`;
      }
    });

    if (btnPrevFrame) {
      btnPrevFrame.addEventListener('click', () => {
        video.pause();
        video.currentTime = Math.max(0, video.currentTime - 1 / 30);
      });
    }

    if (btnNextFrame) {
      btnNextFrame.addEventListener('click', () => {
        video.pause();
        video.currentTime = Math.min(video.duration, video.currentTime + 1 / 30);
      });
    }
  }
};

window.App = App;
document.addEventListener('DOMContentLoaded', () => App.init());
