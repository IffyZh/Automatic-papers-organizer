# 项目控制文档索引

这里放的是“怎样维护和推进 TraceDoc 项目”的说明，不是 PDF/OCR 的实现代码。

## 先读什么？

| 你要做的事 | 先读的文件 |
|---|---|
| 第一次接手项目，想知道总体目标 | 仓库根目录 `README.md` |
| 让 Codex 做任何改动 | `AGENTS.md` |
| 不知道怎样给 Codex 下任务 | `CODEX_WORK_PROTOCOL.md` |
| 不知道 Python、`.venv`、测试命令是什么 | `DEVELOPMENT_ENVIRONMENT.md` |
| 想看当前正在做的任务 | `PHASE_0_BOOTSTRAP.md` 或后续任务书 |
| 完全没有开发经验 | `BEGINNER_START_HERE.md` |

## 项目环境的硬规则

TraceDoc 的开发环境是仓库根目录中的 `.venv`，目标 Python 为 3.11.x。

以后执行命令时优先使用：

```powershell
.\.venv\Scripts\python.exe -m <命令>
```

例如：

```powershell
.\.venv\Scripts\python.exe -m tracedoc doctor
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
```

不要直接使用裸 `python`、`pip`、`pytest` 或 `ruff`，除非已经确认它们指向本项目的 `.venv`。

## 为什么不把环境目录上传到 GitHub？

`.venv` 是每台电脑自己生成的环境，里面包含该电脑上的 Python 路径和安装包。它应被 `.gitignore` 忽略。

GitHub 保存的是：

- 代码；
- 文档；
- 依赖清单；
- 测试；
- 让另一台电脑能重新创建相同环境的说明。

GitHub 不保存：

- `.venv` 本体；
- 本地文献 PDF；
- OCR 模型；
- SQLite 数据库；
- 渲染页图像与缓存。
