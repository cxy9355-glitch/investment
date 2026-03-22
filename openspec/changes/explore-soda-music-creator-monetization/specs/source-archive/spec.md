## ADDED Requirements

### Requirement: Source archive preserves readable local copies
The research archive SHALL store each selected source as a local readable note in Markdown and SHALL map each note to a title, source URL, evidence grade, and relevant research question.

#### Scenario: Analyst audits a citation
- **WHEN** the analyst needs to verify a claim
- **THEN** the archive provides a local readable note and the original source reference

### Requirement: Source archive distinguishes evidence quality
The research archive SHALL label official platform material, reputable media/industry reporting, and anecdotal creator feedback separately.

#### Scenario: Analyst reviews archive quality
- **WHEN** the analyst scans the source index
- **THEN** each source is labeled by evidence grade and source type rather than treated as equal-quality input
