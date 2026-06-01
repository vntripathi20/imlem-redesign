import { useEffect, useState } from 'react';
import { getStatistics } from '../api.js';

function Statistics() {
  const [statistics, setStatistics] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getStatistics()
      .then((payload) => {
        setStatistics(payload.records || []);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <section>
      <h1 className="page-title">Statistics</h1>
      <p>View historical performance summaries and league results.</p>

      {loading && <p>Loading statistics…</p>}
      {!loading && (
        <div className="table-wrapper">
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
              {statistics.length ? (
                statistics.map((row) => (
                  <tr key={row.id}>
                    <td>{row.year}</td>
                    <td>{row.summary}</td>
                    <td>{row.topSchool}</td>
                    <td>{row.notes || '—'}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="4">No statistics records available yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export default Statistics;
