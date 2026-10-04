---
name: ui-reference-to-code
description: "将截图、网站或设计参考转为设计规格、组件规划、代码及浏览器视觉修复。用于参考研究、截图还原、网站借鉴、现有 UI 改版和继续打磨；适配当前技术栈与业务内容。"
metadata:
  version: "2.0.0"
---

# UI Reference to Code v2

把参考转成可追溯的设计决定和可观察的页面结果：Reference → Design Tokens → Components → Code → Visual QA。

## 1. 选择入口并恢复上下文

先读 [任务模式](references/task-modes.md)。输出路由：`mode / source / modifiers / resume / target / scope / reference-policy`。

- A Research：只研究；在参考与实现建议处交付。
- B Screenshot to Code：拆截图、提取规格、实现并比较。
- C Website Reference to Code：观察网站桌面、手机及关键交互，提取规则。
- D Existing UI Redesign：基于现有项目改版，保留功能、API、路由、数据和业务事实。
- E Pixel Fidelity、F Inspiration 是修饰项，可与 B/C/D 组合。
- “继续”先读取已有 `.ui-design/record.md`，核对当前代码与页面，再推进未完成项。

用户范围优先；新任务已有可用目标项目选 D，并保留 B/C 来源标签；继续任务沿用已恢复模式，用户改变目标时重新路由。输入缺失时先用现有资料推进可执行部分，不虚构截图、参考或项目。

## 2. 建立 brief 与基线

确认当前目录、工作区指令、已有改动、页面目标、受众、主要动作、内容与资源。读取清单和源码确认实际技术栈、组件库及启动方式，保存改动区域的功能 / 内容基线。

输出：`Brief + Stack + Preservation Baseline`。列出此次允许改变的 UI 范围及必须保留的业务行为；事实不明确时保留原文或标记待确认。

## 3. 观察并拆解参考

读取 [参考采集与素材](references/research-and-assets.md) 及 [Reference Decomposition](references/reference-decomposition.md)。优先查看用户给的图或精确链接；补充少量能回答具体问题的参考。

输出：`Reference Board + Reference Design Spec`，覆盖布局、字体、颜色、形状、图像、交互、动效。尺寸附采样视口、来源和测量 / 估计状态；静态截图里的交互、时长及未知字体保持 unknown。

A 模式在输出 Design Language、Reusable Patterns、Implementation Notes 后结束；其他模式继续。

## 4. 翻译成设计系统及本地组件

读取 [Visual Translation](references/visual-translation.md)。从参考规格形成 tokens，再生成 `Reference Element → Local Component → Implementation` 映射和实现计划；复用项目已有控件与布局。

输出：`Design Tokens + Component Map + Implementation Plan`。多个同源页面复用已提炼的设计系统。简单任务用聊天或一份 record；复杂、多轮项目按需拆分 `.ui-design/` 记录。

设计沿用参考和业务主张。渐变、玻璃、发光、圆角、抽象球和动画都需要具体依据；极简编辑参考应保留其信息密度与节奏。

## 5. 实现并运行

需要工具时读 [工具路由](references/tool-routing.md)。工具可选；代码采用当前 HTML/React/Next/Vue/Nuxt/Svelte/Astro 等栈，按项目清单和现有组件选择实现，不因参考更换框架。

先完成本轮重点区域，再扩展确认的规则。记录改动文件、组件状态、响应式与 reduced-motion 路径。现有项目保留重要内容、真实数字、API 语义、产品能力与功能阶段说明。

使用适合的真实截图、用户素材、可用资源或原创视觉，记录依据；不复制参考品牌内容或未获许可素材。构建及功能检查覆盖实际变更，修复发现的问题。

## 6. Visual QA Loop（实现模式必经）

读取 [Browser Validation](references/browser-validation.md) 与 [Visual Fidelity](references/visual-fidelity.md)。启动可访问预览，实际打开桌面和手机，查看截图与关键操作；对照参考或批准设计规格，写 `Visual Difference Report + Fidelity Scores + Evidence`。

Critical 优先，随后 Major。修复后重拍相关视口，重新比较。默认初检后最多 3 轮有证据的修复，用户另定预算时沿用；已满足条件可提前完成。任一关键维度低于 7/10、未解决 Critical/Major 或缺失必需观察时，不能标记视觉完成。

无法使用浏览器时继续静态 / 构建检查，记录未验证项与恢复动作，交付状态为 `unverified`；构建成功不能替代截图比较。不要用重复无进展的调用掩盖阻塞。

需机器判定持久化 QA 时，使用 `python3 scripts/qa_gate.py <qa.json>`；它只检查报告条件，不替代截图观察或自动计算保真度。

## 7. 完成与交付

读 [Review and Handoff](references/review-and-handoff.md)，按范围交付并更新 record。完成条件：

- Research：来源与观察范围可追溯，设计语言明确，建议可执行。
- Implementation：代码检查通过、页面可打开、关键功能保留、桌面和手机已观察、视觉 QA 达标。
- Pixel Fidelity：再加至少一次同状态 Reference vs Implementation 差异分析；缺少对照证据不能称高保真验证完成。

区分 `verified`、`needs-repair`、`unverified`，报告真实限制。发布按当前授权与适用托管流程执行；成功状态才报告上线。

## 开发与示例

维护技能、检查模式或完成条件时读 [行为测试](references/test-cases.md)。需要实践背景时读 [JOHO 案例](references/joho-case-study.md)；案例配色和项目数不作为新项目默认值。
