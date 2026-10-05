---
name: ui-reference-to-code
description: "将截图、网站或 Pinterest 等设计参考转为艺术方向、构图与字体策略、代码（含 React Three Fiber 3D 特效）及可追溯的浏览器 QA。用于一键复刻参考首屏、参考研究、截图还原、网站借鉴、现有 UI 改版和审美打磨；适配当前技术栈与业务内容。触发词：复刻、一键复刻、Pinterest、做个酷炫首页、3D 首屏、replica。"
metadata:
  version: "3.5.0"
---

# UI Reference to Code v3.5 — Aesthetic Director

把值得采用的参考转成有视觉主张的页面：Intent → Taste Curation → Visual Thesis / Aesthetic DNA → Art Direction → Composition → Hero Review → Implementation → Aesthetic Critique → Evidence QA。支持先选一个可复刻的参考模板，再提炼构图规则并原创翻译到用户项目。

## Choose the task

先读 [任务模式](references/task-modes.md)，记录 `mode / source / modifiers / resume / target / scope / reference-policy`。

- A Reference Research 只研究；B Screenshot to Code 和 C Website Reference 从图或网页制作；D Existing Redesign 改现有项目。
- E Pixel Fidelity 要求匹配源图；F Inspiration 要求按采用的设计意图创新。E/F 冲突时分别限定区域或先明确近期目标。
- “继续”先读 `.ui-design/record.md` 并核实当前代码。用户最新范围优先，不编造历史。

## Direct the design

检查工作区指令、受众、目标、技术栈、功能与内容基线。阅读 [参考采集](references/research-and-assets.md) 和 [审美判断](references/aesthetic-intelligence.md)，按当前设计问题筛选少量参考；选定一个 Primary Reference，明确次参考与功能参考的局部职责。阅读 [参考拆解](references/reference-decomposition.md)，保留实测、估计、未知项及“观察 → 审美解释 → 原则 → 实现”的联系。

视觉任务在编码前形成具体的 Visual Thesis 与 Aesthetic DNA。按 [Art Direction](references/art-direction.md) 决定阅读顺序、主视觉、构图轮廓、字体气质、比例、素材焦点、层次、留白与整页节奏；重要 landing page 指定一个 Signature Moment。明确本任务的 Anti-Patterns。局部修改沿用有效方向，补充此次改变即可；E 高保真保住参考的意图，不强加原创构图。

## Prototype then implement

阅读 [视觉翻译](references/visual-translation.md)，把方向接到 Design Spec、tokens、region IDs 和本地组件映射。视觉型 landing page 默认先实现 Nav + Hero + First Transition，取得桌面与手机截图并按 [审美评审](references/aesthetic-review.md) 自行评审。主视觉、比例或素材失去方向时先修首屏，再展开全页；这是内部设计检查，不增加用户审批。截图不可得则记录阻断与未验证范围，不声称 Hero Gate 已过。

保留授权范围内的内容、数字、API、路由、链接与行为。不要复制来源的品牌文案或未获许可素材。工具依赖见 [工具路由](references/tool-routing.md)。

## Capture and verify

实现模式需要真实桌面与手机浏览器观察和相关功能操作。多轮任务使用 [Browser Validation](references/browser-validation.md)：先建 run 和 scoped preservation baseline；每次截图记录 route、URL、CSS viewport、DPR、theme、state、scroll、timestamp、source revision 和 region IDs。先实际查看图像，再注册为 evidence artifact，并在 QA 里通过 `artifact_id` 引用。

## One-Click Replica（默认入口）

用户给出 Pinterest Pin / 截图 / 网址，并说“复刻 / 做成 3D 首屏”时，不再逐项追问，按下面默认值直接跑完整条链；只有缺参考图、要下载文件或要写入既有项目时才停下确认。所有步骤都通过同一个入口 `node scripts/replica.mjs <init|assets|shoot|gate|qa>`，是否通过**只看脚本退出码**，不看自述。

