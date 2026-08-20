import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = path.resolve(import.meta.dirname, "../..");
const analysisDir = path.join(root, "work", "analysis");
const outputDir = path.join(root, "outputs", "geo_ai_jiangmen_20260729");
const summary = JSON.parse(await fs.readFile(path.join(analysisDir, "final_summary.json"), "utf8"));
const rows = JSON.parse(await fs.readFile(path.join(analysisDir, "recommendations_enriched.json"), "utf8"));

await fs.mkdir(outputDir, { recursive: true });

const wb = Workbook.create();
const navy = "#17324D";
const blue = "#2E6F95";
const teal = "#2A9D8F";
const sand = "#E9C46A";
const coral = "#E76F51";
const ink = "#23313F";
const pale = "#EEF4F7";
const line = "#D7E1E8";
const white = "#FFFFFF";

function title(sheet, text, endCol = "J") {
  sheet.mergeCells(`A1:${endCol}1`);
  sheet.getRange("A1").values = [[text]];
  sheet.getRange(`A1:${endCol}1`).format = {
    fill: navy,
    font: { bold: true, color: white, size: 16 },
    horizontalAlignment: "left",
    verticalAlignment: "center",
  };
  sheet.getRange("A1").format.rowHeight = 34;
  sheet.showGridLines = false;
}

function sectionHeader(range) {
  range.format = {
    fill: blue,
    font: { bold: true, color: white },
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "all", style: "thin", color: line },
  };
  range.format.rowHeight = 28;
}

function tableBody(range) {
  range.format = {
    font: { color: ink, size: 10 },
    verticalAlignment: "top",
    wrapText: true,
    borders: { preset: "all", style: "thin", color: line },
  };
}

function addTable(sheet, range, name, style = "TableStyleMedium2") {
  const table = sheet.tables.add(range, true, name);
  table.style = style;
  table.showFilterButton = true;
  table.showBandedRows = true;
  return table;
}

function setWidths(sheet, widths) {
  for (const [col, width] of Object.entries(widths)) {
    sheet.getRange(`${col}:${col}`).format.columnWidth = width;
  }
}

const dash = wb.worksheets.add("总览");
title(dash, "江门家居、装修及全屋定制 AI 搜索可见性基准｜180次盲测", "N");
dash.getRange("A3:B8").values = [
  ["指标", "结果"],
  ["独立AI测试", ""],
  ["推荐记录", ""],
  ["规范化品牌", ""],
  ["候选引用页", ""],
  ["成功打开页", ""],
];
sectionHeader(dash.getRange("A3:B3"));
tableBody(dash.getRange("A4:B8"));
dash.getRange("B4:B8").format.numberFormat = "0";
dash.getRange("D3:E7").values = [
  ["证据结果", "推荐记录数"],
  ["有效支持", ""],
  ["部分支持", ""],
  ["不支持", ""],
  ["未核验", ""],
];
sectionHeader(dash.getRange("D3:E3"));
tableBody(dash.getRange("D4:E7"));
dash.getRange("A10:C20").values = [
  ["总体位次", "品牌", "被推荐次数"],
  ...summary.overall.slice(0, 10).map((x, i) => [i + 1, x.brand, x.count]),
];
sectionHeader(dash.getRange("A10:C10"));
tableBody(dash.getRange("A11:C20"));
dash.getRange("A22:D28").values = [
  ["赛道", "第一名", "次数", "平均位次"],
  ...Object.entries(summary.track_top10).map(([track, items]) => [
    track,
    items[0]?.brand ?? "无",
    items[0]?.count ?? 0,
    items[0]?.average_rank ?? "",
  ]),
];
sectionHeader(dash.getRange("A22:D22"));
tableBody(dash.getRange("A23:D28"));
dash.getRange("X3:Y13").values = [
  ["品牌", "次数"],
  ...summary.overall.slice(0, 10).map((x) => [x.brand, x.count]),
];
const brandChart = dash.charts.add("bar", dash.getRange("X3:Y13"));
brandChart.title = "总体推荐次数 TOP10";
brandChart.hasLegend = false;
brandChart.setPosition("G3", "N18");
brandChart.series.items[0].fill = blue;
dash.getRange("X15:Y19").values = [
  ["证据结果", "记录数"],
  ["有效支持", 192],
  ["部分支持", 31],
  ["不支持", 119],
  ["未核验", 415],
];
const supportChart = dash.charts.add("doughnut", dash.getRange("X15:Y19"));
supportChart.title = "引用证据分级";
supportChart.hasLegend = true;
supportChart.setPosition("G20", "N35");
dash.getRange("A30:B35").values = [
  ["说明", "口径"],
  ["排名含义", "仅代表本次5平台、36问题、180次独立AI搜索结果，不是官方市场排名。"],
  ["推荐计数", "同一平台同一问题中，同一品牌最多计1次；组合推荐分别记录。"],
  ["有效支持", "实际打开页面并检出对应品牌、“江门”和相关业务词。"],
  ["部分支持", "页面仅支持品牌+业务、品牌+江门或品牌身份。"],
  ["未核验", "AI未提供链接、引用与品牌未建立对应、或页面无法访问。"],
];
sectionHeader(dash.getRange("A30:B30"));
tableBody(dash.getRange("A31:B35"));
setWidths(dash, { A: 18, B: 31, C: 14, D: 16, E: 14, F: 3, G: 12, H: 12, I: 12, J: 12, K: 12, L: 12, M: 12, N: 12 });
dash.freezePanes.freezeRows(1);

