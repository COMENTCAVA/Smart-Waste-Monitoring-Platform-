// app/static/js/theme.js
(() => {
  const key = 'wdp-theme';
  const toggle = document.getElementById('themeToggle');
  const root   = document.documentElement;

  // 1) Détecte le thème initial
  const stored = localStorage.getItem(key);
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  let theme = stored || (prefersDark ? 'dark' : 'light');

  // 2) Applique le thème
  function applyTheme(t) {
    root.setAttribute('data-theme', t);
    toggle.checked = (t === 'dark');
  }
  applyTheme(theme);

  // 3) Écoute le switch utilisateur
  toggle.addEventListener('change', () => {
    theme = toggle.checked ? 'dark' : 'light';
    localStorage.setItem(key, theme);
    applyTheme(theme);
  });

  // 4) Réagir aux changements système (optionnel)
  window.matchMedia('(prefers-color-scheme: dark)')
    .addEventListener('change', e => {
      if (!localStorage.getItem(key)) {
        applyTheme(e.matches ? 'dark' : 'light');
      }
    });
})();