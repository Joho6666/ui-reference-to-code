# Visual Fidelity — 差异、评分与修复次序

输入：reference 与 implementation 截图 / 设计规格、相同采样条件、关键行为证据。输出：按严重度的差异报告及六项内部评分。分数用于继续修复，不能代替证据。

## Screenshot Comparison

E 模式先对齐 viewport、DPR、scroll、theme 与状态。源图的 scale / crop 未知时先解释，不做绝对像素误差断言。F 或明显原创改版对照已采用并记录的 design tokens、component map 与内容目标，不能因“与参考长得不同”扣分；除用户要求先审稿外，不增加审批步骤。

按区域比较：

| 组 | 比较项 | 可记录的具体偏差 |
| --- | --- | --- |
| Geometry | x/y、width/height、spacing、alignment | Hero 左边界相差约 24 CSS px；卡间距比规格大 12px |
| Typography | 字号、换行、weight、line-height、字宽 | 标题由 2 行变 3 行；替代字体更宽影响按钮对齐 |
| Visual | 颜色、shadow、border、radius、图像裁切 | surface 色差、边框强度、圆角与主体焦点 |
| Composition | hierarchy、balance、whitespace、visual weight | 主按钮弱于装饰、卡片太密、空白切断阅读 |

每条写 `region/state → expected → observed → evidence → impact → fix → recheck`。未知值写范围 / 置信度；有像素 diff 工具时记录工具、条件和结果，抗锯齿或动态内容先解释，单个总 diff 比例不直接决定达标。

## Visual Difference Report

```text
Critical: ID / region / expected / observed / evidence / fix / resolved
Major: 同上
Minor: 同上
Unsupported observations: 无法确认项及恢复动作
```

- Critical：遮挡主要 CTA、无法操作、重要内容消失、手机结构不可用、错误业务事实等。
- Major：明显错误的标题换行、容器/布局/图片构图失衡、重要控件状态或键盘路径缺失等。
- Minor：不影响层级和主要操作的小间距、边框或阴影差异。

severity 取决于当前任务目标；E 中显著几何偏差可为 Major，F 中有意改编不视为缺陷。修复同一 root cause 后重查关联区域，避免逐项堆局部覆盖。

## 六维评分

| 维度 | 证据依据 |
| --- | --- |
| Layout Fidelity | 区域位置、尺寸、对齐、间距、层级与选定布局规则 |
| Typography Fidelity | 实际字体 / 替代、字号、换行、行高与视觉重量 |
| Color Fidelity | 颜色角色、实际主题、surface、边框与文字可读性 |
| Component Fidelity | 控件形状与状态、布局、图片框、实际组件映射 |
| Responsive Fidelity | 手机实际画面及操作、桌面与手机间一致性、相关断点 |
| Interaction Fidelity | 真实触发 / 状态 / 反馈、键盘 / 触屏、动效与主要操作 |

每项提供分数及至少一个证据引用与判断理由。没有观察证据写 unknown / null；明确无关的可 N/A 并解释。实现 layout、responsive 必查。Screenshot-only 源交互未知时评价已声明的本地功能，不宣称与源交互一致。

评分锚点：

- 9–10：关键属性与目标吻合，相关视口 / 状态已观察，只有无影响的偏差或无偏差。
- 7–8：关键结构与行为达到本次要求，有证据支持，剩余 Minor 不影响用途。
- 4–6：存在可观察 Major、明显几何 / 排版失配或状态不完整，需要修复。
- 0–3：关键目标失败或结构 / 操作不可用。
- unknown：证据不足，绝不默认填 8/9 分。

若报告仍有未解决 Major/Critical，即使分数高也不能 verified。任一适用维度 <7 继续修；必要证据 missing 为 unverified。评分不平均抵消低分，也不在最终答复炫耀总分。

## 修复记录与停止条件

记录每轮 `old difference → changed property/component → new evidence → remaining difference`，保留优先级。至少一个实际同状态对照是 E 完成前提。达到修复预算或外部条件阻塞时写 needs-repair / unverified 和可执行下一步，不能称视觉验收完成。

无浏览器时静态检查仅支持代码观察；没有截图的 layout/color/responsive 不能判满。源图无法取得时可完成可审阅实现并说明保真验证尚缺材料。
