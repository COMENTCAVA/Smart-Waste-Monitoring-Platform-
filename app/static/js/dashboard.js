// static/js/dashboard.js

console.log('📊 dashboard.js chargé');

let currentPage = 1,
    hasNext     = true;

async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status} pour ${url}`);
  return res.json();
}

//Ici les fonctions charts.js
async function initCharts() {
  // Camembert manuel
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

  // Bar charts
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

// 3) Chargement paginé des images + suppression AJAX
async function loadImages(reset = false) {
  if (reset) {
    currentPage = 1;
    hasNext     = true;
    document.getElementById('imagesContainer').innerHTML = '';
  }
  if (!hasNext) return;

  // URL avec filtres
  const params = new URLSearchParams({
    page:         currentPage,
    per_page:     21,
    date_from:    document.getElementById('filterDateFrom').value,
    date_to:      document.getElementById('filterDateTo').value,
    label_manual: document.getElementById('filterManual').value,
    label_auto:   document.getElementById('filterAuto').value
  });
  const resp = await fetchJSON(`/api/images?${params}`);
  const cont = document.getElementById('imagesContainer');

  resp.images.forEach(img => {
    const col = document.createElement('div');
    col.className = 'col';

    // États « vide » / « pleine »
    const mState = img.label === 'Pleine'           ? 'pleine' : 'vide';
    const aState = img.predicted_label === 'Pleine' ? 'pleine' : 'vide';

    // HTML de la card
    col.innerHTML = `
      <div class="image-card position-relative">
        <!-- 1) Bouton supprimer en haut à droite -->
        <button
          class="image-card__delete"
          data-id="${img.id}"
          aria-label="Supprimer cette image"
        >
          <i class="bi bi-trash-fill"></i>
        </button>

        <!-- 2) Image lazy + tooltip -->
        <img src="${img.url}" loading="lazy"
             class="w-100"
             data-bs-toggle="tooltip"
             title="
Taille      : ${img.file_size} octets
Contraste   : ${img.contrast}
Contours    : ${img.edges_count}
Date upload : ${new Date(img.uploaded_at).toLocaleString()}
             "
             alt="Image">

        <!-- 3) Badges overlay bas -->
        <div class="image-card__info">
          <span class="image-card__badge-inline image-card__badge-inline--${mState}"
                title="Étiquette manuelle">
            <i class="bi bi-person-lines-fill"></i>
            ${img.label || 'Vide'}
          </span>
          <span class="image-card__badge-inline image-card__badge-inline--${aState}"
                title="Prédiction automatisée">
            <i class="bi bi-robot"></i>
            ${img.predicted_label || 'Vide'}
          </span>
        </div>
      </div>
    `;

    cont.appendChild(col);
  });

  // (Re)initialiser tooltips
  document.querySelectorAll('[data-bs-toggle="tooltip"]')
          .forEach(el => new bootstrap.Tooltip(el));

  // Pagination
  hasNext = resp.has_next;
  currentPage++;
  document.getElementById('loadMore').style.display = hasNext ? 'block' : 'none';
}

// 4) Initialisation et événements
window.addEventListener('DOMContentLoaded', () => {
  // Charts + 1ère page d’images
  initCharts().catch(e => console.error('initCharts :', e));
  loadImages(true).catch(e => console.error('loadImages :', e));

  // Filtrer
  document.getElementById('applyFilters')
    .addEventListener('click', e => {
      e.preventDefault();
      loadImages(true);
    });

  // Charger plus
  document.getElementById('loadMore')
    .addEventListener('click', () => loadImages(false));

  // Suppression AJAX déléguée
  document.getElementById('imagesContainer')
    .addEventListener('click', e => {
      const btn = e.target.closest('.image-card__delete');
      if (!btn) return;
      const id = btn.dataset.id;
      if (!confirm('Supprimer cette image ?')) return;

      fetch(`/delete/${id}`, { method:'POST' })
        .then(res => {
          if (!res.ok) throw new Error(`HTTP ${res.status}`);
          // on retire la colonne sans rechargement
          btn.closest('.col').remove();
        })
        .catch(err => {
          console.error('Suppression AJAX échouée :', err);
          alert("Échec suppression, réessayez.");
        });
    });
});