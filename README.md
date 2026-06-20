# TraceDoc

> **高可靠、可追溯的批量文档解析与检索系统**  
> 状态：架构讨论稿（已更新）  
> 运行目标：Windows 原生、本地优先、无 LLM 核心依赖

---

## 1. 项目定义

TraceDoc 用于批量导入、解析、校验、审核和检索两类文档：

1. **原生文本 PDF**  
   例如 arXiv 论文、现代电子书、可搜索的学术文献。此类文件应直接读取 PDF 内嵌文字对象、坐标与版面信息，**不应重新 OCR**。

2. **扫描 / 图像型 PDF 与单页图像**  
   例如历史文献扫描本、影印资料、无可靠文本层的 PDF。此类文件走 OCR 与版面分析路径。

系统的核心产物不是“自动生成答案”，而是可验证的文本证据库。每一条可检索文本都必须能追溯到：

- 原始文件；
- PDF 文件页码；
- 视觉印刷页码（如 `xxii`、`293`，若可识别）；
- 页面中的局部文本块（PageBlock）；
- 解析方式、解析器版本与质量状态；
- 必要时的原始页面图像与 bbox 高亮。

本项目暂时不属于人格 AI、记忆系统或通用聊天 RAG 的组成部分。它是独立的文献数字化与检索基础设施。

---

## 2. 已确定的范围

### 2.1 第一阶段主要文献类型

- 17 世纪前后英文历史文献的现代印刷校勘版；
- 可能夹杂拉丁文；
- 常见单栏正文；
- 脚注、尾注、页眉、页脚、印刷页码；
- 可出现表格与图注；
- 现代可搜索 PDF 与扫描 PDF 混合；
- 文档规模：初期数千页至约一万页。

### 2.2 第一阶段明确承诺

- 单栏正文 + 脚注的可靠处理；
- 原生文本 PDF 与扫描 PDF 的独立入口；
- 页级路由与风险分流；
- 文件 + PDF 页码 + PageBlock 来源定位；
- 默认显示命中原始行附近若干行；
- block 级人工审核；
- 支持跨页自然段；
- 本地批量处理、断点续跑、可重跑与版本留档；
- 文献元数据候选补全与人工确认。

### 2.3 暂不作为 MVP 承诺

- 双栏报刊、词典式多栏、边注、印章、手稿；
- 高精度复杂表格还原；
- 公式的可靠 LaTeX 重建；
- 化学结构式、图内文字的高精度解析；
- 逐字符 OCR 校对器；
- 多人协作、复杂权限系统、云端同步；
- LLM 驱动的自动摘要、问答或 OCR 判定。

系统应为这些后续能力保留扩展接口，但不得为支持它们而让 MVP 过度复杂。

---

## 3. 核心设计决策

### D-01：页面而非文件是最小路由单位

同一个 PDF 可以同时包含：

- 原生文字页；
- 扫描图像页；
- 带隐藏 OCR 层的扫描页；
- 图表或表格页；
- 局部嵌入扫描图片的原生文字页。

因此，系统按 **Page** 选择处理路径，而不是按整个文件只选一种解析器。

```text
Document
└── Page
    ├── native_text
    ├── ocr_required
    ├── hybrid_review
    └── manual_review
```

### D-02：原生文本与 OCR 走独立入口

```text
原始文件
    ↓
页面分类器
    ├── 原生文本入口
    │   ├── PDF 内嵌文本与坐标提取
    │   ├── 双解析一致性验证
    │   └── 结构化入库
    │
    ├── OCR 入口
    │   ├── 页面渲染与预处理
    │   ├── OCR + 版面分析
    │   ├── 交叉验证
    │   └── 结构化入库
    │
    └── 混合 / 高风险入口
        ├── 局部 OCR 或重处理
        └── 人工审核
```

### D-03：PageBlock 永不跨页；LogicalParagraph 可以跨页

PDF 页面坐标只在单页内成立，因此：

```text
PageBlock
    页面局部视觉文本块。
    永远只属于一页。
    拥有明确 bbox。
    用于定位、审核和高亮。

LogicalParagraph
    人类阅读意义上的逻辑自然段。
    由一个或多个 PageBlock 组成。
    可以跨页。
    不拥有单一 bbox，而拥有多个来源片段。

SearchChunk
    面向检索的文本单位。
    可包含一个或多个 LogicalParagraph。
    永远保留全部来源 PageBlock。
```

### D-04：来源定位的 MVP 标准

每条检索命中至少返回：

