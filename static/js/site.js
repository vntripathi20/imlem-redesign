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

  // Live countdown: server renders the day count; this keeps it right if the tab stays open past midnight.
  var cd = document.querySelector('[data-countdown]');
  if (cd) {
    var target = new Date(cd.getAttribute('data-countdown') + 'T00:00:00');
    var out = cd.querySelector('[data-count-days]');
    var tick = function () {
      var now = new Date();
      var today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      var days = Math.round((target - today) / 86400000);
      out.textContent = String(Math.max(days, 0));
    };
    tick();
    setInterval(tick, 60 * 60 * 1000);
  }

  // Keep keyboard focus useful after in-page jumps
  window.addEventListener('hashchange', function () {
    var el = document.getElementById(location.hash.slice(1));
    if (el) { if (!el.hasAttribute('tabindex')) el.setAttribute('tabindex', '-1'); el.focus({ preventScroll: true }); }
  });
})();
