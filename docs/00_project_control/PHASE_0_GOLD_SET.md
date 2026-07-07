# P0-2：建立微型 Gold Set（样本与人工标注基准）

> **给初学者的一句话说明：**
> 这一步不是让程序“开始读完所有文献”。它是先挑少量、代表不同困难的 PDF 页面，并人工写下“这一页里有什么、哪些文字块应该被识别、哪里可能出错”。以后任何 PDF 提取器或 OCR 工具都拿这份基准来比较。

## 1. P0-2 的真正产物

P0-2 要交付的是一套**不依赖某个具体库**的微型人工基准，而不是一套正式解析结果。

它包含：

1. 样本清单：每份来源 PDF、每个纳入页面和页面类型；
2. 原始文件指纹：文件名、文件大小、SHA-256、来源说明；
3. 页面级人工标签：这页属于原生文本、扫描、混合或文本层不可信；
4. 版面/风险标签：正文、脚注、尾注、边栏、表格、图注、外部链接、页眉页脚、页码、跨页段落候选等；
5. 少量人工确认的 PageBlock：至少标出正文块、脚注块和一个困难块；
6. 少量“金标准文本片段”：用于比较文字准确性、断词和阅读顺序；
7. 标注手册：别人或未来的自己可以按同一规则继续标；
8. 一份空白工具对比表：P1 才用它记录各提取器/OCR 的结果。

## 2. 为什么先做基准，而不是立刻选工具？

工具是“答题者”，Gold Set 是“试卷和评分标准”。

如果先选定某个工具，再用它自己的输出决定什么是正确的，结果会循环论证：工具看起来总会比较像自己。

本项目的长期目标是可核验的来源链。因而基准必须以原 PDF 页面、人工标注和保留的原始材料为中心，而不是以某个工具导出的文本为中心。

## 3. 微型 Gold Set 的规模

README 中的正式 Gold Set 目标是约 200–500 页；P0-2 不需要一开始达到这个规模。正式范围仍应覆盖原生文本、扫描、脚注/尾注、标题、跨页、不同页码、英拉混排、表格/图注，以及“有文本层但不可信”的扫描件。fileciteturn18file0L34-L55

P0-2 的建议规模为 **24–40 页**，优先保证类型覆盖，而不是页数好看。

建议构成：

| 样本类 | 建议页数 | 需要故意包含的困难 |
|---|---:|---|
| 排版较好的原生文本 PDF | 6–10 | 标题、页码、普通正文、至少一个脚注或尾注页 |
| 排版较差的原生文本 PDF | 6–10 | 字体编码异常、断词、脚注、阅读顺序疑点、边栏或表格之一 |
| 纯扫描 PDF | 6–10 | 清晰页与较差页、脚注、罗马/阿拉伯页码、可能的拉丁文 |
| 有文本层但不可信的扫描 PDF | 6–10 | OCR 错字、乱码、顺序错误、不可用链接、错误页码或错误段落边界 |

可以有一页同时属于多个“困难标签”；但“输入来源类型”只选一个主类型。

## 4. P0-2 要测试什么？

### 4.1 现在要定义、但暂不自动实现的项目

- 页面路由的正确答案：native_text / ocr_required / hybrid_review / manual_review；
- PageBlock 的人工参照位置与类别；
- 文字片段的人工参照转录；
- 阅读顺序是否明确；
- 跨页连接是否明确、可疑或不存在；
- 哪些文本应进入正文候选、脚注候选、表格/图注候选或仅保留为 unknown；
- 哪些页面必须人工审核；
- 规范化允许做什么、严禁做什么。

### 4.2 P1 才实际比较的项目

- pdftext、pdfplumber 或其他原生文本提取器的逐页输出；
- OCR 引擎的逐页输出；
- 文字覆盖率、乱码、阅读顺序、bbox 与人工 PageBlock 的差异；
- 各工具的耗时、依赖、Windows 安装成本与失败模式；
- PageBlock 自动分割是否达到可接受水平；
- 搜索是否能从 Gold Set 找回正确块和页。

## 5. 分块、向量化与存储：本阶段怎样处理？

### 5.1 PageBlock 人工标注：要做，但不是自动分块实现

要在若干代表页上人工标出**页面内**块，例如：

- `title`
- `body_text`
- `footnote`
- `endnote`
- `header`
- `footer`
- `page_number`
- `caption`
- `table`
- `sidebar`
- `unknown`

这给后续自动分块提供判卷标准。每个 PageBlock 永远只属于一个 PDF 页。

不需要在 P0-2 写自动分块代码，也不要强行标完每页的每个字。

### 5.2 向量化和向量数据库：不做

P0-2 不引入 embedding、向量数据库或任何向量化存储。

原因：

- 当前核心问题是文字是否可靠、位置是否可回到原页；
- 向量检索无法修复 OCR 错误、错页、错块或丢失 bbox；
- 向量结果难以替代精确来源链；
- 早期检索基线应先用 SQLite FTS5、短语检索和字符串模糊匹配；
- 引入向量库会增加环境、评估和版本管理复杂度，但不会帮助建立 Gold Set。

未来若需要语义检索，应把它作为**可替换的召回层**，并用同一 Gold Set 增加“能否召回正确 PageBlock”的测试；它不是当前数据底座。

### 5.3 自动存储：只存标注元数据，不建正式数据库

P0-2 可以把标注保存为 Git 可追踪的 JSON/JSONL/YAML 文本文件。

不创建 SQLite schema，不创建正式索引，不保存任何工具的完整原始输出到 Git。真实 PDF、OCR 输出、渲染图和将来的数据库仍留在被忽略的 `data/` 路径中。