```text
文件名
+ PDF 页码
+ 印刷页码（存在时）
+ 命中的 PageBlock
+ 命中原始行附近若干行
+ 解析方式与质量状态
```

bbox 页面高亮是增强功能。MVP 默认可直接返回文字来源并打开对应页。

### D-05：文本必须分层保存

```text
1. 原始证据层
   原始 PDF、图像、渲染页面。永不修改。

2. 原始转录层
   原生 PDF 提取文本或 OCR 原始文本。保留提取器输出。

3. 规范化检索层
   用于比较和检索的副本，可规范化空格、连字符、Unicode 兼容字符等。
   不覆盖原始转录。

4. 逻辑结构层
   视觉块、逻辑自然段、脚注关联、跨页链接、章节结构。

5. 检索层
   面向关键词、模糊匹配与后续语义检索的 SearchChunk。
```

### D-06：脚注、尾注、页眉、页脚和页码不删除

它们需要被识别、分类、单独保存和可选索引，而不是被不可逆清洗。

默认检索优先正文；用户可选择是否同时检索：

- 脚注；
- 尾注；
- 图注；
- 参考文献；
- 页眉页脚；
- 表格文本。

### D-07：双解析验证是风险信号，不是真理概率

两个解析器一致时，结果可视为低风险自动入库候选；它不意味着绝对正确。

系统应显示可解释的原因，例如：

```text
- 主提取器和验证提取器的正文文本覆盖率一致；
- 第 3 个文本块的行序存在冲突；
- 页面下方检测到脚注区域；
- 原生文本层疑似来自旧 OCR，建议转 OCR 路径；
- 页面末尾与下一页首块可能属于同一自然段。
```

### D-08：Windows 原生优先

MVP 以 Windows 原生 Python 环境为目标，不要求 WSL、Docker、Linux 或远程服务。

### D-09：核心路径不依赖 LLM

OCR、原生 PDF 提取、交叉验证、风险评分、人工审核、关键词检索和模糊检索均可无 LLM 实现。

本地 embedding、摘要和复杂查询解释属于后续可选能力，不应成为第一阶段依赖。

---

## 4. 系统架构

```text
原始 PDF / 图片
    ↓
文件导入、哈希、去重、页渲染
    ↓
页面分类器
    ├─ native_text
    ├─ ocr_required
    ├─ hybrid_review
    └─ manual_review
    ↓
对应解析入口
    ├─ Native PDF parser + validator
    └─ OCR parser + validator
    ↓
统一 ParsedPage / PageBlock 协议
    ↓
差异检测、质量评分、风险说明
    ↓
canonicalization
    ├─ PageBlock 确认
    ├─ 页眉页脚/脚注分类
    ├─ LogicalParagraph 重建
    └─ 跨页自然段链接
    ↓
人工审核队列
    ↓
SearchChunk 生成
    ↓
SQLite FTS5 + 模糊检索
    ↓
检索结果：文本上下文 + 精确来源
```

---

## 5. 页面分类器

页面分类器的任务不是理解全部页面语义，而是决定该页应走哪条处理路径。

```python
from enum import Enum

class PageIngestionMode(str, Enum):
    NATIVE_TEXT = "native_text"
    OCR_REQUIRED = "ocr_required"
    HYBRID_REVIEW = "hybrid_review"
    MANUAL_REVIEW = "manual_review"
```

### 5.1 初始特征

对每页先运行轻量原生文字提取，计算：

- `native_char_count`：可提取字符数量；
- `meaningful_word_count`：非空、非纯标点的词数；
- `bad_unicode_ratio`：替换字符、控制字符、异常私有字符比例；
- `text_bbox_coverage`：文字 bbox 对页面正文区域的覆盖程度；
- `image_area_ratio`：大图像或扫描图占页面的比例；
- `word_position_consistency`：文字坐标是否合理分布；
- `font_mapping_health`：字体映射是否出现明显乱码；
- `native_parser_agreement`：两个 native 提取器的文本与布局一致度。

### 5.2 初始路由规则

```text
NATIVE_TEXT：
- 有足够文字对象；
- 乱码比例低；
- 文本坐标覆盖正文区域；
- 两个 native 提取器基本一致；
- 页面不是扫描图占主导。

OCR_REQUIRED：
- 基本提取不到可用文字；
- 页面主体是一张扫描图；
- 文本层为空、极少或明显乱码；
- 文字坐标异常。

HYBRID_REVIEW：
- 有正文文字，但局部存在图片文字、扫描区域或图表；
- 可搜索文本层疑似旧 OCR；
- 两个 native 提取器存在明显差异；
- 表格、图注或局部复杂版面导致结构不可信。

MANUAL_REVIEW：
- 原生提取与 OCR 均无法得到可靠结果；
- 页面无法自动归类；
- 需要人工决定是否进入正式证据库。
```

