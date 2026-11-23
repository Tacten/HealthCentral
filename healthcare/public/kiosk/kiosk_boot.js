window.addEventListener('DOMContentLoaded', function () {
  // Load jsQR library for QR code scanning
  var jsqr = document.createElement('script');
  jsqr.src = 'https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.min.js';
  jsqr.async = false;
  document.body.appendChild(jsqr);

  var script = document.createElement('script');
  script.src = '/assets/healthcare/kiosk/kiosk.js';
  script.async = false;
  document.body.appendChild(script);
});