const trackSheet = wb.worksheets.add("五赛道Top10");
title(trackSheet, "五条关键词赛道｜推荐最多的10个品牌", "G");
const trackData = [["赛道", "赛道位次", "品牌", "推荐次数", "平均位次", "品牌范围", "统计口径"]];
for (const track of Object.keys(summary.track_top10).filter((x) => x !== "楼盘场景")) {
  summary.track_top10[track].forEach((item, i) => {
    trackData.push([track, i + 1, item.brand, item.count, item.average_rank, item.brand_scope, "本次AI搜索"]);
  });
}
trackSheet.getRangeByIndexes(2, 0, trackData.length, trackData[0].length).values = trackData;
sectionHeader(trackSheet.getRange("A3:G3"));
tableBody(trackSheet.getRange(`A4:G${trackData.length + 2}`));
addTable(trackSheet, `A3:G${trackData.length + 2}`, "TrackTop10Table");
trackSheet.getRange(`D4:D${trackData.length + 2}`).conditionalFormats.add("dataBar", { color: teal });
setWidths(trackSheet, { A: 22, B: 11, C: 20, D: 12, E: 12, F: 17, G: 14 });
trackSheet.freezePanes.freezeRows(3);

const brandSheet = wb.worksheets.add("品牌统计");
title(brandSheet, "品牌统计｜次数、平均位次、关键词与引用依赖", "P");
const brandHeaders = [
  "总体位次", "品牌", "品牌范围", "推荐次数", "平均位次", "主要关键词1", "次数1",
  "主要关键词2", "次数2", "最常引用网站", "网站引用次数", "官网引用", "第三方引用",
  "官网占比", "有效/部分支持", "未核验/不支持",
];
const brandData = [brandHeaders, ...summary.overall.map((x, i) => [
  i + 1,
  x.brand,
  x.brand_scope,
  x.count,
  x.average_rank,
  x.main_tracks[0]?.track ?? "",
  x.main_tracks[0]?.count ?? 0,
  x.main_tracks[1]?.track ?? "",
  x.main_tracks[1]?.count ?? 0,
  x.most_cited_sites[0]?.site ?? "",
  x.most_cited_sites[0]?.count ?? 0,
  x.official_count,
  x.third_party_count,
  x.official_share ?? "",
  x.valid_count + x.partial_count,
  x.unverified_count + x.unsupported_count,
])];
brandSheet.getRangeByIndexes(2, 0, brandData.length, brandData[0].length).values = brandData;
sectionHeader(brandSheet.getRange("A3:P3"));
tableBody(brandSheet.getRange(`A4:P${brandData.length + 2}`));
brandSheet.getRange(`N4:N${brandData.length + 2}`).format.numberFormat = "0.0%";
brandSheet.getRange(`D4:D${brandData.length + 2}`).conditionalFormats.add("dataBar", { color: blue });
brandSheet.getRange(`N4:N${brandData.length + 2}`).conditionalFormats.add("colorScale", { colors: ["#F6D7D0", "#F5E6A7", "#BFE3DD"], thresholds: ["min", "50%", "max"] });
addTable(brandSheet, `A3:P${brandData.length + 2}`, "BrandStatsTable");
setWidths(brandSheet, { A: 10, B: 18, C: 17, D: 11, E: 11, F: 21, G: 9, H: 21, I: 9, J: 26, K: 12, L: 10, M: 11, N: 10, O: 14, P: 14 });
brandSheet.freezePanes.freezeRows(3);
brandSheet.freezePanes.freezeColumns(2);

