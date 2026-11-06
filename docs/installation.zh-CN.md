# 安装与启用

[English](installation.md) | **简体中文**

## 选择一种安装方式

需要客户端管理安装和升级时，使用原生插件或扩展；只需要可移植规则时，使用不带 Hook 和运行依赖的独立 Skill。每个客户端尽量只发现一份安装；共享的 `.agents/skills` 可能被多个客户端同时发现。

克隆 `https://github.com/Cyrus-terra/supercoding.git` 或解压 ZIP。下文命令从仓库根目录运行。仓库已包含客户端封装，但不代表已经进入官方市场、npm 或 ClawHub。

## 客户端兼容性

官方格式核对日期为 **2026-11-06**。各客户端的安装、调用、更新和排错分别说明：

| 客户端 | 仓库中的原生封装 | 安装专页 |
| --- | --- | --- |
| Claude Code | `.claude-plugin/` 和 marketplace | [Claude Code](clients/claude-code.zh-CN.md) |
| CodeBuddy | `.codebuddy-plugin/` 和 marketplace | [CodeBuddy](clients/codebuddy.zh-CN.md) |
| Codex | `.codex-plugin/` 和 `.agents/plugins/marketplace.json` | [Codex](clients/codex.zh-CN.md) |
| Gemini CLI | `gemini-extension.json` | [Gemini CLI](clients/gemini-cli.zh-CN.md) |
| Hermes Agent | `.hermes-plugin/` 清单和注册模块 | [Hermes](clients/hermes.zh-CN.md) |
| OpenClaw | `openclaw.plugin.json`、`package.json`、`index.js` | [OpenClaw](clients/openclaw.zh-CN.md) |

六种封装使用同一份[英文运行规则](../skills/supercoding/SKILL.md)。通过客户端使用 DeepSeek 等模型时，安装格式仍由客户端决定。打包或适配器检查不等于模型遵循验证，见[实际评测与边界（英文）](../tests/evals/protocol.md)。本机 Codex 可执行文件不完整、没有 Gemini CLI，这两个客户端的真实集成尚未验证。

## 验证证据

各层独立：**P**（打包/适配器测试）、**N**（宿主原生校验）、**L**（真实发现/生命周期）、**M**（成功完成模型任务）。目前本地证据如下：

| 客户端 | P | N | L | M |
| --- | --- | --- | --- | --- |
| Claude Code | 清单、Hook 输出和 POSIX 展开 | 此前通过 | 观察到命名空间发现与 Hook | API 连接阻塞 |
| CodeBuddy | 清单、Hook 输出和 POSIX 展开 | 此前通过 | 未评分 | 无交互工具权限阻塞 |
| Codex | 清单与 marketplace 契约 | 未运行 | 本机可执行文件不完整，未运行 | 未运行 |
| Gemini CLI | 清单与变量替换模拟 | 未运行 | 没有 CLI，未运行 | 未运行 |
| Hermes Agent | fake context 注册与首次提醒 | 未运行 | 未运行真实插件会话 | 未运行 |
| OpenClaw | 清单与无依赖 JS 导入 | 未运行 | 未运行 Gateway 发现 | 未运行 |

历史宿主/客户端观察不是对后续改动的重新验证。确定性适配器测试不能替代真实宿主运行。Windows Hook 启动、远端 CI、自动触发率和模型效果提升均需独立证据，详见[协议与历史记录（英文）](../tests/evals/protocol.md)。

## 独立 Skill 安装

将完整 `skills/supercoding/`（包括八份参考）复制到客户端的技能目录，保留已有目录和软链接。Windows 手动复制不需要 Python。最终结构应为 `skills/supercoding/SKILL.md`，不要多嵌套一个仓库目录。

| 客户端参数 | 默认用户级目标 |
| --- | --- |
| `claude` | `~/.claude/skills/supercoding` |
| `codebuddy` | `~/.codebuddy/skills/supercoding` |
| `codex` | `~/.agents/skills/supercoding` |
| `gemini` | `~/.gemini/skills/supercoding` |
| `hermes` | `~/.hermes/skills/supercoding` |
| `openclaw` | `~/.openclaw/skills/supercoding` |

使用 Python 3.9+ 时，管理工具提供受保护的安装，并将文件哈希记录在运行目录之外。选择**一个**客户端：

```sh
python3 -B scripts/manage.py install --client codex --source .
```

自定义 profile、仅项目使用、远程主机或容器，应显式指定 agent 实际运行位置：

```sh
python3 -B scripts/manage.py install --target "/absolute/project/.agents/skills/supercoding" --source .
```

已有目标会停止安装，不修改全局指令、信任配置或插件缓存。目标或祖先路径包含软链接时拒绝操作，应单独核对共享源并更新。macOS 临时目录如果通过系统 `/var` 软链接访问，请使用规范的 `/private/...` 路径；管理器会拒绝系统 `/tmp` 别名，安全检查必须使用规范临时路径。

## 可选会话插件

Claude Code 和 CodeBuddy 仍支持会话级本地加载：

```sh
claude --plugin-dir "/absolute/path/to/supercoding"
codebuddy --plugin-dir "/absolute/path/to/supercoding"
```

这不是永久安装。SessionStart 简短提醒只读取本地文件并输出 JSON，不联网更新、不扫描项目。Gemini 通过扩展 Hook 使用同一提醒，Hermes 使用自身的注册 Hook；Codex 和 OpenClaw 通过原生 Skill 注册加载规则，不使用这份 shell 提醒。

Hook 要求 `python3`（Python 3.9+）和兼容 shell。Windows Hook 启动未验证，不具备条件时使用独立 Skill。遵循客户端信任提示。

