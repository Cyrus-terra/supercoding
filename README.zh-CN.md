# supercoding

[English](README.md) | **简体中文**

**面向 AI 编码助手的开发规范：复用已有能力，保持改动精简，关注性能与页面质量。**

适用于前端、后端、脚本、测试和构建配置。沿用项目技术栈，指导助手处理搜索结果乱序、接口数据过大、业务规则复用、loading 和页面布局等实际工程问题。

一个轻量入口，八份按需参考。上下文已有且未变化的规则直接沿用，微小修改可以只使用入口。纯 README、文档编写、翻译和普通交流不触发。

## 按客户端安装

每个客户端选择**一种**原生插件/扩展或独立 Skill。六个客户端使用同一套规则；通过支持的客户端使用 DeepSeek 等模型时，安装格式不变。

| 客户端 | 可用安装方式 | 操作说明 |
| --- | --- | --- |
| Claude Code | marketplace 插件、本地会话插件、独立 Skill | [Claude Code](docs/clients/claude-code.zh-CN.md) |
| CodeBuddy | marketplace 插件、本地会话插件、独立 Skill | [CodeBuddy](docs/clients/codebuddy.zh-CN.md) |
| Codex | 仓库 marketplace 插件、独立 Skill | [Codex](docs/clients/codex.zh-CN.md) |
| Gemini CLI | 原生扩展、独立 Skill | [Gemini CLI](docs/clients/gemini-cli.zh-CN.md) |
| Hermes Agent | 原生插件、独立 Skill | [Hermes](docs/clients/hermes.zh-CN.md) |
| OpenClaw | 原生插件、独立 Skill | [OpenClaw](docs/clients/openclaw.zh-CN.md) |

本地安装、测试或管理独立副本时，先获取源码：

```sh
git clone https://github.com/Cyrus-terra/supercoding.git
cd supercoding
```

例如，使用 Python 3.9+ 为 Codex 安装受管理的独立副本：

```sh
python3 -B scripts/manage.py install --client codex --source .
```

没有 Python 时，手动将 `skills/supercoding/` 复制到客户端技能目录，保留已有安装；默认路径、Windows、项目级范围和默认启用见[共用安装指南](docs/installation.zh-CN.md)。原生插件由宿主管理。新增打包必须推送后远程安装命令才能获取；本仓库不宣称已经进入官方市场、npm 或 ClawHub。

## 首次使用

新建客户端会话，确认 `supercoding` 或 `supercoding:supercoding` 可用，然后尝试：

```text
使用 supercoding 给订单页增加状态筛选。
复用现有请求层和组件，处理分页、loading、失败状态，
并检查新增控件与原页面布局的关系。
```

发现 Skill 不等于每次编码都使用。需要默认启用时，将[编码指令](docs/installation.zh-CN.md#所有编码任务默认使用)加入客户端实际加载的上下文文件。中英文任务共用英文规则，回复跟随你的语言偏好。

## 更新，不静默覆盖

原生插件/扩展通过客户端更新，自动升级取决于宿主配置。会话 Hook 不联网检查或安装更新。

独立副本支持只读检查和预览、验证后完整备份更新、保护自定义内容以及回退：

```sh
python3 -B scripts/manage.py check --client codex
python3 -B scripts/manage.py update --client codex --dry-run
python3 -B scripts/manage.py update --client codex
python3 -B scripts/manage.py rollback --client codex
```

上述联网命令需要对应的稳定 GitHub Release。正式发布前或离线使用时，在检查/更新命令后加 `--source .`，从可信本地源码读取。手动或定制安装在审阅后需要显式 `update --replace`；工具拒绝软链接。见[更新与恢复说明](docs/installation.zh-CN.md#版本检查更新和回退)。

## 具体管什么

| 方向 | 实际规范 |
| --- | --- |
| 复用与精简 | 先找现有能力，提取稳定共同规则，保持职责边界，避免万能组件和假设性抽象。 |
| 接口与数据 | 复用请求层，在数据源分页，按需取字段，关注 N+1、事务、幂等和权限。 |
| 异步与交互 | 合适范围的 loading 和错误反馈，防响应乱序和重复提交，保持筛选、分页及选择一致。 |
| 页面质量 | 每次页面功能变更都检查布局、样式作用域、设计变量、长文本、支持宽度、焦点和交互状态。 |
| 性能与验证 | 限制数据与并发规模，按实际需要选择流式处理、缓存或懒加载，用相关检查和测量支持结论。 |

[运行入口（英文）](skills/supercoding/SKILL.md)直接链接八份参考。助手先看项目约束与相关代码，再读必要规则，完成最小完整改动并验证。本 Skill 不额外强制 TDD、多代理、worktree 或审批流程。

## 旧项目怎么处理

在客户端系统、安全和权限约束内，用户明确要求与项目明确规范优先于通用 Skill。沿用现有技术栈、请求层和设计系统；旧代码缺陷不会因保持一致而成为规范。

打开项目不会自动审计。编码时只检查相关旧代码，新增与修改部分应用规范。全面审查需要明确提出，仅授权审查不等于授权修复。

## 验证与维护

```sh
python3 -B scripts/validate_skill.py
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
```

确定性检查覆盖打包、本地链接、共享规则完整性、适配器和独立更新/恢复行为，不能证明模型遵循率或性能提升。此前观察到 Claude 插件发现和 Hook 执行，但 API 连接失败阻止了修复；CodeBuddy 案例被无头权限阻止。本机 Codex 可执行文件不完整、没有 Gemini CLI，二者真实集成尚未验证。Windows Hook 启动尚未验证。

两个[可运行案例及实际记录（英文）](tests/evals/protocol.md)覆盖搜索乱序和受控 CSV 处理；发布与验证细节见[维护指南（英文）](docs/development.md)。README 和安装说明双语，运行规则、维护及评测材料保持英文。

## 授权

采用 [MIT 协议（英文）](LICENSE)。允许商业使用、修改与分发，须保留版权与许可声明，不提供担保。