const platformSheet = wb.worksheets.add("平台对比");
title(platformSheet, "平台对比｜推荐覆盖与证据可核验性", "K");
const platformData = [[
  "平台", "测试数", "有推荐测试", "零推荐测试", "推荐记录", "品牌数", "带链接记录",
  "有效", "部分支持", "不支持", "未核验",
], ...summary.platform_stats.map((x) => [
  x.platform, x.sample_count, x.samples_with_recommendations, x.zero_recommendation_samples,
  x.recommendation_rows, x.unique_brands, x.linked_rows, x.valid, x.partial, x.unsupported, x.unverified,
])];
platformSheet.getRangeByIndexes(2, 0, platformData.length, platformData[0].length).values = platformData;
sectionHeader(platformSheet.getRange("A3:K3"));
tableBody(platformSheet.getRange(`A4:K${platformData.length + 2}`));
addTable(platformSheet, `A3:K${platformData.length + 2}`, "PlatformTable");
platformSheet.getRange("X3:Z8").values = [
  ["平台", "有效+部分", "未核验+不支持"],
  ...summary.platform_stats.map((x) => [x.platform, x.valid + x.partial, x.unsupported + x.unverified]),
];
const platformChart = platformSheet.charts.add("bar", platformSheet.getRange("X3:Z8"));
platformChart.title = "平台证据结构";
platformChart.hasLegend = true;
platformChart.setPosition("M10", "T27");
setWidths(platformSheet, { A: 14, B: 10, C: 13, D: 12, E: 12, F: 10, G: 12, H: 9, I: 10, J: 10, K: 10, L: 3, M: 14, N: 12, O: 14 });
platformSheet.freezePanes.freezeRows(3);

const sceneSheet = wb.worksheets.add("楼盘场景");
title(sceneSheet, "楼盘场景｜被推荐最多的品牌", "F");
const sceneData = [["位次", "品牌", "推荐次数", "平均位次", "品牌范围", "说明"],
  ...summary.track_top10["楼盘场景"].map((x, i) => [
    i + 1, x.brand, x.count, x.average_rank, x.brand_scope, "问题31—36合计",
  ]),
];
sceneSheet.getRangeByIndexes(2, 0, sceneData.length, sceneData[0].length).values = sceneData;
sectionHeader(sceneSheet.getRange("A3:F3"));
tableBody(sceneSheet.getRange(`A4:F${sceneData.length + 2}`));
addTable(sceneSheet, `A3:F${sceneData.length + 2}`, "SceneTable");
const sceneChart = sceneSheet.charts.add("bar", sceneSheet.getRange(`B3:C${sceneData.length + 2}`));
sceneChart.title = "楼盘场景推荐次数 TOP10";
sceneChart.hasLegend = false;
sceneChart.setPosition("H3", "O20");
setWidths(sceneSheet, { A: 10, B: 20, C: 12, D: 12, E: 18, F: 18, G: 3, H: 12, I: 12, J: 12, K: 12, L: 12, M: 12, N: 12, O: 12 });
sceneSheet.freezePanes.freezeRows(3);

const sourceSheet = wb.worksheets.add("来源质量");
title(sourceSheet, "引用来源质量｜来源类型、可访问性与支持度", "H");
const sourceData = [["来源类型", "推荐记录", "去重URL", "有效", "部分支持", "不支持", "未核验", "判读"],
  ...summary.source_type_stats.map((x) => [
    x.source_type, x.recommendation_rows, x.unique_urls, x.valid, x.partial, x.unsupported, x.unverified,
    x.source_type === "品牌官网" ? "身份/服务范围较强，能力细节仍需交叉核验" :
    x.source_type === "软文/转载平台" ? "软文和重复转载风险较高" :
    x.source_type === "政府或官方机构" ? "权威但常与家装推荐结论无直接关系" :
    x.source_type === "未提供链接" ? "无法复核" : "按页面逐条判断",
  ]),
];
sourceSheet.getRangeByIndexes(2, 0, sourceData.length, sourceData[0].length).values = sourceData;
sectionHeader(sourceSheet.getRange("A3:H3"));
tableBody(sourceSheet.getRange(`A4:H${sourceData.length + 2}`));
addTable(sourceSheet, `A3:H${sourceData.length + 2}`, "SourceQualityTable");
setWidths(sourceSheet, { A: 20, B: 12, C: 10, D: 10, E: 11, F: 10, G: 10, H: 34 });
sourceSheet.freezePanes.freezeRows(3);

