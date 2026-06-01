import { useEffect, useMemo, useState } from 'react';
import { getClusters, getMeets, updateMeet } from '../api.js';

function CoordinatorDashboard() {
  const [clusters, setClusters] = useState([]);
  const [meets, setMeets] = useState([]);
  const [selectedCluster, setSelectedCluster] = useState('');
  const [message, setMessage] = useState('');
  const [activeMeetId, setActiveMeetId] = useState(null);
  const [updates, setUpdates] = useState({ date: '', time: '', location: '' });

  useEffect(() => {
    Promise.all([getClusters(), getMeets()]).then(([clusterPayload, meetsPayload]) => {
      const clusterList = clusterPayload.records || [];
      setClusters(clusterList);
      if (clusterList[0]) setSelectedCluster(clusterList[0].id);
      setMeets(meetsPayload.records || []);
    });
  }, []);

  const clusterMeets = useMemo(() => meets.filter((meet) => meet.clusterId === selectedCluster), [meets, selectedCluster]);

  const handleSelectMeet = (meet) => {
    setActiveMeetId(meet.id);
    setUpdates({ date: meet.date || '', time: meet.time || '', location: meet.location || '' });
  };

  const handleSave = async (event) => {
    event.preventDefault();
    if (!activeMeetId) return;
    try {
      await updateMeet(activeMeetId, updates);
      setMessage('Meet information updated successfully.');
    } catch (err) {
      setMessage(err.message);
    }
  };

  return (
    <section>
      <h1 className="page-title">Coordinator Dashboard</h1>
      <p>Update only your assigned cluster and meet details from a simple interface.</p>
      {message && <p style={{ color: '#2e5c3f' }}>{message}</p>}

      <div className="filters" style={{ marginBottom: '1.5rem' }}>
        <select value={selectedCluster} onChange={(e) => setSelectedCluster(e.target.value)}>
          {clusters.map((cluster) => (
            <option key={cluster.id} value={cluster.id}>{cluster.name}</option>
          ))}
        </select>
      </div>

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Location</th>
              <th>Time</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {clusterMeets.length ? (
              clusterMeets.map((meet) => (
                <tr key={meet.id}>
                  <td>{meet.date}</td>
                  <td>{meet.location || 'TBD'}</td>
                  <td>{meet.time || 'TBD'}</td>
                  <td>
                    <button
                      type="button"
                      className="button-secondary"
                      onClick={() => handleSelectMeet(meet)}
                    >
                      Edit
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="4">No meets assigned to this cluster.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {activeMeetId && (
        <form onSubmit={handleSave} className="card" style={{ marginTop: '1.5rem' }}>
          <h2>Edit Meet Details</h2>
          <input
            type="date"
            value={updates.date}
            onChange={(e) => setUpdates((prev) => ({ ...prev, date: e.target.value }))}
          />
          <input
            type="text"
            value={updates.time}
            onChange={(e) => setUpdates((prev) => ({ ...prev, time: e.target.value }))}
            placeholder="Time"
          />
          <input
            type="text"
            value={updates.location}
            onChange={(e) => setUpdates((prev) => ({ ...prev, location: e.target.value }))}
            placeholder="Location"
          />
          <button type="submit" className="button-primary">Save Updates</button>
        </form>
      )}
    </section>
  );
}

export default CoordinatorDashboard;
