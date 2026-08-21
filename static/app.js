const apiBase = '/api';
const root = document.getElementById('root');
let currentUser = null;

const protectedRoutes = {
  '#/admin': ['admin'],
  '#/coach': ['coach'],
};

const PAGE_TITLES = {
  '#/': 'Home',
  '#/meets': 'Meet Information',
  '#/meets/calculator-rules': 'Calculator Rules',
  '#/standings': 'Standings',
  '#/statistics': 'Statistics',
  '#/study-materials': 'Study Materials',
  '#/league': 'League Information',
  '#/coaches': "Coaches' Corner",
  '#/contact': 'Contact Information',
  '#/links': 'Links',
  '#/admin': 'Admin Dashboard',
  '#/coach': 'Coach Dashboard',
  '#/login': 'Log In',
};

function escapeHtml(value) {
  if (value == null) return '';
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

async function loadCurrentUser() {
  try {
    const res = await fetchJson(`${apiBase}/me`);
    currentUser = res.user;
  } catch {
    currentUser = null;
  }
}

const publicSections = [
  { title: 'Meet Information', hash: '#/meets' },
  { title: 'Standings', hash: '#/standings' },
  { title: 'Statistics', hash: '#/statistics' },
  { title: 'Study Materials', hash: '#/study-materials' },
  { title: 'League Information', hash: '#/league' },
  { title: "Coaches' Corner", hash: '#/coaches' },
  { title: 'Contact Information', hash: '#/contact' },
  { title: 'Links', hash: '#/links' },
];

function fetchJson(url, options = {}) {
  return fetch(url, options).then((res) => {
    if (!res.ok) return res.json().then((body) => Promise.reject(body));
    return res.json();
  });
}

const sectionBlurbs = {
  'Meet Information': 'Dates and locations for all five meets this season.',
  Standings: 'Division-by-division school scores, updated meet by meet.',
  Statistics: 'Historical performance summaries and league results by year.',
  'Study Materials': 'Past questions, answer keys, and solutions, organized by year and meet.',
  'League Information': 'How the league is structured, its goals, and how schools take part.',
  "Coaches' Corner": 'Where coaches log in to manage their roster and school info.',
  'Contact Information': 'Who to reach for questions about meets and registration.',
  Links: 'Outside resources for practice and problem-solving.',
};

/* Flat-style vector icons (clip art) for the section index — self-contained SVG, no image requests. */
const sectionIcons = {
  'Meet Information': `<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <rect x="6" y="9" width="28" height="24" rx="3" fill="#eaf1fb" stroke="#0c4a9e" stroke-width="1.5"/>
    <rect x="6" y="9" width="28" height="7" rx="3" fill="#0c4a9e"/>
    <rect x="12" y="4" width="3" height="8" rx="1.5" fill="#c9821e"/>
    <rect x="25" y="4" width="3" height="8" rx="1.5" fill="#c9821e"/>
    <circle cx="14" cy="23" r="2" fill="#c9821e"/>
    <circle cx="20" cy="23" r="2" fill="#0c4a9e"/>
    <circle cx="26" cy="23" r="2" fill="#0c4a9e"/>
    <circle cx="14" cy="29" r="2" fill="#0c4a9e"/>
  </svg>`,
  Standings: `<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <path d="M13 8h14v9a7 7 0 0 1-14 0V8Z" fill="#fbeed9" stroke="#b3791a" stroke-width="1.5"/>
    <path d="M13 10H8a5 5 0 0 0 5 8" stroke="#1a56b0" stroke-width="1.5" fill="none"/>
    <path d="M27 10h5a5 5 0 0 1-5 8" stroke="#1a56b0" stroke-width="1.5" fill="none"/>
    <rect x="17" y="24" width="6" height="5" fill="#b3791a"/>
    <rect x="13" y="29" width="14" height="3" rx="1.5" fill="#0a1a33"/>
  </svg>`,
  Statistics: `<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <rect x="6" y="30" width="28" height="2" fill="#0a1a33"/>
    <rect x="9" y="20" width="6" height="10" rx="1" fill="#1a56b0"/>
    <rect x="17" y="13" width="6" height="17" rx="1" fill="#b3791a"/>
    <rect x="25" y="23" width="6" height="7" rx="1" fill="#163a63"/>
  </svg>`,
  'Study Materials': `<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <path d="M20 12c-3-2.5-8-3-12-2v18c4-1 9-.5 12 2 3-2.5 8-3 12-2V10c-4-1-9-.5-12 2Z" fill="#e8f0fc" stroke="#1a56b0" stroke-width="1.5" stroke-linejoin="round"/>
    <path d="M20 12v18" stroke="#b3791a" stroke-width="1.5"/>
  </svg>`,
  'League Information': `<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <path d="M20 6l11 4v9c0 8-5 12-11 15C14 31 9 27 9 19v-9l11-4Z" fill="#fbeed9" stroke="#b3791a" stroke-width="1.5" stroke-linejoin="round"/>
    <circle cx="20" cy="17" r="1.8" fill="#0a1a33"/>
    <rect x="18.5" y="20" width="3" height="7" rx="1.2" fill="#0a1a33"/>
  </svg>`,
  "Coaches' Corner": `<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <rect x="9" y="8" width="22" height="26" rx="2.5" fill="#e8f0fc" stroke="#1a56b0" stroke-width="1.5"/>
    <rect x="15" y="5" width="10" height="6" rx="2" fill="#b3791a"/>
    <path d="M14 20l4 4 8-8" stroke="#0a1a33" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
    <rect x="14" y="28" width="12" height="2" rx="1" fill="#163a63"/>
  </svg>`,
  'Contact Information': `<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <rect x="6" y="11" width="28" height="19" rx="2.5" fill="#e8f0fc" stroke="#1a56b0" stroke-width="1.5"/>
    <path d="M7 12l13 10 13-10" stroke="#b3791a" stroke-width="1.5" fill="none" stroke-linejoin="round"/>
  </svg>`,
  Links: `<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <rect x="4" y="16" width="18" height="10" rx="5" transform="rotate(-35 13 21)" fill="none" stroke="#1a56b0" stroke-width="3.5"/>
    <rect x="18" y="14" width="18" height="10" rx="5" transform="rotate(-35 27 19)" fill="none" stroke="#b3791a" stroke-width="3.5"/>
  </svg>`,
};

function renderNav(sections) {
  return `
    <ul class="index-list">
      ${sections
        .map(
          (section, i) => `
        <li>
          <a href="${section.hash}">
            <span class="index-icon">${sectionIcons[section.title] || ''}</span>
            <span class="index-num">${String(i + 1).padStart(2, '0')}</span>
            <span class="index-text">
              <span class="index-title">${section.title}</span>
              <span class="index-desc">${sectionBlurbs[section.title] || ''}</span>
            </span>
            <span class="index-arrow">&rarr;</span>
          </a>
        </li>`
        )
        .join('')}
    </ul>
  `;
}

function renderPrimaryNav() {
  const nav = document.getElementById('primary-nav');
  const utility = document.getElementById('utility-links');
  if (nav) {
    nav.innerHTML = publicSections
      .map((section) => `<a href="${section.hash}" data-hash="${section.hash}">${section.title}</a>`)
      .join('');
  }
  if (!utility) return;

  if (!currentUser) {
    utility.innerHTML = `<a href="#/login" data-hash="#/login">Log in</a>`;
    return;
  }

  const dashboardHash = { admin: '#/admin', coach: '#/coach' }[currentUser.role] || '#/';
  utility.innerHTML = `
    <a href="${dashboardHash}" data-hash="${dashboardHash}">${currentUser.name} (${currentUser.role})</a>
    <a href="#" id="logout-link">Log out</a>
  `;
  document.getElementById('logout-link').addEventListener('click', async (event) => {
    event.preventDefault();
    await fetchJson(`${apiBase}/logout`, { method: 'POST' });
    currentUser = null;
    renderPrimaryNav();
    window.location.hash = '#/';
    navigate();
  });
}

function renderLogin(redirectHash) {
  root.innerHTML = `
    <section>
      <h1 class="page-title">Log In</h1>
      <p>Log in to access your coach or administrator dashboard.</p>
      <div class="card" style="max-width:420px">
        <form id="login-form" class="form-grid single-column">
          <div class="field">
            <label class="field-label" for="login-email">Email</label>
            <input id="login-email" name="email" type="email" autocomplete="username" required />
          </div>
          <div class="field">
            <label class="field-label" for="login-password">Password</label>
            <input id="login-password" name="password" type="password" autocomplete="current-password" required />
          </div>
          <button class="button-primary" type="submit">Log In</button>
          <p id="login-error" class="login-error" role="alert" style="display:none"></p>
        </form>
      </div>
    </section>
  `;
  document.getElementById('login-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const errorEl = document.getElementById('login-error');
    errorEl.style.display = 'none';
    try {
      const user = await fetchJson(`${apiBase}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: form.email.value, password: form.password.value }),
      });
      currentUser = user;
      renderPrimaryNav();
      window.location.hash = redirectHash || '#/';
      navigate();
    } catch (err) {
      errorEl.textContent = err.error || 'Login failed.';
      errorEl.style.display = 'block';
    }
  });
}

function renderFooter() {
  const footer = document.getElementById('footer');
  if (!footer) return;
  footer.innerHTML = `
    <div class="footer-grid">
      <div>
        <h3>Explore</h3>
        ${publicSections.slice(0, 4).map((s) => `<a href="${s.hash}">${s.title}</a>`).join('')}
      </div>
      <div>
        <h3>More</h3>
        ${publicSections.slice(4).map((s) => `<a href="${s.hash}">${s.title}</a>`).join('')}
      </div>
      <div>
        <h3>League Staff</h3>
        <a href="#/coaches">Coaches' Corner</a>
        <a href="#/admin">Admin Dashboard</a>
      </div>
      <div>
        <h3>Get in Touch</h3>
        <a href="mailto:info@imlem.org">info@imlem.org</a>
        <a href="#/contact">Contact Page</a>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© ${new Date().getFullYear()} Intermediate Math League of Eastern Massachusetts</span>
      <span>Academic archive interface — historical data preserved.</span>
    </div>
  `;
}

function setActiveNav(hash) {
  document.querySelectorAll('#primary-nav a, #utility-links a').forEach((a) => {
    a.classList.toggle('active', a.dataset.hash === hash);
  });
}

function renderHome(stats) {
  const { schoolCount = 0, divisionCount = 0, meetCount = 0, nextMeet = null, leader = null } = stats || {};
  root.innerHTML = `
    <section>
      <div class="hero-banner">
        <svg class="hero-motif" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
          <path d="M20 90 A40 40 0 0 1 100 90 Z" fill="#fbeed9" fill-opacity="0.92" stroke="#c98d2c" stroke-width="2"/>
          <line x1="60" y1="90" x2="60" y2="52" stroke="#8f5c12" stroke-width="1.2"/>
          <line x1="60" y1="90" x2="35" y2="60" stroke="#8f5c12" stroke-width="1"/>
          <line x1="60" y1="90" x2="85" y2="60" stroke="#8f5c12" stroke-width="1"/>
          <circle cx="70" cy="22" r="4" fill="#e8f0fc" stroke="#1a56b0" stroke-width="2"/>
          <line x1="70" y1="22" x2="46" y2="88" stroke="#1a56b0" stroke-width="3" stroke-linecap="round"/>
          <line x1="70" y1="22" x2="92" y2="70" stroke="#0a1a33" stroke-width="3" stroke-linecap="round"/>
          <circle cx="46" cy="88" r="2.5" fill="#b3261e"/>
        </svg>
        <div class="hero-copy">
          <span class="eyebrow">Intermediate Math League of Eastern Massachusetts</span>
          <h1>Middle school math competition, five meets a season.</h1>
          <p>Schools across Eastern Massachusetts compete in arithmetic, algebra, geometry, number theory, and a team round — ranked across named divisions.</p>
          <div class="hero-actions">
            <a class="button-primary" href="#/meets">View meet schedule</a>
            <a class="button-secondary" href="#/standings">Current standings</a>
          </div>
        </div>
        <div class="hero-visual">
          <div class="hero-image-frame">
            <img class="hero-image" src="/images/50-years.png" alt="Illustration marking IMLEM's 50th anniversary, 1974 to 2026" />
            <p class="hero-image-caption">50 years of IMLEM</p>
          </div>
        </div>
      </div>

      <div class="next-meet-strip">
        <span class="badge gold">Next meet</span>
        ${
          nextMeet
            ? `<span class="next-meet-when">${escapeHtml(nextMeet.date)}${nextMeet.time ? ` &middot; ${escapeHtml(nextMeet.time)}` : ''}</span>
               <span class="next-meet-where">${nextMeet.location ? escapeHtml(nextMeet.location) : 'Location to be announced'}${nextMeet.announcement ? ` — ${escapeHtml(nextMeet.announcement)}` : ''}</span>`
            : `<span class="next-meet-where">No meets scheduled yet.</span>`
        }
        <a class="next-meet-link" href="#/meets">Full schedule &rarr;</a>
      </div>

      <div class="home-layout">
        <div class="home-main">
          <div class="section-header">
            <h2>Get to know IMLEM</h2>
          </div>
          <p class="lede">From meet schedules and live standings to the study materials archive — here's everything coaches, students, and families come here for.</p>
          ${renderNav(publicSections)}
        </div>

        <aside class="home-aside">
          <div class="aside-panel">
            <h3>At a glance</h3>
            <dl class="stat-list">
              <div><dt>Schools</dt><dd>${schoolCount}</dd></div>
              <div><dt>Divisions</dt><dd>${divisionCount}</dd></div>
              <div><dt>Meets per year</dt><dd>5</dd></div>
              <div><dt>Meets scheduled</dt><dd>${meetCount}</dd></div>
            </dl>
          </div>

          ${
            leader
              ? `<div class="aside-panel">
                  <h3>Division leader</h3>
                  <p class="aside-highlight">${escapeHtml(leader.school)}</p>
                  <p>${escapeHtml(leader.division)} Division &middot; ${leader.total} pts</p>
                  <a class="aside-link" href="#/standings">Full standings &rarr;</a>
                </div>`
              : ''
          }

          <div class="aside-panel">
            <h3>League staff</h3>
            <a class="aside-link" href="#/coaches">Coaches' Corner &rarr;</a>
            <a class="aside-link" href="#/admin">Admin dashboard &rarr;</a>
          </div>
        </aside>
      </div>
    </section>
  `;
}

function renderStudyMaterials(data) {
  const year = data.years?.[0]?.year || '';
  const meet = data.years?.[0]?.meets?.[0]?.meetNumber || '';
  const selectedYear = data.years.find((entry) => entry.year === year);
  const selectedMeet = selectedYear?.meets?.find((entry) => entry.meetNumber === meet);

  root.innerHTML = `
    <section>
      <h1 class="page-title">Study Materials Archive</h1>
      <p>Access archived PDFs by year, meet number, and file type.</p>
      <div class="card">
        <h2>${selectedYear?.year || 'No year available'}</h2>
        ${selectedMeet ? `<p>${selectedMeet.files.length} files available</p>` : '<p>No materials found.</p>'}
        ${selectedMeet ? selectedMeet.files.map((file) => `
          <div style="margin-top:0.9rem">
            <a class="link-button" href="${escapeHtml(file.url)}" target="_blank" rel="noreferrer">Download ${escapeHtml(file.title)}</a>
            <span style="margin-left:0.75rem;color:#5a6a7d">${escapeHtml(file.type)}</span>
          </div>`).join('') : ''}
      </div>
    </section>
  `;
}

function renderMeetInfo(data) {
  root.innerHTML = `
    <section>
      <h1 class="page-title">Meet Information</h1>
      <p>Review upcoming and past meets, locations, and announcements.</p>
      <p><a class="link-button" href="#/meets/calculator-rules">Calculator Rules</a></p>
      <div class="table-wrapper">
        <table>
          <caption class="sr-only">Meet dates, locations, times, and announcements</caption>
          <thead>
            <tr>
              <th scope="col">Date</th>
              <th scope="col">Location</th>
              <th scope="col">Time</th>
              <th scope="col">Announcement</th>
            </tr>
          </thead>
          <tbody>
            ${(data.records || []).length
              ? (data.records || [])
                  .map(
                    (meet) => `
              <tr>
                <td>${escapeHtml(meet.date)}</td>
                <td>${meet.location ? escapeHtml(meet.location) : 'TBD'}</td>
                <td>${meet.time ? escapeHtml(meet.time) : 'TBD'}</td>
                <td>${meet.announcement ? escapeHtml(meet.announcement) : '—'}</td>
              </tr>`
                  )
                  .join('')
              : '<tr><td colspan="4">No meet records available.</td></tr>'}
          </tbody>
        </table>
      </div>
    </section>
  `;
}

function renderStandings(divisions) {
  root.innerHTML = `
    <section>
      <h1 class="page-title">Standings</h1>
      <p>League standings are organized into named divisions. Schools are ranked by total points across the five meets.</p>
      ${divisions
        .map((division) => {
          const teams = [...(division.teams || [])].sort((a, b) => {
            const totalA = a.scores.reduce((sum, val) => sum + (val || 0), 0);
            const totalB = b.scores.reduce((sum, val) => sum + (val || 0), 0);
            return totalB - totalA;
          });
          return `
          <div class="card" style="margin-top:1rem">
            <h2>${escapeHtml(division.name)} Division</h2>
            <div class="table-wrapper">
              <table>
                <caption class="sr-only">${escapeHtml(division.name)} Division standings by meet</caption>
                <thead>
                  <tr><th scope="col">School</th><th scope="col">M1</th><th scope="col">M2</th><th scope="col">M3</th><th scope="col">M4</th><th scope="col">M5</th><th scope="col">Total</th></tr>
                </thead>
                <tbody>
                  ${teams.length
                    ? teams
                        .map((team) => {
                          const total = team.scores.reduce((sum, val) => sum + (val || 0), 0);
                          return `<tr><td>${escapeHtml(team.name)}</td>${team.scores
                            .map((val) => `<td>${val ?? '—'}</td>`)
                            .join('')}<td>${total}</td></tr>`;
                        })
                        .join('')
                    : '<tr><td colspan="7">No schools entered yet.</td></tr>'}
                </tbody>
              </table>
            </div>
          </div>`;
        })
        .join('')}
    </section>
  `;
}

function renderCalculatorRules() {
  root.innerHTML = `
    <section>
      <h1 class="page-title">Calculator Rules</h1>
      <div class="card">
        <p>Calculators are allowed in meets 4 and 5. All team members should have calculators for these meets.</p>
        <p>Programmable or graphing calculators are NOT allowed.</p>
      </div>
      <p>
        <a class="link-button" href="#/meets">Back to Meet Information...</a>
      </p>
      <p>
        <a class="link-button" href="#/">Back to the Intermediate Math League of Eastern Massachusetts homepage...</a>
      </p>
    </section>
  `;
}

function renderStatistics(data) {
  root.innerHTML = `
    <section>
      <h1 class="page-title">Statistics</h1>
      <p>View historical performance summaries and league results.</p>
      <div class="table-wrapper">
        <table>
          <caption class="sr-only">League statistics by year</caption>
          <thead>
            <tr>
              <th scope="col">Year</th>
              <th scope="col">Summary</th>
              <th scope="col">Top School</th>
              <th scope="col">Notes</th>
            </tr>
          </thead>
          <tbody>
            ${(data.records || []).length
              ? (data.records || [])
                  .map(
                    (row) => `
              <tr>
                <td>${escapeHtml(row.year)}</td>
                <td>${escapeHtml(row.summary)}</td>
                <td>${row.topSchool ? escapeHtml(row.topSchool) : '—'}</td>
                <td>${row.notes ? escapeHtml(row.notes) : '—'}</td>
              </tr>`
                  )
                  .join('')
              : '<tr><td colspan="4">No statistics records available yet.</td></tr>'}
          </tbody>
        </table>
      </div>
    </section>
  `;
}

function renderStaticPage(title, text, cards = []) {
  root.innerHTML = `
    <section>
      <h1 class="page-title">${title}</h1>
      <p>${text}</p>
      <div class="grid-card-list" style="margin-top:1.5rem">
        ${cards.map((card) => `
          <div class="card">
            <h2>${card.title}</h2>
            <p>${card.copy}</p>
          </div>
        `).join('')}
      </div>
    </section>
  `;
}

function renderLinks() {
  root.innerHTML = `
    <section>
      <h1 class="page-title">Links</h1>
      <p>A curated list of useful external resources for IMLEM students, coaches, and families.</p>
      <div class="card">
        <h2>Art of Problem Solving</h2>
        <p><a class="link-button" href="http://www.artofproblemsolving.com/community/c308_massachusetts" target="_blank" rel="noreferrer">Massachusetts Forum</a></p>
      </div>
      <div class="card">
        <h2>Official IMLEM Materials</h2>
        <p>Direct access to league resources and archived competition documents.</p>
      </div>
      <div class="card">
        <h2>Additional Practice</h2>
        <p>Use reliable study and problem-solving resources to prepare for future meets.</p>
      </div>
    </section>
  `;
}

function makeToast(message) {
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.setAttribute('role', 'status');
  toast.setAttribute('aria-live', 'polite');
  toast.textContent = message;
  root.prepend(toast);
  setTimeout(() => toast.remove(), 4000);
}

function renderPasswordFormCard() {
  return `
    <div class="card" style="margin-top:1.5rem;max-width:420px">
      <h2>Change Password</h2>
      <form id="password-form" class="form-grid single-column">
        <div class="field">
          <label class="field-label" for="password-form-current">Current password</label>
          <input id="password-form-current" name="currentPassword" type="password" autocomplete="current-password" required />
        </div>
        <div class="field">
          <label class="field-label" for="password-form-new">New password</label>
          <input id="password-form-new" name="newPassword" type="password" autocomplete="new-password" minlength="8" required />
          <span class="field-hint">Minimum 8 characters.</span>
        </div>
        <button class="button-primary" type="submit">Update Password</button>
      </form>
    </div>
  `;
}

function attachPasswordFormHandler() {
  const form = document.getElementById('password-form');
  if (!form) return;
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    try {
      await fetchJson(`${apiBase}/me/password`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ currentPassword: form.currentPassword.value, newPassword: form.newPassword.value }),
      });
      makeToast('Password updated.');
      form.reset();
    } catch (err) {
      makeToast(err.error || 'Password update failed.');
    }
  });
}

function renderAdmin(divisions, meets, users) {
  const coachUsers = (users || []).filter((u) => u.role === 'coach');
  root.innerHTML = `
    <section>
      <h1 class="page-title">Admin Dashboard</h1>
      <p>Manage the study materials archive, meets, divisions, schools, and coach accounts.</p>

      <div class="card" style="margin-bottom:1.5rem">
        <div class="division-manager-header">
          <h2>Divisions</h2>
          <button id="add-division-toggle" class="button-secondary" type="button" aria-label="Add new division">+ New Division</button>
        </div>
        <div id="division-form-wrapper" style="display:none;max-width:320px;margin-top:1rem">
          <form id="division-form">
            <div class="field">
              <label class="field-label" for="division-form-name">Division name</label>
              <input id="division-form-name" name="name" placeholder="e.g. Euclid" />
            </div>
            <button class="button-primary" type="submit">Create Division</button>
          </form>
        </div>
        <ul class="division-list">
          ${divisions
            .map(
              (division) => `
            <li class="division-block">
              <div class="division-row">
                <span class="division-name">${escapeHtml(division.name)}</span>
                <button class="delete-x division-delete-x" type="button" data-division-id="${division.id}" data-division-name="${escapeHtml(division.name)}" aria-label="Delete ${escapeHtml(division.name)}">&times;</button>
              </div>
              ${division.teams.length
                ? `<ul class="school-list">${division.teams
                    .map(
                      (team) => `
                  <li class="school-item">
                    <span>${escapeHtml(team.name)}</span>
                    <button class="delete-x school-delete-x" type="button" data-division-id="${division.id}" data-team-id="${team.id}" data-team-name="${escapeHtml(team.name)}" aria-label="Remove ${escapeHtml(team.name)}">&times;</button>
                  </li>`
                    )
                    .join('')}</ul>`
                : '<p class="school-empty">No schools yet.</p>'}
            </li>`
            )
            .join('')}
        </ul>
      </div>

      <div class="card" style="margin-bottom:1.5rem">
        <h2>Meets</h2>
        <ul class="division-list">
          ${meets.length
            ? meets
                .map(
                  (meet) => `
            <li class="division-block">
              <div class="division-row">
                <span class="division-name">${escapeHtml(meet.date)}${meet.time ? ' &middot; ' + escapeHtml(meet.time) : ''}${meet.location ? ' — ' + escapeHtml(meet.location) : ''}</span>
                <button class="delete-x meet-delete-x" type="button" data-meet-id="${meet.id}" aria-label="Delete meet on ${escapeHtml(meet.date)}">&times;</button>
              </div>
            </li>`
                )
                .join('')
            : '<p class="school-empty">No meets scheduled yet.</p>'}
        </ul>
      </div>

      <div class="card" style="margin-bottom:1.5rem">
        <h2>Coach Accounts</h2>
        <ul class="division-list">
          ${coachUsers.length
            ? coachUsers
                .map(
                  (user) => `
            <li class="division-block">
              <div class="division-row">
                <span class="division-name">${escapeHtml(user.name)} — ${escapeHtml(user.email)}</span>
                <button class="delete-x user-delete-x" type="button" data-user-id="${user.id}" data-user-name="${escapeHtml(user.name)}" aria-label="Delete account for ${escapeHtml(user.name)}">&times;</button>
              </div>
            </li>`
                )
                .join('')
            : '<p class="school-empty">No coach accounts yet.</p>'}
        </ul>
      </div>

      <div class="form-grid">
        <div class="card">
          <h2>Upload Study Materials</h2>
          <form id="upload-form">
            <div class="field">
              <label class="field-label" for="upload-form-year">Year</label>
              <input id="upload-form-year" name="year" placeholder="e.g. 2026" />
            </div>
            <div class="field">
              <label class="field-label" for="upload-form-meet">Meet number</label>
              <input id="upload-form-meet" name="meetNumber" placeholder="1–5" />
            </div>
            <div class="field">
              <label class="field-label" for="upload-form-type">File type</label>
              <select id="upload-form-type" name="type"><option value="questions">Questions</option><option value="answers">Answers</option><option value="solutions">Solutions</option></select>
            </div>
            <div class="field">
              <label class="field-label" for="upload-form-file">PDF file</label>
              <input id="upload-form-file" type="file" name="file" accept="application/pdf" />
            </div>
            <button class="button-primary" type="submit">Upload PDF</button>
          </form>
        </div>
        <div class="card">
          <h2>Create New Meet</h2>
          <form id="meet-form">
            <div class="field">
              <label class="field-label" for="meet-form-date">Date</label>
              <input id="meet-form-date" type="date" name="date" />
            </div>
            <div class="field">
              <label class="field-label" for="meet-form-time">Time</label>
              <input id="meet-form-time" name="time" placeholder="e.g. 4:00 PM" />
            </div>
            <div class="field">
              <label class="field-label" for="meet-form-location">Location</label>
              <input id="meet-form-location" name="location" placeholder="Host school or venue" />
            </div>
            <div class="field">
              <label class="field-label" for="meet-form-announcement">Announcement (optional)</label>
              <input id="meet-form-announcement" name="announcement" placeholder="Any notes for coaches" />
            </div>
            <button class="button-primary" type="submit">Create Meet</button>
          </form>
        </div>
        <div class="card">
          <h2>Add School to Division</h2>
          <form id="division-team-form">
            <div class="field">
              <label class="field-label" for="division-team-form-division">Division</label>
              <select id="division-team-form-division" name="divisionId">${divisions.map((division) => `<option value="${division.id}">${escapeHtml(division.name)}</option>`).join('')}</select>
            </div>
            <div class="field">
              <label class="field-label" for="division-team-form-name">School name</label>
              <input id="division-team-form-name" name="name" placeholder="School name" />
            </div>
            <div class="field">
              <label class="field-label" for="division-team-form-description">Description (optional)</label>
              <input id="division-team-form-description" name="description" placeholder="Description (optional)" />
            </div>
            <button class="button-secondary" type="submit">Add School</button>
          </form>
        </div>
        <div class="card">
          <h2>Edit School Info</h2>
          <form id="edit-school-form">
            <div class="field">
              <label class="field-label" for="edit-school-form-ref">School</label>
              <select id="edit-school-form-ref" name="schoolRef">
                ${divisions
                  .flatMap((division) => division.teams.map((team) => `<option value="${division.id}|${team.id}" data-name="${escapeHtml(team.name)}" data-description="${escapeHtml(team.description || '')}">${escapeHtml(division.name)} — ${escapeHtml(team.name)}</option>`))
                  .join('')}
              </select>
            </div>
            <div class="field">
              <label class="field-label" for="edit-school-form-name">School name</label>
              <input id="edit-school-form-name" name="name" placeholder="School name" />
            </div>
            <div class="field">
              <label class="field-label" for="edit-school-form-description">Description</label>
              <input id="edit-school-form-description" name="description" placeholder="Description" />
            </div>
            <button class="button-secondary" type="submit">Save School Info</button>
          </form>
        </div>
        <div class="card">
          <h2>Record Meet Score</h2>
          <form id="division-score-form">
            <div class="field">
              <label class="field-label" for="division-score-form-team">School</label>
              <select id="division-score-form-team" name="teamRef">
                ${divisions
                  .flatMap((division) => division.teams.map((team) => `<option value="${division.id}|${team.id}">${escapeHtml(division.name)} — ${escapeHtml(team.name)}</option>`))
                  .join('')}
              </select>
            </div>
            <div class="field">
              <label class="field-label" for="division-score-form-meet">Meet number (1–5)</label>
              <input id="division-score-form-meet" name="meetNumber" placeholder="1–5" />
            </div>
            <div class="field">
              <label class="field-label" for="division-score-form-score">Score</label>
              <input id="division-score-form-score" name="score" placeholder="Score" />
            </div>
            <button class="button-primary" type="submit">Save Score</button>
          </form>
        </div>
        <div class="card">
          <h2>Create Coach Account</h2>
          <form id="create-coach-form">
            <div class="field">
              <label class="field-label" for="create-coach-form-school">School</label>
              <select id="create-coach-form-school" name="schoolRef">
                ${divisions
                  .flatMap((division) => division.teams.map((team) => `<option value="${division.id}|${team.id}">${escapeHtml(division.name)} — ${escapeHtml(team.name)}</option>`))
                  .join('')}
              </select>
            </div>
            <div class="field">
              <label class="field-label" for="create-coach-form-name">Coach name</label>
              <input id="create-coach-form-name" name="name" placeholder="Coach name" />
            </div>
            <div class="field">
              <label class="field-label" for="create-coach-form-email">Email</label>
              <input id="create-coach-form-email" name="email" type="email" placeholder="Email" />
            </div>
            <div class="field">
              <label class="field-label" for="create-coach-form-password">Temporary password</label>
              <input id="create-coach-form-password" name="password" type="password" placeholder="Min 8 characters" minlength="8" />
            </div>
            <button class="button-secondary" type="submit">Create Coach Account</button>
          </form>
        </div>
      </div>

      ${renderPasswordFormCard()}
    </section>
  `;

  attachPasswordFormHandler();

  document.getElementById('upload-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    try {
      await fetchJson(`${apiBase}/upload-file`, { method: 'POST', body: data });
      makeToast('File uploaded successfully.');
      form.reset();
    } catch (err) {
      makeToast(err.error || 'Upload failed.');
    }
  });

  document.getElementById('meet-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = {
      date: form.date.value,
      time: form.time.value,
      location: form.location.value,
      announcement: form.announcement.value,
    };
    try {
      await fetchJson(`${apiBase}/meets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      makeToast('Meet created successfully.');
      location.reload();
    } catch (err) {
      makeToast(err.error || 'Create meet failed.');
    }
  });

  document.getElementById('add-division-toggle').addEventListener('click', () => {
    const wrapper = document.getElementById('division-form-wrapper');
    wrapper.style.display = wrapper.style.display === 'none' ? 'block' : 'none';
  });

  document.getElementById('division-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    try {
      await fetchJson(`${apiBase}/divisions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: form.name.value }),
      });
      makeToast('Division created successfully.');
      location.reload();
    } catch (err) {
      makeToast(err.error || 'Create division failed.');
    }
  });

  document.querySelectorAll('.division-delete-x').forEach((button) => {
    button.addEventListener('click', async () => {
      const { divisionId, divisionName } = button.dataset;
      if (!confirm(`Delete "${divisionName}" and all its schools? This cannot be undone.`)) return;
      try {
        await fetchJson(`${apiBase}/divisions/${divisionId}`, { method: 'DELETE' });
        makeToast('Division deleted.');
        location.reload();
      } catch (err) {
        makeToast(err.error || 'Delete failed.');
      }
    });
  });

  document.querySelectorAll('.school-delete-x').forEach((button) => {
    button.addEventListener('click', async () => {
      const { divisionId, teamId, teamName } = button.dataset;
      if (!confirm(`Remove "${teamName}" from this division? This cannot be undone.`)) return;
      try {
        await fetchJson(`${apiBase}/divisions/${divisionId}/teams/${teamId}`, { method: 'DELETE' });
        makeToast('School removed.');
        location.reload();
      } catch (err) {
        makeToast(err.error || 'Remove failed.');
      }
    });
  });

  document.querySelectorAll('.meet-delete-x').forEach((button) => {
    button.addEventListener('click', async () => {
      if (!confirm('Delete this meet? This cannot be undone.')) return;
      try {
        await fetchJson(`${apiBase}/meets/${button.dataset.meetId}`, { method: 'DELETE' });
        makeToast('Meet deleted.');
        location.reload();
      } catch (err) {
        makeToast(err.error || 'Delete failed.');
      }
    });
  });

  document.querySelectorAll('.user-delete-x').forEach((button) => {
    button.addEventListener('click', async () => {
      const { userId, userName } = button.dataset;
      if (!confirm(`Delete coach account "${userName}"? This cannot be undone.`)) return;
      try {
        await fetchJson(`${apiBase}/users/${userId}`, { method: 'DELETE' });
        makeToast('Account deleted.');
        location.reload();
      } catch (err) {
        makeToast(err.error || 'Delete failed.');
      }
    });
  });

  document.getElementById('division-team-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    try {
      await fetchJson(`${apiBase}/divisions/${form.divisionId.value}/teams`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: form.name.value, description: form.description.value }),
      });
      makeToast('School added to division.');
      location.reload();
    } catch (err) {
      makeToast(err.error || 'Add school failed.');
    }
  });

  const editSchoolForm = document.getElementById('edit-school-form');
  const fillEditSchoolForm = () => {
    const opt = editSchoolForm.schoolRef.options[editSchoolForm.schoolRef.selectedIndex];
    if (!opt) return;
    editSchoolForm.name.value = opt.dataset.name || '';
    editSchoolForm.description.value = opt.dataset.description || '';
  };
  editSchoolForm.schoolRef.addEventListener('change', fillEditSchoolForm);
  fillEditSchoolForm();
  editSchoolForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const [divisionId, teamId] = editSchoolForm.schoolRef.value.split('|');
    try {
      await fetchJson(`${apiBase}/divisions/${divisionId}/teams/${teamId}/info`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: editSchoolForm.name.value, description: editSchoolForm.description.value }),
      });
      makeToast('School info saved.');
      location.reload();
    } catch (err) {
      makeToast(err.error || 'Save failed.');
    }
  });

  document.getElementById('division-score-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const [divisionId, teamId] = form.teamRef.value.split('|');
    try {
      await fetchJson(`${apiBase}/divisions/${divisionId}/teams/${teamId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ meetNumber: form.meetNumber.value, score: Number(form.score.value) }),
      });
      makeToast('Score recorded.');
      form.reset();
    } catch (err) {
      makeToast(err.error || 'Save score failed.');
    }
  });

  document.getElementById('create-coach-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const [divisionId, schoolId] = form.schoolRef.value.split('|');
    try {
      await fetchJson(`${apiBase}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: form.name.value,
          email: form.email.value,
          password: form.password.value,
          divisionId,
          schoolId,
        }),
      });
      makeToast('Coach account created.');
      form.reset();
    } catch (err) {
      makeToast(err.error || 'Create coach account failed.');
    }
  });
}

function renderCoach(data) {
  const { division, school } = data;
  const total = school.scores.reduce((sum, v) => sum + (v || 0), 0);
  root.innerHTML = `
    <section>
      <h1 class="page-title">Coach Dashboard</h1>
      <p>${escapeHtml(school.name)} &middot; ${escapeHtml(division.name)} Division</p>

      <div class="card" style="margin-top:1.5rem">
        <h2>School Info</h2>
        <form id="school-info-form">
          <div class="field">
            <label class="field-label" for="school-info-form-name">School name</label>
            <input id="school-info-form-name" name="name" value="${escapeHtml(school.name)}" placeholder="School name" />
          </div>
          <div class="field">
            <label class="field-label" for="school-info-form-description">Short description</label>
            <textarea id="school-info-form-description" name="description" rows="3" placeholder="Short description">${escapeHtml(school.description || '')}</textarea>
          </div>
          <button class="button-primary" type="submit">Save School Info</button>
        </form>
      </div>

      <div class="card" style="margin-top:1.5rem">
        <h2>Team Roster</h2>
        <form id="roster-form">
          <div class="field">
            <label class="field-label" for="roster-form-roster">Roster</label>
            <textarea id="roster-form-roster" name="roster" rows="6" placeholder="One student name per line">${escapeHtml((school.roster || []).join('\n'))}</textarea>
            <span class="field-hint">One student name per line.</span>
          </div>
          <button class="button-primary" type="submit">Save Roster</button>
        </form>
      </div>

      <div class="card" style="margin-top:1.5rem">
        <h2>Results</h2>
        <div class="table-wrapper">
          <table>
            <caption class="sr-only">${escapeHtml(school.name)} results by meet</caption>
            <thead><tr><th scope="col">Division</th><th scope="col">M1</th><th scope="col">M2</th><th scope="col">M3</th><th scope="col">M4</th><th scope="col">M5</th><th scope="col">Total</th></tr></thead>
            <tbody>
              <tr>
                <td>${escapeHtml(division.name)}</td>
                ${school.scores.map((s) => `<td>${s ?? '—'}</td>`).join('')}
                <td>${total}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      ${renderPasswordFormCard()}
    </section>
  `;

  attachPasswordFormHandler();

  document.getElementById('school-info-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    try {
      await fetchJson(`${apiBase}/my-school`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: form.name.value, description: form.description.value }),
      });
      makeToast('School info saved.');
    } catch (err) {
      makeToast(err.error || 'Save failed.');
    }
  });

  document.getElementById('roster-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const roster = form.roster.value.split('\n').map((s) => s.trim()).filter(Boolean);
    try {
      await fetchJson(`${apiBase}/my-school`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ roster }),
      });
      makeToast('Roster saved.');
    } catch (err) {
      makeToast(err.error || 'Save failed.');
    }
  });
}

function attachLinkListeners() {
  document.addEventListener('click', (event) => {
    const anchor = event.target.closest('a[href^="#/"]');
    if (!anchor) return;
    event.preventDefault();
    window.location.hash = anchor.getAttribute('href');
  });
}

async function navigate() {
  const hash = window.location.hash || '#/';
  const requiredRoles = protectedRoutes[hash];
  if (requiredRoles) {
    if (!currentUser) {
      renderLogin(hash);
      setActiveNav(hash);
      return;
    }
    if (!requiredRoles.includes(currentUser.role)) {
      root.innerHTML = `
        <section>
          <h1 class="page-title">Access Denied</h1>
          <p>Your account (${currentUser.role}) does not have access to this page.</p>
          <a class="link-button" href="#/">Return home</a>
        </section>`;
      setActiveNav(hash);
      return;
    }
  }

  if (hash === '#/login') {
    renderLogin('#/');
  } else if (hash === '#/' || hash === '') {
    const [meetsData, divisionsData] = await Promise.all([
      fetchJson(`${apiBase}/meets`),
      fetchJson(`${apiBase}/divisions`),
    ]);
    const records = meetsData.records || [];
    const today = new Date().toISOString().slice(0, 10);
    const upcoming = records.filter((m) => m.date >= today).sort((a, b) => (a.date > b.date ? 1 : -1));

    let leader = null;
    let schoolCount = 0;
    (divisionsData.records || []).forEach((division) => {
      (division.teams || []).forEach((team) => {
        schoolCount += 1;
        const total = team.scores.reduce((sum, val) => sum + (val || 0), 0);
        if (total > 0 && (!leader || total > leader.total)) {
          leader = { school: team.name, division: division.name, total };
        }
      });
    });

    renderHome({
      schoolCount,
      divisionCount: (divisionsData.records || []).length,
      meetCount: records.length,
      nextMeet: upcoming[0] || null,
      leader,
    });
  } else if (hash === '#/study-materials') {
    const data = await fetchJson(`${apiBase}/study-materials`);
    renderStudyMaterials(data);
  } else if (hash === '#/meets') {
    const meets = await fetchJson(`${apiBase}/meets`);
    renderMeetInfo(meets);
  } else if (hash === '#/meets/calculator-rules') {
    renderCalculatorRules();
  } else if (hash === '#/standings') {
    const divisions = await fetchJson(`${apiBase}/divisions`);
    renderStandings(divisions.records || divisions);
  } else if (hash === '#/statistics') {
    const data = await fetchJson(`${apiBase}/statistics`);
    renderStatistics(data);
  } else if (hash === '#/league') {
    renderStaticPage('League Information', 'This section preserves league structure, policies, and historic context.', [
      { title: 'About IMLEM', copy: 'A long-running academic math league built for middle schools.' },
      { title: 'League Goals', copy: 'Academic integrity, clear competition structure, and support for coaches.' },
      { title: 'Participation', copy: 'Coaches manage their own school, and the league office manages divisions, meets, and the archive.' },
    ]);
  } else if (hash === '#/coaches') {
    root.innerHTML = `
      <section>
        <h1 class="page-title">Coaches' Corner</h1>
        <p>This page is the primary access point for coaches and administrators to manage rosters, meet scheduling, and archive uploads.</p>
        <div class="grid-card-list" style="margin-top:1.5rem">
          <div class="card">
            <h2>Coach Dashboard</h2>
            <p>View and edit your school's info, roster, and results.</p>
            <a class="button-primary" href="#/coach">Open Coach Dashboard</a>
          </div>
          <div class="card">
            <h2>Admin Dashboard</h2>
            <p>Upload study materials, manage divisions and schools, and create coach accounts.</p>
            <a class="button-secondary" href="#/admin">Open Admin</a>
          </div>
        </div>
      </section>
    `;
  } else if (hash === '#/links') {
    renderLinks();
  } else if (hash === '#/contact') {
    root.innerHTML = `
      <section>
        <h1 class="page-title">Contact Information</h1>
        <p>Questions about schedules, archive access, and coordination should be directed to league staff.</p>
        <div class="card" style="max-width:620px">
          <h2>General Office</h2>
          <p>Email: <a href="mailto:info@imlem.org">info@imlem.org</a></p>
          <p>Reply time is kept to a minimum so staff can focus on administration.</p>
        </div>
      </section>
    `;
  } else if (hash === '#/admin') {
    const [divisionsData, meetsData, usersData] = await Promise.all([
      fetchJson(`${apiBase}/divisions`),
      fetchJson(`${apiBase}/meets`),
      fetchJson(`${apiBase}/users`),
    ]);
    renderAdmin(divisionsData.records || [], meetsData.records || [], usersData.accounts || []);
  } else if (hash === '#/coach') {
    const mySchool = await fetchJson(`${apiBase}/my-school`);
    renderCoach(mySchool);
  } else {
    root.innerHTML = `
      <section>
        <h1 class="page-title">Page not found</h1>
        <p>That page doesn't exist. <a class="link-button" href="#/">Return home</a>.</p>
      </section>
    `;
  }
  const normalizedHash = hash === '' ? '#/' : hash;
  document.title = `${PAGE_TITLES[normalizedHash] || 'Page Not Found'} — IMLEM`;
  setActiveNav(normalizedHash);
  const nav = document.getElementById('primary-nav');
  if (nav) nav.classList.remove('open');
  const toggle = document.getElementById('nav-toggle');
  if (toggle) toggle.setAttribute('aria-expanded', 'false');
}

function initShell() {
  renderPrimaryNav();
  renderFooter();
  attachLinkListeners();
  const toggle = document.getElementById('nav-toggle');
  const nav = document.getElementById('primary-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const isOpen = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(isOpen));
    });
  }
}

window.addEventListener('hashchange', navigate);
window.addEventListener('load', async () => {
  await loadCurrentUser();
  initShell();
  navigate();
});
