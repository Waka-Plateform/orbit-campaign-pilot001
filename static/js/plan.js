import { toast, subscribe } from './sse.js';

const json = (url, options = {}) => fetch(url, { headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }, ...options }).then(async (r) => { if (!r.ok) throw new Error(await r.text()); return r.json(); });
const $ = (id) => document.getElementById(id);
const timezones = ['Europe/Paris', 'UTC', 'Europe/Brussels', 'Europe/Luxembourg'];

function setText(id, value) { const node = $(id); if (node) node.textContent = value ?? '0'; }
function toLocalInput(value) { if (!value) return ''; const d = new Date(value); if (Number.isNaN(d.getTime())) return ''; return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16); }
function fromLocalInput(value) { return value ? new Date(value).toISOString() : null; }

function windowRow(item = {}) {
  const row = document.createElement('div');
  row.className = 'plan-window-row';
  row.innerHTML = `
    <label class="orbit-label"><span>Jours</span><input class="orbit-input" data-window-field="days" value="${(item.days || [1,2,3,4,5]).join(',')}"></label>
    <label class="orbit-label"><span>Début</span><input class="orbit-input" data-window-field="start_hour" type="number" min="0" max="23" value="${item.start_hour ?? 9}"></label>
    <label class="orbit-label"><span>Fin</span><input class="orbit-input" data-window-field="end_hour" type="number" min="0" max="23" value="${item.end_hour ?? 19}"></label>
    <button class="orbit-button orbit-button-danger" type="button"><i class="bi bi-trash"></i> Supprimer</button>`;
  row.querySelector('button').addEventListener('click', () => row.remove());
  return row;
}

function collectWindows() {
  return [...document.querySelectorAll('.plan-window-row')].map((row) => ({
    days: row.querySelector('[data-window-field="days"]').value.split(',').map((v) => Number(v.trim())).filter(Boolean),
    start_hour: Number(row.querySelector('[data-window-field="start_hour"]').value),
    end_hour: Number(row.querySelector('[data-window-field="end_hour"]').value)
  }));
}

async function loadPlan() {
  const root = document.querySelector('[data-section="plan"], [data-section="main"]');
  if (!root) return;
  if (root.dataset.section === 'main') return loadMain();
  timezones.forEach((tz) => { const option = document.createElement('option'); option.value = tz; option.textContent = tz; $('plan-timezone').appendChild(option); });
  const data = await json('/api/console/plan');
  const plan = data.plan || data;
  setText('plan-status', plan.status || data.status || 'scheduled');
  setText('plan-window-deferred', data.deferred_by_window || 0);
  setText('plan-throttled', data.throttled || 0);
  setText('plan-batch-label', plan.batch_size || 0);
  $('plan-start-at').value = toLocalInput(plan.start_at);
  $('plan-end-at').value = toLocalInput(plan.end_at);
  $('plan-timezone').value = plan.timezone || 'Europe/Paris';
  $('plan-max-minute').value = plan.throttle?.max_per_minute ?? 0;
  $('plan-max-hour').value = plan.throttle?.max_per_hour ?? 0;
  $('plan-max-day').value = plan.throttle?.max_per_day ?? 0;
  $('plan-batch-size').value = plan.batch_size ?? 50;
  const holder = $('plan-windows'); holder.innerHTML = '';
  (plan.allowed_windows?.length ? plan.allowed_windows : [{ days:[1,2,3,4,5], start_hour:9, end_hour:19 }]).forEach((w) => holder.appendChild(windowRow(w)));
}

async function savePlan(event) {
  event.preventDefault();
  const payload = {
    start_at: fromLocalInput($('plan-start-at').value),
    end_at: fromLocalInput($('plan-end-at').value),
    timezone: $('plan-timezone').value,
    allowed_windows: collectWindows(),
    throttle: { max_per_minute: Number($('plan-max-minute').value), max_per_hour: Number($('plan-max-hour').value), max_per_day: Number($('plan-max-day').value) },
    batch_size: Number($('plan-batch-size').value)
  };
  await json('/api/console/plan', { method: 'POST', body: JSON.stringify(payload) });
  toast('Plan enregistré.');
  await loadPlan();
}

