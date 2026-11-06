# CodeBuddy

[English](codebuddy.md) | **简体中文**

## 推荐安装

需要长期使用时，将 `skills/supercoding/` 复制到 `~/.codebuddy/skills/supercoding/`。需要会话提醒时加载仓库插件：

```sh
codebuddy --plugin-dir "/absolute/path/to/supercoding"
```

新增打包推送后可在 CodeBuddy 中持久安装，本地测试则添加源码绝对路径：

```text
/plugin marketplace add Cyrus-terra/supercoding
/plugin install supercoding@supercoding
/plugin marketplace update supercoding
/plugin update supercoding@supercoding
```

后两条分别刷新元数据和更新安装副本。是否自动更新由 CodeBuddy 配置决定，Hook 不下载代码。避免再保留一份独立安装。

## 更新和检查

独立文件是快照，更新前先检查并预览：

```sh
python3 scripts/manage.py check --target "$HOME/.codebuddy/skills/supercoding" --source .
python3 scripts/manage.py update --target "$HOME/.codebuddy/skills/supercoding" --source . --dry-run
```

有可用命令时运行 `codebuddy plugin validate`。更新后启动新会话。未管理或被修改的目标必须显式使用 `--replace`；符号链接目标会被拒绝。

## 限制

插件提醒只读，不授予额外权限，不自动审计仓库，也不会静默更新安装。固定来源可使用已审阅 tag/commit 的本地 checkout 和 marketplace。清单与 marketplace 通过本机客户端校验；此前无头实现案例被工具权限阻止，不能算完成模型评测。

命令和格式依据 CodeBuddy 随客户端安装的插件及 marketplace 文档核对；版本不同时以本机帮助为准。
