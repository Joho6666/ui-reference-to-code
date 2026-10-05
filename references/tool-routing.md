# Tool Routing — 什么时候调用工具

输入：模式、当前问题、实际能力与项目依赖。输出：工具选择及原因 / 替代路径。工具服务于页面目标，缺 MCP 仍可继续规格、实现与验证。

## 先发现实际能力

确认技能文件、浏览器可控页面、MCP schema 和项目依赖。区分 installed、configured、called、integrated、rendered，按实际状态报告。使用现有命令与版本，不编造工具名，不把技能调用当作安装所有工具的授权。

| 触发条件 | 工具 / 技能 | 返回给工作流 | 无工具时 |
| --- | --- | --- | --- |
| 要观察参考网站 / 当前页面 | 可用浏览器工具（Claude Code：内置浏览器 / Playwright；Codex：ego-browser 等） | 采样截图、DOM、状态与操作 | 可用用户图像 / 当前资料，未知观察标记 unknown |
| 主视觉、字体与构图需要方向 | frontend-design | 有依据的视觉主张 | 依据 brief 与源规格自行形成方案 |
| 要系统化 UX、tokens 或响应式 | ui-ux-pro-max | design-system / domain / stack 建议 | 使用本技能翻译模板与已有组件 |
| 用户明确点名 frontend-skill | 读取当前版本指令 | 该技能规定的设计辅助 | 未点名不自动调用当前 explicit-only 版本 |
| 已有或计划使用 Semi，需 API / 状态依据 | semi-design-guide + Semi MCP | 项目版本的组件文档与示例 | 官方文档；原生栈采用本地实现 |
| 真实数据或关系用图比表更清楚 | ECharts | 注册所需图表、数据定义、交互 | 本地文字 / 表格 / SVG 关系图 |
| 3D 明确增强主题或必要交互 | Spline | 场景、导出、体积及替代状态 | 静态 / 原创图像及 CSS |
| 用户给 Figma 稿或要求设计稿 / 系统迁移 | 当前环境相应 Figma 技能与工具 | 指定稿件 / 节点、截图、组件属性、资源 | 用户已给图像；不宣称读到 inaccessible 稿件 |
| 实现后的视觉 / responsive 观察 | harness 浏览器自动化（ego-browser / ego-lite / playwright / 浏览器窗格）+ `scripts/page_checks.mjs`；有 Playwright 时用 `replica.mjs shoot` |
| 素材缺口（背景、场景、纹理） | harness 内置生图（Codex `image_gen`）→ `scripts/gen_image.py`；见 [Image Generation](image-generation.md) | 桌面 / 手机证据与比较 | 按 Browser Validation 交付 unverified |
| 当前任务需要发布 | 所选托管技能 / 工具 | 构建 / 上传状态及成功 URL | 保留可审阅本地结果，明确发布限制 |

通常一个主要设计技能加针对性资料即可。已批准方案只需修局部时，直接用当前 tokens 和组件，不重新调研。

## 浏览器与 Figma

按安装技能及 runtime help 的实际 API 工作，线上教程版本可能不同。用户接管与登录验证依浏览器控制规则处理；在查看结果后再结束空间。Figma 请求按相关技能选择读取、设计生成或迁移，保持原栈与用户授权范围。

浏览器能力缺失与页面自身失败分别定位。DOM 文本、HTTP 200、Canvas 元素、iframe load 都不等于视觉通过。实现验证和停止条件统一见 [Browser Validation](browser-validation.md)。

## Semi MCP

[官方 MCP / Skills 文档](https://semi.design/zh-CN/start/mcp-skills) 提供组件文档、代码块和源码查询。先发现 schema 与版本参数，以目标项目安装版本为准：文档 → 确实需要的代码块 → 仍无法解释行为时才查文件 / 函数。

现有典型方法包括 get_semi_document、get_semi_code_block、get_component_file_list、get_file_code、get_function_code；工具未暴露时不能假设可用。确认 React 与图标、主题和样式接入；原生 HTML 参考规范并实现本地控件，不宣称集成了运行时组件。

已配置服务但未暴露时，可在环境支持且当前任务需要时沿用注册配置通过 MCP SDK 连接；不硬编码个人缓存路径。没有可用连接则官方资料退路即可。

## ECharts 与 Spline

ECharts 先定义问题、数据来源与口径。标签可重叠须说明；示意数据必须标记，不能变成商业成果。依据 [官方导入指南](https://echarts.apache.org/handbook/zh/basics/import/) 按实际版本引入核心、图表、组件与 renderer，或使用合适静态分发。处理尺寸、resize/dispose、按需加载及文本 / 表格替代，保留适用许可证。

Spline 先判断静态视觉还是实时交互。核对具体资源使用依据，用官方导出；按 [场景优化指南](https://docs.spline.design/exporting-your-scene/how-to-optimize-your-scene) 评估几何、材质、纹理、体积与嵌入。点击 / 延迟加载、静态 fallback、页面滚动与 reduced motion 都有明确状态。实际观察 GPU 场景，而不是只观察 iframe load。

## 运行与发布

运行栈和组件复用统一见 [Visual Translation](visual-translation.md)。找到实际 Node/Python/包管理器和启动脚本再修 PATH，不无依据重装环境。发布复用用户选定站点身份和访问范围，遵循当前授权及托管技能。只研究 / 本地范围不会因为某工具可发布而扩大。
