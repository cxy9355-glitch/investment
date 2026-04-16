# 公募持仓与估值筛选看板

这是一个纯静态研究站点，面向 GitHub Pages 发布。页面只依赖当前目录下的 HTML、CSS、JS 和 `data/` JSON 文件，不需要后端服务。

## 页面结构

- `index.html`：主看板，支持在“占总股本比例”和“池内占比”两种口径之间切换，并进行搜索、候选筛选和指标阈值筛选。
- `stock.html?code=600519`：个股详情页，展示单只股票的估值、盈利质量、双口径排名和历史走势。
- `methodology.html`：口径说明、候选规则和当前数据限制。

## 数据来源

站点数据由 `build_dashboard_data.py` 从已验证的研究中间表导出，优先读取：

- `G:\Codex\个人\tmp\fund_analysis`

如果该目录不存在，则回退到仓库内的：

- `investment\tmp\fund_analysis`

## 更新流程

1. 在研究目录中更新基础 CSV。
2. 在当前目录执行：

```powershell
python .\build_dashboard_data.py
```

3. 本地预览：

```powershell
python -m http.server 8123
```

4. 打开 `http://127.0.0.1:8123/index.html` 验证主看板、详情页和方法页。
5. 将 `static/public-fund-dashboard/` 整体发布到 GitHub Pages。

## 发布建议

- GitHub Pages 直接指向 `static/public-fund-dashboard/` 对应目录。
- 若使用仓库根目录发布，确保同步带上 `.nojekyll`。
- 每次重新导出后，重点抽查 `贵州茅台`、`宁德时代`、`中际旭创`、`五粮液` 这类代表性股票在两种口径下是否正常出现。
