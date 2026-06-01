import { Routes, Route, NavLink, useNavigate } from 'react-router-dom';
import Home from './pages/Home.jsx';
import StudyMaterials from './pages/StudyMaterials.jsx';
import MeetInfo from './pages/MeetInfo.jsx';
import Statistics from './pages/Statistics.jsx';
import LeagueInfo from './pages/LeagueInfo.jsx';
import CoachesCorner from './pages/CoachesCorner.jsx';
import Contact from './pages/Contact.jsx';
import AdminDashboard from './pages/AdminDashboard.jsx';
import CoordinatorDashboard from './pages/CoordinatorDashboard.jsx';

const sections = [
  { label: 'Meet Information', path: '/meets' },
  { label: 'Statistics', path: '/statistics' },
  { label: 'Study Materials', path: '/study-materials' },
  { label: 'League Information', path: '/league' },
  { label: "Coaches' Corner", path: '/coaches' },
  { label: 'Contact', path: '/contact' },
  { label: 'Admin', path: '/admin' },
  { label: 'Coordinator', path: '/coordinator' },
];

function App() {
  const navigate = useNavigate();

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <span className="brand">IMLEM</span>
          <p className="tagline">Intermediate Math League of Eastern Massachusetts</p>
        </div>
        <button className="small-button" onClick={() => navigate('/')}>Home</button>
      </header>

      <main>
        <Routes>
          <Route path="/" element={<Home sections={sections} />} />
          <Route path="/study-materials" element={<StudyMaterials />} />
          <Route path="/meets" element={<MeetInfo />} />
          <Route path="/statistics" element={<Statistics />} />
          <Route path="/league" element={<LeagueInfo />} />
          <Route path="/coaches" element={<CoachesCorner />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/coordinator" element={<CoordinatorDashboard />} />
        </Routes>
      </main>

      <footer className="footer">
        <span>IMLEM archive system · clean academic design · historical data preserved</span>
      </footer>
    </div>
  );
}

export default App;
