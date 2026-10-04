---
name: ui-reference-to-code
description: "将截图、网站或设计参考转为设计规格、组件规划、代码及可追溯的浏览器 QA。用于参考研究、截图还原、网站借鉴、现有 UI 改版和继续打磨；适配当前技术栈与业务内容。"
metadata:
  version: "2.1.0"
---

# UI Reference to Code v2.1

把参考转成可追溯的页面结果：Reference → Design Spec → Components → Code → Browser Capture → Evidence → Visual QA → Handoff。

## Choose the task

先读 [任务模式](references/task-modes.md)，记录 `mode / source / modifiers / resume / target / scope / reference-policy`。

- A Reference Research 只研究；B Screenshot to Code 和 C Website Reference 从图或网页制作；D Existing Redesign 改现有项目。
- E Pixel Fidelity 要求匹配源图；F Inspiration 要求按采用的设计意图创新。E/F 冲突时分别限定区域或先明确近期目标。
- “继续”先读 `.ui-design/record.md` 并核实当前代码。用户最新范围优先，不编造历史。

## Implement within scope

检查工作区指令、目标、技术栈、功能与内容基线。阅读 [参考采集](references/research-and-assets.md) 和 [参考拆解](references/reference-decomposition.md)，把实测、估计与未知值区分开。阅读 [视觉翻译](references/visual-translation.md)，产出 Design Spec、tokens、region IDs、组件映射及实施计划，再用项目当前栈完成修改。

保留授权范围内的内容、数字、API、路由、链接与行为。不要复制来源的品牌文案或未获许可素材。工具依赖见 [工具路由](references/tool-routing.md)。

## Capture and verify

实现模式需要真实桌面与手机浏览器观察和相关功能操作。多轮任务使用 [Browser Validation](references/browser-validation.md)：先建 run 和 scoped preservation baseline；每次截图记录 route、URL、CSS viewport、DPR、theme、state、scroll、timestamp、source revision 和 region IDs。先实际查看图像，再注册为 evidence artifact，并在 QA 里通过 `artifact_id` 引用。

按 [Visual Fidelity](references/visual-fidelity.md) 记录比较、差异及有依据的评分。修复 Critical/Major 后重新捕获。通过 `python3 scripts/qa_gate.py <run>/qa-<iteration>.json` 取得单一机器状态。按 [Handoff](references/review-and-handoff.md) 报告机器已核验条件及仍靠 Agent/人工判断的内容。

浏览器不可用、证据过期、图片或保留项缺失时，继续能完成的代码检查，并如实标记 `unverified`；实际回归或低分标记 `needs-repair`。构建成功或自报高分不能替代浏览器证据。

## Maintenance

修改模式、schema 或行为时读 [行为测试](references/test-cases.md)。用 `python3 -m unittest discover -s tests -v` 运行确定性检查。Run / Evidence / QA 契约位于 [schemas/contracts.json](schemas/contracts.json)。Evidence 和 gate 使用 Python 标准库；[可选 visual diff](references/browser-validation.md#compare-and-repair) 需要 Pillow。
