import { loadJson } from "./utils.js";

const nodes = {
  methodUpdatedAt: document.getElementById("methodUpdatedAt"),
  definitionList: document.getElementById("definitionList"),
  candidateRule: document.getElementById("candidateRule"),
  limitationsList: document.getElementById("limitationsList")
};

async function bootstrap() {
  const methodology = await loadJson("./data/metadata/methodology.json");
  nodes.methodUpdatedAt.textContent = `数据更新：${methodology.updatedAt}`;
  nodes.definitionList.innerHTML = methodology.definitions
    .map(
      (item) => `
      <section class="info-card definition-card">
        <p class="eyebrow">${item.label}</p>
        <h2>${item.summary}</h2>
        <p class="hero-copy">${item.detail}</p>
      </section>
    `
    )
    .join("");
  nodes.candidateRule.textContent = methodology.candidateRule;
  nodes.limitationsList.innerHTML = methodology.limitations
    .map((item) => `<li>${item}</li>`)
    .join("");
}

bootstrap().catch((error) => {
  nodes.candidateRule.textContent = `载入失败：${error.message}`;
});
