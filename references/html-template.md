# HTML 报告固定骨架模板（v1.4 新增）

> 地位：`references/html-template.md`，[SUPPLEMENTAL]，由 SKILL.md 第九章第 8 条引用。
> 用途：把 `aesthetics.md` 的 Design Tokens 与结构节奏，固化为**可直接套用的 HTML 骨架**，保证任何盘跑完都能稳定产出同等质量报告——**非逐盘手写**。
> 使用方式：以下骨架为固定结构，产 HTML 时只替换 `{{…}}` 占位符与各区块内容，**不改动 CSS 变量与区块顺序**。

---

## 一、固定 CSS 变量（Design Tokens，与 aesthetics.md 一致）

```css
:root {
  --brand: #1e3a34;      /* 主色·墨绿：标题/强调/深色结论卡 */
  --brand-light: #e8f0ee;/* 主色浅底：提示块/表头 */
  --bg: #faf9f5;         /* 页面底·米白 */
  --panel: #ffffff;      /* 卡片底 */
  --ink: #2a2a28;        /* 正文 */
  --ink-light: #6b6b66;  /* 次要文字/标注 */
  --border: #e6e4dc;     /* 分隔线 */
  --gold: #b8891e;       /* 五行·金 */
  --wood: #3e7a4f;       /* 五行·木 */
  --water: #2f6d9e;      /* 五行·水 */
  --fire: #c0392b;       /* 五行·火 */
  --earth: #9a6a3a;      /* 五行·土 */
}
```

五行字类（固定）：`.m`金 `.wx`木 `.s`水 `.h`火 `.t`土；喜忌符号：`●`喜用 `○`忌神（正交通道，禁用红=忌）。

---

## 二、固定区块骨架（第一轮：用户未提供经历 / 喜忌清晰）

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>跃渊 · {{姓名}}</title>
<style>
  /* ① 粘贴「一、固定 CSS 变量」中的 :root 块 */
  /* ② 粘贴下方「三、基础排版样式」（固定不动） */
</style>
</head>
<body>
<div class="wrap">
  <div class="eyebrow">跃渊 v{{版本号}} · {{性别：男填"乾造"／女填"坤造"，二选一，禁止并列}}</div>
  <h1>{{姓名}}</h1>
  <div class="tag-row">
    <span class="badge">不确定度：{{高/中/低}}</span>
    <span class="badge">{{大运齐全 / 大运缺失}}</span>
  </div>

  <!-- 预期管理提示（不确定度≥中或存在路线竞争时强制） -->
  <div class="alert"><strong>请先读这一句：</strong>{{预期管理文案}}<strong>结论是验证出来的，不是算出来的。</strong></div>

  <!-- 核心总评（焦点，最大字号） -->
  <section class="verdict">
    <h2>{{核心总评：格局/喜忌一句话}}</h2>
    <p>{{一句支撑：旺衰依据 + 关键争议}}</p>
  </section>

  <!-- 路线判定 / 竞争假设（仅临界盘并列两条相反路线；一般盘为「当前判断 + 已排除」） -->
  <h2>路线判定</h2>
  <div class="routes">
    <div class="route-card">{{路线 A 摘要卡（喜/忌/3-4 点）}}</div>
    <div class="route-card alt">{{路线 B 摘要卡 或「已排除」说明}}</div>
  </div>

  <!-- 小白通俗层（喜忌明确即给，无路线竞争时第一轮就出） -->
  <h2>喜用神翻译 · 你的八字在说什么</h2>
  <div class="test-card">{{翻译层内容：能量型态 + 喜忌人生语言}}</div>

  <h2>五行喜用 · 生活中的助力参考</h2>
  <div class="meta">{{喜用五行 1-2 条：方位/颜色/环境/职业意象}}</div>
  <p class="section-note">* 传统民俗趋避习惯，非科学论断、不保证效果，仅作意象参考。健康问题请咨询专业医师。</p>

  <h2>基于此方向的领域解读</h2>
  <div class="meta">
    <div class="meta-item"><strong>学业/事业</strong>{{…}}</div>
    <div class="meta-item"><strong>财富</strong>{{…}}</div>
    <div class="meta-item"><strong>婚恋</strong>{{…}}</div>
    <div class="meta-item"><strong>身心</strong>{{…}}</div>
  </div>

  <!-- 专业层（进阶内容，小白可跳过） -->
  <h2>盘基信息 <span class="label">进阶内容 · 小白可跳过</span></h2>
  <table>{{四柱表：天干/地支/藏干/空亡}}</table>

  <h2>用神六维一致性 <span class="label">进阶内容 · 小白可跳过</span></h2>
  <div class="meta">{{六维 meta-item × 6}}</div>

  <h2>关键变量 <span class="label">进阶内容 · 小白可跳过</span></h2>
  <div class="meta">{{合化/自刑/病型等关键变量}}</div>

  <h2>大运流年 <span class="label">进阶内容 · 小白可跳过</span></h2>
  <table>{{大运表}}</table>

  <h2>Phase A · 预注册预测</h2>
  <div class="test-card">{{最优假设/用神/关键争议/高概率主题/推翻条件}}</div>

  <div class="disclaimer">{{免责声明}}</div>