const detailSheet = wb.worksheets.add("180题明细");
title(detailSheet, "180次AI搜索推荐明细｜每个品牌推荐记录一行", "O");
const detailHeaders = [
  "平台", "问题编号", "关键词赛道", "搜索问题", "推荐品牌", "推荐位次", "推荐理由",
  "引用页面", "URL", "来源类型", "发布时间", "是否有效支持结论", "搜索日期", "会话URL", "品牌范围",
];
const detailData = [detailHeaders, ...rows.map((x) => [
  x.platform,
  x.question_number,
  x.track,
  x.question,
  x.brand,
  x.rank,
  x.reason,
  x.citation_title,
  x.citation_url,
  x.source_type,
  x.publication_date,
  x.support,
  x.search_date,
  x.conversation_url,
  x.brand_scope,
])];
detailSheet.getRangeByIndexes(2, 0, detailData.length, detailData[0].length).values = detailData;
sectionHeader(detailSheet.getRange("A3:O3"));
tableBody(detailSheet.getRange(`A4:O${detailData.length + 2}`));
detailSheet.getRange(`F4:F${detailData.length + 2}`).format.numberFormat = "0";
addTable(detailSheet, `A3:O${detailData.length + 2}`, "Detail180Table", "TableStyleMedium2");
detailSheet.getRange(`L4:L${detailData.length + 2}`).conditionalFormats.add("containsText", { text: "是（", format: { fill: "#D9EDE8", font: { color: "#1E6B60" } } });
detailSheet.getRange(`L4:L${detailData.length + 2}`).conditionalFormats.add("containsText", { text: "否（", format: { fill: "#F8DCD6", font: { color: "#A53D2D" } } });
setWidths(detailSheet, { A: 13, B: 9, C: 20, D: 42, E: 18, F: 9, G: 55, H: 40, I: 45, J: 18, K: 13, L: 27, M: 13, N: 42, O: 18 });
detailSheet.getRange(`A4:O${detailData.length + 2}`).format.rowHeight = 42;
detailSheet.freezePanes.freezeRows(3);
detailSheet.freezePanes.freezeColumns(6);

const linkSheet = wb.worksheets.add("引用核验");
title(linkSheet, "候选引用页核验｜135个去重页面", "M");
const linkHeaders = [
  "URL", "最终URL", "网站", "来源类型", "HTTP状态", "成功打开", "页面标题",
  "发布时间", "正文长度", "检出品牌", "含江门", "含业务词", "错误信息",
];
const linkData = [linkHeaders, ...summary.link_validation.map((x) => [
  x.url,
  x.final_url,
  x.site,
  x.source_type,
  x.status ?? "",
  x.opened ? "是" : "否",
  x.page_title,
  x.publication_date,
  x.text_length,
  (x.brand_hits ?? []).join("、"),
  x.jiangmen_hit ? "是" : "否",
  x.topic_hit ? "是" : "否",
  x.error,
])];
linkSheet.getRangeByIndexes(2, 0, linkData.length, linkData[0].length).values = linkData;
sectionHeader(linkSheet.getRange("A3:M3"));
tableBody(linkSheet.getRange(`A4:M${linkData.length + 2}`));
addTable(linkSheet, `A3:M${linkData.length + 2}`, "LinkValidationTable");
setWidths(linkSheet, { A: 46, B: 42, C: 24, D: 18, E: 10, F: 10, G: 48, H: 13, I: 12, J: 30, K: 10, L: 10, M: 38 });
linkSheet.getRange(`A4:M${linkData.length + 2}`).format.rowHeight = 36;
linkSheet.freezePanes.freezeRows(3);

