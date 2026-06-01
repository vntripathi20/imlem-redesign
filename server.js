import express from 'express';
import cors from 'cors';
import multer from 'multer';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { v4 as uuid } from 'uuid';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const app = express();
const PORT = process.env.PORT || 4000;
const dataDir = path.join(__dirname, 'data');
const uploadRoot = path.join(__dirname, 'uploads');

app.use(cors({ origin: 'http://localhost:5173' }));
app.use(express.json());
app.use('/uploads', express.static(uploadRoot));

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const { year, meetNumber, type } = req.body;
    const yearPath = path.join(uploadRoot, String(year), String(meetNumber), type || 'files');
    fs.mkdirSync(yearPath, { recursive: true });
    cb(null, yearPath);
  },
  filename: (req, file, cb) => {
    const timestamp = Date.now();
    const safeName = file.originalname.replace(/[^a-zA-Z0-9._-]/g, '_');
    cb(null, `${timestamp}_${safeName}`);
  },
});

const upload = multer({
  storage,
  fileFilter: (req, file, cb) => {
    if (file.mimetype !== 'application/pdf') {
      return cb(new Error('Only PDF files are accepted'));
    }
    cb(null, true);
  },
  limits: { fileSize: 50 * 1024 * 1024 },
});

function readJSON(name) {
  const filePath = path.join(dataDir, name);
  if (!fs.existsSync(filePath)) return null;
  return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
}

function writeJSON(name, data) {
  const filePath = path.join(dataDir, name);
  fs.mkdirSync(dataDir, { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8');
}

function ensureData(name, defaultValue) {
  const existing = readJSON(name);
  if (existing) return existing;
  writeJSON(name, defaultValue);
  return defaultValue;
}

const studyMaterials = ensureData('study-materials.json', {
  years: [],
});
const meets = ensureData('meets.json', {
  records: [],
});
const clusters = ensureData('clusters.json', {
  records: [],
});
const statistics = ensureData('statistics.json', {
  records: [],
});
const users = ensureData('users.json', {
  accounts: [
    {
      id: 'admin-1',
      name: 'Site Administrator',
      role: 'admin',
      clusterId: null,
      email: 'admin@imlem.org',
    },
    {
      id: 'coord-1',
      name: 'Cluster Coordinator',
      role: 'coordinator',
      clusterId: 'cluster-1',
      email: 'coord@imlem.org',
    },
  ],
});

app.get('/api/study-materials', (req, res) => {
  res.json(readJSON('study-materials.json'));
});

app.get('/api/meets', (req, res) => {
  res.json(readJSON('meets.json'));
});

app.get('/api/clusters', (req, res) => {
  res.json(readJSON('clusters.json'));
});

app.get('/api/statistics', (req, res) => {
  res.json(readJSON('statistics.json'));
});

app.get('/api/users', (req, res) => {
  res.json(readJSON('users.json'));
});

app.post('/api/upload-file', upload.single('file'), (req, res) => {
  const { year, meetNumber, type, title } = req.body;
  if (!year || !meetNumber || !type || !req.file) {
    return res.status(400).json({ error: 'year, meetNumber, type and file are required' });
  }

  const archive = readJSON('study-materials.json');
  const yearKey = String(year);
  let yearEntry = archive.years.find((entry) => entry.year === yearKey);
  if (!yearEntry) {
    yearEntry = { year: yearKey, meets: [] };
    archive.years.push(yearEntry);
  }

  let meetEntry = yearEntry.meets.find((entry) => entry.meetNumber === String(meetNumber));
  if (!meetEntry) {
    meetEntry = { meetNumber: String(meetNumber), files: [] };
    yearEntry.meets.push(meetEntry);
  }

  const fileEntry = {
    id: uuid(),
    type,
    title: title || req.file.originalname,
    filename: req.file.filename,
    originalName: req.file.originalname,
    url: `/uploads/${encodeURIComponent(yearKey)}/${encodeURIComponent(String(meetNumber))}/${encodeURIComponent(type)}/${encodeURIComponent(req.file.filename)}`,
    uploadedAt: new Date().toISOString(),
  };

  meetEntry.files.push(fileEntry);
  writeJSON('study-materials.json', archive);
  res.json({ success: true, file: fileEntry });
});

app.post('/api/meets', (req, res) => {
  const incoming = req.body;
  if (!incoming || !incoming.clusterId || !incoming.date) {
    return res.status(400).json({ error: 'clusterId and date are required' });
  }

  const store = readJSON('meets.json');
  const record = {
    id: uuid(),
    clusterId: incoming.clusterId,
    date: incoming.date,
    time: incoming.time || '',
    location: incoming.location || '',
    announcement: incoming.announcement || '',
    createdAt: new Date().toISOString(),
  };
  store.records.push(record);
  writeJSON('meets.json', store);
  res.json(record);
});

app.put('/api/meets/:id', (req, res) => {
  const id = req.params.id;
  const updates = req.body;
  const store = readJSON('meets.json');
  const record = store.records.find((entry) => entry.id === id);
  if (!record) return res.status(404).json({ error: 'Meet not found' });

  Object.assign(record, {
    location: updates.location ?? record.location,
    date: updates.date ?? record.date,
    time: updates.time ?? record.time,
    announcement: updates.announcement ?? record.announcement,
    updatedAt: new Date().toISOString(),
  });

  writeJSON('meets.json', store);
  res.json(record);
});

app.post('/api/announcements', (req, res) => {
  const { clusterId, message } = req.body;
  if (!clusterId || !message) {
    return res.status(400).json({ error: 'clusterId and message are required' });
  }
  const store = readJSON('clusters.json');
  const cluster = store.records.find((entry) => entry.id === clusterId);
  if (!cluster) return res.status(404).json({ error: 'Cluster not found' });

  cluster.announcement = message;
  cluster.updatedAt = new Date().toISOString();
  writeJSON('clusters.json', store);
  res.json(cluster);
});

app.listen(PORT, () => {
  console.log(`IMLEM API server listening on http://localhost:${PORT}`);
});
