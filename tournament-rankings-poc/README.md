# Tournament Rankings POC

A proof-of-concept for calculating team and club rankings based on tournament placements.

## Purpose

This POC demonstrates the core business logic for:
- Calculating points for teams based on tournament placements
- Aggregating team points into club totals
- Producing clean, readable outputs

## Design Decisions

- **Tie-breaking**: Alphabetical order by team/club name
- **Missing data**: Skip entries with missing rank/stageType and log warnings
- **Point precision**: Integer points only
- **Scope**: Single tournament per run

## Project Structure

```
src/
├── models/
│   └── domain.ts           # Type definitions
├── config/
│   └── scoringRules.ts     # Points configuration
├── services/
│   ├── scoringService.ts   # Points calculation
│   └── aggregationService.ts # Club aggregation
└── demo/
    └── runDemo.ts          # Demo runner
```

## Installation

```bash
npm install
```

## Running the Demo

```bash
npm start
```

Or for development with ts-node:

```bash
npm run dev
```

## Extending the POC

The scoring rules are config-driven in `src/config/scoringRules.ts`.
Modify the rules array to change point allocations.

## Future Enhancements (Not in POC)

- Multi-tournament aggregation
- Season-based filtering
- Weighted scoring by age group
- Export to CSV/JSON
- Time-based point decay