## 6. 文本规范化：现在确定“契约”，不现在定最终算法

P0-2 应冻结以下原则：

1. 永远保留原始 PDF、原始提取文本与原始 OCR 输出；
2. `raw_text`、`normalized_search_text` 和人工校对文本是不同层；
3. 规范化结果必须可追溯到输入文本和所用规则版本；
4. 不得默默删除脚注、页码、页眉页脚、表格或外部链接；这些对象先分类、再决定是否索引；
5. 不得把 17 世纪拼写或拉丁文“现代化”；
6. Unicode 标准化、空白折叠和可解释的断词候选可以进入实验清单；
7. 行末连字符是否合并，必须记录为规则或候选，不能不可逆地猜测；
8. 自动“纠正”OCR 拼写错误不属于 P0-2。

P0-2 的交付物应包含一个小型规范化测试清单：每个案例给出 raw 输入、期望的安全输出/候选、以及不允许发生的破坏性变化。

## 7. 样本与标注的文件组织

真实 PDF 不提交到 Git。建议的本机结构：

```text
data/
├─ raw/
│  └─ gold_set/                 # 原始 PDF；被 Git 忽略
├─ rendered_pages/
│  └─ gold_set/                 # 以后生成的页面图；被 Git 忽略
└─ parser_outputs/
   └─ gold_set/                 # P1 的工具原始输出；被 Git 忽略

docs/01_gold_set/
├─ README.md                     # 使用说明与样本选择规则
├─ manifest.template.jsonl       # 清单模板
├─ annotations.template.jsonl    # 页面/块标注模板
├─ normalization_cases.template.jsonl
└─ ANNOTATION_GUIDE.md           # 人工标注手册
```

## 8. 最小标注字段

### 8.1 文档/页面清单

每个纳入页面至少有：

```json
{
  "sample_id": "scan_untrusted_001_p012",
  "document_id": "scan_untrusted_001",
  "source_filename": "example.pdf",
  "source_sha256": "<sha256>",
  "pdf_page_index": 11,
  "printed_page_label": "12",
  "primary_input_type": "text_layer_untrusted",
  "risk_tags": ["ocr_errors", "footnotes", "bad_reading_order"],
  "included_for": ["routing", "text_accuracy", "block_location"],
  "notes": "Short human explanation of why this page is useful."
}
```

### 8.2 页面与 PageBlock 标注

每页至少有：

```json
{
  "sample_id": "scan_untrusted_001_p012",
  "page_route_gold": "hybrid_review",
  "review_required": true,
  "reading_order_status": "ambiguous",
  "blocks": [
    {
      "gold_block_id": "scan_untrusted_001_p012_b01",
      "block_type": "body_text",
      "bbox_pdf_points": [72.0, 110.0, 520.0, 400.0],
      "order_on_page": 1,
      "gold_text_excerpt": "A short manually checked excerpt.",
      "transcription_scope": "excerpt",
      "notes": "Why this block is difficult or important."
    }
  ],
  "page_notes": "Explain uncertainty; do not hide it."
}
```

坐标如果暂时无法可靠测量，可写 `bbox_pdf_points: null`，并将 `bbox_status` 标为 `pending_manual_measurement`。不要编造坐标。

## 9. 人工标注原则

- 先做少量高质量标注，再扩大页数；
- 一页若难以判断，不要强迫给唯一答案；记录 `ambiguous` 和原因；
- 页码应区分 PDF 页序号与印刷页码；
- 外部链接按版面对象记录，但 P0-2 不验证链接是否有效；
- 对表格只标 `table` 区域和“需要保留/需要审核”，不要求重建单元格结构；
- 对边栏先标 `sidebar` 或 `unknown`，不在此阶段解决复杂阅读顺序；
- 脚注、尾注不是垃圾文本；先标出来，是否进入检索由后续策略决定；
- 文本层存在不等于可信，必须允许 `text_layer_untrusted`。

## 10. 本任务明确禁止

- 不选择或宣布最终原生 PDF 主解析器；
- 不安装 PDF/OCR 工具或模型；
- 不实际运行批量提取、OCR、自动分块或 benchmark；
- 不建立 SQLite schema、FTS5 索引、向量库或 embedding；
- 不把真实 PDF、图片、OCR 输出或数据库提交到 Git；
- 不用 LLM 自动生成 Gold 标注；
- 不把规范化实验规则写成不可逆清洗流程；
- 不要求完整人工转录全部页面。

## 11. 验收标准

- [ ] `docs/01_gold_set/` 中存在样本选择说明、标注手册与三个模板；
- [ ] 模板明确区分 PDF 页面序号、印刷页码、输入类型、风险标签与人工不确定性；
- [ ] 标注格式支持 PageBlock、bbox 缺失状态、文字片段和跨页候选；
- [ ] 规范化文档明确 raw/normalized/corrected 三层不可互相覆盖；
- [ ] 文档明确说明：向量化、自动分块、OCR、工具选型与正式索引不属于 P0-2；
- [ ] Git 不跟踪真实样本文献或生成数据；
- [ ] 所有新增文档对初学者可读。

## 12. 给 Codex 的实施提示

在实施前，先阅读：

- `AGENTS.md`
- `docs/00_project_control/DEVELOPMENT_ENVIRONMENT.md`
- 本任务书
- `README.md` 的 Gold Set、风险/审核、数据模型与开发阶段相关章节

本任务只创建 Gold Set 文档、模板与目录说明。不要写 PDF 处理代码、不要安装依赖、不要运行 OCR 或下载模型。
