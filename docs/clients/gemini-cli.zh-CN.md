# Gemini CLI

[English](gemini-cli.md) | **简体中文**

## 原生扩展

仓库包含 `gemini-extension.json`，Gemini 会发现共享的 `skills/` 目录。可从仓库或发布源安装：

```sh
gemini extensions install https://github.com/Cyrus-terra/supercoding
# Git 来源需要自动刷新时，可加 --auto-update。
gemini extensions update supercoding
```

更新要重启 Gemini CLI 会话后才生效。使用 `/extensions list` 检查扩展；工作区本地激活前需要信任工作区。

## 独立 Skill

将 `skills/supercoding/` 复制到 `~/.gemini/skills/supercoding/` 或可信项目的 skills 目录。变更后使用 `/skills list` 和 `/skills reload`。比较本地源码：

```sh
python3 scripts/manage.py check --client gemini --source .
python3 scripts/manage.py update --client gemini --source . --dry-run
```

共享 SessionStart Hook 只输出简短编码提醒，不执行扩展更新；源码复制和更新由 Gemini 管理器负责。本地开发可用 `gemini extensions install /absolute/path/to/supercoding` 测试本地源码，不安装全局上下文文件或权限。需要固定来源时用 `--ref <tag-or-commit>`，是否加入 `--auto-update` 由用户明确选择。

## 证据分层

**P：**清单检查和 shell 变量替换模拟。**N/L/M：**没有 Gemini CLI，均未运行。模拟不能证明 Gemini 真实展开或扩展激活，详见[共用矩阵](../installation.zh-CN.md#验证证据)。

官方依据：[扩展格式与生命周期](https://geminicli.com/docs/extensions/reference/)。本机没有 Gemini CLI，shell 和配置检查不能替代真实启用测试。
