import { useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { TournamentResult, ResultRow } from '../types';
import { calculateTeamScores } from '../services/scoringService';
import { aggregateClubScores } from '../services/aggregationService';
import { TeamRankings } from '../components/TeamRankings';
import { ClubRankings } from '../components/ClubRankings';
import { extractAgeFromCategory, extractGenderFromCategory, extractDivisionFromCategory, getUniqueAgeGroups, getUniqueGenders, getUniqueDivisions } from '../utils/categoryParser';

interface TournamentDetailPageProps {
  tournaments: TournamentResult[];
}

export const TournamentDetailPage = ({ tournaments }: TournamentDetailPageProps) => {
  const { tournamentId } = useParams<{ tournamentId: string }>();
  const navigate = useNavigate();

  const handleGoBack = () => {
    // Check if there's history to go back to
    if (window.history.state && window.history.state.idx > 0) {
      navigate(-1);
    } else {
      // Fallback to tournaments page if no history
      navigate('/tournaments');
    }
  };
  
  const tournament = tournaments.find(t => t.tournamentId === tournamentId);

  if (!tournament) {
    return (
      <div className="page-content">
        <div className="page-header">
          <h1>Tournament Not Found</h1>
          <p>The tournament you're looking for doesn't exist.</p>
        </div>
        <button onClick={handleGoBack} className="back-button">
          ← Back
        </button>
      </div>
    );
  }

  // Get unique age groups and divisions
  const categoryNames = tournament.results.map(r => r.categoryName);
  const ageGroups = useMemo(() => getUniqueAgeGroups(categoryNames), [categoryNames]);
  const divisions = useMemo(() => getUniqueDivisions(categoryNames), [categoryNames]);
  const genders = useMemo(() => getUniqueGenders(categoryNames), [categoryNames]);

  // Set defaults: youngest age and COPA division
  const defaultAge = ageGroups.length > 0 ? ageGroups[0] : 'all';
  const defaultDivision = divisions.includes('COPA') ? 'COPA' : (divisions.length > 0 ? divisions[0] : 'all');

  const [selectedAgeGroup, setSelectedAgeGroup] = useState(defaultAge);
  const [selectedDivision, setSelectedDivision] = useState(defaultDivision);
  const [selectedGender, setSelectedGender] = useState<string>('');

  // Helper function to filter by age and division only
  const filterByAgeAndDivision = (results: ResultRow[]) => {
    return results.filter((result: ResultRow) => {
      const age = extractAgeFromCategory(result.categoryName);
      const division = extractDivisionFromCategory(result.categoryName);
      
      const ageMatch = selectedAgeGroup === 'all' || age === selectedAgeGroup;
      const divisionMatch = selectedDivision === 'all' || division === selectedDivision;
      
      return ageMatch && divisionMatch;
    });
  };

  // Separate results by gender
  const genderSections = useMemo(() => {
    return genders.map(gender => {
      const genderResults = tournament.results.filter((result: ResultRow) => {
        const resultGender = extractGenderFromCategory(result.categoryName);
        return resultGender === gender;
      });
      
      const filteredResults = filterByAgeAndDivision(genderResults);
      const teamScores = calculateTeamScores(filteredResults);
      const clubScores = aggregateClubScores(teamScores);
      
      return {
        gender,
        teamScores,
        clubScores,
        hasResults: filteredResults.length > 0
      };
    });
  }, [tournament.results, selectedAgeGroup, selectedDivision, genders]);

  // Ensure a gender is always selected and division has data
  useMemo(() => {
    const currentSection = genderSections.find(s => s.gender === selectedGender);
    const hasAnyResults = genderSections.some(s => s.hasResults);
    
    // If no results at all with current filters, try to find a division that has data
    if (!hasAnyResults) {
      // Try each division to find one with results
      const divisionsToTry = ['COPA', 'LIGA', 'Other', 'all'];
      for (const div of divisionsToTry) {
        if (div !== selectedDivision && divisions.includes(div)) {
          // Check if this division would have results
          const testResults = tournament.results.filter((result: ResultRow) => {
            const age = extractAgeFromCategory(result.categoryName);
            const division = extractDivisionFromCategory(result.categoryName);
            const ageMatch = selectedAgeGroup === 'all' || age === selectedAgeGroup;
            const divisionMatch = div === 'all' || division === div;
            return ageMatch && divisionMatch;
          });
          
          if (testResults.length > 0) {
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
  }, [genderSections, selectedGender, selectedDivision, selectedAgeGroup, divisions, tournament.results]);

  // Get currently selected section
  const currentSection = genderSections.find(s => s.gender === selectedGender);

  return (
    <div className="page-content">
      <button onClick={handleGoBack} className="back-button">
        ← Back
      </button>

      <div className="page-header">
        <h1>{tournament.tournamentName}</h1>
        <p>Season {tournament.season}</p>
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
        <div className="gender-section">
          <div className="rankings-grid">
            <TeamRankings teams={currentSection.teamScores} limit={50} />
            <ClubRankings clubs={currentSection.clubScores} limit={50} />
          </div>
        </div>
      )}
    </div>
  );
};
