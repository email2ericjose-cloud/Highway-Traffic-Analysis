/**
 * Trajectory Analysis Studio
 * Interactive Space-Time Diagram (x-t) and Bird's Eye View Roadway Canvas.
 */

const TrajectoryStudio = {
  data: null,
  activeClass: 'all',
  selectedVehicleId: 3,
  comparedVehicleId: 946,
  canvas: null,
  ctx: null,

  async init() {
    this.canvas = document.getElementById('canvasSpaceTime');
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');

    this.bindEvents();
    await this.loadData();
    this.render();
  },

  async loadData() {
    try {
      const res = await fetch('/api/trajectories');
      if (res.ok) {
        this.data = await res.json();
        this.populateVehicleSelectors();
      }
    } catch (e) {
      console.warn('Could not load trajectory data:', e);
    }
  },

  populateVehicleSelectors() {
    if (!this.data || !this.data.trajectories) return;

    const sel1 = document.getElementById('selectTrajVeh1');
    const sel2 = document.getElementById('selectTrajVeh2');
    if (!sel1 || !sel2) return;

    sel1.innerHTML = '';
    sel2.innerHTML = '<option value="">None (Single Vehicle)</option>';

    Object.values(this.data.trajectories).forEach(veh => {
      const opt1 = document.createElement('option');
      opt1.value = veh.track_id;
      opt1.textContent = `Veh #${veh.track_id} (${veh.class_name.toUpperCase()} - ${veh.direction})`;
      if (veh.track_id === 3) opt1.selected = true;
      sel1.appendChild(opt1);

      const opt2 = document.createElement('option');
      opt2.value = veh.track_id;
      opt2.textContent = `Veh #${veh.track_id} (${veh.class_name.toUpperCase()} - ${veh.direction})`;
      if (veh.track_id === 946) opt2.selected = true;
      sel2.appendChild(opt2);
    });
  },

  bindEvents() {
    const btnFilterAll = document.getElementById('btnFilterClassAll');
    const sel1 = document.getElementById('selectTrajVeh1');
    const sel2 = document.getElementById('selectTrajVeh2');

    if (sel1) {
      sel1.addEventListener('change', (e) => {
        this.selectedVehicleId = parseInt(e.target.value);
        this.render();
      });
    }

    if (sel2) {
      sel2.addEventListener('change', (e) => {
        this.comparedVehicleId = e.target.value ? parseInt(e.target.value) : null;
        this.render();
      });
    }

    window.addEventListener('resize', () => {
      if (this.canvas) {
        this.resizeCanvas();
        this.render();
      }
    });
    this.resizeCanvas();
  },

  resizeCanvas() {
    if (!this.canvas) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width * window.devicePixelRatio;
    this.canvas.height = 360 * window.devicePixelRatio;
    this.canvas.style.height = '360px';
  },

  filterByClass(cls) {
    this.activeClass = cls;
    document.querySelectorAll('.btn-filter-class').forEach(btn => {
      if (btn.getAttribute('data-class') === cls) {
        btn.classList.add('bg-amber-800', 'text-white');
      } else {
        btn.classList.remove('bg-amber-800', 'text-white');
      }
    });
    this.render();
  },

  render() {
    if (!this.ctx || !this.data || !this.data.trajectories) return;

    const width = this.canvas.width;
    const height = this.canvas.height;
    const ctx = this.ctx;
    const colors = ThemeManager.getCurrentColors();

    ctx.clearRect(0, 0, width, height);

    // Coordinate mapping
    const padding = { left: 60 * window.devicePixelRatio, right: 30 * window.devicePixelRatio, top: 30 * window.devicePixelRatio, bottom: 40 * window.devicePixelRatio };
    const tMin = 0.0, tMax = 20.03;
    const xMin = -40.0, xMax = 120.0;

    const mapX = (t) => padding.left + ((t - tMin) / (tMax - tMin)) * (width - padding.left - padding.right);
    const mapY = (x) => height - padding.bottom - ((x - xMin) / (xMax - xMin)) * (height - padding.top - padding.bottom);

    // Draw Grid
    ctx.strokeStyle = colors.grid;
    ctx.lineWidth = 1 * window.devicePixelRatio;
    ctx.fillStyle = colors.textMuted;
    ctx.font = `${11 * window.devicePixelRatio}px JetBrains Mono`;

    // Time lines (horizontal axis)
    for (let t = 0; t <= 20; t += 4) {
      const cx = mapX(t);
      ctx.beginPath();
      ctx.moveTo(cx, padding.top);
      ctx.lineTo(cx, height - padding.bottom);
      ctx.stroke();
      ctx.fillText(`${t}s`, cx - 8 * window.devicePixelRatio, height - padding.bottom + 20 * window.devicePixelRatio);
    }

    // Distance lines (vertical axis)
    for (let x = -40; x <= 120; x += 40) {
      const cy = mapY(x);
      ctx.beginPath();
      ctx.moveTo(padding.left, cy);
      ctx.lineTo(width - padding.right, cy);
      ctx.stroke();
      ctx.fillText(`${x}m`, 10 * window.devicePixelRatio, cy + 4 * window.devicePixelRatio);
    }

    // Draw Background Trajectories
    Object.values(this.data.trajectories).forEach(veh => {
      if (this.activeClass !== 'all' && veh.class_name !== this.activeClass) return;
      if (veh.track_id === this.selectedVehicleId || veh.track_id === this.comparedVehicleId) return;

      ctx.beginPath();
      ctx.strokeStyle = veh.direction === 'Westbound' ? 'rgba(128, 99, 66, 0.28)' : 'rgba(57, 124, 120, 0.28)';
      ctx.lineWidth = 1.2 * window.devicePixelRatio;

      veh.points.forEach((pt, i) => {
        const px = mapX(pt.t);
        const py = mapY(pt.x);
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      });
      ctx.stroke();
    });

    // Draw Highlighted Vehicle 1 (Follower, e.g. #3 Van)
    const veh1 = this.data.trajectories[this.selectedVehicleId];
    if (veh1) {
      ctx.beginPath();
      ctx.strokeStyle = '#B43B35'; // Critical Red
      ctx.lineWidth = 3.5 * window.devicePixelRatio;
      veh1.points.forEach((pt, i) => {
        const px = mapX(pt.t);
        const py = mapY(pt.x);
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      });
      ctx.stroke();

      // Label
      if (veh1.points.length > 0) {
        const last = veh1.points[veh1.points.length - 1];
        ctx.fillStyle = '#B43B35';
        ctx.font = `bold ${12 * window.devicePixelRatio}px Plus Jakarta Sans`;
        ctx.fillText(`Veh #${veh1.track_id} (${veh1.class_name})`, mapX(last.t) + 6, mapY(last.x));
      }
    }

    // Draw Highlighted Vehicle 2 (Leader, e.g. #946 Bus)
    const veh2 = this.data.trajectories[this.comparedVehicleId];
    if (veh2) {
      ctx.beginPath();
      ctx.strokeStyle = '#397C78'; // Teal
      ctx.lineWidth = 3.5 * window.devicePixelRatio;
      veh2.points.forEach((pt, i) => {
        const px = mapX(pt.t);
        const py = mapY(pt.x);
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      });
      ctx.stroke();

      if (veh2.points.length > 0) {
        const last = veh2.points[veh2.points.length - 1];
        ctx.fillStyle = '#397C78';
        ctx.font = `bold ${12 * window.devicePixelRatio}px Plus Jakarta Sans`;
        ctx.fillText(`Veh #${veh2.track_id} (${veh2.class_name})`, mapX(last.t) + 6, mapY(last.x));
      }
    }

    // Mark Conflict Point if comparing #3 and #946 at Frame 341 (t = 11.37s)
    if (this.selectedVehicleId === 3 && this.comparedVehicleId === 946) {
      const conflictT = 11.37;
      const conflictX = -16.3;
      const cx = mapX(conflictT);
      const cy = mapY(conflictX);

      ctx.beginPath();
      ctx.arc(cx, cy, 7 * window.devicePixelRatio, 0, Math.PI * 2);
      ctx.fillStyle = '#B43B35';
      ctx.fill();
      ctx.strokeStyle = '#FFFFFF';
      ctx.lineWidth = 2 * window.devicePixelRatio;
      ctx.stroke();

      ctx.fillStyle = '#B43B35';
      ctx.font = `bold ${11 * window.devicePixelRatio}px JetBrains Mono`;
      ctx.fillText('CRITICAL CONFLICT (TTC: 0.11s, Gap: 0.50m)', cx + 12, cy - 8);
    }
  }
};

window.TrajectoryStudio = TrajectoryStudio;
