import { useEffect, useState } from 'react';
import { createMeet, getClusters, getStudyMaterials, postAnnouncement, uploadStudyFile } from '../api.js';

function AdminDashboard() {
  const [clusters, setClusters] = useState([]);
  const [year, setYear] = useState('2024');
  const [meetNumber, setMeetNumber] = useState('1');
  const [type, setType] = useState('questions');
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [location, setLocation] = useState('');
  const [date, setDate] = useState('');
  const [time, setTime] = useState('');
  const [clusterId, setClusterId] = useState('');
  const [announcement, setAnnouncement] = useState('');

  useEffect(() => {
    getClusters().then((payload) => {
      setClusters(payload.records || []);
      if (payload.records?.[0]) {
        setClusterId(payload.records[0].id);
      }
    });
  }, []);

  const handleUpload = async (event) => {
    event.preventDefault();
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    formData.append('year', year);
    formData.append('meetNumber', meetNumber);
    formData.append('type', type);
    formData.append('title', file.name);

    try {
      await uploadStudyFile(formData);
      setMessage('File uploaded successfully.');
      setFile(null);
      event.target.reset();
    } catch (err) {
      setMessage(err.message);
    }
  };

  const handleMeetCreate = async (event) => {
    event.preventDefault();
    if (!clusterId || !date) return;
    try {
      await createMeet({ clusterId, date, time, location });
      setMessage('Meet created successfully.');
    } catch (err) {
      setMessage(err.message);
    }
  };

  const handleAnnouncement = async (event) => {
    event.preventDefault();
    if (!clusterId || !announcement) return;
    try {
      await postAnnouncement({ clusterId, message: announcement });
      setMessage('Announcement updated.');
      setAnnouncement('');
    } catch (err) {
      setMessage(err.message);
    }
  };

  return (
    <section>
      <h1 className="page-title">Admin Dashboard</h1>
      <p>Manage archives and league operations from one simple interface.</p>
      {message && <p style={{ color: '#2e5c3f' }}>{message}</p>}

      <div className="form-grid">
        <form onSubmit={handleUpload} className="card">
          <h2>Upload Study Materials</h2>
          <select value={year} onChange={(e) => setYear(e.target.value)}>
            <option>2024</option>
            <option>2023</option>
            <option>2022</option>
          </select>
          <input
            type="text"
            value={meetNumber}
            onChange={(e) => setMeetNumber(e.target.value)}
            placeholder="Meet number"
          />
          <select value={type} onChange={(e) => setType(e.target.value)}>
            <option value="questions">Questions</option>
            <option value="answers">Answers</option>
            <option value="solutions">Solutions</option>
          </select>
          <input type="file" accept="application/pdf" onChange={(e) => setFile(e.target.files?.[0] || null)} />
          <button type="submit" className="button-primary">Upload PDF</button>
        </form>

        <form onSubmit={handleMeetCreate} className="card">
          <h2>Create New Meet</h2>
          <select value={clusterId} onChange={(e) => setClusterId(e.target.value)}>
            {clusters.map((cluster) => (
              <option key={cluster.id} value={cluster.id}>{cluster.name}</option>
            ))}
          </select>
          <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
          <input type="text" value={time} onChange={(e) => setTime(e.target.value)} placeholder="Meet time" />
          <input type="text" value={location} onChange={(e) => setLocation(e.target.value)} placeholder="Location" />
          <button type="submit" className="button-primary">Create Meet</button>
        </form>

        <form onSubmit={handleAnnouncement} className="card">
          <h2>Cluster Announcements</h2>
          <select value={clusterId} onChange={(e) => setClusterId(e.target.value)}>
            {clusters.map((cluster) => (
              <option key={cluster.id} value={cluster.id}>{cluster.name}</option>
            ))}
          </select>
          <textarea
            value={announcement}
            onChange={(e) => setAnnouncement(e.target.value)}
            rows="4"
            placeholder="Announcement text"
          />
          <button type="submit" className="button-secondary">Save Announcement</button>
        </form>
      </div>
    </section>
  );
}

export default AdminDashboard;
