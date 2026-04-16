## 1. Data Contract And Export

- [x] 1.1 Define the static JSON contract for dashboard summary rows, stock detail payloads, and shared methodology metadata.
- [x] 1.2 Implement an export step that converts the verified research outputs into ranking datasets for both concentration methodologies.
- [x] 1.3 Implement an export step that writes per-stock detail payloads for the published stock universe.
- [x] 1.4 Generate methodology metadata with definitions, update timestamps, and known dataset limitations.

## 2. Main Dashboard

- [x] 2.1 Create the static dashboard page shell with top-level methodology switching, filter controls, summary cards, and a compact results table.
- [x] 2.2 Load summary ranking datasets on the client and render the default dashboard view from static artifacts only.
- [x] 2.3 Implement client-side search, candidate filtering, valuation threshold filtering, and profitability threshold filtering.
- [x] 2.4 Implement client-side sorting and methodology-aware column value switching without changing the visible table schema.

## 3. Stock Detail And Methodology Views

- [x] 3.1 Create a reusable stock detail page template or route that accepts a stock identifier and loads the matching detail payload.
- [x] 3.2 Render stock snapshot metrics, concentration context, valuation context, profitability context, and candidate rationale on the detail view.
- [x] 3.3 Add methodology and source context surfaces so readers can understand definitions and provenance from the published metadata.

## 4. Publishing And Verification

- [x] 4.1 Wire the exported static artifacts into the site directory structure needed for GitHub Pages publishing.
- [x] 4.2 Verify that dashboard list views load without fetching all per-stock detail payloads.
- [x] 4.3 Verify that representative names such as 贵州茅台、宁德时代、中际旭创, and 五粮液 render correctly under both methodologies.
- [x] 4.4 Document the publish/update workflow so the site can be regenerated from the research workspace without a backend.
