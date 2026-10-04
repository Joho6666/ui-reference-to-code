# Review and Handoff — 交付状态与内容

浏览器采样、修复循环见 [Browser Validation](browser-validation.md)，差异与评分见 [Visual Fidelity](visual-fidelity.md)。本文件只负责交付和恢复条件。

## 完成判定

| 任务 | 完成证据 | 缺失时的交付 |
| --- | --- | --- |
| A Research | 每条直接来源及观察范围、可迁移规则、区域、实现与成本 | 标明受限来源，利用现有证据完成有限范围研究 |
| B/C/D Implementation | 实际代码检查、可访问页面、保留基线、桌面和手机截图已查看、关键操作、适用分数 ≥7、无未修 Critical/Major | needs-repair 有具体缺陷；unverified 缺必需证据 |
| E Pixel Fidelity | 实现条件 + 至少一次匹配状态的源与实现截图差异分析 | 可审阅实现；保真验证未完成 |
| F Inspiration | 实现条件 + 与已采用并记录的原创设计系统 / 意图比较 | 不把与某一个参考相似程度当目标 |

状态由报告真实条件决定，不能用平均分掩盖低分，或以 DOM/构建正确替代画面。微小改动仅检查其区域与相关功能，但桌面 / 手机证据仍要涵盖被改区域。

## 简洁交付契约

Research：Reference Board、Design Language、Reusable Patterns、Implementation Notes；每条可追溯，可在聊天合并呈现。

Implementation：改动及目的、页面 / 预览、保留的关键行为、实际检查证据、状态和限制。有 QA 记录时链接它，分数以内部修复使用为主。未满足 verified 时明确缺什么与下一步，不结束成“全部完成”。

发布只在当前任务范围及适用工具流程要求时执行，沿用已有站点身份与访问范围。报告成功链接必须来自成功结果；失败保留可审阅代码并说明环节。

多轮完成或受限交付时更新 [record](visual-translation.md)：代码版本、已做决定、QA 最后证据、未解决项与下一动作。下一轮从真实剩余问题开始，验证过且未影响的证据可复用。

## 自查

- 输出是否说明 measured / estimated / unknown，而不是虚构精度？
- 保留重要内容、数字、API / 路由与产品阶段说明了吗？
- 实际画面、操作和完成状态有证据对应吗？
- 设计与素材的使用依据、替代和性能取舍清楚吗？
- 当前任务仅局部时，是否避免无用途的其他区域与工具工作？