---

## 6. 原生文本 PDF 入口

### 6.1 目标

对 arXiv、现代电子书、论文、报告等文本型 PDF：

- 直接读取 PDF 嵌入文本；
- 读取词、行、字体、坐标与绘制对象；
- 不经过 OCR；
- 尽量恢复视觉行和单栏阅读顺序；
- 将最终结果与原始 PDF 页保持可定位关系。

### 6.2 建议模块

| 模块 | 角色 | LLM | 许可证 / 注意事项 |
|---|---|---:|---|
| `pdftext` | 默认主提取器候选 | 否 | Apache-2.0；适合批量文字、block、line 提取 |
| `pdfplumber` | 默认验证提取器候选 | 否 | MIT；适合字/词/线条/坐标检查 |
| `docling-parse` | 可选原生坐标提取候选 | 否 | MIT；适合字符、词、行级坐标 |
| `PyMuPDF` | 调试、高级定位与 PDF 操作候选 | 否 | AGPL 或商业许可；核心依赖前需评估许可 |
| `GROBID` | 学术论文结构与元数据增强，可选 | 非 LLM，但使用机器学习模型 | Java/服务式；不作为通用书籍解析器 |

第一阶段推荐：

```text
主提取器：pdftext
验证提取器：pdfplumber
可选调试：PyMuPDF
```

### 6.3 原生 PDF 双解析验证

两套提取器先各自输出词、行和 bbox，不直接比较最终段落。

处理步骤：

```text
1. 各自提取 words / lines / bboxes；
2. 生成仅用于比较的轻度规范化文本副本；
3. 在同一页面中按 y 坐标、x 范围、bbox overlap、文本相似度对齐行；
4. 计算每页的文本、覆盖、布局和顺序一致性；
5. 生成可解释风险说明；
6. 根据风险分流到自动入库、抽检或人工审核。
```

建议记录：

```text
text_agreement
coverage_agreement
layout_agreement
order_agreement
glyph_health
structure_warnings
routing_decision
```

---

## 7. OCR / 扫描 PDF 入口

### 7.1 目标

对扫描 PDF、图片文献和不可信文本层页面：

- 页面渲染；
- 旋转、倾斜、清晰度等质量检查；
- OCR 与版面分析；
- 第二解析器交叉验证；
- 保留 OCR 原文、置信信息和 bbox；
- 不让 OCR 结果覆盖原始页面证据。

### 7.2 建议模块

| 模块 | 角色 | LLM |
|---|---|---:|
| PaddleOCR / PP-Structure | 主 OCR、文字检测、版面分析 | 否 |
| Docling | 结构化验证候选 | 否，核心本地模型不等于对话式 LLM |
| MinerU | 复杂页第二意见候选 | 可能依赖视觉模型；不作为 MVP 必需模块 |
| OCRmyPDF | 扫描 PDF 预处理、生成文本层 | 否 |
| Tesseract | 独立传统 OCR 基线 | 否 |

第一阶段仅需先验证：

```text
主 OCR：PaddleOCR
验证器：Docling 或传统 OCR 基线
```

---

## 8. PageBlock、脚注与逻辑段落

### 8.1 PageBlock

`PageBlock` 是单页的视觉文本块：

```text
- 永不跨页；
- 必须有 page_index；
- 通常有 bbox；
- 必须保存 raw_text；
- 可保存 normalized_text；
- 具有 block_type；
- 可关联 parser 与 parse_run；
- 用于检索来源、审核、页面高亮。
```

建议的初始类型：

```text
title
section_header
body_text
footnote
endnote
caption
table
page_header
page_footer
page_number
reference
unknown
```

### 8.2 LogicalParagraph

`LogicalParagraph` 是系统重建的逻辑自然段：

```text
- 可由一个或多个 PageBlock 构成；
- 可跨页；
- 不拥有单一 bbox；
- 保存 fragment 顺序；
- 保存段落链接状态与置信信息；
- 可人工确认或拒绝跨页链接。
```

建议字段：

```text
logical_paragraph_id
fragment_block_ids
source_page_indices
text_raw_joined
text_normalized_joined
link_status
link_confidence
review_status
```

