/**
 * Critical Distance & Collision Risk Studio
 * Dynamic AASHTO Stopping Distance Formula Recalculation, Conflict Frame Inspector, and Conflict Table.
 */

const SafetyStudio = {
  events: [],
  allConflicts: [],
  currentEventIndex: 0,
  reactionTime: 1.5,
  deceleration: 3.4,

  async init() {
    this.bindControls();
    await this.loadData();
    this.recalculateAndRender();
  },

  async loadData() {
    try {
      const resCrit = await fetch('/api/critical-distances');
      if (resCrit.ok) {
        const critData = await resCrit.json();
        this.events = critData.events || [];
      }

      const resConf = await fetch('/api/conflicts');
      if (resConf.ok) {
        this.allConflicts = await resConf.json();
        this.renderConflictTable(this.allConflicts);
      }
    } catch (e) {
      console.warn('Error loading safety data:', e);
    }
  },

  bindControls() {
    const sliderTr = document.getElementById('sliderReactionTime');
    const valTr = document.getElementById('valReactionTime');
    if (sliderTr) {
      sliderTr.addEventListener('input', (e) => {
        this.reactionTime = parseFloat(e.target.value);
        if (valTr) valTr.textContent = `${this.reactionTime.toFixed(1)}s`;
        this.recalculateAndRender();
      });
    }

    const sliderDecel = document.getElementById('sliderDeceleration');
    const valDecel = document.getElementById('valDeceleration');
    if (sliderDecel) {
      sliderDecel.addEventListener('input', (e) => {
        this.deceleration = parseFloat(e.target.value);
        if (valDecel) valDecel.textContent = `${this.deceleration.toFixed(1)} m/s²`;
        this.recalculateAndRender();
      });
    }

    const selectEvent = document.getElementById('selectConflictEvent');
    if (selectEvent) {
      selectEvent.addEventListener('change', (e) => {
        this.currentEventIndex = parseInt(e.target.value);
        this.renderInspector();
      });
    }

    const inputSearch = document.getElementById('inputSearchConflicts');
    if (inputSearch) {
      inputSearch.addEventListener('input', (e) => {
        this.filterTable(e.target.value);
      });
    }
  },

  calcSafeDistance(vFollowerKmh, vLeaderKmh, tr, af) {
    const vf = vFollowerKmh / 3.6; // m/s
    const vl = vLeaderKmh / 3.6;   // m/s
    const dReaction = vf * tr;
    const dBraking = (vf * vf) / (2 * af) - (vl * vl) / (2 * af);
    const dSafe = dReaction + Math.max(0, dBraking);
    return Math.max(1.0, dSafe);
  },

  recalculateAndRender() {
    if (!this.events || this.events.length === 0) return;

    this.events.forEach(ev => {
      const dSafe = this.calcSafeDistance(ev.v_follower_kmh, ev.v_leader_kmh, this.reactionTime, this.deceleration);
      ev.dynamic_d_safe = roundVal(dSafe, 2);
      ev.dynamic_margin = roundVal(ev.clear_gap_m - dSafe, 2);
    });

    this.populateEventSelect();
    this.renderInspector();
  },

  populateEventSelect() {
    const select = document.getElementById('selectConflictEvent');
    if (!select) return;

    select.innerHTML = '';
    this.events.forEach((ev, idx) => {
      const opt = document.createElement('option');
      opt.value = idx;
      opt.textContent = `Rank #${ev.rank}: Veh #${ev.follower_id} (${ev.follower_class}) -> Veh #${ev.leader_id} (${ev.leader_class}) [Frame ${ev.frame_id}]`;
      if (idx === this.currentEventIndex) opt.selected = true;
      select.appendChild(opt);
    });
  },

  renderInspector() {
    const ev = this.events[this.currentEventIndex];
    if (!ev) return;

    // Image update
    const img = document.getElementById('imgConflictFrame');
    if (img) {
      img.src = `/outputs/${ev.image_rel_path}`;
    }

    // Telemetry text updates
    setElemText('dispRank', `Rank #${ev.rank}`);
    setElemText('dispVehPair', `Veh #${ev.follower_id} (${ev.follower_class.toUpperCase()}) following Veh #${ev.leader_id} (${ev.leader_class.toUpperCase()})`);
    setElemText('dispTTC', `${ev.ttc_sec.toFixed(2)}s`);
    setElemText('dispDRAC', `${ev.drac_mps2.toFixed(1)} m/s²`);
    setElemText('dispClosingSpeed', `${ev.closing_speed_kmh.toFixed(1)} km/h`);
    setElemText('dispObservedGap', `${ev.clear_gap_m.toFixed(2)} m`);
    setElemText('dispSafeStopping', `${ev.dynamic_d_safe.toFixed(2)} m`);

    const dispMargin = document.getElementById('dispSafetyMargin');
    if (dispMargin) {
      const m = ev.dynamic_margin;
      dispMargin.textContent = `${m > 0 ? '+' : ''}${m.toFixed(2)} m`;
      dispMargin.className = `font-mono font-bold text-sm ${m < 0 ? 'text-red-600' : 'text-emerald-600'}`;
    }

    const badgeRisk = document.getElementById('badgeRiskTier');
    if (badgeRisk) {
      badgeRisk.textContent = ev.risk_tier;
      badgeRisk.className = 'px-2.5 py-1 rounded-full text-xs font-bold font-mono bg-red-100 text-red-800 border border-red-300';
    }
  },

  renderConflictTable(list) {
    const tbody = document.getElementById('tbodyConflicts');
    if (!tbody) return;

    tbody.innerHTML = '';
    list.slice(0, 30).forEach(c => {
      const tr = document.createElement('tr');
      tr.className = 'border-b hover:bg-amber-50/40 cursor-pointer transition text-xs';
      tr.style.borderColor = 'var(--border-color)';
      
      const isCritical = c.min_ttc_sec <= 1.5;
      const badgeClass = isCritical ? 'bg-red-100 text-red-800 border-red-300' : 'bg-amber-100 text-amber-800 border-amber-300';

      tr.innerHTML = `
        <td class="p-2 font-mono font-bold text-center">${c.rank}</td>
        <td class="p-2 font-semibold">#${c.follower_id} <span class="text-slate-500 font-normal">(${c.follower_class})</span> &rarr; #${c.leader_id} <span class="text-slate-500 font-normal">(${c.leader_class})</span></td>
        <td class="p-2 font-mono text-center font-bold ${isCritical ? 'text-red-700' : 'text-amber-700'}">${c.min_ttc_sec.toFixed(2)}s</td>
        <td class="p-2 font-mono text-center">${c.max_drac_mps2.toFixed(1)}</td>
        <td class="p-2 font-mono text-center">${c.max_closing_speed_kmh.toFixed(1)} km/h</td>
        <td class="p-2 font-mono text-center text-slate-600">${c.hotspot_zone_m}</td>
        <td class="p-2 text-center">
          <span class="px-2 py-0.5 rounded-full text-[10px] font-bold border ${badgeClass}">${c.risk_tier.split(':')[0]}</span>
        </td>
      `;

      tr.addEventListener('click', () => {
        // Find if this event is in top 10
        const foundIdx = this.events.findIndex(e => e.rank === c.rank);
        if (foundIdx >= 0) {
          this.currentEventIndex = foundIdx;
          this.renderInspector();
          document.getElementById('sectionSafetyInspector')?.scrollIntoView({ behavior: 'smooth' });
        }
      });

      tbody.appendChild(tr);
    });

    const countElem = document.getElementById('countConflicts');
    if (countElem) countElem.textContent = `${list.length} conflict pairs registered (showing top 30)`;
  },

  filterTable(query) {
    if (!query) {
      this.renderConflictTable(this.allConflicts);
      return;
    }
    const q = query.toLowerCase();
    const filtered = this.allConflicts.filter(c => {
      return (
        c.follower_id.toString().includes(q) ||
        c.leader_id.toString().includes(q) ||
        c.follower_class.toLowerCase().includes(q) ||
        c.leader_class.toLowerCase().includes(q) ||
        c.hotspot_zone_m.toLowerCase().includes(q)
      );
    });
    this.renderConflictTable(filtered);
  }
};

function roundVal(num, dec = 2) {
  return Math.round(num * Math.pow(10, dec)) / Math.pow(10, dec);
}

function setElemText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

window.SafetyStudio = SafetyStudio;
