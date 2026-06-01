const apiBase = '/api';
const root = document.getElementById('root');
const publicSections = [
  { title: 'Meet Information', hash: '#/meets' },
  { title: 'Statistics', hash: '#/statistics' },
  { title: 'Study Materials', hash: '#/study-materials' },
  { title: 'League Information', hash: '#/league' },
  { title: "Coaches' Corner", hash: '#/coaches' },
  { title: 'Contact Information', hash: '#/contact' },
  { title: 'Links', hash: '#/links' },
];

const adminSections = [
  { title: 'Admin', hash: '#/admin' },
  { title: 'Coordinator', hash: '#/coordinator' },
];

function fetchJson(url, options = {}) {
  return fetch(url, options).then((res) => {
    if (!res.ok) return res.json().then((body) => Promise.reject(body));
    return res.json();
  });
}

function renderNav(sections) {
  return `
    <div class="nav-grid">
      ${sections
        .map(
          (section) => `
        <a class="card link-button" href="${section.hash}">
          <h2>${section.title}</h2>
          <p>Open ${section.title.toLowerCase()}.</p>
        </a>`
        )
        .join('')}
    </div>
  `;
}

function renderHome() {
  root.innerHTML = `
    <section>
      <div class="hero-card">
        <div>
          <span class="eyebrow">Intermediate Math League of Eastern Massachusetts</span>
          <h1 class="page-title">A Modern Archive for IMLEM</h1>
          <p>Explore meet information, archived study materials, historical statistics, coaches’ resources, and useful external links in a clean blue-themed interface.</p>
          <div class="hero-actions">
            <a class="button-primary" href="#/study-materials">Study Materials</a>
            <a class="button-secondary" href="#/meets">Meet Information</a>
          </div>
        </div>
        <img class="hero-image" src="/images/50-years.png" alt="50 years celebration" />
      </div>
      ${renderNav(publicSections)}
      <div class="card" style="margin-top: 1.5rem;">
        <h2>Coordinator & Admin Access</h2>
        <p>Administrative and coordinator tools are available for league staff, while the public site preserves the original navigation structure.</p>
        <div class="hero-actions" style="margin-top:1rem;">
          ${adminSections.map((section) => `<a class="button-secondary" href="${section.hash}">${section.title}</a>`).join('')}
        </div>
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
            <a class="link-button" href="${file.url}" target="_blank" rel="noreferrer">Download ${file.title}</a>
            <span style="margin-left:0.75rem;color:#5a6a7d">${file.type}</span>
          </div>`).join('') : ''}
      </div>
    </section>
  `;
}

function renderMeetInfo(data, clusters) {
  const clusterMap = Object.fromEntries((clusters || []).map((cluster) => [cluster.id, cluster.name]));
  root.innerHTML = `
    <section>
      <h1 class="page-title">Meet Information</h1>
      <p>Review upcoming and past meets, cluster duties, and locations.</p>
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Cluster</th>
              <th>Location</th>
              <th>Time</th>
              <th>Announcement</th>
            </tr>
          </thead>
          <tbody>
            ${(data.records || []).length
              ? (data.records || [])
                  .map(
                    (meet) => `
              <tr>
                <td>${meet.date}</td>
                <td>${clusterMap[meet.clusterId] || meet.clusterId}</td>
                <td>${meet.location || 'TBD'}</td>
                <td>${meet.time || 'TBD'}</td>
                <td>${meet.announcement || '—'}</td>
              </tr>`
                  )
                  .join('')
              : '<tr><td colspan="5">No meet records available.</td></tr>'}
          </tbody>
        </table>
      </div>
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
          <thead>
            <tr>
              <th>Year</th>
              <th>Summary</th>
              <th>Top School</th>
              <th>Notes</th>
            </tr>
          </thead>
          <tbody>
            ${(data.records || []).length
              ? (data.records || [])
                  .map(
                    (row) => `
              <tr>
                <td>${row.year}</td>
                <td>${row.summary}</td>
                <td>${row.topSchool || '—'}</td>
                <td>${row.notes || '—'}</td>
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
  toast.textContent = message;
  root.prepend(toast);
  setTimeout(() => toast.remove(), 4000);
}

function renderAdmin(clusters) {
  root.innerHTML = `
    <section>
      <h1 class="page-title">Admin Dashboard</h1>
      <p>Manage archives, meets, and announcements from a simple interface.</p>
      <div class="form-grid">
        <div class="card">
          <h2>Upload Study Materials</h2>
          <form id="upload-form">
            <input name="year" placeholder="Year" />
            <input name="meetNumber" placeholder="Meet number" />
            <select name="type"><option value="questions">Questions</option><option value="answers">Answers</option><option value="solutions">Solutions</option></select>
            <input type="file" name="file" accept="application/pdf" />
            <button class="button-primary" type="submit">Upload PDF</button>
          </form>
        </div>
        <div class="card">
          <h2>Create New Meet</h2>
          <form id="meet-form">
            <select name="clusterId">${clusters.map((cluster) => `<option value="${cluster.id}">${cluster.name}</option>`).join('')}</select>
            <input type="date" name="date" />
            <input name="time" placeholder="Meet time" />
            <input name="location" placeholder="Location" />
            <button class="button-primary" type="submit">Create Meet</button>
          </form>
        </div>
        <div class="card">
          <h2>Cluster Announcement</h2>
          <form id="announcement-form">
            <select name="clusterId">${clusters.map((cluster) => `<option value="${cluster.id}">${cluster.name}</option>`).join('')}</select>
            <textarea name="message" rows="4" placeholder="Announcement text"></textarea>
            <button class="button-secondary" type="submit">Save Announcement</button>
          </form>
        </div>
      </div>
    </section>
  `;

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
      clusterId: form.clusterId.value,
      date: form.date.value,
      time: form.time.value,
      location: form.location.value,
    };
    try {
      await fetchJson(`${apiBase}/meets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      makeToast('Meet created successfully.');
      form.reset();
    } catch (err) {
      makeToast(err.error || 'Create meet failed.');
    }
  });

  document.getElementById('announcement-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = {
      clusterId: form.clusterId.value,
      message: form.message.value,
    };
    try {
      await fetchJson(`${apiBase}/announcements`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      makeToast('Announcement updated.');
      form.reset();
    } catch (err) {
      makeToast(err.error || 'Save announcement failed.');
    }
  });
}

