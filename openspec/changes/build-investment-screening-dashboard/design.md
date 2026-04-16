## Context

The investment workspace already contains manually verified Excel and CSV outputs for public-fund holding rankings, valuation percentiles, and shortlist logic. The current delivery format is spreadsheet-first, which is effective for analysis but awkward for interactive browsing, filtering, and public sharing.

The desired experience is a lightweight static dashboard that can be published to GitHub Pages, with a strong bias toward speed and low maintenance:

- no backend service
- no runtime data processing beyond client-side filtering and sorting
- easy sharing of a single stock page by URL
- explicit support for multiple ranking methodologies, especially:
  - holding depth relative to a stock's total shares
  - concentration inside the total public-fund holding pool

## Goals / Non-Goals

**Goals:**
- Provide a single primary dashboard page that supports methodology switching, sorting, and fast filtering.
- Provide shareable stock detail pages with concise metrics, context, and source links.
- Export site-ready static JSON artifacts from the research workspace so the site can be regenerated from verified outputs.
- Keep the initial architecture simple enough for GitHub Pages hosting and incremental maintenance.

**Non-Goals:**
- Building a backend API, database, or authentication layer.
- Supporting intraday data refresh or live market feeds.
- Replacing the research spreadsheets as the source-of-truth workflow.
- Building a full CMS or article publishing system in this change.

## Decisions

### 1. Use a static-site architecture with precomputed JSON artifacts

The site will be generated from existing verified research outputs into lightweight JSON bundles committed with the site. The browser will only read and render these artifacts.

Why this approach:
- matches GitHub Pages constraints
- avoids introducing server infrastructure
- keeps methodology reproducible from the research workspace
- makes debugging easier because published data is explicit

Alternative considered:
- generating the UI directly from Excel files in the browser
  - rejected because payloads are heavy, parsing is brittle, and field evolution becomes harder to manage

### 2. Split dashboard ranking data from stock detail data

The site data model will be separated into:
- summary ranking datasets for the dashboard
- per-stock detail datasets for stock pages
- shared metadata for methodology definitions and update timestamps

Why this approach:
- the dashboard only needs compact sortable/filterable rows
- stock pages can load richer time-series and notes on demand
- avoids forcing every page to download the full research payload

Alternative considered:
- one monolithic dataset for all views
  - rejected because it increases page weight and tightly couples list and detail views

### 3. Normalize dashboard columns across methodologies

The dashboard will keep the same user-facing columns regardless of methodology, while switching the underlying values. For example, users will see:
- current methodology value
- cumulative methodology value
- average methodology value
- peak methodology value

Why this approach:
- users can switch methodology without relearning the table
- simplifies rendering logic and filtering behavior
- reduces terminology clutter in the primary interface

Alternative considered:
- separate table schemas for each methodology
  - rejected because it makes comparison harder and increases UI complexity

### 4. Make methodology switching a first-class control

The dashboard will expose methodology switching at the top of the page and treat it as the main context selector for the whole table.

Why this approach:
- ranking differences are material and can radically reorder the results
- readers need immediate clarity about what the current list means
- this addresses the exact interpretability problem discovered during exploration

Alternative considered:
- placing methodology inside advanced filters
  - rejected because it hides the most important contextual control

### 5. Scope the MVP to three page types

The MVP will include:
- main dashboard page
- stock detail page template
- methodology page

Why this approach:
- enough structure to be useful and shareable
- still small enough to implement and maintain quickly
- leaves room to add thematic research landing pages later without blocking launch

Alternative considered:
- a richer multi-section portal homepage
  - rejected for MVP because it adds navigation and content overhead before the data workflows are proven

## Risks / Trade-offs

- [Static data can become stale] -> Mitigation: surface update timestamps and make methodology/source metadata visible on the site.
- [Multiple methodologies can confuse readers] -> Mitigation: keep methodology switching explicit and provide short plain-language definitions near the control.
- [Too many columns can overwhelm the dashboard] -> Mitigation: keep a narrow default column set and push richer context into stock detail pages.
- [Data export logic may drift from spreadsheet logic] -> Mitigation: treat exported JSON as a derived artifact from verified research tables, not an independent calculation workflow.
- [Per-stock detail pages increase artifact count] -> Mitigation: use a predictable `stocks/<code>.json` structure and a single reusable page template.

## Migration Plan

1. Stabilize the site data contract for dashboard rows, stock detail payloads, and methodology metadata.
2. Export static JSON bundles from the current research outputs.
3. Build the dashboard page against the summary datasets.
4. Add stock detail routing/template behavior against per-stock payloads.
5. Publish the static site to GitHub Pages.
6. Keep the existing spreadsheet outputs in place during rollout as the verification fallback.

Rollback strategy:
- if the site is incomplete or misleading, keep publishing only the spreadsheet outputs and remove the static dashboard from the public entry point

## Open Questions

- Whether stock detail pages should be standalone HTML files or one template driven by query parameters/hash routing.
- Whether the main dashboard should expose advanced filters by default or behind a collapsible panel.
- Whether the first public release should support downloading the current table view as CSV from the browser.
