import { useEffect, useMemo, useState } from 'react';
import { getStudyMaterials } from '../api.js';

function StudyMaterials() {
  const [data, setData] = useState({ years: [] });
  const [year, setYear] = useState('');
  const [meet, setMeet] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getStudyMaterials()
      .then((payload) => {
        setData(payload);
        setLoading(false);
        if (payload.years.length) {
          setYear(payload.years[0].year);
        }
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const selectedYear = useMemo(() => data.years.find((entry) => entry.year === year), [data.years, year]);
  const meetOptions = selectedYear ? selectedYear.meets : [];
  const selectedMeet = meetOptions.find((entry) => entry.meetNumber === meet) || meetOptions[0] || null;

  useEffect(() => {
    if (!meet && meetOptions.length) {
      setMeet(meetOptions[0].meetNumber);
    }
  }, [meetOptions, meet]);

  return (
    <section>
      <h1 className="page-title">Study Materials Archive</h1>
      <p>Access all archived PDFs by year, meet number, and file type.</p>

      {loading && <p>Loading archive data…</p>}
      {error && <p style={{ color: '#b12a1f' }}>{error}</p>}

      {!loading && !error && (
        <>
          <div className="filters">
            <select value={year} onChange={(e) => setYear(e.target.value)}>
              {data.years.map((entry) => (
                <option key={entry.year} value={entry.year}>
                  {entry.year}
                </option>
              ))}
            </select>

            <select value={meet} onChange={(e) => setMeet(e.target.value)}>
              {meetOptions.map((entry) => (
                <option key={entry.meetNumber} value={entry.meetNumber}>
                  Meet {entry.meetNumber}
                </option>
              ))}
            </select>
          </div>

          {selectedMeet ? (
            <div className="card" style={{ marginTop: '1rem' }}>
              <h2>Meet {selectedMeet.meetNumber}</h2>
              <p>{selectedMeet.files.length} file(s) available for download.</p>

              <div style={{ marginTop: '1rem' }}>
                {selectedMeet.files.map((file) => (
                  <div key={file.id} style={{ marginBottom: '0.85rem' }}>
                    <a href={file.url} target="_blank" rel="noreferrer" className="link-button">
                      Download {file.title}
                    </a>
                    <span style={{ marginLeft: '0.75rem', color: '#5a6a7d' }}>{file.type}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p>No materials found for this selection.</p>
          )}
        </>
      )}
    </section>
  );
}

export default StudyMaterials;
