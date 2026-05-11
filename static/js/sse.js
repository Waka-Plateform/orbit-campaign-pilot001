const toastHost = () => document.getElementById('toast-host');
export function toast(message) {
  const host = toastHost();
  if (!host) return;
  const node = document.createElement('div');
  node.className = 'orbit-toast';
  node.textContent = message;
  host.appendChild(node);
  window.setTimeout(() => node.remove(), 4200);
}
export function subscribe(eventName, handler) {
  if (!('EventSource' in window)) return null;
  const source = new EventSource('/events');
  source.addEventListener(eventName, (event) => {
    try { handler(JSON.parse(event.data)); } catch { handler(event.data); }
  });
  source.addEventListener('error', () => toast('Flux temps réel interrompu. Nouvelle tentative automatique.'));
  return source;
}
window.OrbitSSE = { subscribe, toast };
