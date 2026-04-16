# 投研数据 MCP 安装说明

更新时间：2026-04-16

## 1. 适用范围

这套配置用于 Codex 投研工作流，覆盖：

- `akshare_one`
  - A 股 / 港股 / 中概相关市场数据、新闻、财务报表
- `yahoo_finance`
  - 美股行情、新闻、财务摘要
- `edgartools`
  - SEC / EDGAR 财报、8-K、10-K、10-Q、13F 等
- `jupyter-notebook` skill
  - 后续做数据分析、可视化、因子验证时更方便

## 2. 前置要求

- Windows
- 已安装 `Python 3.11+`
- 已安装 Codex 桌面端
- 默认使用 PowerShell 7：`pwsh`

## 3. 安装命令

先安装 `uv`：

```powershell
python -m pip install --user uv
```

再安装 EdgarTools：

```powershell
python -m pip install --user "edgartools[ai]"
```

如果要补 `jupyter-notebook` skill：

```powershell
python "$env:USERPROFILE\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" --repo openai/skills --path skills/.curated/jupyter-notebook
```

## 4. Codex 配置

编辑 `C:\Users\<你的用户名>\.codex\config.toml`，加入下面三段：

```toml
[mcp_servers.akshare_one]
command = "python"
args = ["-m", "uv", "tool", "run", "--from", "akshare-one-mcp", "akshare-one-mcp"]

[mcp_servers.yahoo_finance]
command = "python"
args = ["-m", "uv", "tool", "run", "--from", "yahoo-finance-server", "yahoo-finance-server"]

[mcp_servers.edgartools]
command = "python"
args = ["-m", "edgar.ai", "--transport", "stdio"]
env = { PYTHONIOENCODING = "utf-8", EDGAR_IDENTITY = "Chuxiaoyu cxy9355@hotmail.com" }
```

说明：

- `EDGAR_IDENTITY` 最好填真实姓名和邮箱，避免 SEC 请求被限流或拒绝。
- `yahoo_finance` 如果所处网络环境访问 Yahoo 不稳定，可以额外在该服务里补代理环境变量。

## 5. 推荐验证方式

安装完成后，先本地验证：

```powershell
python -m uv --version
python -c "import edgar.ai; print('edgar-ok')"
python -m uv tool run --from akshare-one-mcp python -c "import akshare_one_mcp; print('akshare-ok')"
python -m uv tool run --from yahoo-finance-server python -c "import yahoo_finance_server; print('yahoo-ok')"
```

看到 `edgar-ok`、`akshare-ok`、`yahoo-ok` 就说明依赖没问题。

## 6. 生效方式

- 重启 Codex
- 重启后确认 MCP 列表里出现：
  - `akshare_one`
  - `yahoo_finance`
  - `edgartools`

## 7. 常见问题

- `uv` 命令找不到
  - 优先使用 `python -m uv ...`，比直接调用 `uv` 更稳。
- `EdgarTools` 测试时在中文 Windows 控制台报编码错误
  - 一般不影响实际作为 MCP 启动；配置中保留 `PYTHONIOENCODING = "utf-8"` 即可。
- Yahoo Finance 偶发拉取失败
  - 大概率是网络或代理问题，不一定是 MCP 本身故障。

## 8. 后续可选扩展

- `FRED`：做美国宏观、利率、通胀、就业序列
- `mcp-local-rag`：把自己的研报、纪要、PDF 建成本地检索库
- `spreadsheet` skill：做估值表、对比表、批量数据整理