const methodSheet = wb.worksheets.add("方法与限制");
title(methodSheet, "研究方法、判断口径与限制", "F");
const methods = [
  ["项目", "说明"],
  ["测试范围", "DeepSeek、豆包、腾讯元宝、文心一言、千问；每个平台36个问题，共180次独立搜索。"],
  ["独立性", "每个问题单独新开会话或独立搜索，不把上一题答案作为下一题上下文。"],
  ["搜索期间", "2026-07-25—2026-07-29（Asia/Shanghai）。"],
  ["推荐记录", "记录AI明确给出的3—5个推荐；若AI输出组合品牌则分别记录；千问第29、31题未给出品牌推荐。"],
  ["品牌归一", "对简称、移动端名称和门店名称进行统一；保留实际AI输出中的相关性错误与异常品牌。"],
  ["引用初筛", "搜索摘要不直接作为证据；仅将带URL且标题初步对应品牌的页面纳入实际打开核验。"],
  ["有效支持", "页面成功打开，且正文检出对应品牌、“江门”和家居/装修/定制/设计等业务词。"],
  ["部分支持", "页面只支持品牌身份、品牌+业务或品牌+江门，不能完整支持推荐理由。"],
  ["不支持", "页面成功打开但未检出推荐品牌，视为引用错配。"],
  ["未核验", "AI未提供链接、引用标题无法与品牌建立对应、或页面无法访问；不作推断。"],
  ["来源类型", "区分品牌官网、政府/官方机构、行业协会、权威媒体、地图/点评、内容平台、用户/论坛、行业平台、软文/转载及其他网站。"],
  ["排名声明", "所有位次只代表本次AI搜索输出，不是官方市场排名、销量排名或质量排名。"],
  ["关键限制", "AI结果会随时间、账号、地区、模型版本和检索索引变化；品牌官网自述不能单独证明实际交付质量。"],
];
methodSheet.getRangeByIndexes(2, 0, methods.length, 2).values = methods;
sectionHeader(methodSheet.getRange("A3:B3"));
tableBody(methodSheet.getRange(`A4:B${methods.length + 2}`));
setWidths(methodSheet, { A: 18, B: 92 });
methodSheet.getRange(`A4:B${methods.length + 2}`).format.rowHeight = 46;
methodSheet.freezePanes.freezeRows(3);

dash.getRange("B4:B8").formulas = [
  ["=SUM('平台对比'!B4:B8)"],
  ["=COUNTA('180题明细'!A4:A760)"],
  ["=COUNTA('品牌统计'!B4:B108)"],
  ["=COUNTA('引用核验'!A4:A138)"],
  ["=COUNTIF('引用核验'!F4:F138,\"是\")"],
];
dash.getRange("E4:E7").formulas = [
  ["=SUM('来源质量'!D4:D13)"],
  ["=SUM('来源质量'!E4:E13)"],
  ["=SUM('来源质量'!F4:F13)"],
  ["=SUM('来源质量'!G4:G13)"],
];

const previews = [
  ["总览", "A1:N35"],
  ["五赛道Top10", "A1:G28"],
  ["品牌统计", "A1:P28"],
  ["平台对比", "A1:T27"],
  ["楼盘场景", "A1:O20"],
  ["来源质量", "A1:H15"],
  ["180题明细", "A1:O28"],
  ["引用核验", "A1:M28"],
  ["方法与限制", "A1:F16"],
];
for (const [sheetName, range] of previews) {
  const png = await wb.render({ sheetName, range, scale: 1, format: "png" });
  const safe = sheetName.replace(/[\\/:*?"<>|]/g, "_");
  await fs.writeFile(path.join(outputDir, `preview_${safe}.png`), new Uint8Array(await png.arrayBuffer()));
}

const inspection = await wb.inspect({
  kind: "workbook,sheet,table",
  include: "id,name,range",
  tableMaxRows: 3,
  tableMaxCols: 8,
  maxChars: 12000,
});
await fs.writeFile(path.join(outputDir, "workbook_inspection.ndjson"), inspection.ndjson ?? String(inspection), "utf8");

const xlsx = await SpreadsheetFile.exportXlsx(wb);
const workbookPath = path.join(outputDir, "江门AI搜索可见性测试明细_180题.xlsx");
await xlsx.save(workbookPath);
console.log(JSON.stringify({ workbookPath, previews: previews.length, rows: rows.length }, null, 2));
