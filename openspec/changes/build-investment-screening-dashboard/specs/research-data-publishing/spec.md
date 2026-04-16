## ADDED Requirements

### Requirement: Published site data is exported as static artifacts
The system SHALL publish dashboard-ready research data as static artifacts that can be hosted on GitHub Pages without server-side processing.

#### Scenario: Site data is packaged for publishing
- **WHEN** the research workspace prepares a release of the dashboard
- **THEN** it SHALL generate static data artifacts for dashboard rankings, stock detail views, and shared metadata

### Requirement: Dashboard summary data is separated from stock detail data
The system SHALL separate compact ranking payloads from richer per-stock payloads so list views and detail views can load independently.

#### Scenario: Dashboard reads summary data
- **WHEN** the main dashboard loads
- **THEN** it SHALL be able to render from a summary ranking dataset without requiring all per-stock detail payloads

#### Scenario: Stock detail reads focused data
- **WHEN** a stock detail view loads
- **THEN** it SHALL be able to load a stock-specific payload without requiring the full ranked universe payload

### Requirement: Published artifacts include methodology metadata
The system SHALL include metadata that explains available methodologies, definitions, update timing, and dataset limitations.

#### Scenario: Reader inspects methodology information
- **WHEN** the site renders methodology or source information
- **THEN** it SHALL be able to read definitions, update timestamp, and known limitations from published metadata artifacts
