## Context

The investment workspace already has a long-hold institutional holding dataset, quadrant panel, and case judgement fields. The next step is not another screen or ranking table, but a company-first research workflow that starts with business greatness and only then uses institutional holding behavior as a discovery and operation-learning layer.

Visa is the first case because its business model is relatively clean: global payment network, light-asset economics, high capital returns, and a long history of institutional ownership. The user will review the Visa case before the workflow is generalized into a reusable skill.

## Goals / Non-Goals

**Goals:**

- Produce one complete Visa research document in `机构持仓研究`.
- Use a fixed seven-part structure that puts company greatness before institutional behavior.
- Create a maintainable archive table in `机构持仓研究` for the final category and re-evaluation triggers.
- Create an initial global skill only after the Visa workflow has a concrete accepted example.

**Non-Goals:**

- Do not calibrate the template with MCO, AAPL, GOOG, or other companies in this change.
- Do not modify existing Excel workbook schemas or dashboard code.
- Do not turn the archive category into a buy/sell signal. It is a research maintenance classification.
- Do not treat institutional ownership as proof of greatness. It is supporting evidence and operation material.

## Decisions

1. Use one company only for the first workflow pass.

   Rationale: The template is still being shaped by the user's review. Multiple companies would create false precision and make it harder to see whether the structure works.

2. Put the research document and archive table under `机构持仓研究`.

   Rationale: The work belongs to the long-hold institutional research line and should remain close to the current dataset, quadrant notes, and case intake rules.

3. Use Markdown for the first archive table.

   Rationale: A Markdown table is easy to review, diff, and edit while the category system is still changing. It can later be migrated into Excel or a structured dataset if the workflow stabilizes.

4. Create the global skill after the Visa sample is complete.

   Rationale: The skill should encode a proven workflow, not a hypothetical template. Later companies can be used to iterate the skill.

## Risks / Trade-offs

- [Risk] The Visa case may overfit to an unusually clean business model. -> Mitigation: Mark the initial skill as v0.1 and explicitly expect later iteration when applying it to messier companies.
- [Risk] The archive category may be mistaken for a direct trading recommendation. -> Mitigation: Name it as an observation archive category and include valuation state plus re-evaluation triggers.
- [Risk] Valuation data can change quickly. -> Mitigation: Record the review date and valuation source/date in the archive table.
- [Risk] Institutional behavior may dominate the narrative again. -> Mitigation: Require the first four sections to be company-first before any institutional operation review appears.
