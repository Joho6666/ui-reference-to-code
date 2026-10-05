# Image generation for hero imagery

用 GPT 图像模型补**参考里有、但我们没有素材**的画面（背景氛围、产品场景、纹理、插画）。目标是让首屏的「最强素材」不再是渐变色块。

## 什么时候生成，什么时候不

| 适合生成 | 不要生成 |
| --- | --- |
| 氛围背景、光效、抽象纹理 | Logo、商标、品牌字标（模型会画错字） |
| 产品 / 场景示意图（原创） | 真实人物肖像或名人 |
| 手绘 / 插画风格的配图 | 复制参考图本身（只取关系，不取像素） |
| 3D 模型的贴图占位、环境反射素材 | 需要精确地理 / 数据的内容（用真实数据或开源贴图，如地球贴图包） |

地球、地图这类**有公开真实素材**的，先用 `assets list` 的开源包；生成图是真实素材不存在时的补充，不是替代。

## 选工具（按顺序）

1. **harness 自带生图工具**（Codex 的内置 `image_gen`，或其他 harness 的等价工具）：优先。生成后运行
   `node scripts/replica.mjs image --record-only --out <文件> --prompt "<提示词>"` 补一条来源记录。
2. **`scripts/gen_image.py`**（OpenAI Images API，需要 `OPENAI_API_KEY`）：没有内置工具时使用。
   - 先 `--dry-run` 看请求；**费用由用户确认**，得到明确同意后才加 `--yes`。
   - 提示词含 logo / 商标 / “复制这张图” 时脚本直接拒绝。
3. 都没有：让用户提供图，或做 CSS / 程序化替代，并在报告里标注为临时素材。

## 提示词模板（从 Replica Card 填）

```text
<主体与场景，一句话>。
Style: <参考的材质/摄影语言，如 cinematic night photography, soft film grain>.
Light: <光向与色温，如 single key light from upper left, cool rim light>.
Palette: <color_roles 的 hex，如 deep navy #040814, teal #3fe0d0, warm highlights #ffc46b>.
Composition: <画幅与留白，如 wide 3:2, subject on the right third, empty dark area on the left for headline>.
Constraints: no text, no logos, no watermark, no people's faces, photorealistic / illustration.
```

要点：**为文字留空**（写明哪一侧留空），**写死调色板和光向**（与 CSS tokens 一致），**明确 no text**。

## 流程

1. 生成 2–3 张候选（`--n 3`，或分别生成）。
2. **逐张查看**：光向是否统一、有没有乱码文字 / 手指 / 伪影、留白位置是否对。
3. 选一张，转 WebP 并控制体积（背景 ≤ 300KB，桌面 1600px 宽、手机另出 800px 宽）。
4. 放入 `public/`，在模板里挂载（`theme.assets.heroImage`，见 r3f-hero 模板），并保留 CSS 回退。
5. 来源记录在 `.ui-design/generated-assets.json`（模型、提示词、尺寸、sha256、日期），交付时写进报告。
6. 作为 Wow Gate 的 `material` / `negative-space` 项的证据：图要和 3D 主体的光向、色彩一致，否则回到第 1 步。

## 与许可的关系

生成图仅作为本项目的原创素材使用；不得把参考作品的图片作为输入「改图」来规避版权。提示词里只描述关系（构图、光、色），不引用作品名或艺术家姓名。
