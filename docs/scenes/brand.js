const clamp = (v) => Math.max(0, Math.min(1, v));
const ease = (v) => v * v * (3 - 2 * v);
const p = (t, a, b) => ease(clamp((t - a) / (b - a)));
const $ = (id) => document.getElementById(id);

function fade(id, t, a, d = 0.4) {
  const v = p(t, a, a + d);
  const e = $(id);
  e.style.opacity = v;
  e.style.transform = `translateY(${(1 - v) * 8}px)`;
}

function typed(id, text, t, a, cps = 30) {
  $(id).textContent = text.slice(0, Math.max(0, Math.floor((t - a) * cps)));
}

function draw(id, t, a, d = 0.5) {
  const e = $(id);
  e.style.strokeDasharray = '1';
  const v = p(t, a, a + d);
  e.style.strokeDashoffset = String(1 - v);
  e.style.opacity = v > 0 ? 1 : 0;
  if (v >= 1) e.setAttribute('marker-end', e.dataset.m || '');
  else e.removeAttribute('marker-end');
}

function bar(id, t, a, b) {
  $(id).style.width = `${p(t, a, b) * 100}%`;
}

window.addEventListener('load', async () => {
  await document.fonts.ready;
  const t = parseFloat(new URLSearchParams(location.search).get('t') || String(window.DURATION));
  window.render(t);
  document.body.dataset.ready = '1';
});
