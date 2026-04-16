## ADDED Requirements

### Requirement: Dashboard supports methodology-aware ranking
The system SHALL provide a primary screening dashboard that ranks stocks under at least two public-fund holding concentration methodologies and makes the active methodology explicit to the reader.

#### Scenario: User switches methodology
- **WHEN** the reader changes the active methodology on the dashboard
- **THEN** the ranking order, methodology-derived values, and methodology label SHALL update together

#### Scenario: Active methodology is visible
- **WHEN** the dashboard is rendered
- **THEN** the page SHALL show which ranking methodology is currently active in plain language

### Requirement: Dashboard supports fast filtering and sorting
The system SHALL allow readers to filter and sort the ranked stock list using compact, investment-relevant controls without requiring a backend service.

#### Scenario: Reader filters the ranked list
- **WHEN** the reader applies one or more filters such as stock search, candidate-only, valuation percentile threshold, profitability threshold, or minimum concentration value
- **THEN** the dashboard SHALL update the visible rows to match the active filter set

#### Scenario: Reader changes sort order
- **WHEN** the reader selects or toggles a supported sort field
- **THEN** the dashboard SHALL reorder the visible rows according to the selected field and direction

### Requirement: Dashboard uses a compact default column set
The system SHALL present a concise default table schema that prioritizes ranking, methodology values, valuation context, candidate status, and recent research freshness.

#### Scenario: Dashboard loads default columns
- **WHEN** the dashboard first renders
- **THEN** the visible table SHALL include ranking identity, current methodology value, cumulative methodology value, valuation indicators, candidate status, and latest report recency fields

#### Scenario: Dashboard remains readable on first view
- **WHEN** the reader lands on the dashboard without expanding additional context
- **THEN** the table SHALL avoid requiring the full research dataset to understand the top-ranked names
