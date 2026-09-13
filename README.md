# 江门家居 GEO / AI 搜索可见性基准

这是一个可复用的 GEO（生成式引擎优化）研究项目，用于测试品牌在 AI 搜索回答中的自然提及、正式推荐、推荐位次、平台覆盖和证据质量。

仓库同时包含：

- 可直接交给 Codex 使用的 `geo-ai-visibility-baseline` Skill；
- 完整的测试、留证、纠错、分析和交付流程；
- 2026-07-29 江门家居、装修及全屋定制市场基线数据；
- Word、Excel、PDF、图表及可追溯的原始回答。

“推荐位次”仅表示某次 AI 测试回答中的输出顺序，不代表官方市场排名。

## 下载与本地使用

任何人都可以下载这个公开仓库，并在自己的电脑中修改副本：

1. 在 GitHub 页面选择 **Code → Download ZIP**，或使用[一键下载 ZIP](https://github.com/dadiaoliyaqiao-max/geo-ai-jiangmen-benchmark/archive/refs/heads/main.zip)。
2. 也可以通过 Git 克隆：

   ```bash
   git clone https://github.com/dadiaoliyaqiao-max/geo-ai-jiangmen-benchmark.git
   cd geo-ai-jiangmen-benchmark
   ```

3. 安装并登录 Codex，在 Codex 中打开仓库根目录。
4. 让 Codex 先读取 `README.md`、`HANDOFF.md` 和 `AGENTS.md`。
5. 在豆包、腾讯元宝、DeepSeek 等网页端分别登录自己的账号；不要复制他人的 Cookie 或浏览器配置。

如需把工作流安装成个人 Skill，可在仓库根目录运行：

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
Copy-Item -Recurse ".\skills\geo-ai-visibility-baseline" "$env:USERPROFILE\.codex\skills\"
```

重新打开 Codex 后，可以直接说：

```text
使用 $geo-ai-visibility-baseline，为我的目标品牌执行一次可追溯的 AI 搜索可见性基线测试。
```

## 可复用工作流

核心入口位于 `skills/geo-ai-visibility-baseline/`：

- `SKILL.md`：任务边界、平台预检、独立提问、恢复和交付要求；
- `references/platform-runbook.md`：豆包、腾讯元宝、DeepSeek 的执行与异常处理；
- `references/run-layout-and-schema.md`：问题库、原始记录和纠错清单结构；
- `references/analysis-and-deliverables.md`：提及、推荐、位次、证据和报告口径；
- `scripts/init_run.py`：初始化新的日期批次；
- `scripts/audit_run.py`：审计问题完整性、原始回答和截图；
- `scripts/summarize_records.py`：汇总目标品牌与竞品的核心指标。

完整的人工作业说明见 [`docs/WORKFLOW.md`](docs/WORKFLOW.md)。

同事可以在自己的本地副本中自由新增、删除、改写或重排搜索问题，并以新的日期批次执行。每轮测试开始前应先确认问题库；开始采集后应固定该版本，避免中途改题导致不同平台结果不可比较。

在任意项目中，`target_recommended` 表示“本次目标品牌是否进入正式推荐或候选名单”。当目标品牌设置为健威家居时，它就是“是否推荐健威家居”。单纯提到品牌但未将其列入推荐名单，只计为提及。

## 2026-07-29 基线

- 测试平台：豆包、DeepSeek、腾讯元宝、文心一言、千问；
- 独立问题：36 个；
- 原始测试：180 次；
- 推荐记录：757 条；
- 标准化品牌：105 个；
- 去重引用链接：202 个；
- 三平台重点复盘：豆包、DeepSeek、腾讯元宝，共 108 次测试、465 条推荐记录。

主要成果：

- `outputs/geo_ai_jiangmen_20260729/江门全屋定制、装修与全屋设计AI搜索基准报告.docx`
- `outputs/geo_ai_jiangmen_20260729/江门AI搜索可见性测试明细_180题.xlsx`
- `outputs/geo_ai_jiangmen_20260729/report_render/江门全屋定制、装修与全屋设计AI搜索基准报告.pdf`

## 目录

- `skills/`：可复用的 Codex Skill。
- `docs/`：面向使用者的完整流程说明。
- `work/raw/`：平台原始回答，不得覆盖或静默修改。
- `work/analysis/`：品牌标准化、链接核验、统计和汇总数据。
- `work/scripts/`：数据构建、核验、统计与审计脚本。
- `work/build/`：报告和工作簿生成脚本。
- `outputs/`：最终报告、工作簿、PDF和预览。
- `HANDOFF.md`：跨电脑或新任务交接说明。
- `AGENTS.md`：Codex 在本项目中必须遵守的规则。

## 权限与安全

公开访客可以查看、克隆、下载和 Fork，也可以在自己的本地副本中编辑；他们不能直接修改本仓库或向 `main` 分支推送。只有仓库所有者明确授予写权限的账号才能修改原仓库。别人提交 Pull Request 时，是否合并仍由仓库所有者决定。

仓库不应包含密码、Cookie、令牌、浏览器用户目录、`.env` 或个人登录配置。新的复测数据必须放入新的日期目录，不能覆盖已有基线；公开前应再次检查数据是否适合对外发布。

## 许可

本仓库采用 [MIT License](LICENSE)。下载者可以复制和修改本地副本，但需保留许可证中的版权与许可声明。