### 8.3 跨页自然段的规则

第一页最后一个正文块与下一页第一个正文块可能属于同一自然段。初始规则应综合：

- 两者均为 `body_text`；
- 字体、字号、栏位置相近；
- 上一页末尾不是明显标题或分节；
- 下一页开头不是标题、首行强缩进或新章节；
- 页面之间不存在正文区域切换；
- 脚注区、页眉页脚已排除；
- 两个解析器未报告严重冲突。

自动链接必须可逆：

```text
auto_linked
needs_review
manually_confirmed
manually_rejected
```

不应只用句号判断段落是否结束。

### 8.4 页眉、页脚、页码与脚注

这些对象不删除，只分类、保存并可按查询选项过滤。

建议的初始识别线索：

```text
页眉：
- 页面顶部；
- 跨多页重复；
- 常为书名、章节名或栏目名。

页脚：
- 页面底部；
- 跨多页重复；
- 常为出版社、版权、章节信息。

页码：
- 靠近底部或顶部中央；
- 短字符串；
- 阿拉伯数字或罗马数字。

脚注：
- 页面下部；
- 常有更小字号；
- 与正文存在明显垂直间隔；
- 往往以符号、数字或字母锚点开头。
```

---

## 9. 规范化与清洗策略

不执行破坏性清洗。每层独立保存。

### 9.1 原始转录层

保留：

- 原始空格与换行；
- 脚注标记；
- 页眉、页脚、页码；
- 连字符；
- PDF 提取器原始 Unicode；
- OCR 输出及其置信或模型信息。

### 9.2 规范化检索层

可做：

- Unicode 引号、破折号、连字兼容处理；
- 多余空格归并；
- 跨行断词候选恢复；
- 连续换行规范化；
- 用于比较时可暂时忽略页码或脚注锚点。

不应：

- 静默删除脚注；
- 静默删除页码；
- 覆盖原始文本；
- 未留历史地替换旧拼写；
- 把编辑性结构错误当作“清洗”掩盖。

对于 17 世纪英文，默认不做现代英语拼写替换。若未来需要历史拼写检索扩展，应作为额外索引字段而不是覆盖原文。

---

## 10. 人工审核 MVP

人工审核以 **PageBlock 级** 为主，同时支持跨页逻辑段落确认。

最小界面布局：

```text
左侧：
原始 PDF 页或渲染页面图像。

中间：
主解析器的 PageBlock、文本与 bbox。

右侧：
验证解析器文本、差异、风险原因、路由建议。
```

最小操作：

- 接受主解析结果；
- 接受验证结果；
- 编辑整个 block 文本；
- 合并 / 拆分 PageBlock；
- 确认或拒绝跨页段落链接；
- 标记脚注、页眉、页脚、页码；
- 标记为“无法可靠 OCR / 提取”；
- 请求以另一条路径重跑；
- 确认或修订文献元数据候选。

第一版不做逐字符校对器。

---

## 11. 检索设计

### 11.1 默认展示单位

检索结果默认显示：

> **命中的原始行附近若干行**，而不是强制输出完整自然段。

这样可避免自然段重建错误影响阅读，也更接近用户核验原文的需要。

来源仍以 `PageBlock` 为准。

建议展示：

```text
命中片段：
前 2–4 行
+ 命中行
+ 后 2–4 行

来源：
文件：...
PDF 页：...
印刷页：...
类型：正文 / 脚注 / 图注
提取方式：native_text / OCR
质量状态：...
```

如命中邻近页面边界，可同时提示：

```text
上一页末尾可能为同一逻辑自然段。
下一页开头可能为同一逻辑自然段。
```

### 11.2 MVP 检索能力

```text
SQLite FTS5：
关键词、短语、布尔检索。

SQLite FTS5 bm25：
基本排序。

RapidFuzz：
OCR 错误、拼写误差和近似短句检索。

过滤条件：
文献、文件、页码范围、年份、作者、文本类型、审核状态。
```

本地语义向量检索可在文本与来源链稳定后再加入。

---

## 12. 元数据补全

元数据补全是独立 enrichment 阶段，不阻塞 OCR 与原生文本入库。

```text
导入与文本解析
    ↓
从封面、首页、题名、作者、DOI、ISBN、出版信息中提取候选
    ↓
查询外部来源
    ↓
生成候选匹配
    ↓
高置信自动接受或人工确认
```

可能的外部来源按文献类型选择：

