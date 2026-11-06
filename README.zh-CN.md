# supercoding

[English](README.md) | **简体中文**

**为 AI 编码助手补足工程判断：复用已有能力，保持改动精简，验证真正重要的行为。**

supercoding 是一个跨语言的 **Agent Skill**，提供六个客户端的原生插件/扩展封装。沿用项目技术栈，指导助手处理搜索结果乱序、接口数据过大、业务规则复用、loading 和页面布局等实际工程问题。它不是 MCP 服务，也不是强制执行的开发方法论。

一个轻量入口，八份按需参考。纯 README、文档编写、翻译和普通交流不触发。

[如何工作](#如何工作) · [安装](#安装) · [首次使用](#首次使用) · [包含什么](#包含什么) · [更新](#更新) · [验证与贡献](#验证与贡献)

## 如何工作

1. **先理解现有实现。** 读取项目约束、相关代码与调用方，新增之前先寻找可复用的组件、请求层和测试。
2. **按实际风险加载规则。** 页面功能关注布局，异步任务关注状态归属，性能优化先找瓶颈。上下文已有且未变化的完整规则直接沿用，微小修改可以只使用入口。
3. **完成最小完整改动。** 保持契约，限制增长型数据与任务，覆盖相关失败路径。不把小功能扩成框架，也不顺手清理无关代码。
4. **先验证，再宣称完成。** 检查问题原触发路径及受影响行为，区分实际测量、静态推断和未执行的检查。

列表慢，先区分查询、传输和渲染成本，而不是直接加缓存；两个表格相似，先找稳定共同规则，而不是合成万能组件；出现缺陷，先验证原因，而不是叠加猜测式补丁。

supercoding 不额外强制需求访谈、设计文档、TDD、多代理、worktree 或审批流程，已有项目流程仍按项目要求执行。

## 安装

每个客户端选择**一种**原生插件/扩展或独立 Skill。六个客户端使用同一套规则；通过支持的客户端使用 DeepSeek 等模型时，安装格式不变。

| 客户端 | 可用安装方式 | 操作说明 |
| --- | --- | --- |
| Claude Code | marketplace 插件、本地会话插件、独立 Skill | [Claude Code](docs/clients/claude-code.zh-CN.md) |
| CodeBuddy | marketplace 插件、本地会话插件、独立 Skill | [CodeBuddy](docs/clients/codebuddy.zh-CN.md) |
| Codex | 仓库 marketplace 插件、独立 Skill | [Codex](docs/clients/codex.zh-CN.md) |
| Gemini CLI | 原生扩展、独立 Skill | [Gemini CLI](docs/clients/gemini-cli.zh-CN.md) |
| Hermes Agent | 原生插件、独立 Skill | [Hermes](docs/clients/hermes.zh-CN.md) |
| OpenClaw | 原生插件、独立 Skill | [OpenClaw](docs/clients/openclaw.zh-CN.md) |

安装受管理的独立副本时，先获取源码，使用 Python 3.9+ 安装。以下以 Codex 为例：

```sh
git clone https://github.com/Cyrus-terra/supercoding.git
cd supercoding
python3 -B scripts/manage.py install --client codex --source .
```

没有 Python 时，可将 `skills/supercoding/` 复制到客户端技能目录，不覆盖已有安装。默认路径、Windows、项目级范围和排错见[共用安装指南](docs/installation.zh-CN.md)。本仓库提供插件/扩展封装，但不宣称已进入官方市场、npm 或 ClawHub。各客户端真实验证的限制见对应安装指南。

## 首次使用

新建客户端会话，确认 `supercoding` 或 `supercoding:supercoding` 可用，然后尝试：

```text
使用 supercoding 给订单页增加状态筛选。
复用现有请求层和组件，处理分页、loading、失败状态，
并检查新增控件与原页面布局的关系。
```

发现 Skill 不等于每次编码都使用。需要默认启用时，将[编码指令](docs/installation.zh-CN.md#所有编码任务默认使用)加入客户端实际加载的上下文文件。中英文任务共用英文规则，回复跟随你的语言偏好。

## 包含什么

[运行入口（英文）](skills/supercoding/SKILL.md)直接路由到八份专项参考。这些是规则模块，不是八个独立安装的 Skill。

| 参考模块 | 帮助助手做出的判断 |
| --- | --- |
| [架构与复用](skills/supercoding/references/architecture-and-reuse.md) | 职责如何划分，什么值得复用，如何精简并保持原行为与副作用。 |
| [接口与请求](skills/supercoding/references/api-and-requests.md) | 返回多少数据，何时拆分或聚合接口，如何复用请求与错误处理。 |
| [异步与资源](skills/supercoding/references/async-and-resources.md) | loading 和结果归谁管理，如何防止旧结果覆盖和重复提交，资源何时释放。 |
| [表格与表单](skills/supercoding/references/tables-and-forms.md) | 筛选、分页、选择、校验、批量操作和导出如何保持一致。 |
| [样式与页面](skills/supercoding/references/styles-and-ui.md) | 新功能如何融入原布局、支持宽度、无障碍交互和完整用户操作路径。 |
| [性能](skills/supercoding/references/performance.md) | 瓶颈在哪里，如何限制数据与并发，何时缓存或懒加载有效，测量是否支持改动。 |
| [后端与数据](skills/supercoding/references/backend-and-data.md) | 查询、事务、权限、幂等和后台任务如何在规模增长时保持正确性。 |
| [验证与评审](skills/supercoding/references/verification.md) | 如何验证调试假设、核实评审反馈、选择相关检查，并如实报告证据。 |

## 旧项目与执行边界

在客户端系统、安全和权限约束内，用户明确要求与项目明确规范优先于通用 Skill。沿用现有技术栈、请求层和设计系统；旧代码缺陷不会因保持一致而成为规范。

打开项目不会自动审计。编码时只检查相关旧代码，新增与修改部分应用规范。全面审查需要明确提出，仅授权审查不等于授权修复。加载 Skill 不授予推送、部署或外部发布权限。

## 更新

原生插件/扩展通过客户端更新，自动升级取决于宿主配置。会话 Hook 不联网检查或安装更新。

受管理的独立副本支持只读检查与预览、完整目录备份、保护自定义内容和回退。例如，在源码目录中：

```sh
python3 -B scripts/manage.py check --client codex
python3 -B scripts/manage.py update --client codex --dry-run
```

联网检查/更新需要对应的稳定 GitHub Release。正式发布前或离线使用时，加 `--source .` 从可信本地源码读取。执行更新前先阅读[更新与恢复说明](docs/installation.zh-CN.md#版本检查更新和回退)；定制安装需要显式替换，工具拒绝软链接目标。

## 验证与贡献

在仓库根目录执行：

```sh
python3 -B scripts/validate_skill.py
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
```

确定性检查覆盖打包、本地链接、适配器和独立更新/恢复行为，**不能证明**自动触发、模型遵循率、视觉正确性或性能提升。真实客户端集成与模型行为需要独立证据，见[评测场景、可运行案例及已观察到的限制（英文）](tests/evals/protocol.md)。

改进应对应具体失败场景，包含可观察的评测案例，并保持按需加载。检查与发布要求见[维护指南（英文）](docs/development.md)。README 和安装说明双语，运行规则、维护及评测材料保持英文。

## 授权

采用 [MIT 协议（英文）](LICENSE)。允许商业使用、修改与分发，须保留版权与许可声明，不提供担保。
