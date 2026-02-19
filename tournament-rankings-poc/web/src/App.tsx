import { useMemo } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Navigation } from './components/Navigation';
import { HomePage } from './pages/HomePage';
import { OverallTeamRankingsPage } from './pages/OverallTeamRankingsPage';
import { OverallClubRankingsPage } from './pages/OverallClubRankingsPage';
import { TeamDetailPage } from './pages/TeamDetailPage';
import { ClubDetailPage } from './pages/ClubDetailPage';
import { TournamentsPage } from './pages/TournamentsPage';
import { TournamentDetailPage } from './pages/TournamentDetailPage';
import { ScoringPage } from './pages/ScoringPage';
import { AdminPage } from './pages/AdminPage';
import { calculateOverallTeamScores, calculateOverallClubScores } from './services/overallAggregationService';
import { TournamentResult } from './types';
import realDataJson from './data/realData.json';
import './App.css';

function App() {
  const tournaments = realDataJson as TournamentResult[];
  
  // Calculate overall scores across all tournaments
  const overallTeamScores = useMemo(() => calculateOverallTeamScores(tournaments), [tournaments]);
  const overallClubScores = useMemo(() => calculateOverallClubScores(tournaments), [tournaments]);

  return (
    <BrowserRouter basename="/sgm-rankings-poc">
      <div className="app">
        <Navigation />
        <div className="container">
          <Routes>
            <Route 
              path="/" 
              element={<HomePage />} 
            />
            <Route 
              path="/overall-teams" 
              element={
                <OverallTeamRankingsPage 
                  teamScores={overallTeamScores}
                />
              } 
            />
            <Route 
              path="/overall-clubs" 
              element={
                <OverallClubRankingsPage 
                  clubScores={overallClubScores}
                />
              } 
            />
            <Route 
              path="/team/:teamId" 
              element={
                <TeamDetailPage 
                  tournaments={tournaments}
                />
              } 
            />
            <Route 
              path="/club/:clubId" 
              element={
                <ClubDetailPage 
                  tournaments={tournaments}
                />
              } 
            />
            <Route 
              path="/tournaments" 
              element={
                <TournamentsPage 
                  tournaments={tournaments}
                />
              } 
            />
            <Route 
              path="/tournament/:tournamentId" 
              element={
                <TournamentDetailPage 
                  tournaments={tournaments}
                />
              } 
            />
            <Route 
              path="/scoring" 
              element={<ScoringPage />} 
            />
            <Route 
              path="/admin" 
              element={
                <AdminPage 
                  tournaments={tournaments}
                />
              } 
            />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
