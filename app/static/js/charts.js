/**
 * Chart Manager for UAV Traffic Studio
 * Handles creation and dynamic color updates of all Chart.js visualizations.
 */

const ChartManager = {
  instances: {},

  init() {
    this.createModalSplitChart();
    this.createSpeedDistributionChart();
    this.createFlowDensityChart();
    this.createSSMChart();
    this.createHotspotChart();
  },

  createModalSplitChart() {
    const ctx = document.getElementById('chartModalSplit');
    if (!ctx) return;

    const colors = ThemeManager.getCurrentColors();
    this.instances.modalSplit = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Car (64.6%)', 'Van (16.7%)', 'Bus (14.6%)', 'Truck (2.1%)', 'Motorcycle (2.1%)'],
        datasets: [{
          data: [31, 8, 7, 1, 1],
          backgroundColor: ['#806342', '#397C78', '#476783', '#B77925', '#B43B35'],
          borderColor: colors.cardBg,
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { color: colors.text, boxWidth: 12, font: { size: 11, family: 'Plus Jakarta Sans' } }
          }
        },
        cutout: '68%'
      }
    });
  },

  createSpeedDistributionChart() {
    const ctx = document.getElementById('chartSpeedDist');
    if (!ctx) return;

    const colors = ThemeManager.getCurrentColors();
    this.instances.speedDist = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['15-20', '20-25', '25-30', '30-35', '35-40', '40-45 km/h'],
        datasets: [
          {
            label: 'Observed Vehicle Count',
            data: [6, 18, 14, 7, 2, 1],
            backgroundColor: colors.primary + 'B3',
            borderColor: colors.primary,
            borderWidth: 1.5,
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              footer: () => 'Time-mean speed ut: 26.6 km/h | 85th percentile: 31.7 km/h'
            }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: colors.textMuted, font: { size: 10 } }
          },
          y: {
            grid: { color: colors.grid },
            ticks: { color: colors.textMuted, font: { size: 10 } }
          }
        }
      }
    });
  },

  createFlowDensityChart() {
    const ctx = document.getElementById('chartFlowDensity');
    if (!ctx) return;

    const colors = ThemeManager.getCurrentColors();
    this.instances.flowDensity = new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['0-4s', '4-8s', '8-12s', '12-16s', '16-20s'],
        datasets: [
          {
            label: 'Total Flow Rate (veh/hr)',
            data: [7920, 8460, 9180, 8820, 8740],
            borderColor: colors.primary,
            backgroundColor: colors.primary + '20',
            tension: 0.35,
            fill: true
          },
          {
            label: 'Westbound Flow (veh/hr)',
            data: [4620, 4980, 5340, 5120, 5100],
            borderColor: colors.secondary,
            borderDash: [5, 5],
            tension: 0.35
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: { color: colors.text, boxWidth: 12, font: { size: 11 } }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: colors.textMuted }
          },
          y: {
            grid: { color: colors.grid },
            ticks: { color: colors.textMuted }
          }
        }
      }
    });
  },

  createSSMChart() {
    const ctx = document.getElementById('chartSSM');
    if (!ctx) return;

    const colors = ThemeManager.getCurrentColors();
    this.instances.ssm = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Critical (<1.5s)', 'Severe (1.5-2.5s)', 'Potential (2.5-4.0s)', 'Safe (>4.0s)'],
        datasets: [{
          label: 'TTC Event Instances',
          data: [2391, 380, 475, 422],
          backgroundColor: ['#B43B35', '#B77925', '#476783', '#36734A'],
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: { grid: { display: false }, ticks: { color: colors.textMuted } },
          y: { grid: { color: colors.grid }, ticks: { color: colors.textMuted } }
        }
      }
    });
  },

  createHotspotChart() {
    const ctx = document.getElementById('chartHotspotDist');
    if (!ctx) return;

    const colors = ThemeManager.getCurrentColors();
    this.instances.hotspot = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['[-40,-20]', '[-20,0]', '[0,20]', '[20,40]', '[40,60]', '[60,80]', '[80,100]', '[100,120] m'],
        datasets: [{
          label: 'Conflict Frequency',
          data: [19, 24, 37, 27, 20, 24, 32, 11],
          backgroundColor: ['#476783', '#B77925', '#B43B35', '#B77925', '#476783', '#B77925', '#B43B35', '#36734A'],
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              afterLabel: (ctx) => ctx.dataIndex === 2 ? '⚠️ Primary Bottleneck (37 conflicts)' : (ctx.dataIndex === 6 ? '⚠️ Secondary Bottleneck (32 conflicts)' : '')
            }
          }
        },
        scales: {
          x: { grid: { display: false }, ticks: { color: colors.textMuted } },
          y: { grid: { color: colors.grid }, ticks: { color: colors.textMuted } }
        }
      }
    });
  },

  updateAllCharts() {
    const colors = ThemeManager.getCurrentColors();
    Object.values(this.instances).forEach(chart => {
      if (!chart) return;
      if (chart.options.scales) {
        if (chart.options.scales.x && chart.options.scales.x.ticks) chart.options.scales.x.ticks.color = colors.textMuted;
        if (chart.options.scales.y && chart.options.scales.y.ticks) chart.options.scales.y.ticks.color = colors.textMuted;
        if (chart.options.scales.y && chart.options.scales.y.grid) chart.options.scales.y.grid.color = colors.grid;
      }
      if (chart.options.plugins && chart.options.plugins.legend && chart.options.plugins.legend.labels) {
        chart.options.plugins.legend.labels.color = colors.text;
      }
      chart.update();
    });
  }
};

window.ChartManager = ChartManager;
