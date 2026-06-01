import { NavLink } from 'react-router-dom';

function Home({ sections }) {
  return (
    <section>
      <h1 className="page-title">IMLEM Public Archive</h1>
      <p>Browse meet details, study materials, league information, and coordinator tools.</p>

      <div className="grid-card-list" style={{ marginTop: '1.5rem' }}>
        {sections.map((section) => (
          <NavLink key={section.path} to={section.path} className="card">
            <h2>{section.label}</h2>
            <p>Open the {section.label.toLowerCase()} section for a clean academic experience.</p>
            <span className="link-button">Go</span>
          </NavLink>
        ))}
      </div>
    </section>
  );
}

export default Home;
