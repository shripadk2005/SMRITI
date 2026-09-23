/**
 * MINDCARE NER - Main Application Logic & Accessibility Controls
 */

function initMainApp() {
  initAccessibilityControls();
  initAutoDismissAlerts();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initMainApp);
} else {
  initMainApp();
}


// Initialize font scaling and high contrast accessibility
function initAccessibilityControls() {
  const rootHtml = document.documentElement;
  const body = document.body;

  // 1. Restore font size
  const savedFontSize = localStorage.getItem('mindcare_font_size') || 'font-normal';
  rootHtml.className = rootHtml.className.replace(/font-\w+/g, '');
  rootHtml.classList.add(savedFontSize);

  // Mark active font button
  document.querySelectorAll('[data-font-size]').forEach(btn => {
    if (btn.getAttribute('data-font-size') === savedFontSize) {
      btn.classList.add('active');
    }
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const sizeClass = btn.getAttribute('data-font-size');
      rootHtml.className = rootHtml.className.replace(/font-\w+/g, '');
      rootHtml.classList.add(sizeClass);
      localStorage.setItem('mindcare_font_size', sizeClass);

      document.querySelectorAll('[data-font-size]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });

  // 2. Restore High Contrast Mode
  const savedContrast = localStorage.getItem('mindcare_contrast');
  if (savedContrast === 'high') {
    body.classList.add('theme-high-contrast');
    const contrastBtn = document.getElementById('contrast-toggle-btn');
    if (contrastBtn) contrastBtn.classList.add('active');
  }

  const contrastBtn = document.getElementById('contrast-toggle-btn');
  if (contrastBtn) {
    contrastBtn.addEventListener('click', (e) => {
      e.preventDefault();
      body.classList.toggle('theme-high-contrast');
      const isHigh = body.classList.contains('theme-high-contrast');
      localStorage.setItem('mindcare_contrast', isHigh ? 'high' : 'normal');
      contrastBtn.classList.toggle('active', isHigh);
    });
  }
}

// Auto-dismiss bootstrap alerts after 6 seconds
function initAutoDismissAlerts() {
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(alert => {
    setTimeout(() => {
      try {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
      } catch (e) {}
    }, 6000);
  });
}
