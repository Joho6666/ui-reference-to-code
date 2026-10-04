# Skill Behavior Tests

测试技能选择和实际产物；不能把“包含某个标题”当工作流可靠性。测试必须注明 dry-run / artifact execution / browser execution，未跑的场景写 planned，不编造截图、工具调用或评分。

## 场景与预期可观察行为

| ID | 用户输入 / 环境 | 预期模式及结果 | 失败信号 |
| --- | --- | --- | --- |
| T1 | “参考 Linear 首页，把我的 SaaS 首页设计得更现代，但不要复制。”目标项目未提供 | C + F；采集参考、原创 tokens；实际有目标项目则 D + website + F | 原样复制品牌 / 未许可素材；漏掉原创约束 |
| T2 | “这是截图，帮我尽量还原。”附可查看图，无项目 | B + E；分区、带证据规格、tokens、组件树、实现、同状态比较 | 静态图编出 timing；用自评高分替代对照 |
| T3 | “这个网站太丑，参考 Stripe 改一下，但功能别动。”提供现有 Vue 页面 | D + website；读路由 / API / 功能基线；沿用 Vue 控件 | 强换 React；删业务内容；改 API / 数据 |
| T4 | “帮我找几个适合作品集的参考，不需要写代码。” | A；只交付四类研究产物 | 创建代码、装组件或发布站点 |
| T5 | “继续优化上一次的页面。”record 存在 | resume；先读 record 并核对当前代码，再做剩余项 | 重复采集；把旧截图用在已变化版本 |
| T6 | 现有静态 HTML + 截图 + “尽量还原”，无浏览器或 MCP | D + screenshot + E；tokens / 映射 / 可审阅代码；unverified | 强加框架；宣称桌面 / 手机已观察 |
| T7 | 多页来自同一站点，各页共享颜色和 nav | 提炼一次 design-system，记录页面变体 | 每页新建互相冲突的 tokens |
| T8 | 卡片评分 9、手机布局 6、主要按钮遮挡 | needs-repair，优先 Critical；修改后重拍 | 平均后判通过；只给文字建议无修复 |
| T9 | “参考多网站但原创，只研究”，附现有项目 | A 优先、F 意图；无实现 | 因项目存在选 D 并改代码 |
| T10 | 只有桌面静态截图，无源 mobile / 交互资料 | 位置尺寸标估计；手机 adapted，源交互 unknown | 把适配结果称手机像素还原；编造动效观察 |
| T11 | 编辑风参考 + 商务数据，已有控件与事实 | 沿用该风格、内容和栈；效果有来源依据 | 默认蓝紫玻璃 / 球体；编造效率指标 |

## 怎么运行

1. 为场景准备最小真实输入（图像、可访问页面、目标代码或 record），放到项目外临时工作区，保存 baseline。
2. 让评估者仅收到真实请求、技能路径及输入位置，不给预期表；边界写明只允许临时工作区且不发布。
3. 观察路由、产物、变动文件与工具记录。浏览器场景须保存并查看桌面 / 手机证据；代码检查不能替代它。
4. 对照以上预期，记录 pass / fail / partial 及具体证据，按发现的问题修技能后复跑受影响场景。

最小结果记录：`ID / skill commit / input artifacts / execution level / observed route / output paths / side effects / result / limits`。没有素材时可以做路由 dry-run，但不得称端到端测试通过。

## 可执行 QA gate 测试

在仓库根目录运行：

```sh
python3 -m unittest discover -s tests -v
python3 scripts/qa_gate.py /path/to/qa.json
```

exit code：0 verified、1 needs-repair、2 unverified、3 invalid-report。测试覆盖证据缺失、关键项低分、未解决严重问题、保留基线失败、E 缺源对照、阈值和无效报告。这些是报告判定测试，不是浏览器或模型行为测试。

## v2 验证记录

2026-10-04，v2 候选工作区验证：

| 范围 | 执行级别 | 实际结果与边界 |
| --- | --- | --- |
| T1–T5 | 独立路由 dry-run；评估者未读预期表 | 正确区分 C+F、B+E、D+website、A 与恢复记录；发现八项歧义后更新指令，独立复读确认这些歧义已解决 |
| T6 | 隔离静态 HTML + 实际参考图；无浏览器 / MCP 的 artifact execution | 产出规格、tokens、映射及可审阅代码；业务文案、四个链接和搜索脚本保留；真实处理器在 DOM 替身中执行四种查询通过；六项分数 null，gate 返回 unverified |
| QA helper | 12 个可执行测试 | 缺证据、低分、严重缺陷、内容回归、E 对照条件、无效数据与 CLI 返回码通过 |
| Skill 包 | frontmatter / metadata / 引用检查 | 官方 quick validator 通过，十个参考均由入口可达，内部链接无缺失 |
| 真实浏览器完整回路 | planned | 未在本轮完成；上述 dry-run、DOM 替身及静态检查不能证明画面质量或真实事件路径 |

没有把隔离代码的主题适配称为像素还原；此记录仅描述实际检查，不作为其他网站任务的默认已验收证据。后续维护更新执行版本与实际结果。
