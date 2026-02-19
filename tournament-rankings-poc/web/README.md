# Tournament Rankings Web Frontend

A modern, responsive web interface for displaying tournament rankings and club scores.

## Features

- 🏆 Team rankings with detailed information
- 🏅 Club rankings with aggregated scores
- 📊 Detailed club breakdown showing all teams
- 📱 Fully responsive design
- 🎨 Modern, professional UI with gradient styling

## Technology Stack

- React 18
- TypeScript
- Vite (build tool)
- CSS3 (no external UI libraries)

## Installation

```bash
npm install
```

## Development

```bash
npm run dev
```

This will start the development server at `http://localhost:3000`

## Build

```bash
npm run build
```

## Preview Production Build

```bash
npm run preview
```

## Project Structure

```
src/
├── components/          # React components
│   ├── TournamentHeader.tsx
│   ├── TeamRankings.tsx
│   ├── ClubRankings.tsx
│   └── ClubBreakdown.tsx
├── services/           # Business logic
│   ├── scoringService.ts
│   ├── aggregationService.ts
│   └── scoringRules.ts
├── data/              # Sample data
│   └── sampleData.ts
├── types.ts           # TypeScript types
├── App.tsx            # Main app component
├── App.css            # Styles
└── main.tsx           # Entry point
```

## Features Demonstrated

- Config-driven scoring rules
- Team and club aggregation
- Responsive table layouts
- Modern card-based UI
- Gradient styling and animations
- Mobile-friendly design
