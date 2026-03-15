/* VRA FMS – Dashboard Charts (Chart.js via CDN) */

(function () {
  // Load Chart.js from CDN dynamically
  var script = document.createElement('script');
  script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js';
  script.onload = initCharts;
  document.head.appendChild(script);

  function initCharts() {
    var data = window.VRA_CHART_DATA || {};

    // ── Upload Trend Bar Chart ──────────────────
    var uploadCtx = document.getElementById('uploadChart');
    if (uploadCtx && data.uploadLabels) {
      new Chart(uploadCtx, {
        type: 'bar',
        data: {
          labels: data.uploadLabels,
          datasets: [{
            label: 'Files Uploaded',
            data: data.uploadData,
            backgroundColor: 'rgba(46, 134, 193, 0.75)',
            borderColor: '#1a5276',
            borderWidth: 1.5,
            borderRadius: 6,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: { stepSize: 1, font: { size: 11 } },
              grid: { color: '#eaecee' }
            },
            x: { ticks: { font: { size: 11 } }, grid: { display: false } }
          }
        }
      });
    }

    // ── Status Breakdown Doughnut ───────────────
    var statusCtx = document.getElementById('statusChart');
    if (statusCtx && data.statusLabels && data.statusLabels.length > 0) {
      new Chart(statusCtx, {
        type: 'doughnut',
        data: {
          labels: data.statusLabels,
          datasets: [{
            data: data.statusData,
            backgroundColor: ['#2e86c1', '#1e8449', '#7f8c8d', '#5d6d7e', '#e74c3c'],
            borderWidth: 2,
            borderColor: '#fff',
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: { font: { size: 11 }, padding: 14 }
            }
          },
          cutout: '65%'
        }
      });
    } else if (statusCtx) {
      // No data placeholder
      var parent = statusCtx.parentElement;
      parent.innerHTML = '<p style="text-align:center;color:#99a3a4;padding-top:80px;">No file data yet.</p>';
    }
  }
})();
