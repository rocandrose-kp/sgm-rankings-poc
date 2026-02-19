import { Link, useLocation } from 'react-router-dom';

export const Navigation = () => {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <nav className="navigation">
      <div className="nav-container">
        <div className="nav-brand">
          <h2>🏆 Tournament Rankings</h2>
        </div>
        <ul className="nav-menu">
          <li>
            <Link to="/" className={isActive('/')}>
              Home
            </Link>
          </li>
          <li>
            <Link to="/tournaments" className={isActive('/tournaments')}>
              Tournaments
            </Link>
          </li>
          <li className="nav-divider"></li>
          <li>
            <Link to="/overall-teams" className={isActive('/overall-teams')}>
              Overall Teams
            </Link>
          </li>
          <li>
            <Link to="/overall-clubs" className={isActive('/overall-clubs')}>
              Overall Clubs
            </Link>
          </li>
          <li className="nav-divider"></li>
          <li>
            <Link to="/scoring" className={isActive('/scoring')}>
              Scoring
            </Link>
          </li>
          <li>
            <Link to="/admin" className={isActive('/admin')}>
              Admin
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  );
};
