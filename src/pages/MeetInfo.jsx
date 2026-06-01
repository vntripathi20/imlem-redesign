import { useEffect, useState } from 'react';
import { getMeets, getClusters } from '../api.js';

function MeetInfo() {
  const [meets, setMeets] = useState([]);
  const [clusters, setClusters] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getMeets(), getClusters()])
      .then(([meetResponse, clusterResponse]) => {
        setMeets(meetResponse.records || []);
        setClusters(clusterResponse.records || []);
      })
      .finally(() => setLoading(false));
  }, []);

  const clusterMap = clusters.reduce((map, cluster) => {
    map[cluster.id] = cluster.name;
    return map;
  }, {});

  return (
    <section>
      <h1 className="page-title">Meet Information</h1>
      <p>Review upcoming and past meets, cluster duties, and locations.</p>

      {loading && <p>Loading meet details…</p>}
      {!loading && (
        <div className="table-wrapper">
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
              {meets.length ? (
                meets.map((meet) => (
                  <tr key={meet.id}>
                    <td>{meet.date}</td>
                    <td>{clusterMap[meet.clusterId] || meet.clusterId}</td>
                    <td>{meet.location || 'TBD'}</td>
                    <td>{meet.time || 'TBD'}</td>
                    <td>{meet.announcement || '—'}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5">No meet records available.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export default MeetInfo;
