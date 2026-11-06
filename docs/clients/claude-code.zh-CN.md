# Claude Code

[English](claude-code.md) | **简体中文**

## 推荐安装

需要长期使用时，推荐独立 Skill：将 `skills/supercoding/` 复制到 `~/.claude/skills/supercoding/`，保留九个运行文件。需要会话提醒时，可加载仓库插件：

```sh
claude --plugin-dir "/absolute/path/to/supercoding"
```

新增打包推送后，可在 Claude Code 中执行以下命令持久安装（本地测试时将 `Cyrus-terra/supercoding` 换为源码绝对路径）：

```text
/plugin marketplace add Cyrus-terra/supercoding
/plugin install supercoding@supercoding
/plugin marketplace update supercoding
/plugin update supercoding@supercoding
```

前两条安装，后两条分别刷新 marketplace 和更新已安装插件。自动升级由 Claude 的市场设置控制，不是 Skill 自行升级。这些操作不会移除原有独立副本，应先比较重复安装。

## 更新和检查

独立复制不会自动更新。先比较来源，再使用仓库中的管理脚本：

```sh
python3 scripts/manage.py check --target "$HOME/.claude/skills/supercoding" --source .
python3 scripts/manage.py update --target "$HOME/.claude/skills/supercoding" --source . --dry-run
```

有可用命令时，对插件源运行 `claude plugin validate`；更新后启动新会话。没有确认差异前，不要用 `--replace` 覆盖定制内容。

## 限制

Hook 只读，不扫描项目、不联网更新，也不修改全局指令。需要固定来源时，使用已审阅 tag/commit 的本地 checkout 和 marketplace，不假设宿主统一提供固定版本参数。打包检查不能证明模型遵循。

官方依据：[Claude 插件参考](https://code.claude.com/docs/en/plugins-reference)。本机可验证插件和 marketplace；此前模型调用因连接失败未完成。
