import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { TournamentResult } from '../types';

interface TournamentConfig {
  tournamentId: string;
  tier: 1 | 2 | 3;
}

interface LevelPoints {
  winner: number;
  runnerUp: number;
  semiFinal: number;
}

interface PointsConfig {
  tier1: LevelPoints;
  tier2: LevelPoints;
  tier3: LevelPoints;
  levelMultipliers: {
    COPA: number;
    LIGA: number;
    Other: number;
  };
}

interface AdminPageProps {
  tournaments: TournamentResult[];
}

const DEFAULT_POINTS_CONFIG: PointsConfig = {
  tier1: { winner: 100, runnerUp: 75, semiFinal: 50 },
  tier2: { winner: 75, runnerUp: 50, semiFinal: 35 },
  tier3: { winner: 50, runnerUp: 35, semiFinal: 25 },
  levelMultipliers: {
    COPA: 1.0,
    LIGA: 0.8,
    Other: 0.6
  }
};

export function AdminPage({ tournaments }: AdminPageProps) {
  const navigate = useNavigate();
  const [tournamentConfigs, setTournamentConfigs] = useState<TournamentConfig[]>([]);
  const [pointsConfig, setPointsConfig] = useState<PointsConfig>(DEFAULT_POINTS_CONFIG);
  const [saveMessage, setSaveMessage] = useState<string>('');

  useEffect(() => {
    // Load saved configurations from localStorage
    const savedTournamentConfigs = localStorage.getItem('tournamentConfigs');
    const savedPointsConfig = localStorage.getItem('pointsConfig');

    if (savedTournamentConfigs) {
      setTournamentConfigs(JSON.parse(savedTournamentConfigs));
    } else {
      // Initialize with default tier 1 for all tournaments
      const defaultConfigs = tournaments.map(t => ({
        tournamentId: t.tournamentId,
        tier: 1 as 1 | 2 | 3
      }));
      setTournamentConfigs(defaultConfigs);
    }

    if (savedPointsConfig) {
      setPointsConfig(JSON.parse(savedPointsConfig));
    }
  }, [tournaments]);

  const handleGoBack = () => {
    if (window.history.state && window.history.state.idx > 0) {
      navigate(-1);
    } else {
      navigate('/');
    }
  };

  const handleTierChange = (tournamentId: string, tier: 1 | 2 | 3) => {
    setTournamentConfigs(prev => {
      const existing = prev.find(c => c.tournamentId === tournamentId);
      if (existing) {
        return prev.map(c => 
          c.tournamentId === tournamentId ? { ...c, tier } : c
        );
      } else {
        return [...prev, { tournamentId, tier }];
      }
    });
  };

  const handlePointsChange = (
    tier: 'tier1' | 'tier2' | 'tier3',
    position: 'winner' | 'runnerUp' | 'semiFinal',
    value: string
  ) => {
    const numValue = parseInt(value) || 0;
    setPointsConfig(prev => ({
      ...prev,
      [tier]: {
        ...prev[tier],
        [position]: numValue
      }
    }));
  };

  const handleLevelMultiplierChange = (
    level: 'COPA' | 'LIGA' | 'Other',
    value: string
  ) => {
    const numValue = parseFloat(value) || 0;
    setPointsConfig(prev => ({
      ...prev,
      levelMultipliers: {
        ...prev.levelMultipliers,
        [level]: numValue
      }
    }));
  };

  const handleSave = () => {
    localStorage.setItem('tournamentConfigs', JSON.stringify(tournamentConfigs));
    localStorage.setItem('pointsConfig', JSON.stringify(pointsConfig));
    setSaveMessage('Configuration saved successfully!');
    setTimeout(() => setSaveMessage(''), 3000);
  };

  const handleReset = () => {
    if (window.confirm('Are you sure you want to reset all configurations to defaults?')) {
      const defaultConfigs = tournaments.map(t => ({
        tournamentId: t.tournamentId,
        tier: 1 as 1 | 2 | 3
      }));
      setTournamentConfigs(defaultConfigs);
      setPointsConfig(DEFAULT_POINTS_CONFIG);
      localStorage.removeItem('tournamentConfigs');
      localStorage.removeItem('pointsConfig');
      setSaveMessage('Configuration reset to defaults!');
      setTimeout(() => setSaveMessage(''), 3000);
    }
  };

  const getTournamentTier = (tournamentId: string): 1 | 2 | 3 => {
    const config = tournamentConfigs.find(c => c.tournamentId === tournamentId);
    return config?.tier || 1;
  };

  return (
    <div className="admin-page">
      <button onClick={handleGoBack} className="back-button">
        ← Back
      </button>

      <div className="page-header">
        <h1>Admin Portal - Points Configuration</h1>
        <p className="subtitle">Configure tournament tiers and points allocation</p>
      </div>

      {saveMessage && (
        <div className="save-message">
          {saveMessage}
        </div>
      )}

      <div className="admin-sections">
        {/* Tournament Tier Assignment */}
        <section className="admin-section">
          <h2>Tournament Tier Assignment</h2>
          <p className="section-description">
            Assign each tournament a tier (1 = highest prestige, 3 = lowest prestige)
          </p>
          
          <div className="tournament-tier-list">
            {tournaments.map(tournament => (
              <div key={tournament.tournamentId} className="tournament-tier-item">
                <div className="tournament-info">
                  <span className="tournament-name">{tournament.tournamentName}</span>
                  <span className="tournament-season">{tournament.season}</span>
                </div>
                <div className="tier-selector">
                  <label>Tier:</label>
                  <select
                    value={getTournamentTier(tournament.tournamentId)}
                    onChange={(e) => handleTierChange(tournament.tournamentId, parseInt(e.target.value) as 1 | 2 | 3)}
                  >
                    <option value={1}>Tier 1</option>
                    <option value={2}>Tier 2</option>
                    <option value={3}>Tier 3</option>
                  </select>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Points Configuration by Tier */}
        <section className="admin-section">
          <h2>Points by Tier & Position</h2>
          <p className="section-description">
            Configure base points for each tournament tier and finishing position
          </p>

          <div className="points-grid">
            {(['tier1', 'tier2', 'tier3'] as const).map(tier => (
              <div key={tier} className="tier-points-card">
                <h3>Tier {tier.slice(-1)}</h3>
                <div className="points-inputs">
                  <div className="points-input-group">
                    <label>Winner Points:</label>
                    <input
                      type="number"
                      min="0"
                      value={pointsConfig[tier].winner}
                      onChange={(e) => handlePointsChange(tier, 'winner', e.target.value)}
                    />
                  </div>
                  <div className="points-input-group">
                    <label>Runner-up Points:</label>
                    <input
                      type="number"
                      min="0"
                      value={pointsConfig[tier].runnerUp}
                      onChange={(e) => handlePointsChange(tier, 'runnerUp', e.target.value)}
                    />
                  </div>
                  <div className="points-input-group">
                    <label>Semi-finalist Points:</label>
                    <input
                      type="number"
                      min="0"
                      value={pointsConfig[tier].semiFinal}
                      onChange={(e) => handlePointsChange(tier, 'semiFinal', e.target.value)}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Level Multipliers */}
        <section className="admin-section">
          <h2>Level Multipliers</h2>
          <p className="section-description">
            Configure point multipliers for different competition levels (COPA, LIGA, Other)
          </p>

          <div className="multipliers-grid">
            {(['COPA', 'LIGA', 'Other'] as const).map(level => (
              <div key={level} className="multiplier-card">
                <label>{level} Multiplier:</label>
                <input
                  type="number"
                  min="0"
                  max="2"
                  step="0.1"
                  value={pointsConfig.levelMultipliers[level]}
                  onChange={(e) => handleLevelMultiplierChange(level, e.target.value)}
                />
                <span className="multiplier-hint">
                  (e.g., 1.0 = 100%, 0.8 = 80%)
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* Example Calculations */}
        <section className="admin-section">
          <h2>Example Point Calculations</h2>
          <p className="section-description">
            See how points are calculated with current configuration
          </p>

          <div className="examples-grid">
            <div className="example-card">
              <h4>Tier 1 Tournament - COPA Winner</h4>
              <div className="calculation">
                Base: {pointsConfig.tier1.winner} × COPA Multiplier: {pointsConfig.levelMultipliers.COPA}
                <br />
                <strong>= {Math.round(pointsConfig.tier1.winner * pointsConfig.levelMultipliers.COPA)} points</strong>
              </div>
            </div>
            <div className="example-card">
              <h4>Tier 2 Tournament - LIGA Runner-up</h4>
              <div className="calculation">
                Base: {pointsConfig.tier2.runnerUp} × LIGA Multiplier: {pointsConfig.levelMultipliers.LIGA}
                <br />
                <strong>= {Math.round(pointsConfig.tier2.runnerUp * pointsConfig.levelMultipliers.LIGA)} points</strong>
              </div>
            </div>
            <div className="example-card">
              <h4>Tier 3 Tournament - Other Semi-finalist</h4>
              <div className="calculation">
                Base: {pointsConfig.tier3.semiFinal} × Other Multiplier: {pointsConfig.levelMultipliers.Other}
                <br />
                <strong>= {Math.round(pointsConfig.tier3.semiFinal * pointsConfig.levelMultipliers.Other)} points</strong>
              </div>
            </div>
          </div>
        </section>
      </div>

      <div className="admin-actions">
        <button onClick={handleSave} className="save-button">
          Save Configuration
        </button>
        <button onClick={handleReset} className="reset-button">
          Reset to Defaults
        </button>
      </div>
    </div>
  );
}
