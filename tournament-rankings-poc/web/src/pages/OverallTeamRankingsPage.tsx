import { useState, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { OverallTeamScore } from '../services/overallAggregationService';
import { extractAgeFromCategory, extractGenderFromCategory, extractDivisionFromCategory, getUniqueAgeGroups, getUniqueGenders, getUniqueDivisions } from '../utils/categoryParser';

interface OverallTeamRankingsPageProps {
  teamScores: OverallTeamScore[];
}

export const OverallTeamRankingsPage = ({ teamScores }: OverallTeamRankingsPageProps) => {
  const navigate = useNavigate();

  const handleGoBack = () => {
    // Check if there's history to go back to
    if (window.history.state && window.history.state.idx > 0) {
      navigate(-1);
    } else {
      // Fallback to home page if no history
      navigate('/');
    }
  };
  // Get unique values for filters
  const categoryNames = teamScores.map(t => t.categoryName);
  const ageGroups = useMemo(() => getUniqueAgeGroups(categoryNames), [categoryNames]);
  const divisions = useMemo(() => getUniqueDivisions(categoryNames), [categoryNames]);
  const genders = useMemo(() => getUniqueGenders(categoryNames), [categoryNames]);

  // Set defaults
  const defaultAge = ageGroups.length > 0 ? ageGroups[0] : 'all';
  const defaultDivision = divisions.includes('COPA') ? 'COPA' : (divisions.length > 0 ? divisions[0] : 'all');

  const [selectedAgeGroup, setSelectedAgeGroup] = useState(defaultAge);
  const [selectedDivision, setSelectedDivision] = useState(defaultDivision);
  const [selectedGender, setSelectedGender] = useState<string>('');

  // Filter teams by age and division
  const filterByAgeAndDivision = (teams: OverallTeamScore[]) => {
    return teams.filter((team) => {
      const age = extractAgeFromCategory(team.categoryName);
      const division = extractDivisionFromCategory(team.categoryName);
      
      const ageMatch = selectedAgeGroup === 'all' || age === selectedAgeGroup;
      const divisionMatch = selectedDivision === 'all' || division === selectedDivision;
      
      return ageMatch && divisionMatch;
    });
  };

  // Separate teams by gender
  const genderSections = useMemo(() => {
    return genders.map(gender => {
      const genderTeams = teamScores.filter((team) => {
        const teamGender = extractGenderFromCategory(team.categoryName);
        return teamGender === gender;
      });
      
      const filteredTeams = filterByAgeAndDivision(genderTeams);
      
      return {
        gender,
        teams: filteredTeams,
        hasResults: filteredTeams.length > 0
      };
    });
  }, [teamScores, selectedAgeGroup, selectedDivision, genders]);

  // Ensure a gender is always selected and division has data
  useMemo(() => {
    const currentSection = genderSections.find(s => s.gender === selectedGender);
    const hasAnyResults = genderSections.some(s => s.hasResults);
    
    // If no results at all with current filters, try to find a division that has data
    if (!hasAnyResults) {
      const divisionsToTry = ['COPA', 'LIGA', 'Other', 'all'];
      for (const div of divisionsToTry) {
        if (div !== selectedDivision && divisions.includes(div)) {
          const testTeams = teamScores.filter((team) => {
            const age = extractAgeFromCategory(team.categoryName);
            const division = extractDivisionFromCategory(team.categoryName);
            const ageMatch = selectedAgeGroup === 'all' || age === selectedAgeGroup;
            const divisionMatch = div === 'all' || division === div;
            return ageMatch && divisionMatch;
          });
          
          if (testTeams.length > 0) {
            setSelectedDivision(div);
            return;
          }
        }
      }
    }
    
    // If no gender selected or current selection has no results, select first available
    if (!selectedGender || !currentSection?.hasResults) {
      const firstWithResults = genderSections.find(s => s.hasResults);
      if (firstWithResults) {
        setSelectedGender(firstWithResults.gender);
      }
    }
  }, [genderSections, selectedGender, selectedDivision, selectedAgeGroup, divisions, teamScores]);

  const currentSection = genderSections.find(s => s.gender === selectedGender);

  return (
    <div className="page-content">
      <button onClick={handleGoBack} className="back-button">
        ← Back
      </button>

      <div className="page-header">
        <h1>Overall Team Rankings</h1>
        <p>Combined scores across all tournaments</p>
      </div>

      <div className="gender-tabs">
        {['Mixed', 'Boys', 'Girls'].map((gender) => {
          const section = genderSections.find(s => s.gender === gender);
          const hasResults = section?.hasResults || false;
          
          return (
            <button
              key={gender}
              className={`gender-tab ${selectedGender === gender ? 'active' : ''} ${!hasResults ? 'disabled' : ''}`}
              onClick={() => hasResults && setSelectedGender(gender)}
              disabled={!hasResults}
            >
              {gender}
            </button>
          );
        })}
      </div>

      <div className="filters-no-gender">
        <div className="filter-group">
          <label htmlFor="age-filter">Age Group:</label>
          <select
            id="age-filter"
            value={selectedAgeGroup}
            onChange={(e) => setSelectedAgeGroup(e.target.value)}
          >
            <option value="all">All Ages</option>
            {ageGroups.map((age) => (
              <option key={age} value={age}>
                {age}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="division-filter">Division:</label>
          <select
            id="division-filter"
            value={selectedDivision}
            onChange={(e) => setSelectedDivision(e.target.value)}
          >
            <option value="all">All</option>
            {divisions.map((division) => (
              <option key={division} value={division}>
                {division}
              </option>
            ))}
          </select>
        </div>
      </div>

      {currentSection && currentSection.hasResults && (
        <div className="rankings-card">
          <div className="card-header">
            <h2>🏆 Top Teams (All Tournaments)</h2>
            <span className="result-count">{currentSection.teams.length} teams</span>
          </div>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Rank</th>
                <th>Team</th>
                <th>Category</th>
                <th>Club</th>
                <th>Tournaments</th>
                <th>Total Points</th>
              </tr>
            </thead>
            <tbody>
              {currentSection.teams.map((team, index) => (
                <tr key={`${team.teamId}-${team.categoryName}`}>
                  <td>
                    <span className={`rank-badge rank-${index + 1}`}>
                      {index + 1}
                    </span>
                  </td>
                  <td className="team-name">
                    <Link to={`/team/${team.teamId}`} className="team-link">
                      {team.teamName}
                    </Link>
                  </td>
                  <td className="category-col">{team.categoryName}</td>
                  <td>{team.clubName}</td>
                  <td className="tournaments-col">
                    <span className="tournament-count">
                      {team.tournaments.length} tournament{team.tournaments.length > 1 ? 's' : ''}
                    </span>
                  </td>
                  <td>
                    <span className="points-badge">{team.totalPoints}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      )}
    </div>
  );
};
