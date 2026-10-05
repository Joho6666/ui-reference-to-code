# r3f-globe template

夜景地球首屏：地球从底边升起，多个城市（或任意地点）可切换，切换时地球旋转聚焦。参考构图：Dribbble "Planet Earth" 落地页（居中巨型衬线标题 + 底部升起的星球 + 左右半露的邻居星球）。

```sh
python scripts/replica_init.py --out ./site --template globe --name "Brand" --run-url http://127.0.0.1:5173/
python scripts/fetch_assets.py list --pack earth           # 先把文件清单给用户确认
python scripts/fetch_assets.py fetch --pack earth --out ./site/public/textures --yes   # 用户同意后才加 --yes
cd site && npm install && npx playwright install chromium && npm run dev
```

## 只改这几处
| 文件 | 作用 |
| --- | --- |
| `src/data/cities.ts` | 地点（名称、经纬度、文案）。可换成任意城市/景点/办公室 |
| `src/theme.ts` | 配色、品牌、导航文案 |
| `src/styles.css` | 标题比例、栅格、左右邻居位置 |
| `src/scene/HeroScene.tsx` | `TILT`（地点在球冠上的位置）、`visible`（球露出比例）、太阳方向、大气强度 |

## 已内置
着色器夜景灯光 + 日面 + 菲涅尔边缘光 + 背面大气壳 + 云层 + 星空；地点标记脉冲；键盘/点击/圆点/滑动切换；`prefers-reduced-motion`；CSS 球回退；标题按名字长度保持一行；`canvas[data-ready]` 在贴图加载后才置位。
