# P0-1：项目骨架与 `tracedoc doctor`

> 给初学者的一句话说明：这项任务不处理 PDF，也不做 OCR。它先给项目搭一个干净的空房子，并增加一个检查本机环境是否准备好的命令。

## 1. 为什么先做这个？

以后会加入 PDF 提取、OCR、数据库和检索。先固定目录、测试入口和依赖规则，能避免不同环境、临时脚本和数据文件混在一起。

`tracedoc doctor` 是基础体检命令：它检查 Python、SQLite、FTS5 和运行时数据目录；不读取 PDF，不访问网络。

## 2. 开始前阅读

- `AGENTS.md`
- 本文件
- `README.md` 的第 1、2、14、15、17 节

本任务不要实现 README 中关于 OCR、页面路由、审核 UI、元数据和向量检索的内容。

## 3. 任务目标

在 Windows 原生 Python 3.11 环境中，让下列命令可运行：

```text
python -m tracedoc doctor
```

它必须清楚报告：

1. 当前 Python 可执行文件与版本；
2. 当前 SQLite 版本；
3. SQLite 是否实际支持 FTS5；
4. 项目根目录下 `data/` 是否存在；不存在时应创建或说明结果；
5. 成功、警告或失败原因。

没有 PDF、OCR 模型、数据库文件和网络连接时，该命令仍必须可运行。

## 4. 允许创建的目录与文件

```text
pyproject.toml
.gitignore
.python-version                 # 可选；内容为 3.11

tracedoc/
├─ __init__.py
├─ __main__.py
├─ cli.py
└─ diagnostics.py

tests/
├─ __init__.py
└─ test_diagnostics.py

docs/01_gold_set/README.md
data/README.md
scripts/README.md
```

职责建议：

- `__main__.py`：使 `python -m tracedoc ...` 可执行；
- `cli.py`：只解析 `doctor` 命令和帮助信息；
- `diagnostics.py`：诊断逻辑，尽量返回结构化结果，方便测试；
- `data/README.md`：解释该目录是本机运行数据，不应提交真正文献与生成物。

## 5. 实现限制

- 命令行只使用标准库 `argparse`。
- 诊断只使用标准库，如 `sys`、`sqlite3`、`pathlib`、`platform`。
- FTS5 必须在内存 SQLite 中实际尝试创建虚拟表，不能只假设存在。
- 默认数据目录为项目根目录的 `data/`。
- Python 目标版本为 3.11。
- 运行时依赖必须为零。
- 开发依赖只允许 `pytest` 与 `ruff`。
- 使用 `pyproject.toml` 管理项目和开发依赖。

初学者注释：

- `pyproject.toml`：项目说明书，记录名称、版本、依赖和工具设置。
- `pip install -e .`：可编辑安装；改代码后通常不必再次安装。
- `pytest`：自动测试工具。
- `ruff`：检查常见代码问题与格式问题的工具。

## 6. 明确禁止

不得在本任务中加入或实现：

- PDF 导入、页面渲染、PDF 文本提取、OCR、页面路由、检索、数据库 schema、Web API、GUI；
- Docker、WSL、Oracle、PostgreSQL、Qdrant、Redis、FastAPI、PySide6；
- PaddleOCR、Tesseract、pdftext、pdfplumber、PyMuPDF、Docling、OpenCV、Pillow；
- 本地大模型、embedding、向量数据库、远程 API；
- 真实文献、模型、缓存、数据库文件或大样本；
- 为未来阶段预建大量空模块。

## 7. `.gitignore` 最低要求

需包含有简短注释的规则，忽略：

```text
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
.venv/
venv/
.env

# Runtime data generated locally
data/raw/
data/rendered_pages/
data/parser_outputs/
data/review_exports/
data/*.db
data/*.sqlite
data/*.sqlite3

# Logs and temporary files
*.log
tmp/
.cache/
```

不得忽略 `data/README.md`、`docs/` 或 `tests/`。

## 8. 自动测试

至少测试：

- 诊断逻辑能返回结构化结果；
- 返回 Python 版本、SQLite 版本和 FTS5 检查结果；
- 测试用临时目录可作为数据目录被创建或识别；
- `python -m tracedoc doctor` 返回成功，并输出 `TraceDoc`、`Python`、`SQLite`、`FTS5`；
- `python -m tracedoc --help` 返回成功。

测试不能依赖网络、真实 PDF、OCR 模型或用户目录。

## 9. 验收命令

```text
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
python -m tracedoc --help
python -m tracedoc doctor
```

若开发依赖安装写法需要调整，必须解释原因并维持轻量方案。

## 10. 分支与交付

- 新分支：`feat/p0-1-project-bootstrap`
- 建立指向 `main` 的 PR。
- PR 标题建议：`feat: bootstrap TraceDoc and add doctor command`
- PR 说明必须列出：修改文件、依赖、验证结果、明确未实现的内容。