async function planAction(action) {
  if ((action === 'stop' || action === 'start') && !window.confirm('Confirmer cette action de pilotage ?')) return;
  await json(`/api/console/plan/${action}`, { method: 'POST', body: JSON.stringify({}) });
  toast('Action exécutée.');
  await loadPlan();
}

function renderBreakdown(holder, items = []) { holder.innerHTML = items.map((x) => `<span class="orbit-chip">${x.label || x.name || x.source || 'N/A'} · ${x.count ?? x.value ?? 0}</span>`).join('') || '<div class="orbit-empty">Aucune donnée.</div>'; }
async function loadMain() {
  const data = await json('/api/console/main');
  setText('main-campaign-name', data.name || 'pilot001');
  setText('main-objective', data.objective || data.scope_brief?.objective || 'Informer les clients des nouvelles CGV.');
  setText('main-runtime-status', data.status || data.runtime_status || 'scheduled');
  setText('main-owner', data.owner || 'Orbit');
  setText('main-golive', data.go_live || data.start_at || 'À planifier');
  setText('main-contacts-count', data.contacts_count || data.base?.contacts_count || 3485);
  renderBreakdown($('main-source-breakdown'), data.base?.by_source || []);
  const aud = $('main-audience-breakdown');
  aud.innerHTML = (data.base?.by_audience || data.audiences || []).map((a) => `<div class="console-bar"><div>${a.label || a.id}</div><div class="console-bar-track"><span style="--bar:${Math.min(100, a.percent || 100)}%"></span></div></div>`).join('') || '<div class="orbit-empty">Audience globale.</div>';
  const log = $('main-lifecycle-log');
  log.innerHTML = (data.lifecycle_log || []).map((l) => `<div class="orbit-chip">${l.ts || ''} · ${l.action || l.event || ''}</div>`).join('') || '<div class="orbit-empty">Aucune trace.</div>';
  const metrics = $('main-success-metrics');
  metrics.innerHTML = (data.success_metrics || data.metrics || []).map((m) => `<article class="orbit-card"><h3>${m.label || m.id}</h3><p>${m.current ?? 0} / ${m.target || '>= 90%'}</p><div class="orbit-progress"><span style="--value:${Math.min(100, Number(m.percent ?? m.current ?? 0))}%"></span></div></article>`).join('') || '<div class="orbit-empty">Objectif : délivrabilité email >= 90 %.</div>';
  const flow = $('main-flow-svg'); if (flow) flow.data = `/api/console/main/flow.svg?mode=runtime&v=${encodeURIComponent(data.flow_version || Date.now())}`;
}

function wireMain() {
  document.querySelectorAll('[data-main-action]').forEach((btn) => btn.addEventListener('click', () => planAction(btn.dataset.mainAction === 'finish' ? 'stop' : btn.dataset.mainAction)));
  const drawer = $('main-node-drawer');
  document.querySelectorAll('[data-drawer-close]').forEach((n) => n.addEventListener('click', () => { drawer?.classList.remove('is-open'); document.querySelector('.console-drawer-backdrop')?.classList.remove('is-open'); }));
}

document.addEventListener('DOMContentLoaded', () => {
  loadPlan().catch((e) => toast(e.message));
  $('plan-form')?.addEventListener('submit', savePlan);
  $('plan-add-window')?.addEventListener('click', () => $('plan-windows').appendChild(windowRow()));
  document.querySelectorAll('[data-plan-action]').forEach((btn) => btn.addEventListener('click', () => planAction(btn.dataset.planAction).catch((e) => toast(e.message))));
  wireMain();
  subscribe('kpi.updated', () => loadPlan().catch(() => {}));
});
