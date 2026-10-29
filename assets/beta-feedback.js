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
  minimize.addEventListener('click', () => {
    panel.hidden = true;
    restore.hidden = false;
    restore.focus();
  });
  restore.addEventListener('click', () => {
    panel.hidden = false;
    restore.hidden = true;
    minimize.focus();
  });
})();
