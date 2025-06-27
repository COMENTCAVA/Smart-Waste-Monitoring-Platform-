// static/js/dashboard.js

console.log('📊 dashboard.js chargé');

let currentPage = 1,
    hasNext     = true;

// Helper pour fetch + erreurs
async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status} pour ${url}`);
  return res.json();
}

// 1) Charts + résumé global
async function initCharts() {
  // 1.1 – Stats globales
  const ov = await fetchJSON('/api/stats/overall');
  document.getElementById('overallStats').innerHTML = `
    <div class="col"><h6>Total</h6><strong>${ov.total}</strong></div>
    <div class="col"><h6>Vide (manuel)</h6><strong>${ov.manual_empty_pct}%</strong></div>
    <div class="col"><h6>Pleine (manuel)</h6><strong>${ov.manual_full_pct}%</strong></div>
    <div class="col"><h6>Accuracy</h6><strong>${ov.correct_pct}%</strong></div>`;

  // 1.2 – Camembert manuel
  const ld = await fetchJSON('/api/stats/label_distribution');
  new Chart(
    document.getElementById('labelChart'),
    {
      type: 'pie',
      data: {
        labels: ['Vide','Pleine'],
        datasets: [{
          data: [ld.manual.Vide, ld.manual.Pleine],
          backgroundColor: ['#0d6efd','#198754']
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom' } }
      }
    }
  );

  // 1.3 – Bar charts configurés
  const cfg = [
    { id:'fileSizeChart', api:'/api/stats/file_size_distribution', label:'Images',   color:'#ffc107' },
    { id:'contrastChart', api:'/api/stats/contrast_distribution',  label:'Contraste',color:'#dc3545' },
    { id:'edgesChart',    api:'/api/stats/edges_distribution',     label:'Contours', color:'#6f42c1' }
  ];
  for (const {id, api, label, color} of cfg) {
    const d = await fetchJSON(api);
    new Chart(
      document.getElementById(id),
      {
        type: 'bar',
        data: {
          labels: d.labels,
          datasets: [{ label, data: d.counts, backgroundColor: color }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: { y: { beginAtZero: true } }
        }
      }
    );
  }
}

// 2) Chargement des images + tooltips + suppression
async function loadImages(reset = false) {
  if (reset) {
    currentPage = 1;
    hasNext     = true;
    document.getElementById('imagesContainer').innerHTML = '';
  }
  if (!hasNext) return;

  // Construire l’URL avec filtres
  const params = new URLSearchParams({
    page: currentPage,
    per_page: 21,
    date_from:    document.getElementById('filterDateFrom').value,
    date_to:      document.getElementById('filterDateTo').value,
    label_manual: document.getElementById('filterManual').value,
    label_auto:   document.getElementById('filterAuto').value
  });
  const resp = await fetchJSON(`/api/images?${params}`);
  const cont = document.getElementById('imagesContainer');

  resp.images.forEach(img => {
    // Choix de la couleur des badges
    const manualClass = img.label === 'Pleine' ? 'bg-success' : 'bg-primary';
    const autoClass   = img.predicted_label === 'Pleine' ? 'bg-success' : 'bg-primary';

    const card = document.createElement('div');
    card.className = 'col';
    card.innerHTML = `
      <div class="card h-100 shadow-sm"
           data-bs-toggle="tooltip"
           title="
Taille          : ${img.file_size}
Contraste       : ${img.contrast}
Contours        : ${img.edges_count}
Date upload     : ${new Date(img.uploaded_at).toLocaleString()}
           ">
        <img src="${img.url}"
             class="card-img-top"
             style="height:180px;object-fit:cover">
        <div class="card-body">
          <span class="badge ${manualClass} me-1">
            Manuel: ${img.label}
          </span>
          <span class="badge ${autoClass}">
            Auto : ${img.predicted_label}
          </span>
        </div>
        <div class="card-footer d-flex justify-content-end p-2">
          <form method="post" action="/delete/${img.id}"
                onsubmit="return confirm('Supprimer cette image ?');">
            <button class="btn btn-sm btn-outline-danger">🗑️</button>
          </form>
        </div>
      </div>`;
    cont.appendChild(card);
  });

  // (Re)initialiser les tooltips
  document.querySelectorAll('[data-bs-toggle="tooltip"]')
    .forEach(el => new bootstrap.Tooltip(el));

  hasNext = resp.has_next;
  currentPage++;

  // Afficher ou masquer le bouton Charger plus
  document.getElementById('loadMore').style.display = hasNext ? 'block' : 'none';
}

// 3) Événement du bouton Charger plus et filtres
window.addEventListener('DOMContentLoaded', () => {
  initCharts().catch(e => console.error('initCharts :', e));
  loadImages(true).catch(e => console.error('loadImages :', e));

  document.getElementById('applyFilters')
    .addEventListener('click', e => {
      e.preventDefault();
      loadImages(true);
    });

  document.getElementById('loadMore')
    .addEventListener('click', () => loadImages(false));
});