</div>
</body>
</html>
```

---

## 三、基础排版样式（固定，粘贴即用）

```css
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--ink); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif; line-height:1.75; padding:48px 24px; }
.wrap { max-width:720px; margin:0 auto; }
.eyebrow { font-size:12px; letter-spacing:2px; color:var(--ink-light); text-transform:uppercase; margin-bottom:8px; }
h1 { font-family:"Songti SC","Noto Serif SC",serif; font-size:38px; font-weight:700; margin:0 0 8px; color:var(--brand); letter-spacing:1px; }
h2 { font-family:"Songti SC","Noto Serif SC",serif; font-size:22px; font-weight:600; color:var(--brand); margin:48px 0 18px; padding-bottom:8px; border-bottom:1px solid var(--border); }
h3 { font-size:16px; font-weight:600; color:var(--brand); margin:28px 0 10px; }
.alert { background:var(--brand-light); border-left:3px solid var(--brand); padding:16px 20px; margin:24px 0; border-radius:0 8px 8px 0; }
.alert strong { color:var(--brand); }
.tag-row { margin:12px 0 18px; }
.badge { display:inline-block; font-size:12px; letter-spacing:1px; padding:4px 12px; border:1px solid var(--brand); color:var(--brand); border-radius:999px; margin-right:8px; }
.verdict { margin-bottom:36px; }
.verdict h2 { border:none; padding:0; margin:0 0 16px; font-size:26px; line-height:1.45; }
.verdict p { margin:0; color:var(--ink-light); font-size:15px; }
.routes { display:grid; grid-template-columns:1fr 1fr; gap:16px; margin:24px 0; }
@media (max-width:640px){ .routes{ grid-template-columns:1fr; } .meta{ grid-template-columns:1fr; } }
.route-card { background:var(--panel); border:1px solid var(--border); border-radius:10px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,0.03); }
.route-card h4 { margin:0 0 10px; font-size:15px; color:var(--brand); }
.route-card ul { margin:0; padding-left:18px; font-size:14px; color:var(--ink-light); }
.route-card li { margin-bottom:6px; }
.route-card .tag { font-size:12px; color:#fff; background:var(--brand); padding:2px 8px; border-radius:4px; display:inline-block; margin-top:10px; }
.route-card.alt { border-top:3px solid var(--earth); }
.route-card.alt h4 { color:var(--earth); }
.route-card.alt .tag { background:var(--earth); }
table { width:100%; border-collapse:collapse; background:var(--panel); border-radius:10px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.03); margin:16px 0; }
th,td { padding:12px 14px; text-align:center; border-bottom:1px solid var(--border); font-size:14px; }
th { background:var(--brand-light); color:var(--brand); font-weight:600; }
tr:last-child td { border-bottom:none; }
.meta { display:grid; grid-template-columns:repeat(2,1fr); gap:12px; margin:16px 0; }
.meta-item { background:var(--panel); border:1px solid var(--border); border-radius:8px; padding:12px 14px; font-size:14px; }
.meta-item strong { display:block; font-size:12px; color:var(--ink-light); margin-bottom:4px; font-weight:500; }
.label { display:inline-block; font-size:11px; padding:1px 6px; border-radius:4px; background:#f0efea; color:var(--ink-light); margin-left:6px; vertical-align:middle; }
.test-card { background:var(--brand); color:#fff; border-radius:10px; padding:22px; margin:24px 0; }
.test-card h4 { margin:0 0 12px; font-size:16px; }
.test-card p { margin:0 0 10px; font-size:14px; opacity:0.92; }
.test-card ul { margin:0; padding-left:18px; font-size:14px; opacity:0.92; }
.section-note { font-size:13px; color:var(--ink-light); margin-top:8px; }
.disclaimer { font-size:12px; color:var(--ink-light); margin-top:48px; padding-top:18px; border-top:1px solid var(--border); }
.wx{ color:var(--wood); font-weight:600; } .h{ color:var(--fire); font-weight:600; } .t{ color:var(--earth); font-weight:600; } .m{ color:var(--gold); font-weight:600; } .s{ color:var(--water); font-weight:600; }
.like{ font-weight:600; } .dislike{ opacity:0.55; }
```

---

## 四、第二轮形态（用户给过反馈，Phase B 出现时）

在第一轮骨架的「路线判定」之后、盘基之前，插入以下两段，其余不变：

```html
<!-- Phase B · 阶段性收敛结论（深绿卡，分级措辞） -->
<h2>Phase B · 阶段性收敛结论</h2>
<div class="test-card">
  <h4>基于当前信息，{{目前更支持 / 明显占优}}：{{路线}}，喜 {{五行}} 忌 {{五行}}</h4>
  <p>{{支持句：某年某事与某判断一致}}</p>
  <p>{{温和缺口引导}}</p>
</div>

<!-- 已被削弱/待验证 -->
<div class="alert"><strong>已被削弱：</strong>{{被削弱假设}}<br><strong>诚实边界：</strong>{{部分命中级说明}}</div>
```

---

## 五、产出纪律

1. **只替换 `{{…}}` 与各区块内容，不改 CSS 变量、不改区块顺序、不改排版样式**——保证跨盘视觉一致。
2. 不确定度徽章用「高/中/低」文字（不伪造百分比）。
3. 路线判定区：临界盘并列两条相反路线（对称卡）；一般盘用「当前判断 + 已排除」形态。
4. 身心板块免责声明必须保留（文末弱化）。
5. 五行色只用于干支/藏干/喜忌字标签；十神不上色。
6. **版本号使用 `{{版本号}}` 占位符**，产出时填 SKILL.md frontmatter 的当前版本（v1.8），随 SKILL.md 版本同步更新，禁止写死旧版本号。
