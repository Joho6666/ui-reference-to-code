# Browser Validation — Visual QA Loop

B/C/D 及 E/F 实现都经过本流程。输入：运行代码、保留基线、参考规格 / 设计系统、组件映射。输出：桌面和手机截图、关键行为、Visual Difference Report、分数及交付状态。

## 1. 运行与采样

使用项目实际启动脚本或适合静态项目的 HTTP 服务；保存命令、工作目录、预览 URL 和代码版本。不把 `file://` 成功视为模块、接口或部署验证。

读取当前可用浏览器技能，确认可控页面和实际 API，复用当前任务空间。桌面采用参考视口或项目目标尺寸；手机采用已知目标设备，缺失时可用约 390 CSS px 宽。尺寸是采样选择，不是通用设计参数。

等待字体、图片和相关布局稳定后截图。记录 viewport/DPR、scroll/anchor、theme、state、截图路径及观察范围。换视口后重新进入目标位置，避免旧滚动造成裁切。对动效比较固定相同阶段或观察终态；不得通过禁用所有动效掩盖交互问题。

截图必须实际查看。DOM 支持语义和状态判断；canvas 元素、iframe load、无报错都不能证明可见画面符合设计。

## 2. 每轮操作

```text
实现 → 启动 / 复用预览 → 桌面截图与操作 → 手机截图与操作
     → 同状态比较 → 差异分类 / 评分 → 修 Critical / Major
     → 重拍受影响视口 → 更新报告
```

默认初检后最多 3 轮有针对性的修复（总观察轮数可至 4），用户明确另定预算时沿用；每轮记录修改及前后差异。第一轮已达完成条件可结束，避免为轮数重复检查。后续只重查受影响区域和相关回归；先前有效且代码未影响的手机 / 行为证据可沿用并标明版本。

无进展或同一阻塞重复时定位字体、素材、主题、浏览器控制或输入限制。用已有替代路径继续；达到约定修复预算仍有低分或严重问题，交付待修状态与具体下一步，不能人为抬分或把暂停称完成。

## 3. 当前修改范围检查

| 关注点 | 实际观察 / 操作 |
| --- | --- |
| Hero / 标题 | 溢出、换行、阅读顺序、关键图像与按钮；检查真实加载字体 |
| Container / spacing | 容器上限、左右边距、节间距、卡片密度、对齐与视觉重量 |
| Nav / sticky | 跳转后目标可见、固定导航不遮挡、手机展开与关闭 |
| 图片 | 主体焦点、比例与裁切、加载失败替代；不会把示意图当项目截图 |
| 交互 | 搜索命中 / 空结果 / 清空、tabs、链接、提交、卡片和焦点路径 |
| 响应式 | 堆叠、菜单、横向溢出、触屏替代；发现问题再补断点附近 |
| 动效 | trigger、终态、取消、reduced-motion；hover 不阻止点击 / 滚动 |
| 可访问性 | 修改区域的语义、键盘、focus、文字对比、alt、touch target |

对比度能计算时记录值及目标；不能仅靠感觉宣称通过。触屏目标依据项目可访问性规范，缺少规范时优先至少 24 CSS px 或足够间距，主要按钮更宽松。不要把装饰图的空 alt 当错误，也不要给功能图缺失替代文本找借口。

## 4. 证据不足的退路

浏览器工具缺失 / 失联：先发现已有能力、控制权和服务状态；可使用当前允许的浏览器自动化或已有截图。没有可用运行画面时完成构建、语法、代码及现有功能检查，关键视觉维度保持 unverified，记录恢复动作。

用户手动提供截图可作为观察证据，但需标明版本、视口与未操作状态；它不能证明尚未测试的点击。Pixel Fidelity 缺源截图时用可访问源材料推进并标记未知，不能给出“像素还原已完成”。

## 5. 可持久化 QA JSON

聊天任务可直接写报告；多轮任务按需存 `.ui-design/qa.json`，供 `scripts/qa_gate.py` 判定。下面是**格式样例，无真实验证结果**；真实任务替换全部证据与状态。

```json
{
  "schema_version": 1,
  "mode": "D",
  "modifiers": [],
  "scope": "homepage hero and project cards",
  "iteration": 1,
  "code_checks": "passed",
  "preservation": "passed",
  "browser": {
    "desktop": {"observed": false, "screenshot": "", "viewport": [1440, 900]},
    "mobile": {"observed": false, "screenshot": "", "viewport": [390, 844]}
  },
  "comparison": {"reviewed": false, "kind": "design-spec", "baseline": "", "implemented": "", "same_conditions": false},
  "dimensions": {
    "layout": {"applicable": true, "score": null, "evidence": []},
    "typography": {"applicable": true, "score": null, "evidence": []},
    "color": {"applicable": true, "score": null, "evidence": []},
    "component": {"applicable": true, "score": null, "evidence": []},
    "responsive": {"applicable": true, "score": null, "evidence": []},
    "interaction": {"applicable": true, "score": null, "evidence": []}
  },
  "differences": []
}
```

differences 项：`id、severity (Critical/Major/Minor)、resolved、location、evidence、description`。不适用维度设置 `applicable:false、score:null、reason:具体原因`；layout/responsive 为实现必查，不能豁免。至少执行一次相关关键行为，保留基线状态必须有真实依据。

`comparison.kind`：E 使用 reference，其他使用 reference 或 design-spec。E 要求 same_conditions；手机无源样本时单独标 adapted，不假造手机对照。

执行 `python3 scripts/qa_gate.py <qa.json>`，返回 verified / needs-repair / unverified / invalid-report。脚本检查字段、证据引用和阈值；不会检查图片像素、证明报告真实性或替代 Agent 实际视觉观察。
