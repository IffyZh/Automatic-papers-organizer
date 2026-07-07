# Gold Set 人工标注手册

> 目标不是把每一页变成完美数字文本，而是为未来工具比较建立一份诚实、可复查的参照。

## 1. 标注顺序

对每个候选页面按以下顺序工作：

1. 打开原 PDF，确认它在 PDF 阅读器中显示的页序号；
2. 记录印刷页码；若没有、看不清或不一致，写 `null` 或在 notes 说明；
3. 判断主输入类型；
4. 记录页面对象与风险标签；
5. 给出人工页面路由结论；
6. 只标少量关键 PageBlock，不追求全页逐字；
7. 为每个关键块摘录短小、人工核对过的文字；
8. 把不确定性写下来。

## 2. 主输入类型

只能选一个：

| 值 | 何时使用 |
|---|---|
| `native_text` | PDF 中的文字是可选择、总体可信的真实文本对象。 |
| `ocr_required` | 页面主要是扫描图像，不能依靠现有文本层。 |
| `text_layer_untrusted` | 页面有可选择文本，但它明显是错误或不可靠的 OCR 层。 |
| `hybrid` | 同页存在可信文字对象和需要 OCR 的图像文字，或混合情况无法简单归类。 |
| `manual_review` | 页面状况无法可靠判断，先保留给人工。 |

注意：能复制文字不等于 `native_text`。错误 OCR 也可能被嵌进 PDF 文本层。

## 3. 页面路由结论

| 值 | 意义 |
|---|---|
| `native_text` | 后续应先走原生文本提取路径。 |
| `ocr_required` | 后续应走 OCR 路径。 |
| `hybrid_review` | 后续应同时保留多种证据或进入审核。 |
| `manual_review` | 后续不要自动接受。 |

输入类型描述“页面看起来是什么”；路由结论描述“系统应该怎样处理它”。两者可以不同。

## 4. 常用风险标签

可多选：

```text
footnotes
endnotes
header
footer
page_number
roman_numeral_page_number
arabic_page_number
chapter_title
section_title
cross_page_paragraph_candidate
table
caption
sidebar
external_link_text
ocr_errors
bad_unicode
font_mapping_problem
bad_reading_order
hyphenation
latin_mixed
image_heavy
uncertain_bbox
```

不在列表内的新问题可以使用清晰、简短的新标签，但应在 `notes` 中解释。

## 5. PageBlock 标注

一个 PageBlock 是某一页上的一个局部对象。它绝不跨页。

建议先标：

- 一个正文块；
- 一个脚注/尾注块（如有）；
- 一个最困难或最能代表风险的块；
- 标题、页码或表格区域（若它正是样本被选入的理由）。

### bbox 是什么？

`bbox_pdf_points` 是矩形位置：

```text
[left, top, right, bottom]
```

单位是 PDF point。若无法可靠获得坐标：

```json
"bbox_pdf_points": null,
"bbox_status": "pending_manual_measurement"
```

这是完全可接受的。不要为了填表而猜测坐标。

## 6. 文字摘录规则

- 摘录 1–4 句或一个短段即可；
- 人工检查原页后再录入；
- 保留历史拼写、拉丁文、罗马数字和可见脚注标记；
- 不要把摘录“润色成现代英语”；
- 看不清的字符可用 `[unclear]`，并在 notes 中说明；
- 不要求手工转录整页。

## 7. 表格、边栏和链接

- 表格：标 `table` 区域，说明是否值得后续保留；不重建单元格。
- 边栏：标 `sidebar`。若阅读顺序不明确，标 `ambiguous`。
- 外部链接：只标 `external_link_text`；不要在 P0-2 点击、验证或爬取链接。

## 8. 不确定性不是失败

以下写法是好的标注：

```text
reading_order_status: ambiguous
review_required: true
page_notes: Footnote column visually overlaps the lower body paragraph.
```

以下写法不好：

```text
reading_order_status: clear
page_notes: Probably fine.
```

Gold Set 的价值不在于假装所有页面都有唯一答案，而在于把真实不确定性保留下来。

## 9. 完成一批页面前的检查

- 每页有独一无二的 `sample_id`；
- 每个文件有 SHA-256；
- PDF 页序号使用从 0 开始的 `pdf_page_index`；
- 印刷页码单独记录，不与 PDF 页序号混淆；
- 主输入类型只选一个；
- 路由结论、风险标签和 notes 不互相矛盾；
- 没有真实 PDF、截图或 OCR 大输出被提交到 Git；
- 不确定处被明确记录。
