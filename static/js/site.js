// Progressive enhancement: the site is fully usable without this file.
(function () {
  'use strict';

  // Mobile navigation toggle
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.hidden = false;
    nav.setAttribute('data-open', 'false');
    toggle.addEventListener('click', function () {
      var open = nav.getAttribute('data-open') !== 'true';
      nav.setAttribute('data-open', String(open));
      toggle.setAttribute('aria-expanded', String(open));
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.getAttribute('data-open') === 'true') {
        nav.setAttribute('data-open', 'false');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.focus();
      }
    });
  }

  // Keep keyboard focus useful after in-page jumps
  window.addEventListener('hashchange', function () {
    var el = document.getElementById(location.hash.slice(1));
    if (el) { if (!el.hasAttribute('tabindex')) el.setAttribute('tabindex', '-1'); el.focus({ preventScroll: true }); }
  });
})();
