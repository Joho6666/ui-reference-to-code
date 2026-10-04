# Reference Decomposition — 从可见证据到设计规格

输入：可查看参考图 / 页面、任务 brief、采样环境。输出：Reference Design Spec，足以让实现者决定尺寸、组件、响应式与动效，而不是只描述感觉。

## 1. 固定采样条件

为每个采样记录 `reference_id、URL / 本地图、viewport CSS width × height、DPR、image pixel size、scroll、theme、state、timestamp`。裁剪图说明原图是否已知；设备像素先按已知 DPR 换成 CSS 像素，DPR 未知时保持图像坐标或比例。

网站能取 DOM 时读取目标元素边界与 computed style；截图用实际像素 / 比例估计，不把原图宽度当网站 viewport。先列可见区块及顺序：nav、hero、features、showcase、workflow、CTA、footer 等，仅保留真实出现的区块。

证据值用统一字段：

```text
property | value/unit or range | region/state | evidence | confidence | implication
container.maxWidth | ~1200 CSS px | desktop hero | estimated from 1440px viewport | medium | cap desktop container
heading.fontFamily | unknown | hero | screenshot only | low | use licensed local fallback
motion.duration | unknown | card | static frame | none | observe video before matching timing
```

`evidence` 取 measured-dom、measured-image、estimated、inferred、unknown；confidence 取 high / medium / low / none。同一值必须能找到采样来源。估计范围足够时不伪造小数精度。

## 2. 分解清单

| 类别 | 观察 / 测量 | 规格输出 |
| --- | --- | --- |
| Layout | 容器边界、列数、列宽、grid、gutter、节间与卡间距、左右对齐、视觉顺序 | max-width、padding、grid template、gap、section spacing、alignment |
| Typography | family、display/body、字号、weight、line-height、tracking、标题级差、实际换行 | type scale、标题与正文样式、font source/fallback、line-break evidence |
| Color | 背景、surface、primary/accent、边框、正文、muted、渐变 | role-based colors；截图采色标估计，文字与背景一起检查 |
| Shape | 圆角、边框宽度 / 样式、阴影层数、blur/glass、卡片边界 | radius scale、border、shadow、effects tied to specific regions |
| Imagery | hero、产品图、插画、头像、截图、mask、焦点、比例 | aspect-ratio、object-fit/position、mask、source & usage basis |
| Interaction | nav、hover/focus、sticky、tabs、cards、reveal、carousel、parallax | trigger → state change → user outcome；touch/keyboard equivalents |
| Motion | 触发、时长、easing、方向、stagger、终态、取消 / reduced motion | verified timeline or proposed timing marked as adapted |

## 3. 定量步骤

- 容器：已知视口 W 时，左右边距 L/R，内容宽 `W-L-R`；判断固定上限与流式边距需要多个视口，单样本只给候选。
- Grid：测每列与 gutter，检查是否等宽；用比例表达截图未知尺度。卡间距与节间距单独记录。
- Typography：记录字号与 line box，不把字形实际高度等同 font-size；字体未知时比较字宽、换行与视觉重量，选可用替代并报告差异。
- 图片：记录可见框和主体焦点，先解释裁切再选 cover/contain，避免靠固定高度掩盖比例问题。
- Responsive：网站有手机样本时记录堆叠、导航折叠、间距与字阶变化；只有桌面图则制定假设，并由手机 QA 验证。
- Motion：视频记录至少初始 / 触发中 / 终态，附时间或帧位置；交互网页实际触发一次。仅截图不推断 duration/easing。

## 4. Reference Design Spec 模板

```markdown
# Reference Design Spec — R1
采样：来源 / 证据路径 / viewport / DPR / scroll / theme / state
观察范围与未知项：
区块结构及阅读顺序：
Layout：property/value/evidence/confidence/region
Typography：同上
Color & Shape：同上
Imagery：尺寸/比例/焦点/来源/使用依据
Interaction：触发/状态/反馈/键盘与触屏
Motion：触发/时长/easing/方向/stagger/终态/fallback；未知项
桌面与手机差异：observed 或 adapted
可迁移规则：区域 / 规则 / 业务用途
```

推进条件：重点区域有结构、尺寸依据、字体层级、颜色角色和图片策略；未知项明确，能翻译成实现选择。多参考按来源记录冲突后选一种统一规则，避免每个区块照搬不同系统。
