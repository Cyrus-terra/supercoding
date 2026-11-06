# OpenClaw

[English](openclaw.md) | **简体中文**

## 原生插件

仓库包含 `openclaw.plugin.json` 和无依赖的 `index.js`。可从 Git 或本地源码安装：

```sh
openclaw plugins install git:github.com/Cyrus-terra/supercoding
openclaw plugins list
openclaw plugins inspect supercoding
openclaw plugins update supercoding
```

本地开发可改用 `openclaw plugins install --link /absolute/path/to/supercoding`，审阅信任提示，不绕过检查。Git 安装需要先推送打包；本地链接跟随源码内容，但不会拉取 Git 更新。插件暴露共享的 `skills/` 目录。更新按 Gateway 的 reload 行为生效；必要时使用 `openclaw plugins inspect supercoding --runtime --json`，并启动新对话。本仓库不宣称已发布 npm 或 ClawHub 包。

## 独立 Skill

将 `skills/supercoding/` 复制到当前 agent 的 `skills/supercoding/`，使用 `openclaw skills list` 和 `openclaw skills check` 检查。使用已检出的源码更新：

```sh
python3 scripts/manage.py check --client openclaw --source .
python3 scripts/manage.py update --client openclaw --source . --dry-run
```

managed、workspace 和插件路径可能存在优先级，不检查清楚前不要保留多个副本。新版支持 Git `@<tag-or-commit>` 选择器，依赖新版语法前先查看已装版本帮助。管理器默认路径为 `~/.openclaw/skills/supercoding`，不一定是单个 agent 的工作区。

官方依据：[插件安装更新](https://docs.openclaw.ai/tools/plugin)、[manifest](https://docs.openclaw.ai/plugins/manifest)。本机为 2026.5.7，可能与当前文档不同；metadata 和较长 description 的解析、真实 Gateway 发现存在版本差异，JS 入口/清单检查不等于 Gateway 实测。
