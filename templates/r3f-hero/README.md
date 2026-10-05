# r3f-hero template

可直接运行的 Vite + React 19 + React Three Fiber 首屏脚手架，供 One-Click Replica 使用。**不要手工复制**，用：

```sh
python scripts/replica_init.py --out ./my-site --name "Brand" --variant glass-knot --run-url http://127.0.0.1:5173/
cd my-site && npm install && npm run dev
```

## 复刻时只改这几处

| 文件 | 对应 Replica Card 字段 |
| --- | --- |
| `src/theme.ts` `colors` | `color_roles` |
| `src/theme.ts` `fonts` + `main.tsx` 的 `@fontsource` 导入 | `type_hierarchy` |
| `src/theme.ts` `hero` | `hero_silhouette`（主体靠左/右/居中，占宽比例） |
| `src/theme.ts` `scene` | scene contract（variant / 指针倾斜 / 自转 / dpr） |
| `src/theme.ts` `copy` | 原创文案（不得沿用参考的品牌文案） |
| `src/styles.css` | 栅格、字号比例、首个过渡 |
| `src/scene/HeroScene.tsx` | 新增或调整 3D variant |

## 已内置的质量保证

- 由 `useThree().viewport` 推导主体位置与尺寸，任意比例不裁切。
- 透射玻璃背后有柔和发光，深色页面不发黑。
- CSS 轮廓回退：先绘制，WebGL 就绪后淡出；WebGL 不可用时仍是完整页面。
- `prefers-reduced-motion`：`frameloop="demand"`、无自转、无指针响应、marquee 停止。
- 手机降低几何与采样、限制 dpr。
- 字体通过 `@fontsource` 打包，不依赖外网。
- `canvas[data-ready="true"]` 与 `[data-region]` 标记供 `scripts/capture.mjs` 使用。

## 3D variants

`glass-knot`（折射玻璃）· `liquid-blob`（液态金属）· `orbit-cards`（环绕卡片）。新增 variant：在 `HeroScene.tsx` 写一个组件、调用 `useRig(group)` 获得统一的指针/自转响应、加入 `variants` 表和 `theme.ts` 的 `SceneVariant`。
