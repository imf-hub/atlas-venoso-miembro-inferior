(() => {
  const notice = document.querySelector('.beta-notice');
  const header = document.querySelector('header.top');
  const panel = document.querySelector('#beta-feedback-panel');
  const minimize = document.querySelector('.beta-feedback__minimize');
  const restore = document.querySelector('.beta-feedback__restore');
  if (!notice || !panel || !minimize || !restore) return;

  const measure = () => {
    document.documentElement.style.setProperty('--beta-height', `${notice.getBoundingClientRect().height}px`);
    if (header) document.documentElement.style.setProperty('--atlas-header-height', `${header.getBoundingClientRect().height}px`);
  };
  measure();
  if ('ResizeObserver' in window) {
    const observer = new ResizeObserver(measure);
    observer.observe(notice);
    if (header) observer.observe(header);
  } else {
    window.addEventListener('resize', measure);
  }
  minimize.hidden = false;
  panel.hidden = true;
  restore.hidden = false;
  const reminderKey = 'imf-atlas-feedback-reminder-v1';
  const week = 7 * 24 * 60 * 60 * 1000;
  let lastPrompt = 0;
  try { lastPrompt = Number(localStorage.getItem(reminderKey)) || 0; } catch (_) { /* Storage is optional. */ }
  const remember = (delay = week) => {
    lastPrompt = Date.now() + delay - week;
    try { localStorage.setItem(reminderKey, String(lastPrompt)); } catch (_) { /* Storage is optional. */ }
  };
  const close = () => {
    const hadFocus = panel.contains(document.activeElement);
    panel.hidden = true;
    restore.hidden = false;
    restore.setAttribute('aria-expanded', 'false');
    remember();
    if (hadFocus) restore.focus();
  };
  const open = (manual = false) => {
    panel.hidden = false;
    restore.hidden = true;
    restore.setAttribute('aria-expanded', 'true');
    remember();
    if (manual) minimize.focus();
  };
  minimize.addEventListener('click', close);
  panel.querySelector('.beta-feedback__later').addEventListener('click', close);
  restore.addEventListener('click', () => open(true));
  panel.addEventListener('keydown', event => {
    if (event.key === 'Escape') { event.preventDefault(); close(); }
  });

  const endpoint = 'https://opiniones-atlas-venoso-imf.ferver.chatgpt.site/api/vote';
  const voteKey = 'imf-atlas-vote-v1';
  const like = panel.querySelector('.beta-feedback__like');
  const stars = [...panel.querySelectorAll('input[name="atlas-rating"]')];
  const retry = panel.querySelector('.beta-feedback__send');
  const clearRating = panel.querySelector('.beta-feedback__clear');
  const help = panel.querySelector('.beta-feedback__help');
  let vote = {token: crypto.randomUUID(), like:false, rating:null, revision:0, saved:0};
  const valid = v => v && /^[a-f0-9-]{36}$/.test(v.token) && typeof v.like === 'boolean' &&
    (v.rating === null || Number.isInteger(v.rating) && v.rating >= 1 && v.rating <= 5) &&
    Number.isSafeInteger(v.revision) && Number.isSafeInteger(v.saved);
  try {
    const previous = JSON.parse(localStorage.getItem(voteKey));
    if (valid(previous)) vote = previous;
  } catch (_) { /* The server still saves if browser storage is unavailable. */ }
  const persist = () => {
    try { localStorage.setItem(voteKey, JSON.stringify(vote)); } catch (_) { /* Optional local persistence. */ }
  };
  const paint = () => {
    like.setAttribute('aria-pressed', String(vote.like));
    like.querySelector('span').textContent = vote.like ? '♥' : '♡';
    stars.forEach(star => {
      star.checked = Number(star.value) === vote.rating;
      star.parentElement.classList.toggle('is-selected', Number(star.value) <= (vote.rating || 0));
    });
    panel.querySelector('.beta-feedback__rating-text').textContent = vote.rating ? `${vote.rating} de 5 estrellas` : 'Elige de 1 a 5 estrellas';
    clearRating.hidden = !vote.rating;
  };
  let timer, busy = false;
  const save = async () => {
    if (busy || vote.revision <= vote.saved) return;
    busy = true;
    retry.hidden = true;
    help.textContent = 'Guardando tu valoración…';
    const snapshot = {...vote};
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 12000);
    try {
      const response = await fetch(endpoint, {method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify({token:snapshot.token, like:snapshot.like, rating:snapshot.rating, revision:snapshot.revision}),
        signal:controller.signal, credentials:'omit'});
      if (!response.ok || !(await response.json()).saved) throw new Error('save failed');
      vote.saved = Math.max(vote.saved, snapshot.revision);
      persist();
      if (vote.revision === snapshot.revision) {
        help.textContent = '¡Gracias! Tu valoración quedó guardada para el equipo del IMF.';
        remember(30 * 24 * 60 * 60 * 1000);
      }
    } catch (_) {
      if (vote.revision === snapshot.revision) {
        help.textContent = 'No pudimos guardar tu valoración. Comprueba tu conexión y vuelve a intentarlo.';
        retry.hidden = false;
      }
    } finally {
      clearTimeout(timeout);
      busy = false;
      if (vote.revision > snapshot.revision) timer = setTimeout(save, 1100);
    }
  };
  const change = () => {
    vote.revision = Math.max(Date.now(), vote.revision + 1);
    persist();
    paint();
    help.textContent = 'Guardando tu valoración…';
    retry.hidden = true;
    clearTimeout(timer);
    timer = setTimeout(save, 600);
  };
  like.addEventListener('click', () => { vote.like = !vote.like; change(); });
  stars.forEach(star => star.addEventListener('change', () => { vote.rating = Number(star.value); change(); }));
  retry.addEventListener('click', save);
  clearRating.addEventListener('click', () => { vote.rating = null; change(); });
  window.addEventListener('online', save);
  window.addEventListener('storage', event => {
    if (event.key !== voteKey) return;
    try {
      const other = JSON.parse(event.newValue);
      if (valid(other) && other.revision >= vote.revision) { vote = other; paint(); }
    } catch (_) { /* Ignore unrelated invalid local data. */ }
  });
  paint();
  if (vote.revision > vote.saved) save();
  else if (vote.saved) help.textContent = 'Tu valoración está guardada. Puedes actualizarla cuando quieras.';

  // Count only visible time; do not interrupt a tour, typing, or another dialog.
  let activeSeconds = 0;
  const promptTimer = window.setInterval(() => {
    if (Date.now() - lastPrompt < week) { window.clearInterval(promptTimer); return; }
    if (document.hidden) return;
    activeSeconds += 1;
    if (activeSeconds < 60 || document.querySelector('.stage.tour, dialog[open], [role="dialog"][aria-modal="true"]') ||
        document.activeElement?.matches('input, textarea, select, [contenteditable="true"]')) return;
    open();
    window.clearInterval(promptTimer);
  }, 1000);
})();
