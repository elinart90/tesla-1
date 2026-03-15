/* VRA File Management System – Main JavaScript */

document.addEventListener('DOMContentLoaded', function () {

  // ─── Sidebar Toggle ───────────────────────────
  const sidebar = document.getElementById('sidebar');
  const sidebarToggle = document.getElementById('sidebarToggle');

  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', function () {
      sidebar.classList.toggle('open');
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function (e) {
      if (window.innerWidth <= 768 && sidebar.classList.contains('open')) {
        if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
          sidebar.classList.remove('open');
        }
      }
    });
  }

  // ─── Live Clock ───────────────────────────────
  const clock = document.getElementById('topbarClock');
  if (clock) {
    function updateClock() {
      const now = new Date();
      clock.textContent = now.toLocaleTimeString('en-GB', {
        hour: '2-digit', minute: '2-digit', second: '2-digit'
      });
    }
    updateClock();
    setInterval(updateClock, 1000);
  }

  // ─── Auto-dismiss alerts ──────────────────────
  document.querySelectorAll('.alert').forEach(function (alert) {
    setTimeout(function () {
      if (alert && alert.parentNode) {
        alert.style.opacity = '0';
        alert.style.transition = 'opacity 0.5s';
        setTimeout(() => alert.remove(), 500);
      }
    }, 6000);
  });

});
