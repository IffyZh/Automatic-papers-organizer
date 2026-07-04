# TraceDoc 开发环境：项目内 `.venv`

> 这份说明写给开发初学者。它规定：TraceDoc 的开发、安装依赖、测试和运行命令，都使用仓库根目录里的 `.venv`，而不是系统默认 Python。

## 为什么要这样做？

一台电脑可以同时装 Python 3.11、3.14，甚至更多版本。不同项目也可能需要不同的软件包版本。

如果直接使用裸命令：

```powershell
python -m pytest
pip install <package>
```

Windows 可能会把它们交给系统默认 Python，而不是 TraceDoc 所需的 Python 3.11。这会造成“明明装过依赖却找不到”“测试在错误版本里通过”的混乱。

`.venv` 是项目专用的小隔离环境。它位于仓库根目录，但不会被提交到 Git。

## 当前项目约定

- 推荐 Python：3.11.x。
- 项目专用解释器：`.venv\Scripts\python.exe`。
- `.venv/` 已被 `.gitignore` 忽略，不会上传到 GitHub。
- 系统 Python 3.14 可以保留给其他用途；它不需要卸载。

## 第一次创建环境

在仓库根目录打开 PowerShell，使用已安装的 Python 3.11 创建环境：

```powershell
py -3.11 -m venv .venv
```

然后安装项目和开发工具：

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

> `-e` 的意思是“可编辑安装”：修改项目代码后，通常不需要重新安装项目本身。

## 每次开发前的自检

在开始任何 Codex 任务或手动执行命令前，先运行：

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip --version
```

预期结果：

- Python 显示 `3.11.x`；
- pip 的路径包含 `.venv`。

若其中一项不符合，不要继续安装依赖或运行测试；先修正环境。

## 日常命令：推荐写法

始终明确写出 `.venv` 内的 Python：

```powershell
.\.venv\Scripts\python.exe -m tracedoc doctor
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
```

这是最不容易出错的方式，因为它不会依赖终端的 PATH 设置。

## 可选：激活环境后使用简写

也可以在 PowerShell 中运行：

```powershell
.\.venv\Scripts\Activate.ps1
```

如果终端前出现 `(.venv)`，此时可以简写为：

```powershell
python -m tracedoc doctor
python -m pytest
```

退出环境：

```powershell
deactivate
```

但若 PowerShell 阻止激活脚本，直接使用上一节的完整路径即可；不需要修改系统安全设置。

## 给 Codex 的固定要求

每一份后续任务书都应包含：

```text
开始前必须执行：
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip --version

后续所有安装、测试、静态检查与项目命令必须使用：
.\.venv\Scripts\python.exe -m ...

不要使用裸 python、pip、pytest 或 ruff 命令，
除非先证明它们指向仓库根目录的 .venv。
不要创建第二个虚拟环境。
```

## 出现问题时保留什么？

请保留以下信息再求助：

1. 你运行的完整命令；
2. 完整报错输出；
3. ` .\.venv\Scripts\python.exe --version` 的输出；
4. ` .\.venv\Scripts\python.exe -m pip --version` 的输出；
5. 当前 Git 分支名。
