# Codex 对照试验

目的：用**同一个参考、同一份提示**让 Codex 复刻，与 Claude Code 的结果对比，找出 skill 里哪一步在 Codex 上掉队，再针对性补强。

## 准备

```sh
git clone https://github.com/Joho6666/ui-reference-to-code ~/.codex/skills/ui-reference-to-code   # 已存在则 git pull --ff-only
```

新开一个 Codex 会话（技能列表需要刷新）。工作目录用一个空文件夹。

## 提示（原样粘贴，不要加额外说明）

```text
$ui-reference-to-code
复刻这个 Pinterest 作品的首屏：https://pin.it/3L5aXIoKm
地球改成美国 8 个主要城市（夜景地球、城市灯光，切换时地球旋转聚焦）。
内容不必一样，重点是美观、震撼。要 3D 特效。品牌叫 Nightfall。
```

## 观察清单（请在会话中留意并记录）

| # | 观察点 | 好 | 坏 |
| --- | --- | --- | --- |
| 1 | 是否先读了 SKILL.md 与 wow-playbook | 是 | 直接写代码 |
| 2 | 是否用 `replica.mjs init --template globe` 起项目 | 是 | 自己手写项目 |
| 3 | 下载贴图前是否先 `assets list` 并等你确认 | 是 | 直接下载 / 画渐变球 |
| 4 | 是否运行了 `shoot` 并**实际查看**桌面与手机截图 | 是 | 只跑构建 |
| 5 | 自动检查失败时是否先修 | 是 | 忽略 |
| 6 | 是否填写 wow-review.md 并运行 `gate` | 是 | 自述“完成” |
| 7 | 返工轮数 | ≥ 2 | 0–1 |
| 8 | 最终首屏：标题是否一行、CTA 是否在首屏内、地球是否真实夜景 | 是 | 否 |

## 回传给我

1. 最终的 `desktop.png` 与 `mobile.png`（最后一轮 `captures/iter-N/`）。
2. 最后一份 `wow-review.md` 与 `checks.json`。
3. 观察清单里标“坏”的项，以及 Codex 当时的原话（如果有）。

我会据此判断是 skill 文字问题、脚本缺口，还是 Codex 缺少视觉/执行能力，并做下一轮改进。