## 版本检查、更新和回退

**原生插件：**按客户端专页操作。刷新 marketplace 和更新已安装插件可能是两步；是否自动更新取决于宿主配置。supercoding 不会在启动时拉取代码。

**独立副本：**从可信源码运行 `scripts/manage.py`。`check` 和 `--dry-run` 不写本地文件；不带 `--source` 时查询 GitHub 最新稳定 Release：

```sh
python3 -B scripts/manage.py check --client codex
python3 -B scripts/manage.py update --client codex --dry-run
python3 -B scripts/manage.py update --client codex
```

Release 必须使用与入口版本一致的 `vX.Y.Z` 标签。工具将标签解析为不可变 commit，从有大小限制的归档中只读取九个运行文件。没有正式 Release 时明确报错，不回退到默认分支；网络和限流错误同样明确失败。需要离线使用本地源码：

```sh
python3 -B scripts/manage.py check --client codex --source .
python3 -B scripts/manage.py update --client codex --source . --dry-run
python3 -B scripts/manage.py update --client codex --source .
```

将 `--source` 换成 `--version X.Y.Z` 可选择指定的稳定 Release。更新拒绝降级，需要恢复旧版时使用保留的备份。

从手动复制版本首次迁移，或已安装文件发生修改，需要显式接受替换。先看预览，再执行：

```sh
python3 -B scripts/manage.py update --client codex --source . --replace
python3 -B scripts/manage.py rollback --client codex
```

`--replace` 不自动合并规则：它完整备份旧目录，安装新的标准文件。需要延续的定制内容应单独保存并决定是否重新应用。链接、特殊文件和超限文件会被拒绝，不会跟随或丢弃。

同级 `.supercoding-state/` 保存 receipt、备份、锁和事务记录。回退需要保留它，不要复制到 Skill 内。备份持续保留，清理或归档需自行明确执行。回退验证文件哈希，并保留被换下的版本；未管理的旧备份恢复后仍为未管理状态。规则变化后开启新会话。

### 操作中断

普通异常会尝试恢复旧安装。进程在两次目录重命名之间中断，可能留下 `transaction.json`；后续操作会检测它。执行 `rollback` 可恢复记录并验证过的备份，即使目标目录暂时不存在。进程退出后系统释放管理锁，不要通过删除锁或状态文件绕过正在运行的操作。

这是带事务记录的替换，不宣称断电安全或整个操作具有文件系统原子性。首次安装没有旧备份时中断，或状态/备份验证失败，应检查提示的 `.supercoding-state/` 并手动恢复；工具不会猜测或销毁数据。

## 所有编码任务默认使用

发现 Skill 不代表默认强制使用。将以下内容追加到客户端实际加载的指令文件，保留原有规则；安装不会自动写入：

| 客户端 | 用户级或项目级指令 |
| --- | --- |
| Claude Code | `~/.claude/CLAUDE.md` 或项目 `CLAUDE.md` |
| CodeBuddy | `~/.codebuddy/CODEBUDDY.md` 或项目 `CODEBUDDY.md` |
| Codex | 对应范围的 `AGENTS.md` |
| Gemini CLI | 对应范围的 `GEMINI.md` |
| Hermes / OpenClaw | 当前工作区或 profile 支持的上下文文件 |

```markdown
## supercoding

编写或修改代码前使用 supercoding，包括脚本、测试、构建配置和可运行示例；代码审查按需使用。
上下文已有完整且未变化的规则时直接沿用，否则调用实际可用 Skill 名称或读取 SKILL.md。
只读相关参考；微小任务可以只用入口。页面功能变更需要样式参考，已加载时直接复用。
在客户端约束内，用户明确要求与项目明确规范优先。只检查相关旧代码，不自动全仓审计或整改。
纯 README、文档、报告编写、翻译和普通交流不触发。混合任务仅对编码部分应用规范。
```

插件可能暴露 `supercoding:supercoding`，独立安装通常为 `supercoding`，以实际名称为准。这是 agent 指令，不是写入拦截或额外工具授权。

## 语言与验证

运行规则和参考统一英文，回复跟随用户语言。README 和安装说明双语，维护与评测材料英文。

新会话中确认只有一份入口，用小编码任务观察按需加载，再用同类任务检查上下文复用；用纯文档润色和翻译检查不会触发。这些模型行为需实际观察，确定性打包测试不能替代。

## 安装排错

| 现象 | 处理 |
| --- | --- |
| 没发现 Skill | 检查完整结构、当前 profile/workspace、允许列表和禁用项，按宿主要求重启或刷新。 |
| 重复规则或提醒 | 比较独立、项目、插件和共享路径，再移除已确认重复项。 |
| 已有目标 | 使用 `check` / `update --dry-run`，首次安装命令不能当升级命令。 |
| 未管理或有修改 | 先审阅差异，再显式 `update --replace`，完整保留备份。 |
| 软链接被拒绝 | 检查共享源及使用者，单独更新源，不替换软链接。 |
| 没有稳定 Release / 离线 | 使用可信本地源码的 `--source`，不会静默回退分支。 |
| 锁或未完成事务 | 等当前操作完成；进程中断后通过已验证回退恢复，不删除状态。 |
| 仍是旧行为 | 核对实际加载路径，通过宿主升级或独立工具更新后启动新会话。 |
| Hook 失败 | 检查 Python、shell、信任及路径展开；独立 Skill 不要求 Hook。 |

反馈问题时记录客户端版本、OS、安装模式、相关路径、步骤和原始错误，不附带凭证或私密内容。
