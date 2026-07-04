# 初学者从这里开始：TraceDoc 的第一步

这份说明写给项目维护者，不要求你会 Python、Git 或软件工程。

## 1. 你现在拥有什么？

目前仓库里有两类东西：

- `README.md`：TraceDoc 将来要成为怎样的系统；
- `docs/00_project_control/`：把大目标拆成很多小任务的施工说明。

现在还没有真正的软件功能。这是正常的。第一项任务只会生成一个很小的命令：

```text
python -m tracedoc doctor
```

这个命令不是“医生 AI”，也不是 OCR。它只是检查你的项目环境：Python 是否正确、SQLite 是否存在、FTS5 是否可用、项目数据目录是否可写。

## 2. 重要文件分别做什么？

| 文件 | 用人话解释 |
|---|---|
| `README.md` | 项目的总体蓝图：最终要做什么、暂时不做什么。 |
| `AGENTS.md` | 给 Codex 的长期规则。每次编码前都应阅读。 |
| `CODEX_WORK_PROTOCOL.md` | 你该怎样把任务交给 Codex，避免它乱扩建。 |
| `PHASE_0_BOOTSTRAP.md` | 第一项编码任务：生成最小项目骨架和 `tracedoc doctor`。 |
| `pyproject.toml` | 以后由 Codex 创建；Python 项目的名称、版本、依赖和工具配置。 |
| `.gitignore` | 以后由 Codex 创建；告诉 Git 哪些本机生成物不应上传。 |
| `tracedoc/` | 以后由 Codex 创建；真正的 Python 代码包。 |
| `tests/` | 以后由 Codex 创建；自动测试，防止改一处坏一处。 |
| `data/` | 本机运行时的文献、数据库、渲染图片等数据位置；真实大文件不提交到 Git。 |

## 3. 你不需要现在做什么？

现在不用：

- 安装 Docker；
- 安装 Oracle；
- 安装 PostgreSQL 或向量数据库；
- 下载本地大模型；
- 下载 OCR 模型；
- 创建数据库；
- 准备数千页真实文献；
- 学会所有 Git 命令。

这些事情会在对应阶段、确认确有必要后才逐项加入。第一项任务甚至不读取 PDF。

## 4. 你怎样让 Codex 开始第一项任务？

建议分两步，而不是一句“直接做完”。

### 第一步：只让它复述理解

把下面文字发送给 Codex：

```text
请阅读以下文件：
- AGENTS.md
- docs/00_project_control/PHASE_0_BOOTSTRAP.md
- README.md 的第 1、2、14、15、17 节

暂时不要修改文件，也不要安装依赖。
请用简短条目复述：
1. P0-1 的目标；
2. 本任务允许创建哪些文件；
3. 本任务明确禁止做什么；
4. 需要运行哪些验收命令；
5. 你准备怎样保持运行时依赖为零。
```

它的回答应该明确提到：只搭项目骨架、只做 `tracedoc doctor`、不做 PDF/OCR/数据库/UI、不用 Docker 或重型环境。

### 第二步：确认后让它实施

当它复述正确后，再发送：

```text
你的理解正确。请严格实施 P0-1。
从 main 创建分支 feat/p0-1-project-bootstrap；不要超出任务书范围。
完成后运行任务书中的验收命令，创建指向 main 的 PR，并在 PR 说明中列出：修改文件、依赖、测试结果和明确未做事项。
```

## 5. 做完后你应该看什么？

你不需要逐行读代码。先查看四件事：

1. PR 是否只包含任务书允许的少量文件；
2. `pyproject.toml` 是否只引入开发依赖 `pytest` 与 `ruff`，没有运行时大依赖；
3. PR 是否写明以下命令已通过：
   - `python -m pytest`
   - `python -m ruff check .`
   - `python -m tracedoc --help`
   - `python -m tracedoc doctor`
4. 是否没有出现 Dockerfile、OCR 模型、PDF 解析器、数据库服务、Web 前端等超范围内容。

之后把 PR 链接或 Codex 的完成报告发给我。我会按任务书审查内容、检查是否过度设计，并说明哪些结果可以合并。

## 6. 发生报错时怎么办？

不要急着让 Codex“全部重写”。保留：

- 你执行的完整命令；
- 命令输出的完整报错；
- 当前分支名；
- 对应 PR 链接；
- 你使用的 Python 版本。

把这些给我或 Codex。绝大多数早期问题都只是环境、路径或项目配置问题，不意味着整个设计失败。
