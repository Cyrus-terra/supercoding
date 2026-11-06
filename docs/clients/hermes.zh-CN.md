# Hermes Agent

[English](hermes.md) | **简体中文**

## 原生插件

仓库包含 `.hermes-plugin/plugin.yaml` 和注册模块。通过 Hermes 安装并启用：

```sh
hermes plugins install Cyrus-terra/supercoding --enable
hermes plugins list
hermes plugins update supercoding
```

插件注册按需 Skill `supercoding:supercoding`。安装或更新后启动新会话。新版提供 `hermes plugins doctor`，旧版使用 `hermes plugins list` 和启动诊断。远程安装需要先推送新增适配器。本地测试只在目标不存在时，将源码复制到当前 profile 的插件目录并显式启用，不覆盖已安装插件。

## 独立 Skill

默认 profile 将 `skills/supercoding/` 复制到 `~/.hermes/skills/supercoding/`，自定义 profile 使用其实际目录。用 `hermes skills list` 检查，新会话或 `/reset` 后通过 `/supercoding` 加编码任务调用。独立安装不使用插件的命名空间名称。使用源码更新副本：

```sh
python3 scripts/manage.py check --client hermes --source .
python3 scripts/manage.py update --client hermes --source . --dry-run
```

插件不会把运行状态写入安装目录，也不会在 `pre_llm_call` 中自动更新自身。本机 update 命令拉取已安装来源，不宣称所有版本都提供固定 ref 参数；需要可复现时使用经过审阅的固定 checkout 或独立来源。

官方依据：[Hermes 插件和随附 Skill](https://hermes-agent.nousresearch.com/docs/developer-guide/plugins)。隔离 fake context 已覆盖注册和首次提醒，真实 Hermes 模型会话尚未验证。
