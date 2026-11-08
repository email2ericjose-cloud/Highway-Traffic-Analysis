"""
Build script to generate outputs/dashboard/index.html
====================================================
Embeds the CSS design system, HTML workspaces, interactive trajectory studio,
AASHTO stopping distance calculator, and verified fallback datasets so that
outputs/dashboard/index.html works both standalone (file://) and when served via HTTP.
"""

import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

with open(PROJECT_ROOT / 'app' / 'static' / 'css' / 'studio.css', 'r', encoding='utf-8') as f:
    css = f.read()

with open(PROJECT_ROOT / 'outputs' / 'safety_analysis' / 'critical_distance_analysis.json', 'r', encoding='utf-8') as f:
    crit_json = json.load(f)

with open(PROJECT_ROOT / 'outputs' / 'safety_analysis' / 'ranked_collision_conflicts.json', 'r', encoding='utf-8') as f:
    conflicts_json = json.load(f)

with open(PROJECT_ROOT / 'outputs' / 'analysis' / 'trajectory_studio_data.json', 'r', encoding='utf-8') as f:
    traj_json = json.load(f)

with open(PROJECT_ROOT / 'app' / 'static' / 'index.html', 'r', encoding='utf-8') as f:
    html_src = f.read()

# Replace asset paths for dashboard folder (outputs/dashboard/)
# Relative to outputs/dashboard/, files in outputs/ are at ../
html_adjusted = html_src.replace('/outputs/', '../')
html_adjusted = html_adjusted.replace('src="/outputs/', 'src="../')
html_adjusted = html_adjusted.replace('href="/outputs/', 'href="../')

# Replace external CSS link with inline style
css_block = f"<style>\n{css}\n</style>"
html_adjusted = html_adjusted.replace('<link rel="stylesheet" href="/static/css/studio.css">', css_block)

# Read JS modules
with open(PROJECT_ROOT / 'app' / 'static' / 'js' / 'theme.js', 'r', encoding='utf-8') as f:
    js_theme = f.read()

with open(PROJECT_ROOT / 'app' / 'static' / 'js' / 'charts.js', 'r', encoding='utf-8') as f:
    js_charts = f.read()

with open(PROJECT_ROOT / 'app' / 'static' / 'js' / 'trajectory_studio.js', 'r', encoding='utf-8') as f:
    js_traj = f.read()

with open(PROJECT_ROOT / 'app' / 'static' / 'js' / 'safety_studio.js', 'r', encoding='utf-8') as f:
    js_safety = f.read()

with open(PROJECT_ROOT / 'app' / 'static' / 'js' / 'pipeline_studio.js', 'r', encoding='utf-8') as f:
    js_pipe = f.read()

with open(PROJECT_ROOT / 'app' / 'static' / 'js' / 'app.js', 'r', encoding='utf-8') as f:
    js_app = f.read()

# Adjust fetch calls to try local files first, then API, then fallback data
js_traj_adj = js_traj.replace(
    "const res = await fetch('/api/trajectories');",
    """let res;
      try {
        res = await fetch('../analysis/trajectory_studio_data.json');
        if (!res.ok) res = await fetch('/api/trajectories');
        if (!res.ok) throw new Error('fetch failed');
      } catch (err) {
        if (window.EMBEDDED_TRAJ_DATA) {
          this.data = window.EMBEDDED_TRAJ_DATA;
          this.populateVehicleSelectors();
          return;
        }
      }"""
)

js_safety_adj = js_safety.replace(
    "const resCrit = await fetch('/api/critical-distances');",
    """let resCrit;
      try {
        resCrit = await fetch('../safety_analysis/critical_distance_analysis.json');
        if (!resCrit.ok) resCrit = await fetch('/api/critical-distances');
        if (!resCrit.ok) throw new Error('fetch failed');
      } catch (err) {
        if (window.EMBEDDED_CRITICAL_DATA) {
          this.events = window.EMBEDDED_CRITICAL_DATA.events || [];
        }
      }"""
)

js_safety_adj = js_safety_adj.replace(
    "const resConf = await fetch('/api/conflicts');",
    """let resConf;
      try {
        resConf = await fetch('../safety_analysis/ranked_collision_conflicts.json');
        if (!resConf.ok) resConf = await fetch('/api/conflicts');
        if (!resConf.ok) throw new Error('fetch failed');
      } catch (err) {
        if (window.EMBEDDED_CONFLICTS_DATA) {
          this.allConflicts = window.EMBEDDED_CONFLICTS_DATA;
          this.renderConflictTable(this.allConflicts);
        }
      }"""
)

js_safety_adj = js_safety_adj.replace(
    "src = `/outputs/${ev.image_rel_path}`",
    "src = `../${ev.image_rel_path}`"
)

js_pipe_adj = js_pipe.replace(
    "const res = await fetch('/api/pipeline/status');",
    """let res;
      try {
        res = await fetch('/api/pipeline/status');
        if (!res.ok) res = await fetch('http://localhost:8080/api/pipeline/status');
      } catch (err) { return; }"""
)

js_pipe_adj = js_pipe_adj.replace(
    "fetch('/api/pipeline/run'",
    "fetch('http://localhost:8080/api/pipeline/run'"
)

js_app_adj = js_app.replace(
    "const res = await fetch('/api/status');",
    """let res;
      try {
        res = await fetch('/api/status');
        if (!res.ok) res = await fetch('http://localhost:8080/api/status');
      } catch (err) {}"""
)

# Inline fallback JSON datasets
fallback_script = f"""
  <script>
    window.EMBEDDED_CRITICAL_DATA = {json.dumps(crit_json)};
    window.EMBEDDED_CONFLICTS_DATA = {json.dumps(conflicts_json[:60])};
    window.EMBEDDED_TRAJ_DATA = {json.dumps(traj_json)};
  </script>
"""

combined_js = f"""
  {fallback_script}
  <script>
{js_theme}
{js_charts}
{js_traj_adj}
{js_safety_adj}
{js_pipe_adj}
{js_app_adj}
  </script>
"""

# Remove external script tags from html_adjusted
for s in [
    '<script src="/static/js/theme.js"></script>',
    '<script src="/static/js/charts.js"></script>',
    '<script src="/static/js/trajectory_studio.js"></script>',
    '<script src="/static/js/safety_studio.js"></script>',
    '<script src="/static/js/pipeline_studio.js"></script>',
    '<script src="/static/js/app.js"></script>'
]:
    html_adjusted = html_adjusted.replace(s, '')

# Inject combined script before </body>
html_adjusted = html_adjusted.replace('</body>', f'{combined_js}\n</body>')

output_path = PROJECT_ROOT / 'outputs' / 'dashboard' / 'index.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_adjusted)

print(f"Successfully generated {output_path}! File size: {os.path.getsize(output_path) / 1024:.1f} KB")
