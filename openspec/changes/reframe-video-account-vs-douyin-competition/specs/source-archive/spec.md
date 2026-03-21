## ADDED Requirements

### Requirement: Source archive preserves traceability
The research archive SHALL store each selected source as a local PDF or original PDF and SHALL map each file to a title, category, and source URL.

#### Scenario: Analyst audits a cited source
- **WHEN** the analyst needs to verify a cited claim
- **THEN** the archive provides both the local file and the original source reference

### Requirement: Source archive prioritizes high-signal evidence
The research archive SHALL distinguish official company materials, first-party platform materials, industry data, and interpretive analysis.

#### Scenario: Analyst reviews archive quality
- **WHEN** the analyst scans the source manifest
- **THEN** each source is labeled by evidence category rather than treated as equal-quality input

### Requirement: Source archive supports question-led reading
The research archive SHALL provide a recommended reading order that ties sources back to the primary research question and sub-questions.

#### Scenario: Analyst starts from zero
- **WHEN** the analyst opens the source index
- **THEN** the archive shows which sources should be read first and which research questions they inform
