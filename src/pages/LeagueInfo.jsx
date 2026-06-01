function LeagueInfo() {
  return (
    <section>
      <h1 className="page-title">League Information</h1>
      <p>This section is designed to preserve league structure, policies, and historic context.</p>

      <div className="grid-blocks" style={{ marginTop: '1.5rem' }}>
        <div className="card">
          <h2>About IMLEM</h2>
          <p>The Intermediate Math League of Eastern Massachusetts supports middle school math competitions with historical archives and clear event structure.</p>
        </div>
        <div className="card">
          <h2>League Goals</h2>
          <p>Our focus is on academic integrity, steady growth, and supporting coaches, students, and families across all seasons.</p>
        </div>
        <div className="card">
          <h2>How to Participate</h2>
          <p>Coaches register teams, coordinators manage local clusters, and students prepare with materials from the archive.</p>
        </div>
      </div>
    </section>
  );
}

export default LeagueInfo;
