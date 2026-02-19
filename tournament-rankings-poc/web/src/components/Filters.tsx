import React from 'react';

interface FiltersProps {
  ageGroups: string[];
  genders: string[];
  divisions: string[];
  selectedAgeGroup: string;
  selectedGender: string;
  selectedDivision: string;
  onAgeGroupChange: (ageGroup: string) => void;
  onGenderChange: (gender: string) => void;
  onDivisionChange: (division: string) => void;
}

export const Filters: React.FC<FiltersProps> = ({
  ageGroups,
  genders,
  divisions,
  selectedAgeGroup,
  selectedGender,
  selectedDivision,
  onAgeGroupChange,
  onGenderChange,
  onDivisionChange,
}) => {
  return (
    <div className="filters">
      <div className="filter-group">
        <label htmlFor="age-filter">Age Group:</label>
        <select
          id="age-filter"
          value={selectedAgeGroup}
          onChange={(e) => onAgeGroupChange(e.target.value)}
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
        <label htmlFor="gender-filter">Gender:</label>
        <select
          id="gender-filter"
          value={selectedGender}
          onChange={(e) => onGenderChange(e.target.value)}
        >
          <option value="all">All</option>
          {genders.map((gender) => (
            <option key={gender} value={gender}>
              {gender}
            </option>
          ))}
        </select>
      </div>

      {divisions.length > 0 && (
        <div className="filter-group">
          <label htmlFor="division-filter">Division:</label>
          <select
            id="division-filter"
            value={selectedDivision}
            onChange={(e) => onDivisionChange(e.target.value)}
          >
            <option value="all">All</option>
            {divisions.map((division) => (
              <option key={division} value={division}>
                {division}
              </option>
            ))}
          </select>
        </div>
      )}
    </div>
  );
};
