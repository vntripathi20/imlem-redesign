// Client-side sorting and filtering for the small results tables (progressive enhancement).
(function () {
  'use strict';

  function cellValue(row, idx, kind) {
    var cell = row.children[idx];
    if (!cell) return '';
    var raw = cell.getAttribute('data-v');
    var text = (raw !== null ? raw : cell.textContent).trim();
    if (kind === 'num') {
      var n = parseFloat(text.replace(/[^0-9.\-]/g, ''));
      return isNaN(n) ? null : n;
    }
    return text.toLowerCase();
  }

  function makeSortable(table) {
    var heads = table.tHead ? table.tHead.rows[table.tHead.rows.length - 1].cells : [];
    Array.prototype.forEach.call(heads, function (th, idx) {
      var kind = th.getAttribute('data-sort');
      if (!kind) return;
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'sort-btn';
      btn.innerHTML = th.innerHTML;
      th.textContent = '';
      th.appendChild(btn);
      btn.addEventListener('click', function () {
        var dir = th.getAttribute('aria-sort') === 'ascending' ? 'descending' : 'ascending';
        Array.prototype.forEach.call(heads, function (h) { h.removeAttribute('aria-sort'); });
        th.setAttribute('aria-sort', dir);
        var body = table.tBodies[0];
        var rows = Array.prototype.slice.call(body.rows);
        rows.sort(function (a, b) {
          var x = cellValue(a, idx, kind), y = cellValue(b, idx, kind);
          if (x === null && y === null) return 0;
          if (x === null) return 1;      // blanks always last
          if (y === null) return -1;
          var c = x < y ? -1 : x > y ? 1 : 0;
          return dir === 'ascending' ? c : -c;
        });
        rows.forEach(function (r) { body.appendChild(r); });
      });
    });
  }

  function makeFilter(input) {
    var table = document.getElementById(input.getAttribute('data-filter-table'));
    if (!table) return;
    var count = document.querySelector('[data-filter-count]');
    input.addEventListener('input', function () {
      var q = input.value.trim().toLowerCase();
      var shown = 0, rows = table.tBodies[0].rows;
      Array.prototype.forEach.call(rows, function (r) {
        var school = r.querySelector('th');
        var hit = !q || (school && school.textContent.toLowerCase().indexOf(q) !== -1);
        r.hidden = !hit;
        if (hit) shown++;
      });
      if (count) count.textContent = q ? shown + ' of ' + rows.length + ' schools' : '';
    });
  }

  document.querySelectorAll('table.sortable').forEach(makeSortable);
  document.querySelectorAll('[data-filter-table]').forEach(makeFilter);
})();
