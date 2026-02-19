export function extractAgeFromCategory(categoryName: string): string {
  // Extract age group from category name
  // Examples: "U12/13 GIRLS (9v9)" -> "U12/13", "U9 COPA (7v7)" -> "U9"
  const match = categoryName.match(/U(\d+(?:\/U?\d+)?)/i);
  if (match) {
    return `U${match[1]}`;
  }
  return 'Unknown';
}

export function extractGenderFromCategory(categoryName: string): string {
  // Extract gender from category name
  const upperName = categoryName.toUpperCase();
  
  if (upperName.includes('GIRLS') || upperName.includes('WOMEN')) {
    return 'Girls';
  } else if (upperName.includes('BOYS') || upperName.includes('MEN')) {
    return 'Boys';
  } else if (upperName.includes('MIXED')) {
    return 'Mixed';
  }
  
  return 'Mixed';
}

export function getUniqueAgeGroups(categoryNames: string[]): string[] {
  const ages = new Set<string>();
  categoryNames.forEach((name) => {
    const age = extractAgeFromCategory(name);
    if (age !== 'Unknown') {
      ages.add(age);
    }
  });
  return Array.from(ages).sort((a, b) => {
    // Sort by age number
    const aNum = parseInt(a.match(/\d+/)?.[0] || '0');
    const bNum = parseInt(b.match(/\d+/)?.[0] || '0');
    return aNum - bNum;
  });
}

export function getUniqueGenders(categoryNames: string[]): string[] {
  const genders = new Set<string>();
  categoryNames.forEach((name) => {
    genders.add(extractGenderFromCategory(name));
  });
  return Array.from(genders).sort();
}

export function extractDivisionFromCategory(categoryName: string): string {
  // Extract division from category name (COPA, LIGA, etc.)
  const upperName = categoryName.toUpperCase();
  
  if (upperName.includes('COPA')) {
    return 'COPA';
  } else if (upperName.includes('LIGA')) {
    return 'LIGA';
  }
  
  return 'Other';
}

export function getUniqueDivisions(categoryNames: string[]): string[] {
  const divisions = new Set<string>();
  categoryNames.forEach((name) => {
    const division = extractDivisionFromCategory(name);
    divisions.add(division);
  });
  return Array.from(divisions).sort();
}
