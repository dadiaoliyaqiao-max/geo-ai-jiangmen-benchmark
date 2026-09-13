# GEO / AI 搜索可见性完整工作流程

本文面向需要复用该项目的同事。自动执行规则以 `skills/geo-ai-visibility-baseline/SKILL.md` 为准；本文解释如何从零开始组织一次可追溯测试。

## 1. 明确测试合同

开始前固定以下内容：

- 目标品牌及所有可接受别名；
- 测试平台；
- 原样保留的问题库、主题和意图标签；
- 测试日期、时区和输出目录；
- 提及、正式推荐、位次、TOP1、TOP3、强推荐及楼盘案例的定义；
- 是否需要截图、Excel、Markdown报告和来源核验。

不得为了提高目标品牌表现而在问题中加入品牌名、优势暗示或纠正性追问。

## 2. 安装并调用 Skill

把 `skills/geo-ai-visibility-baseline/` 复制到个人 Codex Skill 目录：

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
Copy-Item -Recurse ".\skills\geo-ai-visibility-baseline" "$env:USERPROFILE\.codex\skills\"
```

重新打开 Codex 后，用 `$geo-ai-visibility-baseline` 调用。也可以直接在 Codex 中打开本仓库，让它读取 Skill 文件和项目规则。

## 3. 准备问题库和日期批次

问题库使用 JSON 数组，每题至少包含：

```json
{
  "question_id": "Q01",
  "question_number": 1,
  "theme": "江门全屋定制",
  "intent_code": "A",
  "intent_name": "直接推荐型",
  "question": "原样提交给平台的问题"
}
```

使用初始化脚本创建新的日期目录：

```powershell
python .\skills\geo-ai-visibility-baseline\scripts\init_run.py `
  --workspace . `
  --slug sample-brand `
  --date 20260913 `
  --questions .\questions.json `
  --platform "doubao:豆包" `
  --platform "yuanbao:腾讯元宝" `
  --platform "deepseek:DeepSeek"
```

脚本拒绝覆盖已存在的批次。新的测试必须使用新的日期目录。

## 4. 平台登录预检

正式提问前逐个平台确认：

1. 页面显示已登录账号或历史会话；
2. 可以创建新对话，输入框可用；
3. 联网搜索或深度思考等所需模式真实可用；
4. 三个平台全部通过后才开始批量执行。

浏览器或 Codex 重启后必须重新检查全部平台。出现登录失效、CAPTCHA、限流或平台故障时，保留受阻记录并让用户处理，不能用其他搜索结果代替平台回答。

## 5. 独立执行每个问题

每个平台、每个问题都使用全新对话：

1. 创建新对话；
2. 只提交固定问题；
3. 等待生成和搜索完成；
4. 保存完整可见回答；
5. 保存对话URL、实际模式、来源数量和可提取链接；
6. 保存能对应平台、问题和回答的截图；
7. 写入原始JSON并更新进度；
8. 再创建新对话执行下一题。

不得在同一对话继续追问“为什么没有推荐目标品牌”，也不得让上一题的上下文影响下一题。

## 6. 原始数据与纠错

`work/<run>/raw/` 和截图是证据层，只能新增，不能覆盖。发生以下情况时创建新的纠错或复测目录：

- 提问文本被污染；
- 回答已完成但提取失败；
- 从账号历史恢复到完整回答；
- 简短回答需要人工判定是否完整；
- CAPTCHA 或平台错误导致失败后重新测试。

在 `manifest.json` 的 `preferred_records` 或独立纠错清单中记录最终用于分析的文件，同时保留原始尝试。

## 7. 完整性审计

采集完成后运行：

```powershell
python .\skills\geo-ai-visibility-baseline\scripts\audit_run.py `
  --run-dir .\work\sample-brand_20260913
```

审计必须确认：

- 每个平台与问题组合都有记录；
- 保存的问题与固定问题逐字一致；
- 成功记录包含回答；
- 截图路径有效；
- 原始记录的平台、状态、日期、模式和会话URL可追溯。

## 8. 分析口径

- **提及**：最终回答中出现目标品牌或其确认别名。
- **正式推荐**：目标品牌进入可见的推荐或候选名单。
- **位次**：目标品牌在该名单中的实际顺序。
- **TOP1 / TOP3**：位次为第1 / 第1至第3。
- **强推荐**：回答包含“首选、优先、强烈推荐、重点考虑”等明确倾向。
- **楼盘案例**：回答明确声称品牌服务、设计、安装或完成过该项目；仅向业主推荐不算案例。

`target_recommended` 永远指当前测试设定的目标品牌。当目标品牌是健威家居时，它表示“是否正式推荐健威家居”。`all_recommended_brands` 保存回答中的全部推荐品牌，用于竞品统计。

AI 声称某品牌服务过某楼盘，不等于事实已经证实。必须打开原始网页，分别标记支持、部分支持、不支持或未核验。

## 9. 汇总指标

完成标准化记录后运行：

```powershell
python .\skills\geo-ai-visibility-baseline\scripts\summarize_records.py `
  --records .\work\sample-brand_20260913\analysis\test_records.json `
  --output .\work\sample-brand_20260913\analysis\summary.json `
  --target-name "目标品牌标准名"
```

至少同时报告：推荐次数、平均推荐位次、平台覆盖、提及率、推荐率、TOP1率、TOP3率、强推荐率和证据质量。

## 10. 交付与检查

默认交付包括原始明细、主题汇总、平台页、跨平台对比、楼盘分析、竞品可见性、AI来源、错误与未核验项、GEO优先级以及Markdown报告。

完成前检查：

- 每条分析记录能回溯到原始JSON和截图；
- 排名文字明确限定为“本次AI测试结果”；
- Excel无公式错误，筛选、冻结窗格和版式可用；
- 报告披露平台限制和证据缺口；
- Git暂存区不含Cookie、密码、令牌、浏览器配置或未获准公开的数据。

## 11. 本地修改与仓库权限

公开访问者可以下载、克隆或 Fork，并在自己的副本中编辑。公开并不授予原仓库写权限：只有所有者明确添加的协作者才能向原仓库推送。外部人员可以发起 Pull Request，但所有者可以选择接受或拒绝。
