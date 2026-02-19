import { TournamentResult } from "../models/domain";
import { calculateTeamScores } from "../services/scoringService";
import { aggregateClubScores } from "../services/aggregationService";

const sampleTournament: TournamentResult = {
  tournamentId: "61805002",
  tournamentName: "Shepparton Cup",
  season: "2025",
  results: [
    {
      categoryId: "61805012",
      categoryName: "U11 COPA (9v9)",
      stageType: "CUP_FINAL",
      rank: 1,
      team: {
        teamId: "team001",
        teamName: "Altona North SC U11 COPA",
        clubId: "club001",
        clubName: "Altona North SC",
      },
    },
    {
      categoryId: "61805012",
      categoryName: "U11 COPA (9v9)",
      stageType: "CUP_FINAL",
      rank: 2,
      team: {
        teamId: "team002",
        teamName: "Glen Eira FC U11 COPA",
        clubId: "club002",
        clubName: "Glen Eira FC",
      },
    },
    {
      categoryId: "61805012",
      categoryName: "U11 COPA (9v9)",
      stageType: "CUP_FINAL",
      rank: 3,
      team: {
        teamId: "team003",
        teamName: "Keilor Park SC U11 COPA",
        clubId: "club003",
        clubName: "Keilor Park SC",
      },
    },
    {
      categoryId: "61805012",
      categoryName: "U11 COPA (9v9)",
      stageType: "CUP_FINAL",
      rank: 4,
      team: {
        teamId: "team004",
        teamName: "Brunswick Juventus U11 COPA",
        clubId: "club004",
        clubName: "Brunswick Juventus",
      },
    },
    {
      categoryId: "61805014",
      categoryName: "U12 COPA (9v9)",
      stageType: "CUP_FINAL",
      rank: 1,
      team: {
        teamId: "team005",
        teamName: "Keilor Park SC U12 COPA",
        clubId: "club003",
        clubName: "Keilor Park SC",
      },
    },
    {
      categoryId: "61805014",
      categoryName: "U12 COPA (9v9)",
      stageType: "CUP_FINAL",
      rank: 2,
      team: {
        teamId: "team006",
        teamName: "Altona North SC U12 COPA",
        clubId: "club001",
        clubName: "Altona North SC",
      },
    },
    {
      categoryId: "61805014",
      categoryName: "U12 COPA (9v9)",
      stageType: "CUP_FINAL",
      rank: 3,
      team: {
        teamId: "team007",
        teamName: "Dandenong City U12 COPA",
        clubId: "club005",
        clubName: "Dandenong City",
      },
    },
    {
      categoryId: "61805016",
      categoryName: "U13 BOYS (11v11)",
      stageType: "CUP_FINAL",
      rank: 1,
      team: {
        teamId: "team008",
        teamName: "Altona North SC U13 Boys",
        clubId: "club001",
        clubName: "Altona North SC",
      },
    },
    {
      categoryId: "61805016",
      categoryName: "U13 BOYS (11v11)",
      stageType: "CUP_FINAL",
      rank: 2,
      team: {
        teamId: "team009",
        teamName: "Werribee City FC U13 Boys",
        clubId: "club006",
        clubName: "Werribee City FC",
      },
    },
    {
      categoryId: "61805018",
      categoryName: "U10/11 GIRLS (9v9)",
      stageType: "PLATE_FINAL",
      rank: 1,
      team: {
        teamId: "team010",
        teamName: "Keilor Park SC U10/11 Girls",
        clubId: "club003",
        clubName: "Keilor Park SC",
      },
    },
    {
      categoryId: "61805018",
      categoryName: "U10/11 GIRLS (9v9)",
      stageType: "PLATE_FINAL",
      rank: 2,
      team: {
        teamId: "team011",
        teamName: "Glen Eira FC U10/11 Girls",
        clubId: "club002",
        clubName: "Glen Eira FC",
      },
    },
    {
      categoryId: "61805020",
      categoryName: "U14 BOYS (11v11)",
      stageType: "PLATE_FINAL",
      rank: 1,
      team: {
        teamId: "team012",
        teamName: "Altona North SC U14 Boys",
        clubId: "club001",
        clubName: "Altona North SC",
      },
    },
    {
      categoryId: "61805020",
      categoryName: "U14 BOYS (11v11)",
      stageType: "PLATE_FINAL",
      rank: 2,
      team: {
        teamId: "team013",
        teamName: "Brunswick Juventus U14 Boys",
        clubId: "club004",
        clubName: "Brunswick Juventus",
      },
    },
    {
      categoryId: "61805020",
      categoryName: "U14 BOYS (11v11)",
      stageType: "PLATE_FINAL",
      rank: 3,
      team: {
        teamId: "team014",
        teamName: "Dandenong City U14 Boys",
        clubId: "club005",
        clubName: "Dandenong City",
      },
    },
  ],
};

function printHeader(title: string): void {
  const width = 60;
  console.log("\n" + "═".repeat(width));
  console.log(title.padStart((width + title.length) / 2).padEnd(width));
  console.log("═".repeat(width) + "\n");
}

function printSection(title: string): void {
  console.log(`\n${title}`);
  console.log("─".repeat(60));
}

function padDots(left: string, right: string, width: number = 60): string {
  const dotsNeeded = width - left.length - right.length;
  const dots = ".".repeat(Math.max(dotsNeeded, 1));
  return `${left} ${dots} ${right}`;
}

function runDemo(): void {
  printHeader(`${sampleTournament.tournamentName} ${sampleTournament.season} - RANKINGS`);

  console.log("Tournament ID:", sampleTournament.tournamentId);
  console.log("Season:", sampleTournament.season);
  console.log("Total Results:", sampleTournament.results.length);

  const teamScores = calculateTeamScores(sampleTournament.results);
  const clubScores = aggregateClubScores(teamScores);

  printSection("🏆 TOP TEAMS");
  teamScores.slice(0, 10).forEach((team, index) => {
    const position = `${index + 1}.`;
    const teamInfo = `${team.teamName}`;
    const points = `${team.totalPoints} pts`;
    console.log(padDots(position + " " + teamInfo, points, 58));
  });

  printSection("🏅 TOP CLUBS");
  clubScores.slice(0, 10).forEach((club, index) => {
    const position = `${index + 1}.`;
    const clubInfo = `${club.clubName}`;
    const points = `${club.totalPoints} pts`;
    console.log(padDots(position + " " + clubInfo, points, 58));
  });

  printSection("📊 DETAILED BREAKDOWN");
  console.log("\nClub Performance:");
  clubScores.forEach((club) => {
    const teamsInClub = teamScores.filter((t) => t.clubId === club.clubId);
    console.log(`\n  ${club.clubName} (${club.totalPoints} pts total)`);
    teamsInClub.forEach((team) => {
      console.log(`    - ${team.teamName}: ${team.totalPoints} pts`);
    });
  });

  console.log("\n" + "═".repeat(60));
  console.log("POC Complete - Business Logic Demonstrated");
  console.log("═".repeat(60) + "\n");
}

runDemo();
