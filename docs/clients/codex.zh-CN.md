# Codex

[English](codex.md) | **简体中文**

## 原生插件

仓库包含 `.codex-plugin/plugin.json` 和 `.agents/plugins/marketplace.json`。添加仓库 marketplace 后，在 `/plugins` 或客户端 marketplace 界面安装 `supercoding`：

```text
codex plugin marketplace add Cyrus-terra/supercoding
codex plugin marketplace upgrade
codex
/plugins
```

仓库已包含对应封装。本地测试可用 `codex plugin marketplace add /absolute/path/to/supercoding`。这是仓库自带市场，不代表进入官方市场。用 `codex plugin marketplace upgrade supercoding` 刷新来源后，还要在 `/plugins` 检查已安装插件；刷新市场不等于安装副本已经变化。

## 独立 Skill

将 `skills/supercoding/` 复制到 `~/.agents/skills/supercoding/` 或 `<project-root>/.agents/skills/supercoding/`，使用 `/skills` 或 `$supercoding` 加载：

```sh
python3 scripts/manage.py check --client codex --source .
python3 scripts/manage.py update --client codex --source . --dry-run
```

Codex marketplace 的刷新和插件升级由客户端管理。插件更新后启动新会话。模型选择不决定 Skill 的安装路径。已有对应 ref 时，可通过 marketplace 的 `--ref <tag-or-commit>` 固定来源，不将最新分支提交当成稳定 Release。

## 证据分层

**P：**确定性清单/marketplace 契约。**N/L/M：**未运行；本机可执行文件不完整，未完成原生校验、发现和模型任务。存在启动入口不等于集成通过，详见[共用矩阵](../installation.zh-CN.md#验证证据)。

官方依据：[插件封装和 marketplace](https://developers.openai.com/plugins/build/plugins.md)、[Skill 编写](https://learn.chatgpt.com/docs/build-skills)。本地封装检查通过，但 Codex 原生可执行文件缺失，客户端发现尚未验证。
