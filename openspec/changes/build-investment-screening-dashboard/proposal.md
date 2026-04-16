## Why

The investment workspace already contains verified public-fund holding and valuation datasets, but the current output is centered on Excel delivery and is cumbersome to browse, filter, and share. A lightweight static dashboard will make the research easier to inspect online and suitable for GitHub Pages publishing without introducing backend complexity.

## What Changes

- Build a static investment screening dashboard optimized for browsing ranked stock lists, switching between holding concentration methodologies, and filtering candidate names quickly.
- Add a stock detail experience that lets readers drill from the dashboard into a single name's key metrics, concentration context, valuation, and research notes.
- Introduce a publishable data packaging flow that exports dashboard-friendly JSON artifacts from the existing research outputs so the site can be hosted on GitHub Pages.
- Add a concise methodology surface that explains metric definitions, ranking logic, and dataset limitations directly in the site.

## Capabilities

### New Capabilities
- `screening-dashboard`: A static dashboard page for ranking, filtering, and comparing stock candidates under multiple holding concentration methodologies.
- `stock-detail-pages`: Shareable stock detail pages that summarize a single name's core metrics, concentration signals, valuation position, and source context.
- `research-data-publishing`: A static data packaging layer that exports site-ready summary and detail datasets, including methodology metadata, from the investment research workspace.

### Modified Capabilities

None.

## Impact

- A new GitHub Pages-friendly static site structure under the investment workspace.
- New exported JSON data artifacts derived from the verified Excel/CSV research outputs.
- New client-side filtering, ranking, and detail-page rendering flows for the dashboard experience.
- Methodology and source explanations surfaced in the published site so readers can understand ranking definitions and limitations.
