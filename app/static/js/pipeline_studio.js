/**
 * Automated Pipeline Studio Controller
 * Handles backend execution trigger, real-time stage tracking, and live log streaming.
 */

const PipelineStudio = {
  timer: null,
  isRunning: false,

  init() {
    this.bindControls();
    this.pollStatus();
  },

  bindControls() {
    const btnRun = document.getElementById('btnRunPipeline');
    if (btnRun) {
      btnRun.addEventListener('click', () => this.triggerPipeline());
    }

    const btnHeaderRun = document.getElementById('btnHeaderRunPipeline');
    if (btnHeaderRun) {
      btnHeaderRun.addEventListener('click', () => {
        window.App.switchTab('tab-pipeline');
        this.triggerPipeline();
      });
    }
  },

  async triggerPipeline() {
    if (this.isRunning) return;

    const btn = document.getElementById('btnRunPipeline');
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i> Starting Pipeline...';
    }

    const videoSelect = document.getElementById('selectPipelineVideo');
    const inputLaneWidth = document.getElementById('inputPipelineLaneWidth');
    const chkSkipTracking = document.getElementById('chkSkipTracking');

    const payload = {
      video: videoSelect ? videoSelect.value : 'videos/National Highway 48.mp4',
      lane_width: inputLaneWidth ? parseFloat(inputLaneWidth.value) : 3.5,
      skip_tracking: chkSkipTracking ? chkSkipTracking.checked : true
    };

    try {
      const res = await fetch('/api/pipeline/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        this.startPolling();
      } else {
        alert('Failed to start pipeline: ' + data.message);
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = '<i class="fa-solid fa-play mr-2"></i> Run Automated Pipeline';
        }
      }
    } catch (e) {
      alert('Error triggering pipeline: ' + e);
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-play mr-2"></i> Run Automated Pipeline';
      }
    }
  },

  startPolling() {
    this.isRunning = true;
    if (this.timer) clearInterval(this.timer);
    this.timer = setInterval(() => this.pollStatus(), 1200);
  },

  stopPolling() {
    this.isRunning = false;
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
    const btn = document.getElementById('btnRunPipeline');
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<i class="fa-solid fa-play mr-2"></i> Run Automated Pipeline';
    }
  },

  async pollStatus() {
    try {
      const res = await fetch('/api/pipeline/status');
      if (!res.ok) return;
      const data = await res.json();

      this.renderStatus(data);

      if (data.status === 'completed' || data.status === 'error') {
        if (this.isRunning) {
          this.stopPolling();
        }
      }
    } catch (e) {
      console.warn('Error polling pipeline status:', e);
    }
  },

  renderStatus(data) {
    // Progress Bar
    const bar = document.getElementById('pipelineProgressBar');
    if (bar) bar.style.width = `${data.progress_percent}%`;

    const txtPct = document.getElementById('pipelineProgressText');
    if (txtPct) txtPct.textContent = `${data.progress_percent}%`;

    const txtStage = document.getElementById('pipelineCurrentStageText');
    if (txtStage) txtStage.textContent = data.current_stage;

    const txtElapsed = document.getElementById('pipelineElapsedText');
    if (txtElapsed) txtElapsed.textContent = `${data.elapsed_seconds}s`;

    // Status Badge
    const badge = document.getElementById('pipelineStatusBadge');
    if (badge) {
      if (data.status === 'running') {
        badge.className = 'px-3 py-1 rounded-full text-xs font-mono font-bold bg-amber-100 text-amber-800 border border-amber-300';
        badge.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-1"></i> RUNNING';
      } else if (data.status === 'completed') {
        badge.className = 'px-3 py-1 rounded-full text-xs font-mono font-bold bg-emerald-100 text-emerald-800 border border-emerald-300';
        badge.innerHTML = '<i class="fa-solid fa-circle-check mr-1"></i> COMPLETED';
      } else if (data.status === 'error') {
        badge.className = 'px-3 py-1 rounded-full text-xs font-mono font-bold bg-red-100 text-red-800 border border-red-300';
        badge.innerHTML = '<i class="fa-solid fa-circle-xmark mr-1"></i> FAILED';
      }
    }

    // Stages List
    const stagesContainer = document.getElementById('pipelineStagesList');
    if (stagesContainer && data.stages) {
      stagesContainer.innerHTML = '';
      data.stages.forEach(st => {
        const item = document.createElement('div');
        item.className = 'flex items-center justify-between p-2.5 rounded-lg border text-xs';
        item.style.borderColor = 'var(--border-color)';
        item.style.background = 'var(--bg-card)';

        let icon = '<i class="fa-solid fa-clock text-slate-400"></i>';
        let statusBadge = '<span class="text-slate-400">Pending</span>';

        if (st.status === 'completed') {
          icon = '<i class="fa-solid fa-circle-check text-emerald-600"></i>';
          statusBadge = `<span class="text-emerald-700 font-semibold font-mono">${st.duration}</span>`;
        } else if (st.status === 'running') {
          icon = '<i class="fa-solid fa-spinner fa-spin text-amber-600"></i>';
          statusBadge = '<span class="text-amber-700 font-semibold font-mono">Running...</span>';
        }

        item.innerHTML = `
          <div class="flex items-center gap-2">
            ${icon}
            <span class="font-medium">${st.id}. ${st.name}</span>
          </div>
          <div>${statusBadge}</div>
        `;
        stagesContainer.appendChild(item);
      });
    }

    // Live Logs Terminal
    const logBox = document.getElementById('pipelineLogTerminal');
    if (logBox && data.logs) {
      logBox.textContent = data.logs.join('\n');
      logBox.scrollTop = logBox.scrollHeight;
    }
  }
};

window.PipelineStudio = PipelineStudio;
