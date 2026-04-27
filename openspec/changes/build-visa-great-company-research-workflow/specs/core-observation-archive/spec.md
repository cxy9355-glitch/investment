## ADDED Requirements

### Requirement: Archive table location
The core observation archive table MUST be stored under `G:\Codex\个人\investment\机构持仓研究`.

#### Scenario: Archive table is easy to find
- **WHEN** the Visa research is completed
- **THEN** the archive table MUST exist in the institutional holding research directory

### Requirement: Archive categories
The archive table MUST support the categories `核心观察样例`, `估值偏贵但核心观察`, `非核心观察`, `暂不归档`, and `反面/退化样例`.

#### Scenario: Visa receives one category
- **WHEN** Visa is added to the archive table
- **THEN** exactly one archive category MUST be assigned from the supported category list

### Requirement: Maintenance fields
The archive table MUST record fields that support later maintenance: company, ticker, market, archive category, valuation state, greatness judgement, identification signals, current action, re-evaluation triggers, latest review date, and linked research document.

#### Scenario: Future opportunity monitoring is possible
- **WHEN** the user revisits the archive table later
- **THEN** the row MUST show what would trigger a re-evaluation of Visa as an investment opportunity

### Requirement: Valuation timestamp
The archive entry MUST record the date of the valuation judgement or latest review so the user can tell when the classification may be stale.

#### Scenario: Valuation may become stale
- **WHEN** valuation changes after the review date
- **THEN** the archive table MUST make the old review date visible for follow-up maintenance

### Requirement: Research document linkage
Each archive row MUST link back to the corresponding full research document.

#### Scenario: Reader wants supporting analysis
- **WHEN** a reader inspects the Visa archive row
- **THEN** the row MUST provide a path or link to the Visa research document that supports the classification
