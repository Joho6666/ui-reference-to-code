# Harness adapters

这个 skill 的行为全部落在**脚本和文件**里（`scripts/`、`templates/`、`references/`），与具体 harness 无关。各 harness 只负责三件事：发现 `SKILL.md`、能执行 shell、能**看到图片**。

| 能力 | 必须 | 缺失时 |
| --- | --- | --- |
| 读取 `SKILL.md` | 是 | 把下面「通用引导提示」粘进系统提示 / `AGENTS.md` |
| 执行 shell（Python 3.9+、Node 18+） | 是 | 无法使用脚本，只能手工，质量不保证 |
| **查看 PNG（视觉）** | 是 | 纯文本模型不得标 `accepted`；用视觉 MCP 或让人类看图 |
| 本地起 dev server | 是 | — |
| Playwright + Chromium | 推荐 | 用 harness 自带浏览器截图，按 `capture.mjs` 的回执格式手写 |

## 安装

| Harness | 命令 |
| --- | --- |
| Claude Code | `git clone https://github.com/Joho6666/ui-reference-to-code ~/.claude/skills/ui-reference-to-code` |
| Codex | `git clone https://github.com/Joho6666/ui-reference-to-code ~/.codex/skills/ui-reference-to-code` |
| 其他（Cursor / Aider / Gemini CLI / opencode …） | 克隆到任意目录，把 `SKILL.md` 与下方引导提示放进该工具的规则文件（`.cursor/rules`、`CONVENTIONS.md`、`GEMINI.md`、`AGENTS.md`） |

## 通用引导提示（任何 harness 都可直接粘贴）

```text
你有一个本地 skill：<skill 目录>/SKILL.md。收到“复刻这个设计 / Pinterest 链接 / 做 3D 首屏”时：
1. 先读 SKILL.md 的 One-Click Replica 一节，再读 references/wow-playbook.md。
2. 只用 `node <skill>/scripts/replica.mjs` 提供的 init / assets / shoot / probe / checks / image / gate 子命令，不要自己手写截图或评分流程。
   必须用浏览器自动化真实渲染（Codex：ego-browser / ego-lite / playwright；Claude Code：浏览器窗格）。
3. 每轮改完必须：shoot -> 实际查看桌面与手机两张 PNG -> 填写 wow-review.md -> gate。
4. 自动检查（折叠线、标题行数、字体、WebGL 挂载）失败时，先修它，再谈审美。
5. 下载文件前先 `assets list`、生成图片前先 `image --dry-run`，给我看清单/费用并等我明确同意。素材缺口用生图补，不要用渐变色块糊弄。
6. 你不能查看图片时，不得给出 accepted，只能报告 unreviewed。
```

## 浏览器自动化（任何 harness 都要用）

| Harness | 首选 | 备选 |
| --- | --- | --- |
| Codex | 当前可用的浏览器技能（ego-browser / ego-lite、`playwright`、`chatcut-web-browser`；以技能列表为准） | `replica.mjs shoot` |
| Claude Code | 内置浏览器窗格（`preview_start` + 截图） | `replica.mjs shoot` |
| 其他 | 自带浏览器工具或 Playwright MCP | 人类截图（只能 `unreviewed`） |

用 harness 浏览器时的固定动作：打开预览 → 桌面宽度（≥1280）执行 `node scripts/replica.mjs probe` 的输出并保存 JSON，截图；窗口缩到约 390 宽再做一次 → `replica.mjs checks --out <dir> --desktop-probe ... --mobile-probe ... --desktop-png ... --mobile-png ...`。检查规则只有一份实现（`scripts/page_checks.mjs`），不论走哪条浏览器路线结果一致。

## 生图

| Harness | 做法 |
| --- | --- |
| Codex | 优先内置 `image_gen`；生成后 `replica.mjs image --record-only` 记来源 |
| 其他 | `replica.mjs image`（需要 `OPENAI_API_KEY`；先 `--dry-run`，用户同意费用后 `--yes`） |

## 视觉能力不足时

- 有视觉 MCP（如 `analyze_ui`、`analyze_image`）：用它读 `desktop.png` / `mobile.png`，把它的描述写进 wow-review 的“what I saw”，并在报告里注明由视觉 MCP 观察。
- 完全没有视觉：停在 `unreviewed`，把截图路径交给人类。

## 兼容性约定（改 skill 时保持）

1. 不依赖任何 harness 专有工具名；工具差异只出现在 `references/tool-routing.md` 和本文件。
2. 脚本只依赖 Python 标准库与 Node 内置模块（Playwright 例外，且可替换）。
3. 所有“是否通过”的判断必须来自脚本退出码，而不是 agent 自述。