- 学术论文：Crossref、OpenAlex、arXiv、NASA ADS；
- 图书和历史版本：WorldCat、Internet Archive、HathiTrust、国家图书馆或馆藏目录；
- 机构报告：机构库与出版者页面。

外部返回记录只能视为候选。必须保存：

```text
metadata_source
external_record_id
query_time
match_score
match_reason
review_status
```

---

## 13. 数据模型

### 13.1 核心表 / 实体

```text
documents
    一个逻辑文献或书籍。

document_files
    一个文献可包含多个文件版本。

document_pages
    页面、渲染图、PDF 页码、印刷页码、图像质量和路由状态。

parse_runs
    某文件/页面被某解析器、版本、参数运行的一次记录。

parsed_blocks
    解析器原始输出。

canonical_blocks
    经规则或人工认可的 PageBlock。

logical_paragraphs
    可跨页的自然段逻辑对象。

logical_paragraph_fragments
    LogicalParagraph 与 canonical_block 的有序关系。

search_chunks
    用于检索的逻辑内容。

chunk_sources
    SearchChunk 与 PageBlock 的多对多来源映射。

metadata_candidates
    自动补全的候选书目信息与审核状态。

review_tasks
    低置信、冲突、人工修订、重跑任务。
```

### 13.2 所有来源对象至少包含

```text
document_id
file_id
page_index
printed_page_label
block_id
bbox
source_kind
extraction_mode
parser_name
parser_version
parse_run_id
quality_status
review_status
created_at
updated_at
```

---

## 14. 推荐技术栈

### 14.1 第一阶段：Windows 原生、尽量简化

| 组件 | 用途 |
|---|---|
| Python 3.11 | 主语言 |
| `venv` 或 `uv` | 环境管理 |
| SQLite | 元数据、审核记录、来源关系 |
| SQLite FTS5 | 全文与关键词检索 |
| `RapidFuzz` | 模糊字符串检索与结果比较 |
| `pdftext` | 原生 PDF 主提取候选 |
| `pdfplumber` | 原生 PDF 验证与坐标调试 |
| PaddleOCR | 扫描页 OCR |
| Pillow / OpenCV | 图像预处理与质量检测 |
| Pydantic | 内部数据协议与 API schema |
| FastAPI | 本地 API 或轻量 Web 后端 |
| PySide6 / 简单 Web 前端 | 任选其一，用于审核界面 |

### 14.2 延后引入

| 组件 | 原因 |
|---|---|
| PostgreSQL | SQLite 在当前规模下足够先验证流程 |
| Qdrant | 先让 FTS + 模糊检索与来源链稳定 |
| 向量 embedding | 属于后续语义检索增强 |
| MinerU | 环境较重，优先用于高风险复杂页 |
| Docker、Redis、任务队列 | 一万页规模初期可用本地任务状态机处理 |
| 远程 LLM / 外部 API | 不属于核心路径 |

---

## 15. 目录结构建议

```text
tracedoc/
├─ README.md
├─ pyproject.toml
├─ data/
│  ├─ raw/
│  ├─ rendered_pages/
│  ├─ parser_outputs/
│  ├─ review_exports/
│  └─ app.db
├─ tracedoc/
│  ├─ ingest/
│  │  ├─ import_file.py
│  │  ├─ hashing.py
│  │  ├─ renderer.py
│  │  └─ page_router.py
│  ├─ parsers/
│  │  ├─ base.py
│  │  ├─ native_pdftext.py
│  │  ├─ native_pdfplumber.py
│  │  ├─ ocr_paddle.py
│  │  └─ normalize.py
│  ├─ quality/
│  │  ├─ native_compare.py
│  │  ├─ ocr_compare.py
│  │  ├─ risk_signals.py
│  │  └─ routing.py
│  ├─ structure/
│  │  ├─ page_blocks.py
│  │  ├─ headers_footers.py
│  │  ├─ footnotes.py
│  │  ├─ paragraphs.py
│  │  └─ cross_page_links.py
│  ├─ storage/
│  │  ├─ models.py
│  │  ├─ sqlite.py
│  │  └─ repository.py
│  ├─ retrieval/
│  │  ├─ fts.py
│  │  ├─ fuzzy.py
│  │  ├─ result_context.py
│  │  └─ filters.py
│  ├─ metadata/
│  │  ├─ extract_candidates.py
│  │  └─ enrich.py
│  ├─ review/
│  │  ├─ tasks.py
│  │  ├─ corrections.py
│  │  └─ page_preview.py
│  └─ api/
│     └─ app.py
├─ tests/
│  ├─ fixtures/
│  ├─ gold_set/
│  ├─ test_native_pdf/
│  ├─ test_ocr/
│  ├─ test_structure/
│  └─ test_retrieval/
└─ scripts/
   ├─ ingest.py
   ├─ reprocess.py
   └─ benchmark.py
```

