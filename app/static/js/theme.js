// app/static/js/theme.js
(() => {
  const key = 'wdp-theme';
  const toggle = document.getElementById('themeToggle');
  const root   = document.documentElement;

  const stored = localStorage.getItem(key);
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  let theme = stored || (prefersDark ? 'dark' : 'light');

  function applyTheme(t) {
    root.setAttribute('data-theme', t);
    toggle.checked = (t === 'dark');
  }
  applyTheme(theme);

  toggle.addEventListener('change', () => {
    theme = toggle.checked ? 'dark' : 'light';
    localStorage.setItem(key, theme);
    applyTheme(theme);
  });

  window.matchMedia('(prefers-color-scheme: dark)')
    .addEventListener('change', e => {
      if (!localStorage.getItem(key)) {
        applyTheme(e.matches ? 'dark' : 'light');
      }
    });
})();