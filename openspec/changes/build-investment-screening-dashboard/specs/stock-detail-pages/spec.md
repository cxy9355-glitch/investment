## ADDED Requirements

### Requirement: Each ranked stock has a shareable detail view
The system SHALL provide a shareable detail page or route for each stock included in the published dashboard datasets.

#### Scenario: Reader opens a stock detail view
- **WHEN** the reader selects a stock from the dashboard
- **THEN** the site SHALL open a dedicated detail view for that stock using a stable, shareable URL or route

### Requirement: Detail view summarizes the stock with concise research context
The system SHALL present each stock with a compact summary of concentration metrics, valuation position, profitability indicators, and research context.

#### Scenario: Detail page shows stock snapshot
- **WHEN** a stock detail view loads successfully
- **THEN** the page SHALL show the stock identity, current methodology value, cumulative methodology value, valuation metrics, profitability metrics, and latest reporting context

#### Scenario: Detail page explains why the stock stands out
- **WHEN** a stock detail view is rendered
- **THEN** the page SHALL include candidate rationale or summary notes that help the reader understand why the stock is notable under the current research workflow

### Requirement: Detail view exposes methodology and source context
The system SHALL make it possible for readers to inspect the methodology meaning and source provenance for the displayed stock data.

#### Scenario: Reader checks source context
- **WHEN** the reader inspects a stock detail page
- **THEN** the page SHALL provide methodology context and source references or links for the underlying research outputs
