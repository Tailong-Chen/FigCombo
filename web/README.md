# FigCombo Web - 科学图表组合工具

一个专业的科学图表组合 Web 应用，支持 Nature、Science、Cell 等顶级期刊的出版级多面板图表创建。

## 功能特性

### 布局系统
- **布局代码语法**：使用简洁的 ASCII 艺术定义面板布局
  - 基础网格：`aab/aac/ddd`
  - 命名区域：`[header:ab/cd] + [body:ef/gh]`
  - 子面板：`a[i,ii,iii]` 或 `a[2x3]`
  - 嵌入图：`a{0.7,0.7,0.25,0.25}` 或 `a<ab/cd>`
- **可视化编辑器**：拖拽式布局构建器
- **实时预览**：即时查看布局效果

### 图表类型
内置 20+ 种科学图表类型：

**统计图表**
- 条形图（分组/堆叠）
- 箱线图（带散点叠加）
- 小提琴图
- 散点图（带回归线）
- 直方图（带 KDE）
- 折线图（带误差带）

**生物信息学**
- 火山图
- MA 图
- 热图（带聚类）
- PCA 图（带置信椭圆）
- 相关矩阵

**生存分析**
- Kaplan-Meier 曲线
- 累积发病率
- 风险表

**影像**
- 多通道显微镜
- 强度分布
- ROI 叠加

**分子生物学**
- 序列 Logo
- 结构域架构
- 通路图

### 期刊支持
- 85+ 期刊预设（Nature、Science、Cell、PNAS 等）
- 自动尺寸、字体、DPI 适配
- 色盲友好配色
- 导出格式：PDF、PNG、SVG、TIFF

## 快速开始

### 安装依赖

```bash
# 后端依赖
pip install flask flask-cors matplotlib numpy pillow seaborn pandas scikit-learn scipy

# 前端依赖
cd frontend
npm install
```

### 启动服务

```bash
# 1. 启动后端 API（端口 5000）
cd /home/ctl/code/Figure_combination/web
python api.py --host 0.0.0.0 --port 5000

# 2. 启动前端开发服务器（端口 5173）
cd frontend
npm run dev
```

### 访问应用

- 前端界面：http://localhost:5173
- API 文档：http://localhost:5000/api/health

## 布局代码语法

### 基础语法

```
# 简单网格 - 2x2
ab/cd

# 混合大小 - a 占据 2x2，b、c、d 各占据 1x1
aab/aac/ddd

# 命名区域
[overview:ab/cd] + [details:efg/hij]
```

### 子面板

```
# 列表表示法 - a 面板包含 3 个子面板
a[i,ii,iii]b/cde

# 网格表示法 - a 面板是 2x3 网格
a[2x3]bc/def
```

### 嵌入图 (Insets)

```
# 绝对位置 - 在 (0.7, 0.7) 处放置 0.25x0.25 的嵌入图
a{0.7,0.7,0.25,0.25}bc/def

# 网格嵌入 - a 面板内嵌 ab/cd 网格
a<ab/cd>ef/gh

# 多个嵌入图
a{0.1,0.1,0.2,0.2}{0.7,0.7,0.25,0.25}bcd/efgh
```

### 复杂示例

```
# Nature 风格复杂图
[top:aa/bb] | [middle:c[2x2]/de] | [bottom:fghi/jklm]

# 显微镜图带多个放大区域
micro{zoom1,0.75,0.75,0.2,0.2}{zoom2,0.2,0.75,0.15,0.15}/quant
```

## API 参考

### 布局端点

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/layout/parse` | 解析布局代码 |
| POST | `/api/layout/validate` | 验证布局 |
| GET | `/api/layout/templates` | 获取模板列表 |

### 图表端点

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/plot-types` | 获取所有图表类型 |
| GET | `/api/plot-types/<category>` | 按分类获取 |
| GET | `/api/plot-types/<name>/schema` | 获取参数模式 |
| GET | `/api/plot-types/<name>/preview` | 获取占位预览 |

### 图表端点

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/figure/generate` | 生成图表 |
| POST | `/api/figure/preview` | 快速预览 |
| POST | `/api/figure/export` | 导出图表 |

### 项目端点

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/project/save` | 保存项目 |
| GET | `/api/project/load/<name>` | 加载项目 |
| GET | `/api/project/list` | 列出项目 |

## 项目结构

```
web/
├── api.py                 # Flask API 后端
├── layout_parser.py       # 布局代码解析器
├── app.py                 # 旧版 Flask 应用（已弃用）
├── uploads/               # 上传文件存储
├── outputs/               # 生成图表输出
├── projects/              # 保存的项目
├── templates/             # HTML 模板
├── static/                # 静态资源
└── frontend/              # React 前端
    ├── package.json
    ├── src/
    │   ├── components/    # React 组件
    │   ├── stores/        # Zustand 状态管理
    │   ├── api/           # API 客户端
    │   ├── types/         # TypeScript 类型
    │   └── utils/         # 工具函数
    └── public/
```

## 开发指南

### 添加新的图表类型

1. 在 `figcombo/plot_types/` 创建图表函数
2. 使用 `@register_plot_type` 装饰器注册
3. 在 `api.py` 的 `PLOT_TYPES` 中添加元数据
4. 实现 `render_placeholder` 方法用于预览

### 添加新的布局模板

1. 在 `api.py` 的 `LAYOUT_TEMPLATES` 中添加模板定义
2. 提供布局代码、描述和推荐尺寸

### 自定义期刊样式

1. 在 `figcombo/knowledge/journal_specs.py` 中添加期刊规格
2. 指定宽度、字体、DPI、配色等参数

## 技术栈

**后端**
- Python 3.9+
- Flask + Flask-CORS
- Matplotlib + Seaborn
- NumPy + Pandas + SciPy
- Scikit-learn (PCA)

**前端**
- React 18 + TypeScript
- Vite
- Tailwind CSS
- Zustand (状态管理)
- @dnd-kit (拖拽)
- CodeMirror 6 (代码编辑)
- Headless UI

## 许可证

MIT License

## 致谢

- 配色方案基于 [Okabe-Ito 色盲友好配色](https://jfly.uni-tokyo.ac.jp/color/)
- 期刊规格参考各出版社官方指南