1. **取参考**：按 [Wow Playbook §5](references/wow-playbook.md#5-pinterest-参考的获取claude-code--codex-通用) 取得一张可实际查看的参考图；取不到就请用户截图，不凭搜索结果写“已观察”。
2. **拆解**：实际查看后，填 `.ui-design/replica-card.md`（实测/估计/未知分开），选一个 Signature Moment 与模板，至少 5 条绑定截图区域的规则。
3. **脚手架**：`node scripts/replica.mjs init --out <dir> --template hero|globe --name <品牌> --run-url <预览地址>`。
   - `hero`：玻璃 / 液态金属 / 环绕卡片主体，见 [r3f-hero](templates/r3f-hero/README.md)。
   - `globe`：夜景地球从底边升起、多地点切换聚焦，见 [r3f-globe](templates/r3f-globe/README.md)。参考是星球 / 地图 / 城市 / 旅行类时优先。
   - 已有项目则按 D 模式把同样做法接入当前技术栈，不套模板。
4. **素材**：需要贴图等二进制素材时 `replica.mjs assets list --pack <name>`，把清单给用户并**等明确同意**，再 `assets fetch ... --yes`（校验 sha256）。不得静默下载，也不得因为没有素材就退化成渐变色块了事。
5. **首屏实现**：只改 `theme.ts` / `data/` / `styles.css` / `scene/HeroScene.tsx`，实现 Header + Hero + First Transition，写 scene contract。
6. **取证与返工（每轮都做）**：
   1. `replica.mjs shoot --url <预览> --run <run> --iteration N` → 桌面+手机截图 + `checks.json`（折叠线、标题行数、字体、WebGL 是否挂载等自动检查）+ 空白的 `wow-review.md`。
   2. **先修自动检查里的失败项**，再谈审美。
   3. **实际查看**两张 PNG，填写 `wow-review.md`（10 项各 0–2 分，每项写出你在图里看到的内容），`evidence.py add --observer agent` 登记。
   4. `replica.mjs gate <wow-review.md>`：退出码 0 accepted / 1 needs-polish（给出最弱两项）/ 2 incomplete / 3 无效。修最弱两项后再来一轮。
   5. 至少 Structure、Material 两轮；有交互再加 Behavior。
7. **交付**：报告 Wow Gate 结果与 verdict、自动检查状态、3D 回退与手机结果、未验证项。通过后把可复用关系写入 `.ui-design/pattern-library.md`。

不能查看图片时，不得给出 accepted，只能报告 `unreviewed`（见 [Harness adapters](docs/HARNESS_ADAPTERS.md)）。默认技术路线是 Three.js / React Three Fiber，CSS 3D 作回退，Spline / ThreeUI 仅在环境确有授权且用户点名时使用。预览服务、浏览器与截图用当前运行环境的工具；缺失时按 `unverified` 交付，不虚报通过。

## Template Replica mode

当用户说“去 Pinterest 找一个好看的 UI、参考一个作品、复刻一个模板、以后每次都按这个方法做”时，启用此模式；已有项目仍使用 `D / mixed / [F]`，新项目先按 brief 建立方向。

1. **建立候选板**：在 Pinterest 优先搜索与页面用途、行业和主视觉有关的关键词；补充一个真实上线产品页和一个功能型参考。记录 URL、截图、可观察范围和来源角色。搜索结果页只能作为候选线索，不能写成已观察设计。
2. **选 Primary Template**：只选一个主参考统领首屏。次参考只能分别负责摄影、字体、动效或转化路径中的一个问题。拒绝平均混合五个网站，也不复制品牌文案、商标或未授权素材。
3. **输出 Replica Card**：在 `.ui-design/` 写一张参考卡，至少包含 `template_name`、`primary_url`、`page_type`、`viewport`、`hero silhouette`、`grid`、`type hierarchy`、`image crop`、`color roles`、`motion`、`mobile transformation`、`unknowns` 和 `adaptation boundary`。
4. **把观察变成规则**：至少写出 5 条可执行规则，例如“主产品占 Hero 右侧约 45%”“标题最多三行”“首个过渡改变布局关系”“CTA 只有一个主要动作”。每条规则必须绑定一个截图区域和实现方式（CSS、组件、素材或 3D）。
5. **只做首屏复刻**：先实现 Header + Hero + First Transition。首轮验收看产品主体、文字换行、留白、比例、图像裁切和手机重排；首屏没有方向时不扩展整页。
6. **进入返工循环**：读取 [Polish Loop Playbook](references/polish-loop-playbook.md)，默认至少完成 Structure 和 Material 两轮；页面有交互或 3D 时再完成 Behavior 轮。每轮修复后必须在相同桌面与手机视口重新捕获、实际查看截图，并写入 difference log。第一轮实现只证明方向，不得直接标记为完成。
7. **沉淀为可复用模板**：把稳定的规则写入 `.ui-design/pattern-library.md`，包括适用页面、禁止组合、可替换 token、组件映射和已验证视口。下一次任务先检索这个库，再决定是否复用。

返工结果使用明确门槛：`accepted` 需要桌面与手机的参考关系都保留、没有未解决的 Major/Critical 差异、最强素材已解决或明确标记为临时、首个过渡改变节奏、3D 有明确职责且有静态回退，并且最新截图已查看；结构可用但素材/比例/字体/节奏仍临时则为 `needs-polish`；没有最新截图或参考观察则为 `unreviewed`。构建通过不能替代审美验收。

详细字段、参考卡模板和审美评分表见 [Template Replica Playbook](references/template-replica-playbook.md)。

当页面需要 3D 模型、Shader 或动画特效时，先读 [Wow Playbook](references/wow-playbook.md)（验收分与实测教训），再读 [3D and Motion Playbook](references/3d-motion-playbook.md)。它会区分 Pinterest 的审美参考、ThreeUI 的实现参考、Three.js 的 API 依据、Spline 的可编辑场景和 Codrops 的实验性动效；先写 scene contract，再选择 CSS 3D、Three.js / React Three Fiber、Spline 或 ThreeUI adaptation。

按 [审美评审](references/aesthetic-review.md) 检查整页节奏、Reference Essence、手机重新编排和 SAFE_DESIGN_WARNING，给出针对截图的删减、比例、构图或素材修复。Aesthetic Score 独立记录，不并入 Fidelity Score 或 QA v2 schema；缺观察时分数为 null。按 [Visual Fidelity](references/visual-fidelity.md) 记录工程比较与差异，修复后重新捕获。通过 `python3 scripts/qa_gate.py <run>/qa-<iteration>.json` 取得机器状态，并按 [Handoff](references/review-and-handoff.md) 分别报告工程 QA 与审美评审结果；机器 verified 不能代表审美达标。

浏览器不可用、证据过期、图片或保留项缺失时，继续能完成的代码检查，并如实标记 `unverified`；实际回归或低分标记 `needs-repair`。构建成功或自报高分不能替代浏览器证据。

## Maintenance

修改模式、schema 或行为时读 [行为测试](references/test-cases.md)。用 `python3 -m unittest discover -s tests -v` 运行确定性检查。Run / Evidence / QA 契约位于 [schemas/contracts.json](schemas/contracts.json)。Evidence 和 gate 使用 Python 标准库；[可选 visual diff](references/browser-validation.md#compare-and-repair) 需要 Pillow。
