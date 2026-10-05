# Reference Decomposition — 从可见证据到设计规格

输入：可查看参考图 / 页面、任务 brief、采样环境和参考角色。输出：Reference Design Spec；先保留 [Aesthetic DNA](aesthetic-intelligence.md#aesthetic-dna-and-reference-essence) 的视觉关系，再记录尺寸、组件、响应式与动效。

## Aesthetic translation

重点区域用四段推理，而非直接把外观列成 tokens：

```text
Reference Observation: 大标题接近半个视口，小标签只在边缘辅助；标 measured/estimated。
Aesthetic Interpretation: 极端比例制造海报式权威，标签不会抢走第一焦点。
Design Principle: 单一主元素占据视觉重量，支持信息保持次要。
Implementation Rule: 根据真实文本/字形试排大字与紧凑标签；先验证占屏比例、换行和可读性。
```

每条带 `reference_id / region_id / evidence / confidence / desktop → mobile`。将“关系失效的信号”也记下：例如标题与标签缩成相近尺寸、主图被替成装饰背景、每节均用同一轮廓。一个 140px/10px 的观察可揭示强比例，最终数值须服从实际语言、可访问性和目标视口，不机械照抄。未知字体不妨碍推断有证据的比例，但不能伪造字形身份。

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
Primary/Secondary/Functional 角色与职责：
Visual Thesis / Aesthetic DNA / Reference Essence（或关联方向记录）：
区块结构及阅读顺序：
Layout：property/value/evidence/confidence/region
Typography：同上
Color & Shape：同上
Imagery：尺寸/比例/焦点/来源/使用依据
Interaction：触发/状态/反馈/键盘与触屏
Motion：触发/时长/easing/方向/stagger/终态/fallback；未知项
桌面与手机差异：observed 或 adapted
可迁移规则：region_id / observation → interpretation → principle → implementation / 业务用途
```

推进条件：重点区域有主导视觉、阅读顺序、关键比例、构图与素材关系，以及结构/尺寸依据；未知项明确。多参考冲突服从 primary 的方向，secondary 只补局部，不把差异平均成一个普通系统。
