// Dashboard interactivity for Nirantar
async function fetchJSON(url, opts) {
  const r = await fetch(url, opts);
  if (!r.ok) throw new Error('fetch failed');
  return await r.json();
}

function animateCounter(el, to) {
  const start = 0;
  const dur = 800;
  const step = (t) => {
    const val = Math.round(start + (to - start) * t);
    el.textContent = val.toLocaleString();
  };
  let startTime = null;
  function tick(ts) {
    if (!startTime) startTime = ts;
    const progress = Math.min(1, (ts - startTime) / dur);
    step(progress);
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

async function loadStatsAndRender() {
  try {
    const stats = await fetchJSON('/dashboard/api/stats');
    document.getElementById('resumes').textContent = stats.resumes.toLocaleString();
    document.getElementById('companies').textContent = stats.companies.toLocaleString();
    document.getElementById('opps').textContent = stats.opportunities.toLocaleString();
    document.getElementById('applications').textContent = stats.applications.toLocaleString();
    document.getElementById('weekly_reports').textContent = stats.weekly_reports.toLocaleString();
    document.getElementById('job_runs').textContent = stats.job_runs.toLocaleString();

    // Animated metric tiles
    const tiles = document.querySelectorAll('.metric .num');
    if (tiles && tiles.length) {
      animateCounter(tiles[0], stats.opportunities ?? 0);
      animateCounter(tiles[1], stats.applications ?? 0);
      animateCounter(tiles[2], Math.floor((stats.job_runs ?? 0) / 10));
      animateCounter(tiles[3], Math.round((stats.applications && stats.resumes) ? (stats.applications / Math.max(stats.resumes,1) * 100) : 0));
    }

    // Chart
    if (window.renderCountsChart) window.renderCountsChart(stats);
  } catch (e) {
    console.warn('stats load failed', e);
  }
}

async function loadApplications(filter='') {
  try {
    const rows = await fetchJSON('/dashboard/api/applications');
    const tbody = document.querySelector('#apps-table tbody');
    tbody.innerHTML = '';
    for (const row of rows) {
      if (filter) {
        const f = filter.toLowerCase();
        const match = (row.title||'').toLowerCase().includes(f) || (row.company||'').toLowerCase().includes(f);
        if (!match) continue;
      }
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${row.company||'-'}</td><td>${row.title||'-'}</td><td>${(Math.round(Math.random()*100))}%</td><td>${row.applied_date||'-'}</td><td><span class='badge applied'>Applied</span></td>`;
      tbody.appendChild(tr);
    }
  } catch (e) { console.warn(e); }
}

document.addEventListener('DOMContentLoaded', () => {
  // wire search
  const search = document.getElementById('apps-search');
  if (search) search.addEventListener('input', (e)=> loadApplications(e.target.value));

  const runBtn = document.getElementById('run-job');
  if (runBtn) runBtn.addEventListener('click', async ()=>{
    runBtn.disabled = true;
    try {
      const res = await fetchJSON('/dashboard/api/run-job', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({job_name:'manual'})});
      document.getElementById('run-result').textContent = 'Triggered: ' + res.job_name;
      await loadStatsAndRender();
      await loadApplications();
    } catch (e) { document.getElementById('run-result').textContent = 'Error'; }
    runBtn.disabled = false;
  });

  // render chart helper
  window.renderCountsChart = function(stats){
    try {
      const ctx = document.getElementById('countsChart').getContext('2d');
      if (window._countsChart) window._countsChart.destroy();
      window._countsChart = new Chart(ctx, {
        type:'line',
        data:{labels:['Resumes','Companies','Jobs','Apps','Reports','Runs'], datasets:[{label:'Counts',data:[stats.resumes,stats.companies,stats.opportunities,stats.applications,stats.weekly_reports,stats.job_runs],fill:true,backgroundColor:'rgba(139,92,246,0.08)',borderColor:'rgba(139,92,246,0.9)',tension:0.4}]},
        options:{plugins:{legend:{display:false}},scales:{x:{grid:{display:false},ticks:{color:'#94A3B8'}},y:{grid:{color:'rgba(255,255,255,0.02)'},ticks:{color:'#94A3B8'}}}
      });
    } catch(e){console.warn(e)}
  }

  loadStatsAndRender();
  loadApplications();
});
