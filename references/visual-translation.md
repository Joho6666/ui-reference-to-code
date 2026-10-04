# Visual Translation — Tokens、组件、技术栈与记录

输入：brief、Reference Design Spec、目标项目清单及 UI 基线。输出：Design Tokens、Component Map、Implementation Plan；跨页面复用时保存 design-system。

## 1. 检测现有栈和保留基线

读取项目清单、入口与目标页面、路由、样式和控件源码，依据实际文件确认：静态 HTML/CSS/JS、React/Next、Vue/Nuxt、Svelte、Astro，以及 Tailwind/shadcn/Semi/MUI/Ant Design 等。保留实际启动脚本、版本、SSR/客户端边界及已有主题机制；不从单个文件名推断完整技术栈。

改版前记录：路由及参数、API 输入输出、数据源、控件行为、主要业务文字、数字、能力和功能阶段。映射每个变动区域到这些保留项；改后检查相同操作与内容。UI 控件重构可调整内部表示，但不得擅自删除业务内容、修改指标、API 语义或将计划功能写成已交付。

## 2. Reference → Design Tokens

给每项 token 标来源属性、selected value、采用理由、桌面 / 手机策略和 unknown 的处理。值可沿用现有设计系统；有意改编要注明 adapted，而不是测得。

以下是**格式示例，数值为假设，不能当本项目测量结果**：

```css
:root {
  --container-max: 80rem; /* R1 estimated width; validate at project viewport */
  --page-gutter: clamp(1rem, 4vw, 3rem);
  --section-space: clamp(3.5rem, 8vw, 7.5rem);
  --font-display: system-ui, sans-serif; /* source font unknown */
  --hero-size: clamp(3rem, 7vw, 6.75rem);
  --hero-leading: 1.02;
  --surface: #f7f8fa;
  --text: #111111;
  --accent: #315bea;
  --radius-card: 1.5rem;
}
```

把原始值映射到少量角色：颜色、字号、spacing、radius、shadow、motion。不要为每张卡片创建独立变量。字体确保实际可用与资源依据；保留已有品牌 token 时解释与参考的对应关系。

## 3. Tokens → Components → Code

必须生成重点元素的映射，简单改动用几行表即可：

| Reference Element | Local Component / 文件 | Implementation | States / responsive | Preservation |
| --- | --- | --- | --- | --- |
| R1 hero CTA | ButtonPrimary → existing Button | existing API + project theme token | focus/disabled/loading | 原 CTA 目标与提交行为 |
| R1 showcase card | ProjectCard → existing card or new | CSS grid + semantic link | focus/hover/touch stack | 原项目链接、描述与阶段 |
| R2 tabs | native / current Tabs | 项目既有实现优先 | selected/keyboard/panel association | 原筛选口径 |

复用判定：现有 API 与语义匹配就复用；仅视觉不同用样式/variant；新增结构才新增组件。原生站的 component map 可映射语义区块与 CSS/JS 文件，不强制 JSX。Next/SSR 的交互留在必要客户端区域；Vue/Svelte 采用本栈状态与生命周期。

实现计划写 `region → files → dependency (if any) → behavior preserved → check`。先改布局和字体，再图片与控件，最后动效；避免全局 override 层层叠加以掩盖错误布局。

## 4. 同源多页设计系统

多页面来自同一参考站点时，先提炼一次，再记录页面变体。真实重复模式再抽象；不要把单例卡片当全站规范。

`.ui-design/design-system.md` 内容：

```text
Source samples & confidence; adopted/adapted rules
Colors; typography; spacing & container; radius; shadows
Buttons; cards; inputs; navigation; section patterns
States & mobile variants; motion & reduced-motion
Local implementation/token file mapping; exceptions & reasons
```

## 5. Anti-Overdesign

每种效果回答“哪个参考状态或业务目标要求它”。大量渐变、玻璃、发光、卡片 hover、区域入场、超大圆角、蓝紫配色、抽象球和低信息密度均不是默认参数。无依据时采用已建立的布局、字体、边框与必要状态反馈；不要删除真实内容来制造留白。

F 模式提炼多个来源共性并作原创组合；E 模式优先源几何和视觉重量，资源不可用时说明替代影响。重要操作应稳定，不被 sticky/parallax 或装饰覆盖。

## 6. 轻量状态保存

不无脑建目录。单轮局部任务可以聊天记录；跨轮任务至少维护 record。以下文件仅在对应产物变长或需要复用时新增：

| 文件 | 何时需要 |
| --- | --- |
| brief.md | 多页面、多角色或复杂保留基线 |
| references.md | 多来源规格及素材记录 |
| design-system.md | 同源多页或跨组件共享 tokens |
| component-map.md | 多区域 / 组件及复用决定 |
| implementation-plan.md | 多阶段实现或依赖顺序 |
| qa.md / qa.json | 多轮差异、分数及证据；JSON 用于 QA gate |
| record.md | 需要跨轮恢复时；链接其余已存在文件 |

record 最小模板：

```text
Current mode/source/modifiers/scope; brief and target project
Actual stack/start command/version; preservation baseline
References/spec/token/component-map links (only existing artifacts)
Assets & data source/status
Completed changes and files
QA iteration/state/screenshots/operations/remaining differences
Next action + why; unresolved inputs/capability limits
Publishing scope/status when applicable
```

继续时核对文件、提交与页面是否改变。过时记录需刷新，不能仅依据旧的高分宣称当前版本已验证。
