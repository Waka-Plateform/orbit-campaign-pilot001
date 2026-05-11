import { toast } from './sse.js';
const $ = (id) => document.getElementById(id);
const api = (url, options = {}) => fetch(url, { headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }, ...options }).then(async (r) => { if (!r.ok) throw new Error(await r.text()); return r.json(); });
const esc = (v) => String(v ?? '').replace(/[&<>"]/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const variables = {
  email: ['email_subscription_id','email_resource_group','email_communication_service_id','email_communication_service_endpoint','email_domain','email_sender_username','email_display_name','email_reply_to'],
  sms: ['sms_subscription_id','sms_resource_group','sms_communication_service_id','sms_communication_service_endpoint','sms_phone_number','sms_phone_number_kind'],
  agents_waka: ['agent_text_id']
};
let current = 'email';
let hydrated = {};
const channelLabels = { email: 'Email', sms: 'SMS', agents_waka: 'Agent texte' };
function fieldLabel(id) { return id.replaceAll('_', ' ').replace(/^email /, '').replace(/^sms /, '').replace(/^agent /, 'agent '); }
function options(items = [], selected = '') { return '<option value="">Sélectionner</option>' + items.map((x) => { const value = x.id || x.value || x.name || x.phone_number || x.address || x.endpoint || x; const label = x.label || x.name || x.display_name || x.phone_number || x.address || value; return `<option value="${esc(value)}" ${value === selected ? 'selected' : ''}>${esc(label)}</option>`; }).join(''); }
async function loadOptionsFor(field, values) {
  if (field.endsWith('subscription_id')) return api(`/api/channels/${current === 'agents_waka' ? 'text' : current}/subscriptions`).catch(() => ({ items: [] }));
  if (field.endsWith('resource_group')) return api(`/api/channels/${current}/${encodeURIComponent(values[`${current}_subscription_id`] || '')}/resource-groups`).catch(() => ({ items: [] }));
  if (field.includes('communication_service_id')) { const sub = values[`${current}_subscription_id`] || ''; const rg = values[`${current}_resource_group`] || ''; const path = current === 'email' ? 'email-services' : 'communication-services'; return api(`/api/channels/${current}/${encodeURIComponent(sub)}/${encodeURIComponent(rg)}/${path}`).catch(() => ({ items: [] })); }
  if (field === 'email_domain') return api(`/api/channels/email/${encodeURIComponent(values.email_communication_service_id || '')}/domains`).catch(() => ({ items: [] }));
  if (field === 'email_sender_username') return api(`/api/channels/email/${encodeURIComponent(values.email_communication_service_id || '')}/${encodeURIComponent(values.email_domain || '')}/senders`).catch(() => ({ items: [] }));
  if (field === 'sms_phone_number') return api(`/api/channels/sms/${encodeURIComponent(values.sms_communication_service_id || '')}/phone-numbers`).catch(() => ({ items: [] }));
  if (field === 'agent_text_id') return api('/api/channels/text/agents').catch(() => ({ items: [] }));
  return { items: [] };
}
function currentValues() { return Object.fromEntries(variables[current].map((id) => [id, document.getElementById(id)?.value || ''])); }
function isSelectField(id) { return id.includes('subscription_id') || id.includes('resource_group') || id.includes('communication_service_id') || id === 'email_domain' || id === 'email_sender_username' || id === 'sms_phone_number' || id === 'agent_text_id' || id === 'sms_phone_number_kind'; }
async function renderForm() {
  $('channels-current-title').textContent = channelLabels[current];
  const config = hydrated[current]?.config || hydrated[current] || {};
  $('channels-form').innerHTML = variables[current].map((id) => `<label class="orbit-label"><span>${esc(fieldLabel(id))}</span>${isSelectField(id) ? `<select id="${esc(id)}" name="${esc(id)}" class="orbit-select"></select>` : `<input id="${esc(id)}" name="${esc(id)}" class="orbit-input" value="${esc(config[id] || '')}">`}</label>`).join('');
  if (current === 'sms') document.getElementById('sms_phone_number_kind').innerHTML = options(['local','toll-free','short-code'], config.sms_phone_number_kind || 'local');
  await refreshCascade(config);
  $('channels-configured-badge').className = `orbit-badge ${hydrated[current]?.configured ? 'orbit-badge-ok' : ''}`;
  $('channels-configured-badge').textContent = hydrated[current]?.configured ? 'Configuré' : 'Non configuré';
}
async function refreshCascade(seed = {}) {
  for (const id of variables[current]) {
    const node = document.getElementById(id);
    if (!node || node.tagName !== 'SELECT' || id === 'sms_phone_number_kind') continue;
    const values = { ...seed, ...currentValues() };
    const data = await loadOptionsFor(id, values);
    node.innerHTML = options(data.items || data.resources || data.agents || data, seed[id] || node.value);
    node.value = seed[id] || node.value || '';
    node.onchange = () => refreshCascade(currentValues()).catch((e) => toast(e.message));
  }
}
async function hydrate() { const data = await api('/api/console/channels'); hydrated = data.channels || data || {}; await renderForm(); }
async function save() { const payload = currentValues(); const backendKind = current === 'agents_waka' ? 'text' : current; await api(`/api/channels/${backendKind}/select`, { method: 'POST', body: JSON.stringify(payload) }); toast(`${channelLabels[current]} sauvegardé.`); await hydrate(); }
function openCreate() { $('channels-create-modal').classList.add('is-open'); const body = $('channels-create-body'); if (current === 'email') body.innerHTML = `<p class="orbit-subtitle">Création disponible : domaine ACS ou sender MailFrom selon la sélection courante.</p><button class="orbit-button orbit-button-primary" data-create-email-domain type="button">Créer domaine</button><button class="orbit-button" data-create-email-sender type="button">Créer sender</button>`; else if (current === 'sms') body.innerHTML = `<label class="orbit-label"><span>Pays</span><input id="create-sms-country" class="orbit-input" value="FR"></label><label class="orbit-label"><span>Type</span><select id="create-sms-kind" class="orbit-select"><option value="local">local</option><option value="toll-free">toll-free</option><option value="short-code">short-code</option></select></label><button class="orbit-button orbit-button-primary" data-create-sms-number type="button">Acheter numéro</button>`; else body.innerHTML = '<div class="orbit-empty">Les agents texte préexistent dans ConversationsDB. Aucune création depuis cette section.</div>'; wireCreate(); }
function wireCreate() { document.querySelector('[data-create-email-domain]')?.addEventListener('click', async () => { const v = currentValues(); await api(`/api/channels/email/${encodeURIComponent(v.email_communication_service_id || '')}/domains/create`, { method: 'POST', body: JSON.stringify({}) }); toast('Création domaine demandée.'); $('channels-create-modal').classList.remove('is-open'); await renderForm(); }); document.querySelector('[data-create-email-sender]')?.addEventListener('click', async () => { const v = currentValues(); await api(`/api/channels/email/${encodeURIComponent(v.email_communication_service_id || '')}/${encodeURIComponent(v.email_domain || '')}/senders/create`, { method: 'POST', body: JSON.stringify({}) }); toast('Création sender demandée.'); $('channels-create-modal').classList.remove('is-open'); await renderForm(); }); document.querySelector('[data-create-sms-number]')?.addEventListener('click', async () => { const v = currentValues(); await api(`/api/channels/sms/${encodeURIComponent(v.sms_communication_service_id || '')}/phone-numbers/purchase`, { method: 'POST', body: JSON.stringify({ country: $('create-sms-country').value, kind: $('create-sms-kind').value }) }); toast('Achat numéro demandé.'); $('channels-create-modal').classList.remove('is-open'); await renderForm(); }); }
document.addEventListener('DOMContentLoaded', () => { if (!document.querySelector('[data-section="channels"]')) return; hydrate().catch((e) => toast(e.message)); document.querySelectorAll('[data-channel-tab]').forEach((b) => b.addEventListener('click', async () => { current = b.dataset.channelTab; document.querySelectorAll('[data-channel-tab]').forEach((x) => x.classList.toggle('is-active', x === b)); await renderForm(); })); $('channels-save').addEventListener('click', () => save().catch((e) => toast(e.message))); $('channels-create').addEventListener('click', openCreate); document.querySelectorAll('[data-channel-create-close]').forEach((b) => b.addEventListener('click', () => $('channels-create-modal').classList.remove('is-open'))); });
