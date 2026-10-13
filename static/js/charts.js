// Hover tooltips for the server-rendered SVG charts (progressive enhancement).
// Without this script each mark still has an SVG <title>, and every chart sits next to a table.
(function () {
  'use strict';
  document.querySelectorAll('.chart-wrap').forEach(function (wrap) {
    var svg = wrap.querySelector('svg.chart');
    if (!svg) return;
    var tip = document.createElement('div');
    tip.className = 'chart-tip';
    tip.hidden = true;
    tip.setAttribute('aria-hidden', 'true');
    wrap.appendChild(tip);
    svg.querySelectorAll('.mark title').forEach(function (t) { t.remove(); });   // avoid a second, native tooltip

    function show(mark) {
      var shape = mark.querySelector('path, circle:last-of-type');
      var box = (shape || mark).getBoundingClientRect();
      var outer = wrap.getBoundingClientRect();
      tip.textContent = mark.getAttribute('data-tip');
      tip.style.left = (box.left + box.width / 2 - outer.left) + 'px';
      tip.style.top = (box.top - outer.top) + 'px';
      tip.hidden = false;
    }
    svg.addEventListener('pointerover', function (e) {
      var mark = e.target.closest('.mark');
      if (mark) show(mark);
    });
    svg.addEventListener('pointerleave', function () { tip.hidden = true; });
  });
})();
