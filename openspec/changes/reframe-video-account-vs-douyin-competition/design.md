## Context

We already collected a first-wave archive of Tencent official materials, WeChat/Video Accounts commentary, industry reports, and Douyin-side platform materials under `video-account-vs-douyin-research/`. That solved the sourcing problem, but not the synthesis problem: the current package does not yet force the research to answer a disciplined question, separate signal from narrative, or state what evidence would strengthen or weaken the thesis.

The change therefore focuses on the research operating model rather than on adding more articles. The goal is to make the next discussion phase evidence-led, falsifiable, and easy to iterate.

## Goals / Non-Goals

**Goals:**
- Create a single research frame that starts from first principles rather than from news chronology.
- Define how the archive maps to thesis questions and how new evidence should update confidence.
- Standardize the comparison framework so Video Accounts and Douyin are evaluated at the ecosystem level, not just by isolated metrics.
- Produce implementation-ready artifacts for the next stage of analysis.

**Non-Goals:**
- Exhaustively collect every public article about Video Accounts or Douyin.
- Build a financial model, valuation model, or final investment recommendation in this change.
- Resolve all missing data gaps from ByteDance first-party disclosure.

## Decisions

### 1. Use a question tree instead of a topic dump

The research will be organized around one primary question: whether Video Accounts is becoming Tencent's next major traffic and transaction entry point in a way that can materially challenge Douyin's role. Sub-questions will cover product purpose, strategic role, competitive boundary, ecosystem leverage, monetization, and AI/search implications.

Alternative considered:
- Organize by article source type alone. Rejected because it helps filing, but not thinking.

### 2. Separate evidence collection from thesis synthesis

The archived PDFs and `sources.csv` will serve as the evidence layer. The thesis memo and competition map will sit on top as synthesis layers. This separation makes it easier to update conclusions without losing source traceability.

Alternative considered:
- Write one long essay that blends quotes, evidence, and conclusions. Rejected because it is harder to revise and easier to overfit to narrative.

### 3. Compare the platforms as systems, not just apps

The comparison framework will cover six dimensions: strategic role, distribution mechanism, creator supply, monetization/transactions, ecosystem integration, and AI/search extension. This reflects the fact that Video Accounts is embedded in WeChat, while Douyin is a self-contained algorithmic platform that extends into ads, ecommerce, and search.

Alternative considered:
- Compare only DAU, GMV, ad revenue, and creator metrics. Rejected because metrics describe outcomes, not underlying mechanisms.

### 4. Make the thesis falsifiable

Each major claim will be expressed as a hypothesis with evidence that can strengthen or weaken confidence. This is especially important because Tencent and ByteDance disclose uneven amounts of first-party data.

Alternative considered:
- Use directional narrative only. Rejected because it encourages confirmation bias.

## Risks / Trade-offs

- [Uneven first-party disclosure] -> Mitigation: label sources by evidence quality and separate official, industry, and analytical interpretations.
- [Narrative overreach from limited data] -> Mitigation: require each thesis claim to name disconfirming evidence and unresolved questions.
- [Research scope keeps expanding] -> Mitigation: lock the framework to six comparison dimensions and a defined reading order before adding more material.
- [Video Accounts is misread as a standalone app] -> Mitigation: require every major conclusion to state the role of WeChat ecosystem integration.

## Migration Plan

1. Preserve the current archived PDFs and source manifest as the raw evidence layer.
2. Add annotations that map each source to one or more thesis questions.
3. Build the competition map and thesis memo on top of the existing archive instead of rebuilding the folder.
4. Iterate by adding missing high-value sources only when they answer a currently open question.

## Open Questions

- Which Tencent statements most directly indicate Video Accounts' internal strategic priority versus external market perception?
- What is the best available evidence for Douyin's role as a search and transaction entry point beyond marketing language?
- Which disconfirming signals would most strongly weaken the thesis that Video Accounts can become Tencent's next major distribution layer?