function renderCoordinator(clusters, meets) {
  const cluster = clusters[0] || { id: '', name: '' };
  const clusterMeets = meets.filter((meet) => meet.clusterId === cluster.id);
  root.innerHTML = `
    <section>
      <h1 class="page-title">Coordinator Dashboard</h1>
      <p>Update your assigned cluster's meet details without editing code.</p>
      <div class="card">
        <h2>Assigned Cluster</h2>
        <p>${cluster.name}</p>
      </div>
      <div class="table-wrapper">
        <table>
          <thead>
            <tr><th>Date</th><th>Location</th><th>Time</th><th>Action</th></tr>
          </thead>
          <tbody>
            ${clusterMeets.length
              ? clusterMeets.map((meet) => `
              <tr>
                <td>${meet.date}</td>
                <td>${meet.location || 'TBD'}</td>
                <td>${meet.time || 'TBD'}</td>
                <td><button class="button-secondary" data-meet-id="${meet.id}">Edit</button></td>
              </tr>`).join('')
              : '<tr><td colspan="4">No meets assigned to this cluster.</td></tr>'}
          </tbody>
        </table>
      </div>
      <div id="coordinator-form"></div>
    </section>
  `;

  document.querySelectorAll('[data-meet-id]').forEach((button) => {
    button.addEventListener('click', async (event) => {
      const meetId = event.currentTarget.dataset.meetId;
      const meet = clusterMeets.find((item) => item.id === meetId);
      if (!meet) return;
      const container = document.getElementById('coordinator-form');
      container.innerHTML = `
        <div class="card">
          <h2>Edit Meet</h2>
          <form id="edit-meet-form">
            <input name="date" type="date" value="${meet.date}" />
            <input name="time" value="${meet.time}" placeholder="Time" />
            <input name="location" value="${meet.location}" placeholder="Location" />
            <button class="button-primary" type="submit">Save Updates</button>
          </form>
        </div>
      `;
      document.getElementById('edit-meet-form').addEventListener('submit', async (saveEvent) => {
        saveEvent.preventDefault();
        const form = saveEvent.currentTarget;
        const payload = {
          date: form.date.value,
          time: form.time.value,
          location: form.location.value,
        };
        try {
          await fetchJson(`${apiBase}/meets/${meetId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
          });
          makeToast('Meet updated successfully.');
          location.reload();
        } catch (err) {
          makeToast(err.error || 'Update failed.');
        }
      });
    });
  });
}

function attachLinkListeners() {
  document.querySelectorAll('a[href^="#/"]').forEach((anchor) => {
    anchor.addEventListener('click', (event) => {
      event.preventDefault();
      window.location.hash = anchor.getAttribute('href');
    });
  });
}

async function navigate() {
  const hash = window.location.hash || '#/';
  if (hash === '#/' || hash === '') {
    renderHome();
  } else if (hash === '#/study-materials') {
    const data = await fetchJson(`${apiBase}/study-materials`);
    renderStudyMaterials(data);
  } else if (hash === '#/meets') {
    const [meets, clusters] = await Promise.all([fetchJson(`${apiBase}/meets`), fetchJson(`${apiBase}/clusters`)]);
    renderMeetInfo(meets, clusters.records || clusters);
  } else if (hash === '#/statistics') {
    const data = await fetchJson(`${apiBase}/statistics`);
    renderStatistics(data);
  } else if (hash === '#/league') {
    renderStaticPage('League Information', 'This section preserves league structure, policies, and historic context.', [
      { title: 'About IMLEM', copy: 'A long-running academic math league built for middle schools.' },
      { title: 'League Goals', copy: 'Academic integrity, clear competition structure, and support for coaches.' },
      { title: 'Participation', copy: 'Coaches register teams, coordinators manage clusters, and students use archive resources.' },
    ]);
  } else if (hash === '#/coaches') {
    root.innerHTML = `
      <section>
        <h1 class="page-title">Coaches' Corner</h1>
        <p>This page provides the primary access point for coordinators and administrators to manage meet scheduling, cluster announcements, and archive uploads.</p>
        <div class="grid-card-list" style="margin-top:1.5rem">
          <div class="card">
            <h2>Admin Dashboard</h2>
            <p>Upload study materials, create new meet records, and manage cluster announcements.</p>
            <a class="button-primary" href="#/admin">Open Admin</a>
          </div>
          <div class="card">
            <h2>Coordinator Dashboard</h2>
            <p>Update assigned cluster meet dates, locations, and announcements safely.</p>
            <a class="button-secondary" href="#/coordinator">Open Coordinator</a>
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
          <p>Phone: (555) 123-4567</p>
          <p>Reply time is kept to a minimum so coordinators can focus on administration.</p>
        </div>
      </section>
    `;
  } else if (hash === '#/admin') {
    const clusters = (await fetchJson(`${apiBase}/clusters`)).records || [];
    renderAdmin(clusters);
  } else if (hash === '#/coordinator') {
    const [clusters, meets] = await Promise.all([fetchJson(`${apiBase}/clusters`), fetchJson(`${apiBase}/meets`)]);
    renderCoordinator(clusters.records || clusters, meets.records || meets);
  } else {
    renderHome();
  }
  attachLinkListeners();
}

window.addEventListener('hashchange', navigate);
window.addEventListener('load', navigate);