---

## 16. 可靠度与审核

### 16.1 不把“置信度”当成黑箱概率

系统应收集多个可解释的风险信号：

```text
- 主解析文本与验证解析文本差异；
- 文字覆盖率差异；
- 行与 bbox 的位置差异；
- 阅读顺序冲突；
- 乱码、异常 Unicode 或字体映射问题；
- 页眉页脚、脚注、图注、表格存在；
- 图像占比过高；
- 页面末尾与下一页首块的段落连接不确定。
```

### 16.2 推荐的处理等级

```text
低风险：
自动进入 canonicalization，并按文献类型抽样审计。

中风险：
允许入库，但生成审核任务；不标记为“完全确认”。

高风险：
不进入正式证据索引，或仅作为未确认候选；要求人工审核或重跑。

不可处理：
保留原始文件与失败日志，标为 manual_review。
```

### 16.3 Gold set

在全面导入前，应建立约 200–500 页人工确认样本，覆盖：

- 原生文本单栏正文；
- 扫描单栏正文；
- 脚注与尾注；
- 章节标题；
- 跨页自然段；
- 罗马数字与阿拉伯数字页码；
- 英文与拉丁文混排；
- 表格和图注；
- 文本层存在但不可信的扫描 PDF。

Gold set 用于测试：

- 页面路由是否正确；
- 原生 PDF 双解析是否能发现问题；
- OCR 风险分流是否合理；
- PageBlock 定位是否稳定；
- 跨页链接误判率；
- 检索是否能找回正确来源。

---

## 17. 开发阶段

### Phase 0：小样本与协议

- 收集代表性样本；
- 建立 gold set；
- 定义 `ParsedPage`、`PageBlock`、`LogicalParagraph`；
- 试跑 pdftext、pdfplumber、PaddleOCR；
- 确认许可证与 Windows 安装路径。

### Phase 1：原生 PDF MVP

```text
PDF
→ 页面分类
→ pdftext 主提取
→ pdfplumber 验证
→ PageBlock
→ SQLite 保存
→ FTS5 + RapidFuzz 检索
→ 返回文件 + 页码 + 行附近上下文
```

### Phase 2：扫描 PDF 入口

```text
扫描 PDF / 图片
→ 渲染与质量检查
→ PaddleOCR
→ 交叉验证
→ PageBlock
→ 与 Native 路径统一入库
```

### Phase 3：结构化与审核

- 页眉、页脚、页码、脚注识别；
- 跨页 LogicalParagraph 链接；
- PageBlock 级人工审核；
- 页面图像 + bbox 高亮；
- 文献元数据候选补全。

### Phase 4：稳定批处理

- 断点续跑；
- 失败重试；
- 增量重跑；
- 审核统计；
- 导入队列与批处理进度；
- 解析器与规则版本管理。

### Phase 5：后续扩展

- 本地向量检索；
- 复杂表格、图注与更多版面类型；
- 多栏文档；
- 历史拼写扩展索引；
- 更丰富的 PDF 阅读与高亮体验。

---

## 18. MVP 成功标准

MVP 成功，当且仅当系统可以：

1. 在 Windows 原生环境中导入数千页至约一万页的文档；
2. 自动区分多数原生文本页与扫描页；
3. 不让原生 PDF 默认走 OCR；
4. 保存每个 PageBlock 的文件、页码、印刷页码和 bbox；
5. 对原生 PDF 使用双解析风险验证；
6. 对扫描页保留 OCR 原文、页面图像与质量状态；
7. 正确处理单栏正文与脚注的基本分离；
8. 支持跨页自然段作为多个 PageBlock 的逻辑链接；
9. 允许用户按关键词、短语和近似文本找到来源；
10. 默认返回命中行附近若干行及文件 + 页码；
11. 支持查看原始页面并可选高亮命中 bbox；
12. 允许人工确认、修订、拆分、合并和重跑高风险 PageBlock；
13. 不依赖对话式 LLM 或远程 API 才能完成核心功能。

---

## 19. 项目口号

> 不只把文档“读出来”，还要让每一行可被找到、定位、核验与修订。

