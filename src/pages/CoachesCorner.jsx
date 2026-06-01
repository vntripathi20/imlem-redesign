function CoachesCorner() {
  return (
    <section>
      <h1 className="page-title">Coaches' Corner</h1>
      <p>Resources and announcements for coaches are kept simple and easy to navigate.</p>

      <div className="grid-blocks" style={{ marginTop: '1.5rem' }}>
        <div className="card">
          <h2>Coordinator Support</h2>
          <p>Find cluster contact details, meet schedules, and instructions for safe meet updates.</p>
        </div>
        <div className="card">
          <h2>Study Advice</h2>
          <p>Use archived questions and solutions to guide students through competition preparation.</p>
        </div>
        <div className="card">
          <h2>Archive Access</h2>
          <p>Study materials are organized by year and meet to keep historic content intact and searchable.</p>
        </div>
      </div>
    </section>
  );
}

export default CoachesCorner;
