# Match Scores Investigation Report

## Objective
Investigate whether match scores (e.g., Team A 3-2 Team B) can be fetched from the API for finals and semi-finals matches.

## Current Data Structure

### What We Have
The current API response (`sample-results-reponse.json`) contains:
- **Match entities** with metadata (match ID, finished status, duration, etc.)
- **MatchActor entities** with team information (home/away teams)
- **References to MatchResult entities** (as hrefs like `"href": "MatchResult({id:69313228})"`)

### What's Missing
The actual **score data** is NOT included in the current response. The MatchActor entities only contain:
```json
{
  "__typename": "MatchActor",
  "name": { "en": "Ballarat Panthers" },
  "id": 66218044,
  "match": { "href": "Match({id:69315245})" },
  "team": { "href": "Team({id:66218044})" }
}
```

No `score`, `goals`, or `points` fields are present.

## Findings

### 1. Match Result References Exist
- Matches have `result` fields that reference MatchResult entities
- Example: `"result": { "href": "MatchResult({id:69313228})" }`
- These are **not resolved** in the current API response

### 2. Score Data Requires Additional API Calls
To get match scores, we would need to:
1. Parse the MatchResult href references from match entities
2. Make separate API calls to fetch each MatchResult entity
3. Parse the score data from those responses

### 3. API Query Structure
The current query fetches tournament results (rankings/placements) but does NOT include match-level data with scores.

## Feasibility Assessment

### Technical Requirements
To implement match score display:

1. **Update Python Parser** (`fetch-all-tournament-results.py`)
   - Identify finals/semi-finals matches for each category
   - Extract MatchResult IDs from match entities
   - Make additional API calls to fetch MatchResult data
   - Parse score information from MatchResult responses
   - Link scores to teams in the results structure

2. **Update Data Structure**
   - Add match score fields to the JSON output
   - Include opponent information
   - Store match type (Cup Final, Plate Final, Semi-final)

3. **Update Frontend**
   - Modify team detail pages to display match scores
   - Show match results alongside tournament placements
   - Format scores nicely (e.g., "Won 3-2 vs Team B")

### Challenges

1. **API Call Volume**
   - Each tournament has multiple categories
   - Each category has multiple finals/semi-finals matches
   - Could require 50-100+ additional API calls per tournament
   - May hit API rate limits

2. **Data Structure Complexity**
   - Need to understand MatchResult entity structure
   - May need to fetch additional entities (teams, etc.)
   - Complex parsing logic required

3. **Unknown API Response Format**
   - Haven't seen actual MatchResult entity structure
   - Don't know exact field names for scores
   - May require trial and error to get right

### Estimated Effort
- **Parser Updates**: 4-6 hours
- **Data Structure Changes**: 2-3 hours  
- **Frontend Display**: 3-4 hours
- **Testing & Debugging**: 3-5 hours
- **Total**: 12-18 hours of development

## Recommendations

### Option A: Full Implementation
Proceed with fetching match scores if this is a high-priority feature. Would require:
- Testing API calls to understand MatchResult structure
- Significant parser modifications
- Frontend updates to display scores

### Option B: Simplified Alternative
Instead of match scores, show **placement details** which we already have:
- "Cup Final - 1st Place (24 pts)"
- "Plate Final - 2nd Place (16 pts)"
- "Semi-final - 3rd/4th Place (20 pts)"

This provides context about performance without needing match scores.

### Option C: Defer Feature
Focus on other improvements first, revisit match scores later when:
- API structure is better understood
- We have working examples of MatchResult entities
- Time permits for the additional development

## Next Steps

If proceeding with Option A:
1. Create test script to fetch a single MatchResult entity
2. Examine the response structure
3. Document the score field names and format
4. Update parser to fetch scores for finals/semi-finals
5. Update frontend to display match scores

## Conclusion

Match scores ARE potentially available through the API, but require:
- Additional API calls (not included in current query)
- Significant parser modifications
- Unknown API response structure needs investigation
- Estimated 12-18 hours of development time

The feature is **technically feasible** but requires substantial additional work beyond the current implementation.
