/**
 * FigCombo Web - Main JavaScript
 * Handles drag-and-drop, canvas rendering, zoom controls, and API communication
 */

// ============================================
// GLOBAL STATE - 全局状态
// ============================================
const state = {
    journal: 'nature',
    size: 'double_column',
    layout: '',
    height_mm: 150,
    panels: {},
    selectedPanel: null,
    templates: [],
    plotTypes: [],
    uploadedImages: [],
    uploadedCode: [],
    currentProject: null,
    theme: localStorage.getItem('theme') || 'light'
};

// ============================================
// ZOOM STATE - 缩放状态
// ============================================
const zoomState = {
    scale: 1.0,
    minScale: 0.25,
    maxScale: 2.0,
    step: 0.25,
    isFitToContainer: false
};

// ============================================
// TEMPLATE LIBRARY - 丰富的属性面板模板库
// ============================================
const templateLibrary = {
    statistics: [
        {
            id: 'grouped_bar',
            name: '分组条形图',
            nameEn: 'Grouped Bar Chart',
            icon: 'bar',
            description: '带误差线的分组条形图，适合比较多个实验组',
            useCase: '适用于比较不同处理组之间的均值差异，如药物处理vs对照组',
            dataFormat: 'CSV格式：\ngroup,value,error\nControl,10,1.5\nTreatment,15,2.0',
            features: ['Okabe-Ito配色', '误差线(SEM)', '无框线图', '7pt字体'],
            plotType: 'bar_plot',
            recommendedParams: { error_type: 'sem', show_individual_points: false, bar_width: 0.7 }
        },
        {
            id: 'box_plot',
            name: '箱线图',
            nameEn: 'Box Plot',
            icon: 'box',
            description: '多组比较的箱线图，展示数据分布',
            useCase: '适用于展示数据分布、中位数、四分位数和异常值',
            dataFormat: 'CSV格式：\ngroup,value\nA,1.2\nA,2.3\nB,1.8\nB,2.5',
            features: ['显示中位数', '显示异常值', '无框线图', '色盲友好'],
            plotType: 'box_plot',
            recommendedParams: { show_notch: false, show_outliers: true }
        },
        {
            id: 'violin_plot',
            name: '小提琴图',
            nameEn: 'Violin Plot',
            icon: 'violin',
            description: '展示大数据集分布的小提琴图',
            useCase: '适用于大数据集(n>30)的分布展示，比箱线图更直观',
            dataFormat: 'CSV格式：\ngroup,value\nGroup1,2.5\nGroup1,3.1\nGroup2,2.8',
            features: ['核密度估计', '内置箱线图', '渐变配色', '无框线图'],
            plotType: 'violin_plot',
            recommendedParams: { show_inner_boxplot: true, bandwidth: 'scott' }
        },
        {
            id: 'scatter_regression',
            name: '散点图+回归',
            nameEn: 'Scatter with Regression',
            icon: 'scatter',
            description: '带回归线的散点图，适合相关性分析',
            useCase: '适用于展示两个变量之间的相关性，如基因表达与表型',
            dataFormat: 'CSV格式：\nx,y\n1.2,3.4\n2.1,4.5\n3.5,5.6',
            features: ['线性回归线', '置信区间', '相关系数R2', '散点抖动'],
            plotType: 'scatter_plot',
            recommendedParams: { show_regression: true, show_confidence_interval: true, point_alpha: 0.6 }
        },
        {
            id: 'time_series',
            name: '时间序列图',
            nameEn: 'Time Series',
            icon: 'line',
            description: '展示动态变化的时间序列图',
            useCase: '适用于展示随时间变化的实验数据，如细胞生长曲线',
            dataFormat: 'CSV格式：\ntime,group,value\n0h,Control,100\n0h,Treat,100\n24h,Control,110',
            features: ['平滑曲线', '误差带', '时间点标记', '图例优化'],
            plotType: 'line_plot',
            recommendedParams: { line_style: 'solid', marker: 'o', markersize: 4 }
        },
        {
            id: 'histogram_overlay',
            name: '叠加直方图',
            nameEn: 'Overlaid Histogram',
            icon: 'hist',
            description: '多组数据分布比较的叠加直方图',
            useCase: '适用于比较不同组的分布特征，如对照组vs处理组',
            dataFormat: 'CSV格式：\ngroup,value\nA,1.2\nA,2.3\nB,1.8\nB,2.5',
            features: ['半透明叠加', '密度曲线', '自动分箱', '无框线图'],
            plotType: 'histogram',
            recommendedParams: { bins: 'auto', alpha: 0.5, density: true }
        }
    ],
    bioinformatics: [
        {
            id: 'volcano_plot',
            name: '火山图',
            nameEn: 'Volcano Plot',
            icon: 'volcano',
            description: '标准Nature风格的差异表达火山图',
            useCase: '适用于RNA-seq差异表达分析，展示log2FC和p值',
            dataFormat: 'CSV格式：\ngene,log2fc,pvalue\nGene1,2.5,0.001\nGene2,-1.8,0.01',
            features: ['阈值线标记', '显著性着色', '基因标签', '交互式悬停'],
            plotType: 'volcano_plot',
            recommendedParams: { fc_threshold: 1.0, p_threshold: 0.05, show_labels: true }
        },
        {
            id: 'ma_plot',
            name: 'MA图',
            nameEn: 'MA Plot',
            icon: 'scatter',
            description: '基因表达差异的MA图',
            useCase: '适用于展示表达量与差异倍数的关系，识别偏差',
            dataFormat: 'CSV格式：\ngene,mean,log2fc\nGene1,100,2.5\nGene2,50,-1.8',
            features: ['中位数参考线', '显著性着色', '低表达过滤', '无框线图'],
            plotType: 'ma_plot',
            recommendedParams: { low_expression_threshold: 10, show_significant: true }
        },
        {
            id: 'heatmap_cluster',
            name: '聚类热图',
            nameEn: 'Clustered Heatmap',
            icon: 'heatmap',
            description: '带聚类树的表达热图',
            useCase: '适用于基因表达矩阵的可视化，展示样本和基因聚类',
            dataFormat: 'CSV格式：\ngene,sample1,sample2\nGene1,5.2,6.1\nGene2,3.4,4.5',
            features: ['层次聚类', '聚类树', '颜色标尺', '行/列标准化'],
            plotType: 'heatmap',
            recommendedParams: { clustering: 'both', cmap: 'RdBu_r', standardization: 'row' }
        },
        {
            id: 'pca_plot',
            name: 'PCA散点图',
            nameEn: 'PCA Scatter',
            icon: 'scatter',
            description: '主成分分析散点图',
            useCase: '适用于样本聚类和批次效应检查',
            dataFormat: 'CSV格式：\nsample,PC1,PC2,group\nS1,10,20,Control\nS2,15,25,Treat',
            features: ['置信椭圆', '方差解释率', '分组着色', '样本标签'],
            plotType: 'pca_plot',
            recommendedParams: { show_ellipse: true, show_variance: true, pc_components: [1, 2] }
        },
        {
            id: 'enrichment_bar',
            name: '富集分析条形图',
            nameEn: 'Enrichment Bar',
            icon: 'bar',
            description: 'GO/KEGG富集分析结果条形图',
            useCase: '适用于展示富集通路的显著性和基因数量',
            dataFormat: 'CSV格式：\nterm,pvalue,gene_count\nPathway1,0.001,25\nPathway2,0.01,18',
            features: ['-log10(p值)着色', '基因数显示', '水平条形', '通路名称截断'],
            plotType: 'enrichment_plot',
            recommendedParams: { orientation: 'horizontal', max_terms: 15, color_by: 'pvalue' }
        }
    ],
    imaging: [
        {
            id: 'multi_channel',
            name: '多通道显微镜',
            nameEn: 'Multi-channel Microscopy',
            icon: 'microscope',
            description: 'DAPI/GFP/Merge多通道展示',
            useCase: '适用于荧光显微镜图像的标准展示',
            dataFormat: '图像文件：\n- DAPI通道 (蓝色)\n- GFP通道 (绿色)\n- Merge合成图',
            features: ['通道标签', '比例尺', '统一对比度', '白色背景'],
            plotType: 'image',
            recommendedParams: { channels: ['DAPI', 'GFP', 'Merge'], scale_bar: '50 μm', background: 'white' }
        },
        {
            id: 'western_blot',
            name: 'Western Blot',
            nameEn: 'Western Blot',
            icon: 'western',
            description: '带定量图的Western Blot展示',
            useCase: '适用于蛋白表达水平的半定量展示',
            dataFormat: '图像+定量数据：\n- 原始条带图\n- 相对表达量CSV',
            features: ['分子量标记', '条带标注', '定量条形图', '统计显著性'],
            plotType: 'composite',
            recommendedParams: { show_mw_marker: true, include_quantification: true, normalization: 'loading_control' }
        },
        {
            id: 'cell_count',
            name: '细胞计数统计',
            nameEn: 'Cell Count Statistics',
            icon: 'bar',
            description: '细胞计数结果的统计图',
            useCase: '适用于细胞增殖、凋亡等计数实验',
            dataFormat: 'CSV格式：\ngroup,count\nControl,150\nTreatment,89',
            features: ['个体数据点', '均值±SEM', '显著性标记', '无框线图'],
            plotType: 'bar_plot',
            recommendedParams: { show_individual_points: true, jitter: 0.2, error_type: 'sem' }
        },
        {
            id: 'fluorescence_intensity',
            name: '荧光强度定量',
            nameEn: 'Fluorescence Intensity',
            icon: 'violin',
            description: '荧光强度的定量分析图',
            useCase: '适用于免疫荧光、报告基因等强度定量',
            dataFormat: 'CSV格式：\ngroup,intensity\nControl,1000\nControl,1200\nTreat,800',
            features: ['背景校正', '相对强度', '统计检验', '小提琴+箱线图'],
            plotType: 'violin_plot',
            recommendedParams: { background_subtraction: true, normalization: 'control', show_stats: true }
        }
    ],
    composite: [
        {
            id: 'layout_1_3',
            name: '大图+3小图',
            nameEn: 'Large + 3 Small',
            icon: 'layout-1-3',
            description: '经典Nature布局：左侧大图，右侧3个小图',
            useCase: '适用于主图+补充实验的经典Nature布局',
            dataFormat: '4个面板：\nA: 主结果\nB-D: 补充数据',
            features: ['A面板占50%', 'B-D垂直排列', '统一间距', '对齐网格'],
            plotType: 'layout',
            recommendedParams: { layout: 'AB\nAC\nAD', panel_ratios: { A: 2, B: 1, C: 1, D: 1 } }
        },
        {
            id: 'layout_2x2',
            name: '2x2网格',
            nameEn: '2x2 Grid',
            description: '4个相关实验的2x2网格布局',
            useCase: '适用于4个相关实验的并列展示',
            dataFormat: '4个面板：\nA B\nC D',
            features: ['等分布局', '统一尺寸', '行列对齐', '紧凑间距'],
            plotType: 'layout',
            recommendedParams: { layout: 'AB\nCD', equal_size: true }
        },
        {
            id: 'layout_timeseries',
            name: '时间序列(6点)',
            nameEn: 'Time Series (6 points)',
            icon: 'layout-1x6',
            description: '6个时间点的横向排列',
            useCase: '适用于时间序列实验的连续展示',
            dataFormat: '6个面板：\nT0 T1 T2 T3 T4 T5',
            features: ['等宽排列', '时间标签', '统一比例', '紧凑布局'],
            plotType: 'layout',
            recommendedParams: { layout: 'ABCDEF', orientation: 'horizontal', time_labels: ['0h', '4h', '8h', '12h', '24h', '48h'] }
        }
    ]
};

let currentTemplateCategory = 'statistics';
let appliedTemplates = new Set();
let selectedTemplateId = null;

// DOM Elements
let elements = {};

// ============================================
// INITIALIZATION
// ============================================
async function init() {
    console.log('Initializing FigCombo Web...');

    // Initialize elements after DOM is ready
    initElements();

    applyTheme(state.theme);
    await loadTemplates();
    await loadPlotTypes();
    await loadUploadedFiles();
    setupEventListeners();
    setupDragAndDrop();
    setupZoomControls();
    setupWindowResize();
    initTemplateLibrary();
    bindMissingEvents();
    updateCanvasDimensions();

    console.log('FigCombo Web initialized successfully');
}

function initElements() {
    elements = {
        journalSelect: document.getElementById('journal-select'),
        sizeSelect: document.getElementById('size-select'),
        btnPreview: document.getElementById('btn-preview'),
        btnExport: document.getElementById('btn-export'),
        btnSaveProject: document.getElementById('btn-save-project'),
        btnLoadProject: document.getElementById('btn-load-project'),
        btnTheme: document.getElementById('btn-theme'),
        figureCanvas: document.getElementById('figure-canvas'),
        canvasContainer: document.getElementById('canvas-container'),
        canvasDimensions: document.getElementById('canvas-dimensions'),
        canvasLayout: document.getElementById('canvas-layout'),
        btnClearCanvas: document.getElementById('btn-clear-canvas'),
        templatesList: document.getElementById('templates-list'),
        propertiesPanel: document.getElementById('properties-panel'),
        imagesGrid: document.getElementById('images-grid'),
        codeList: document.getElementById('code-list'),
        btnUploadImage: document.getElementById('btn-upload-image'),
        btnUploadCode: document.getElementById('btn-upload-code'),
        exportModal: document.getElementById('export-modal'),
        panelModal: document.getElementById('panel-modal'),
        previewModal: document.getElementById('preview-modal'),
        uploadImageModal: document.getElementById('upload-image-modal'),
        uploadCodeModal: document.getElementById('upload-code-modal'),
        projectModal: document.getElementById('project-modal'),
        sampleDataModal: document.getElementById('sample-data-modal'),
        exportFormat: document.getElementById('export-format'),
        exportDpi: document.getElementById('export-dpi'),
        exportFilename: document.getElementById('export-filename'),
        btnConfirmExport: document.getElementById('btn-confirm-export'),
        panelType: document.getElementById('panel-type'),
        imageSelection: document.getElementById('image-selection'),
        plotSelection: document.getElementById('plot-selection'),
        codeSelection: document.getElementById('code-selection'),
        textContent: document.getElementById('text-content'),
        panelImageGrid: document.getElementById('panel-image-grid'),
        plotTypeSelect: document.getElementById('plot-type-select'),
        codeFileSelect: document.getElementById('code-file-select'),
        codeFunctionName: document.getElementById('code-function-name'),
        panelTextContent: document.getElementById('panel-text-content'),
        btnSavePanel: document.getElementById('btn-save-panel'),
        imgTrim: document.getElementById('img-trim'),
        imgAutoContrast: document.getElementById('img-auto-contrast'),
        imgScaleBar: document.getElementById('img-scale-bar'),
        imgColormap: document.getElementById('img-colormap'),
        imgRotation: document.getElementById('img-rotation'),
        imgBrightness: document.getElementById('img-brightness'),
        imgContrast: document.getElementById('img-contrast'),
        imgFlipH: document.getElementById('img-flip-h'),
        imgFlipV: document.getElementById('img-flip-v'),
        previewContainer: document.getElementById('preview-container'),
        previewInfo: document.getElementById('preview-info'),
        btnExportFromPreview: document.getElementById('btn-export-from-preview'),
        imageDropZone: document.getElementById('image-drop-zone'),
        imageFileInput: document.getElementById('image-file-input'),
        imageUploadProgress: document.getElementById('image-upload-progress'),
        codeDropZone: document.getElementById('code-drop-zone'),
        codeFileInput: document.getElementById('code-file-input'),
        codeUploadProgress: document.getElementById('code-upload-progress'),
        projectModalTitle: document.getElementById('project-modal-title'),
        saveProjectSection: document.getElementById('save-project-section'),
        loadProjectSection: document.getElementById('load-project-section'),
        projectName: document.getElementById('project-name'),
        projectsList: document.getElementById('projects-list'),
        projectFileInput: document.getElementById('project-file-input'),
        btnConfirmProject: document.getElementById('btn-confirm-project'),
    };
}

// ============================================
// TEMPLATE LIBRARY FUNCTIONS
// ============================================
function initTemplateLibrary() {
    console.log('Initializing template library...');

    // Tab switching
    document.querySelectorAll('[data-prop-tab]').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('[data-prop-tab]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            document.querySelectorAll('.properties-tab-content').forEach(t => t.classList.remove('active'));
            document.getElementById(`prop-tab-${btn.dataset.propTab}`).classList.add('active');
        });
    });

    // Category buttons
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentTemplateCategory = btn.dataset.category;
            renderTemplateGrid(currentTemplateCategory);
        });
    });

    console.log('Template library initialized');
    renderTemplateGrid('statistics');
    initStylesPanel();
}

function renderTemplateGrid(category) {
    console.log('Rendering templates for category:', category);
    const grid = document.getElementById('template-grid');
    if (!grid) {
        console.error('Template grid element not found');
        return;
    }

    const templates = templateLibrary[category] || [];
    console.log('Found', templates.length, 'templates for category', category);

    grid.innerHTML = templates.map(template => `
        <div class="template-card ${appliedTemplates.has(template.id) ? 'applied' : ''} ${selectedTemplateId === template.id ? 'selected' : ''}"
             data-template-id="${template.id}"
             data-category="${category}">
            <div class="template-preview">
                ${getTemplatePreview(template.icon)}
            </div>
            <h4>${template.name}</h4>
            <div class="template-name-en">${template.nameEn}</div>
            <div class="template-tags">
                <span class="template-tag">${template.plotType}</span>
            </div>
        </div>
    `).join('');

    // Bind click events after rendering
    document.querySelectorAll('.template-card').forEach(card => {
        card.addEventListener('click', (e) => {
            const templateId = card.dataset.templateId;
            const cat = card.dataset.category;
            console.log('Template clicked:', templateId, 'category:', cat);
            selectTemplate(cat, templateId, card);
        });
    });

    console.log('Template grid rendered with', templates.length, 'items');
}

function getTemplatePreview(icon) {
    const previews = {
        bar: `<div class="preview-bar-chart"><div class="preview-bar" style="height:60%"></div><div class="preview-bar" style="height:80%"></div><div class="preview-bar" style="height:50%"></div><div class="preview-bar" style="height:70%"></div><div class="preview-bar" style="height:90%"></div></div>`,
        box: `<div class="preview-box-plot"><div class="preview-box"></div><div class="preview-box"></div><div class="preview-box"></div></div>`,
        violin: `<div class="preview-violin"><div class="preview-violin-shape"></div><div class="preview-violin-shape"></div><div class="preview-violin-shape"></div></div>`,
        scatter: `<div class="preview-scatter"><div class="preview-scatter-line"></div><div class="preview-scatter-dot" style="top:30%;left:20%"></div><div class="preview-scatter-dot" style="top:50%;left:40%"></div><div class="preview-scatter-dot" style="top:40%;left:60%"></div><div class="preview-scatter-dot" style="top:20%;left:80%"></div></div>`,
        line: `<svg width="50" height="40" viewBox="0 0 50 40"><polyline points="5,35 15,25 25,20 35,15 45,5" fill="none" stroke="#E69F00" stroke-width="2"/><circle cx="5" cy="35" r="2" fill="#E69F00"/><circle cx="15" cy="25" r="2" fill="#56B4E9"/><circle cx="25" cy="20" r="2" fill="#009E73"/><circle cx="35" cy="15" r="2" fill="#E69F00"/><circle cx="45" cy="5" r="2" fill="#56B4E9"/></svg>`,
        hist: `<div class="preview-bar-chart"><div class="preview-bar" style="height:40%;opacity:0.7"></div><div class="preview-bar" style="height:70%;opacity:0.7"></div><div class="preview-bar" style="height:90%;opacity:0.7"></div><div class="preview-bar" style="height:60%;opacity:0.7"></div><div class="preview-bar" style="height:30%;opacity:0.7"></div></div>`,
        volcano: `<div class="preview-volcano"><div class="preview-scatter-dot" style="top:20%;left:30%;background:#D55E00"></div><div class="preview-scatter-dot" style="top:15%;left:70%;background:#D55E00"></div><div class="preview-scatter-dot" style="top:60%;left:40%;background:#999"></div><div class="preview-scatter-dot" style="top:70%;left:60%;background:#999"></div></div>`,
        heatmap: `<div class="preview-heatmap"><div class="preview-heatmap-cell c1"></div><div class="preview-heatmap-cell c2"></div><div class="preview-heatmap-cell c3"></div><div class="preview-heatmap-cell c4"></div><div class="preview-heatmap-cell c5"></div><div class="preview-heatmap-cell c6"></div><div class="preview-heatmap-cell c7"></div><div class="preview-heatmap-cell c8"></div><div class="preview-heatmap-cell c3"></div><div class="preview-heatmap-cell c4"></div><div class="preview-heatmap-cell c5"></div><div class="preview-heatmap-cell c6"></div></div>`,
        microscope: `<div class="preview-microscope"><div class="preview-channel dapi"></div><div class="preview-channel gfp"></div><div class="preview-channel merge"></div></div>`,
        western: `<div class="preview-western"><div class="preview-band"></div><div class="preview-band"></div><div class="preview-band"></div><div class="preview-band"></div></div>`,
        'layout-1-3': `<div class="preview-layout-grid layout-1-3"><div class="preview-cell"></div><div class="preview-cell"></div><div class="preview-cell"></div><div class="preview-cell"></div></div>`,
        'layout-2x2': `<div class="preview-layout-grid layout-2x2"><div class="preview-cell"></div><div class="preview-cell"></div><div class="preview-cell"></div><div class="preview-cell"></div></div>`,
        'layout-1x6': `<div class="preview-layout-grid layout-1x6"><div class="preview-cell"></div><div class="preview-cell"></div><div class="preview-cell"></div><div class="preview-cell"></div><div class="preview-cell"></div><div class="preview-cell"></div></div>`
    };
    return previews[icon] || '<span>📊</span>';
}

function selectTemplate(category, templateId, cardElement) {
    console.log('Template selected:', templateId, 'from category:', category);
    selectedTemplateId = templateId;

    // Update UI to show selected state
    document.querySelectorAll('.template-card').forEach(card => {
        card.classList.remove('selected');
    });
    if (cardElement) {
        cardElement.classList.add('selected');
    }

    const templates = templateLibrary[category];
    if (!templates) {
        console.error('Category not found:', category);
        return;
    }

    const template = templates.find(t => t.id === templateId);
    if (!template) {
        console.error('Template not found:', templateId);
        return;
    }

    const infoPanel = document.getElementById('template-info');
    if (!infoPanel) {
        console.error('Template info panel not found');
        return;
    }

    infoPanel.classList.remove('hidden');

    const infoTitle = document.getElementById('info-title');
    const infoDescription = document.getElementById('info-description');
    const infoUseCase = document.getElementById('info-use-case');
    const infoDataFormat = document.getElementById('info-data-format');
    const infoFeatures = document.getElementById('info-features');

    if (infoTitle) infoTitle.textContent = `${template.name} (${template.nameEn})`;
    if (infoDescription) infoDescription.textContent = template.description;
    if (infoUseCase) infoUseCase.textContent = template.useCase;
    if (infoDataFormat) infoDataFormat.textContent = template.dataFormat;
    if (infoFeatures) infoFeatures.innerHTML = template.features.map(f => `<li>${f}</li>`).join('');

    // Create or update apply button
    let applyBtn = document.getElementById('btn-apply-template');
    if (!applyBtn) {
        applyBtn = document.createElement('button');
        applyBtn.id = 'btn-apply-template';
        applyBtn.className = 'btn btn-primary';
        applyBtn.style.cssText = 'width: 100%; margin-top: 12px;';
        applyBtn.textContent = '应用模板';
        infoPanel.appendChild(applyBtn);
    }

    // Remove old event listeners and add new one
    const newApplyBtn = applyBtn.cloneNode(true);
    applyBtn.parentNode.replaceChild(newApplyBtn, applyBtn);
    newApplyBtn.addEventListener('click', () => {
        console.log('Apply template button clicked for:', template.name);
        applyTemplateToPanel(template);
    });

    console.log('Template info displayed:', template.name);
}

function applyTemplateToPanel(template) {
    console.log('Applying template to panel:', template.name);

    if (!state.selectedPanel) {
        showToast('请先选择一个面板', 'error');
        return;
    }

    const label = state.selectedPanel;
    console.log('Selected panel:', label);

    // Create panel configuration based on template
    state.panels[label] = {
        type: template.plotType === 'image' ? 'image' : 'plot',
        plot_type: template.plotType,
        template_id: template.id,
        template_name: template.name,
        style: {
            okabe_ito: true,
            no_spines: true,
            font_size: 7,
            font_family: 'Arial',
            error_type: template.recommendedParams?.error_type || 'sem'
        },
        params: template.recommendedParams
    };

    console.log('Panel state updated:', state.panels[label]);

    appliedTemplates.add(template.id);
    renderTemplateGrid(currentTemplateCategory);
    renderCanvas();
    renderProperties();
    showToast(`已应用模板: ${template.name}`);

    // Switch back to panel tab
    const panelTab = document.querySelector('[data-prop-tab="panel"]');
    if (panelTab) panelTab.click();
}

function initStylesPanel() {
    const journalDisplay = document.getElementById('current-journal-display');
    const sizeDisplay = document.getElementById('current-size-display');

    if (journalDisplay) {
        journalDisplay.textContent = state.journal.charAt(0).toUpperCase() + state.journal.slice(1);
    }

    if (sizeDisplay) {
        const sizeNames = {
            single_column: '单栏 (89mm)',
            mid: '1.5栏 (120mm)',
            double_column: '双栏 (183mm)'
        };
        sizeDisplay.textContent = sizeNames[state.size] || state.size;
    }

    const styleInputs = ['style-okabe-ito', 'style-no-spines', 'style-font-size', 'style-font-family', 'style-error-type', 'style-sig-markers'];
    styleInputs.forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.addEventListener('change', updateGlobalStyle);
        }
    });
}

function updateGlobalStyle() {
    const style = {
        okabe_ito: document.getElementById('style-okabe-ito')?.checked ?? true,
        no_spines: document.getElementById('style-no-spines')?.checked ?? true,
        font_size: document.getElementById('style-font-size')?.value ?? 7,
        font_family: document.getElementById('style-font-family')?.value ?? 'Arial',
        error_type: document.getElementById('style-error-type')?.value ?? 'sem',
        sig_markers: document.getElementById('style-sig-markers')?.value ?? 'asterisk'
    };

    Object.keys(state.panels).forEach(label => {
        const panel = state.panels[label];
        if (panel.type === 'plot') {
            panel.style = { ...panel.style, ...style };
        }
    });

    showToast('样式设置已更新');
}

function showToast(message, type = 'success') {
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

window.selectTemplate = selectTemplate;
window.applyTemplateToPanel = applyTemplateToPanel;

// ============================================
// CORE FUNCTIONS
// ============================================
function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    state.theme = theme;
    localStorage.setItem('theme', theme);
}

function toggleTheme() {
    const newTheme = state.theme === 'light' ? 'dark' : 'light';
    applyTheme(newTheme);
}

async function apiGet(endpoint) {
    const response = await fetch(endpoint);
    return await response.json();
}

async function apiPost(endpoint, data) {
    const options = {
        method: 'POST',
        headers: {}
    };

    if (data instanceof FormData) {
        options.body = data;
    } else {
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(data);
    }

    const response = await fetch(endpoint, options);
    return await response.json();
}

async function loadTemplates() {
    console.log('Loading templates from API...');
    try {
        const result = await apiGet('/api/templates');
        console.log('Templates API result:', result);
        if (result.success) {
            state.templates = result.data.templates;
            console.log('Loaded templates:', state.templates.map(t => t.key));
            renderTemplates();
        } else {
            console.error('Failed to load templates:', result.error);
        }
    } catch (error) {
        console.error('Error loading templates:', error);
    }
}

async function loadPlotTypes() {
    try {
        const result = await apiGet('/api/plot-types');
        if (result.success) {
            state.plotTypes = result.data.plot_types;
            renderPlotTypes();
        }
    } catch (error) {
        console.error('Error loading plot types:', error);
    }
}

async function loadUploadedFiles() {
    try {
        const result = await apiGet('/api/uploaded-files');
        if (result.success) {
            state.uploadedImages = result.data.images;
            state.uploadedCode = result.data.code;
            renderUploadedImages();
            renderUploadedCode();
        }
    } catch (error) {
        console.error('Error loading uploaded files:', error);
    }
}

function renderTemplates(category = 'all') {
    if (!elements.templatesList) return;

    const filtered = category === 'all'
        ? state.templates
        : state.templates.filter(t => t.category === category);

    console.log('Rendering templates:', filtered.map(t => t.key));

    elements.templatesList.innerHTML = filtered.map(template => `
        <div class="template-item" draggable="true" data-template="${template.key}">
            <h4>${template.name}</h4>
            <p>${template.description}</p>
            ${template.ascii ? `<pre class="template-ascii">${escapeHtml(template.ascii)}</pre>` : ''}
            <div class="template-meta">
                <span>${template.panels} panels</span>
                <span>${template.recommended_size}</span>
            </div>
        </div>
    `).join('');

    document.querySelectorAll('.template-item').forEach(item => {
        console.log('Binding drag events to template:', item.dataset.template);
        item.addEventListener('dragstart', handleTemplateDragStart);
        item.addEventListener('dragend', handleTemplateDragEnd);
    });
}

function renderPlotTypes() {
    const categories = {
        statistics: 'Statistics',
        bioinformatics: 'Bioinformatics',
        survival: 'Survival',
        imaging: 'Imaging',
        molecular: 'Molecular',
        other: 'Other'
    };

    let html = '';
    for (const [cat, label] of Object.entries(categories)) {
        const types = state.plotTypes.filter(t => t.category === cat);
        if (types.length > 0) {
            html += `<optgroup label="${label}">`;
            html += types.map(t => `<option value="${t.name}">${t.name}</option>`).join('');
            html += '</optgroup>';
        }
    }

    if (elements.plotTypeSelect) {
        elements.plotTypeSelect.innerHTML = html;
    }
}

function renderUploadedImages() {
    if (!elements.imagesGrid) return;

    if (state.uploadedImages.length === 0) {
        elements.imagesGrid.innerHTML = '<p class="empty-state">No images uploaded yet</p>';
        return;
    }

    elements.imagesGrid.innerHTML = state.uploadedImages.map(img => `
        <div class="asset-image" draggable="true" data-filename="${img.filename}" data-url="${img.url}">
            <img src="${img.url}" alt="${img.filename}" loading="lazy">
            <span class="filename">${img.filename}</span>
        </div>
    `).join('');

    document.querySelectorAll('.asset-image').forEach(item => {
        item.addEventListener('dragstart', handleImageDragStart);
    });
}

function renderUploadedCode() {
    if (!elements.codeList) return;

    if (state.uploadedCode.length === 0) {
        elements.codeList.innerHTML = '<p class="empty-state">No code files uploaded yet</p>';
        return;
    }

    elements.codeList.innerHTML = state.uploadedCode.map(code => `
        <div class="code-item" data-filename="${code.filename}">
            <div class="code-item-info">
                <span class="code-item-name">${code.filename}</span>
                <span class="code-item-meta">${formatFileSize(code.size)}</span>
            </div>
        </div>
    `).join('');

    if (elements.codeFileSelect) {
        elements.codeFileSelect.innerHTML = state.uploadedCode.map(code =>
            `<option value="${code.url}">${code.filename}</option>`
        ).join('');
    }
}

// ============================================
// CANVAS RENDERING
// ============================================
function renderCanvas() {
    console.log('renderCanvas called, layout:', state.layout);

    if (!elements.figureCanvas) return;

    updateCanvasDimensions();

    if (!state.layout) {
        console.log('No layout, showing empty state');
        elements.figureCanvas.innerHTML = `
            <div class="empty-state">
                <p>Drag a template here to start</p>
                <p class="hint">or select from the templates panel</p>
            </div>
        `;
        elements.figureCanvas.style.width = '';
        elements.figureCanvas.style.height = '';
        elements.figureCanvas.style.aspectRatio = '';
        if (elements.canvasLayout) elements.canvasLayout.textContent = '';
        return;
    }

    const lines = state.layout.trim().split('\n').map(l => l.trim()).filter(l => l);
    const nrows = lines.length;
    const ncols = Math.max(...lines.map(l => l.length));

    console.log('Rendering grid:', nrows, 'x', ncols);

    const labels = new Set();
    lines.forEach(line => {
        for (const char of line) {
            if (char !== ' ' && char !== '.') {
                labels.add(char);
            }
        }
    });

    const panelPositions = {};
    labels.forEach(label => {
        let minRow = nrows, maxRow = -1, minCol = ncols, maxCol = -1;
        lines.forEach((line, row) => {
            for (let col = 0; col < line.length; col++) {
                if (line[col] === label) {
                    minRow = Math.min(minRow, row);
                    maxRow = Math.max(maxRow, row);
                    minCol = Math.min(minCol, col);
                    maxCol = Math.max(maxCol, col);
                }
            }
        });
        panelPositions[label] = {
            row: minRow,
            col: minCol,
            rowspan: maxRow - minRow + 1,
            colspan: maxCol - minCol + 1
        };
    });

    const width = getJournalWidth(state.journal, state.size);
    const aspectRatio = width / state.height_mm;

    const MM_TO_PX = 3.78;
    const canvasWidthPx = Math.round(width * MM_TO_PX);
    const canvasHeightPx = Math.round(state.height_mm * MM_TO_PX);

    elements.figureCanvas.style.width = `${canvasWidthPx}px`;
    elements.figureCanvas.style.height = `${canvasHeightPx}px`;
    elements.figureCanvas.style.maxWidth = 'none';
    elements.figureCanvas.style.aspectRatio = aspectRatio;

    elements.figureCanvas.innerHTML = `
        <div class="canvas-panels" style="
            grid-template-columns: repeat(${ncols}, 1fr);
            grid-template-rows: repeat(${nrows}, 1fr);
        ">
            ${Array.from(labels).sort().map(label => {
                const pos = panelPositions[label];
                const panel = state.panels[label] || { type: 'empty' };
                return renderPanel(label, pos, panel);
            }).join('')}
        </div>
    `;

    if (elements.canvasDimensions) elements.canvasDimensions.textContent = `${width} x ${state.height_mm} mm`;
    if (elements.canvasLayout) elements.canvasLayout.textContent = `Layout: ${nrows}x${ncols} grid (${labels.size} panels)`;

    document.querySelectorAll('.canvas-panel').forEach(panel => {
        panel.addEventListener('click', (e) => {
            console.log('Panel clicked:', panel.dataset.label);
            selectPanel(panel.dataset.label);
        });
        panel.addEventListener('dragover', handlePanelDragOver);
        panel.addEventListener('dragleave', handlePanelDragLeave);
        panel.addEventListener('drop', handlePanelDrop);
    });

    document.querySelectorAll('.panel-action-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            clearPanel(btn.dataset.label);
        });
    });

    applyCanvasTransform();

    if (zoomState.isFitToContainer) {
        fitCanvasToContainer();
    } else {
        checkCanvasOverflow();
    }
}

function renderPanel(label, pos, panel) {
    const content = getPanelContent(panel);
    const isEmpty = panel.type === 'empty';

    return `
        <div class="canvas-panel ${state.selectedPanel === label ? 'selected' : ''} ${isEmpty ? 'empty-panel' : ''}"
             data-label="${label}"
             style="
                grid-row: ${pos.row + 1} / span ${pos.rowspan};
                grid-column: ${pos.col + 1} / span ${pos.colspan};
             ">
            <span class="panel-label">${label}</span>
            <div class="panel-content">
                ${content}
            </div>
            <div class="panel-actions">
                <button class="panel-action-btn" data-label="${label}" title="Clear">×</button>
            </div>
        </div>
    `;
}

function getPanelContent(panel) {
    switch (panel.type) {
        case 'image':
            return `<img src="${panel.image_url}" alt="Panel image">`;
        case 'plot':
            return `<div class="plot-placeholder">📊 ${panel.plot_type}</div>`;
        case 'custom_code':
            return `<div class="plot-placeholder">🐍 Custom</div>`;
        case 'text':
            return `<div class="text-content">${escapeHtml(panel.text || '')}</div>`;
        default:
            return `<div class="plot-placeholder">+</div>`;
    }
}

function renderProperties() {
    if (!elements.propertiesPanel) return;

    if (!state.selectedPanel || !state.panels[state.selectedPanel]) {
        elements.propertiesPanel.innerHTML = `
            <div class="empty-properties">
                <p>Select a panel to edit properties</p>
            </div>
        `;
        return;
    }

    const label = state.selectedPanel;
    const panel = state.panels[label];

    elements.propertiesPanel.innerHTML = `
        <div class="property-group">
            <h4>Panel ${label.toUpperCase()}</h4>
            <div class="form-group">
                <label>Type</label>
                <select id="prop-type">
                    <option value="empty" ${panel.type === 'empty' ? 'selected' : ''}>Empty</option>
                    <option value="image" ${panel.type === 'image' ? 'selected' : ''}>Image</option>
                    <option value="plot" ${panel.type === 'plot' ? 'selected' : ''}>Built-in Plot</option>
                    <option value="custom_code" ${panel.type === 'custom_code' ? 'selected' : ''}>Custom Code</option>
                    <option value="text" ${panel.type === 'text' ? 'selected' : ''}>Text</option>
                </select>
            </div>
            <button id="btn-edit-panel" class="btn btn-primary" style="width: 100%;">
                Edit Panel Content
            </button>
        </div>

        ${panel.type === 'image' ? renderImageProperties(panel) : ''}
        ${panel.type === 'plot' ? renderPlotProperties(panel) : ''}
    `;

    document.getElementById('prop-type')?.addEventListener('change', (e) => {
        changePanelType(label, e.target.value);
    });

    document.getElementById('btn-edit-panel')?.addEventListener('click', () => {
        openPanelModal(label);
    });
}

function renderImageProperties(panel) {
    return `
        <div class="property-group">
            <h4>Image Settings</h4>
            <div class="form-group">
                <label>
                    <input type="checkbox" id="prop-trim" ${panel.trim ? 'checked' : ''}>
                    Trim whitespace
                </label>
            </div>
            <div class="form-group">
                <label>
                    <input type="checkbox" id="prop-auto-contrast" ${panel.auto_contrast ? 'checked' : ''}>
                    Auto contrast
                </label>
            </div>
            <div class="form-group">
                <label>Scale Bar</label>
                <input type="text" id="prop-scale-bar" value="${panel.scale_bar || ''}" placeholder="e.g., 50 μm">
            </div>
            <div class="form-group">
                <label>Rotation</label>
                <select id="prop-rotation">
                    <option value="0" ${panel.rotation === 0 ? 'selected' : ''}>0°</option>
                    <option value="90" ${panel.rotation === 90 ? 'selected' : ''}>90°</option>
                    <option value="180" ${panel.rotation === 180 ? 'selected' : ''}>180°</option>
                    <option value="270" ${panel.rotation === 270 ? 'selected' : ''}>270°</option>
                </select>
            </div>
        </div>
    `;
}

function renderPlotProperties(panel) {
    return `
        <div class="property-group">
            <h4>Plot Settings</h4>
            <div class="form-group">
                <label>Plot Type</label>
                <input type="text" value="${panel.plot_type || ''}" disabled>
            </div>
            ${panel.template_name ? `
            <div class="form-group">
                <label>Applied Template</label>
                <span class="style-value">${panel.template_name}</span>
            </div>
            ` : ''}
        </div>
    `;
}

// ============================================
// EVENT LISTENERS
// ============================================
function setupEventListeners() {
    console.log("Setting up event listeners...");

    if (elements.journalSelect) {
        elements.journalSelect.addEventListener('change', (e) => {
            state.journal = e.target.value;
            updateCanvasDimensions();
            renderCanvas();
        });
    }

    if (elements.sizeSelect) {
        elements.sizeSelect.addEventListener('change', (e) => {
            state.size = e.target.value;
            console.log('Size changed to:', state.size);
            updateCanvasDimensions();
            renderCanvas();
        });
    }

    if (elements.btnTheme) {
        elements.btnTheme.addEventListener("click", () => {
            console.log("Theme button clicked");
            toggleTheme();
        });
    }

    if (elements.btnPreview) {
        elements.btnPreview.addEventListener("click", () => {
            console.log("Preview button clicked");
            generatePreview();
        });
    }

    if (elements.btnExport) {
        elements.btnExport.addEventListener('click', () => {
            console.log('Export button clicked');
            openModal(elements.exportModal);
        });
    }

    if (elements.btnSaveProject) {
        elements.btnSaveProject.addEventListener('click', () => {
            console.log('Save project button clicked');
            openProjectModal('save');
        });
    }

    if (elements.btnLoadProject) {
        elements.btnLoadProject.addEventListener('click', () => {
            console.log('Load project button clicked');
            openProjectModal('load');
        });
    }

    if (elements.btnClearCanvas) {
        elements.btnClearCanvas.addEventListener('click', () => {
            console.log('Clear canvas button clicked');
            clearCanvas();
        });
    }

    document.querySelectorAll('.filter-tabs .tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-tabs .tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderTemplates(btn.dataset.category);
        });
    });

    document.querySelectorAll('[data-asset-tab]').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('[data-asset-tab]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const tab = btn.dataset.assetTab;
            if (elements.imagesGrid) elements.imagesGrid.classList.toggle('active', tab === 'images');
            if (elements.codeList) elements.codeList.classList.toggle('active', tab === 'code');
        });
    });

    if (elements.btnUploadImage) {
        elements.btnUploadImage.addEventListener('click', () => {
            console.log('Upload image button clicked');
            openModal(elements.uploadImageModal);
        });
    }

    if (elements.btnUploadCode) {
        elements.btnUploadCode.addEventListener('click', () => {
            console.log('Upload code button clicked');
            openModal(elements.uploadCodeModal);
        });
    }

    document.querySelectorAll('.modal-close, .modal-cancel').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const modal = e.target.closest('.modal');
            closeModal(modal);
        });
    });

    if (elements.btnConfirmExport) {
        elements.btnConfirmExport.addEventListener('click', () => {
            console.log('Confirm export button clicked');
            exportFigure();
        });
    }

    if (elements.panelType) {
        elements.panelType.addEventListener('change', updatePanelEditorVisibility);
    }

    if (elements.btnSavePanel) {
        elements.btnSavePanel.addEventListener('click', () => {
            console.log('Save panel button clicked');
            savePanelSettings();
        });
    }

    document.querySelectorAll('[data-panel-tab]').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('[data-panel-tab]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            document.querySelectorAll('.panel-tab').forEach(t => t.classList.remove('active'));
            document.getElementById(`panel-tab-${btn.dataset.panelTab}`).classList.add('active');
        });
    });

    if (elements.imageDropZone) {
        setupUploadModal(elements.imageDropZone, elements.imageFileInput, elements.imageUploadProgress, 'image');
    }
    if (elements.codeDropZone) {
        setupUploadModal(elements.codeDropZone, elements.codeFileInput, elements.codeUploadProgress, 'code');
    }

    document.querySelectorAll('input[type="range"]').forEach(input => {
        input.addEventListener('input', (e) => {
            const valueSpan = e.target.parentElement.querySelector('.range-value');
            if (valueSpan) {
                valueSpan.textContent = e.target.value;
            }
        });
    });

    if (elements.btnConfirmProject) {
        elements.btnConfirmProject.addEventListener('click', () => {
            console.log('Confirm project button clicked');
            handleProjectAction();
        });
    }

    if (elements.projectFileInput) {
        elements.projectFileInput.addEventListener('change', handleProjectFileSelect);
    }

    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal(modal);
            }
        });
    });
}

// ============================================
// DRAG AND DROP
// ============================================
function setupDragAndDrop() {
    if (!elements.figureCanvas) return;

    elements.figureCanvas.addEventListener('dragover', (e) => {
        e.preventDefault();
        elements.figureCanvas.classList.add('drag-over');
    });

    elements.figureCanvas.addEventListener('dragleave', () => {
        elements.figureCanvas.classList.remove('drag-over');
    });

    elements.figureCanvas.addEventListener('drop', handleCanvasDrop);
}

function handleTemplateDragStart(e) {
    const templateKey = e.target.dataset.template;
    console.log('Template drag start:', templateKey);
    e.dataTransfer.setData('type', 'template');
    e.dataTransfer.setData('template', templateKey);
    e.target.classList.add('dragging');
}

function handleTemplateDragEnd(e) {
    e.target.classList.remove('dragging');
}

function handleImageDragStart(e) {
    e.dataTransfer.setData('type', 'image');
    e.dataTransfer.setData('filename', e.target.dataset.filename);
    e.dataTransfer.setData('url', e.target.dataset.url);
}

function handleCanvasDrop(e) {
    e.preventDefault();
    elements.figureCanvas.classList.remove('drag-over');

    const type = e.dataTransfer.getData('type');
    const templateKey = e.dataTransfer.getData('template');

    console.log('Canvas drop event:', { type, templateKey });

    if (type === 'template' && templateKey) {
        console.log('Template dropped:', templateKey);
        applyTemplate(templateKey);
    }
}

function handlePanelDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('drag-over');
}

function handlePanelDragLeave(e) {
    e.currentTarget.classList.remove('drag-over');
}

function handlePanelDrop(e) {
    e.preventDefault();
    const panel = e.currentTarget;
    panel.classList.remove('drag-over');

    const type = e.dataTransfer.getData('type');
    const label = panel.dataset.label;

    if (type === 'image') {
        const url = e.dataTransfer.getData('url');
        const filename = e.dataTransfer.getData('filename');
        assignImageToPanel(label, url, filename);
    }
}

function applyTemplate(templateKey) {
    console.log('Applying template:', templateKey);

    const template = state.templates.find(t => t.key === templateKey);
    if (!template) {
        console.error('Template not found:', templateKey);
        showToast('Template not found: ' + templateKey, 'error');
        return;
    }

    console.log('Found template:', template);

    const ascii = template.ascii;
    console.log('Template ASCII:', ascii);

    const lines = ascii.split('\n')
        .map(l => l.trim())
        .filter(l => l);

    const layoutStr = lines.join('\n');
    console.log('Parsed layout:', layoutStr);

    state.layout = layoutStr;
    state.panels = {};
    state.selectedPanel = null;

    console.log('Rendering canvas with layout:', state.layout);
    renderCanvas();
    renderProperties();
    showToast('Template applied: ' + template.name);
}

function selectPanel(label) {
    console.log('selectPanel called with label:', label);
    state.selectedPanel = label;

    const panel = state.panels[label];
    console.log('Current panel state:', panel);

    if (!panel || panel.type === 'empty') {
        console.log('Panel is empty, opening modal');
        renderCanvas();
        renderProperties();
        openPanelModal(label);
    } else {
        renderCanvas();
        renderProperties();
    }
}

function clearPanel(label) {
    delete state.panels[label];
    if (state.selectedPanel === label) {
        state.selectedPanel = null;
    }
    renderCanvas();
    renderProperties();
}

function clearCanvas() {
    state.layout = '';
    state.panels = {};
    state.selectedPanel = null;
    renderCanvas();
    renderProperties();
}

function assignImageToPanel(label, url, filename) {
    state.panels[label] = {
        type: 'image',
        image_path: `/static/uploads/${filename}`,
        image_url: url,
        filename: filename
    };
    renderCanvas();
    if (state.selectedPanel === label) {
        renderProperties();
    }
}

function changePanelType(label, type) {
    state.panels[label] = { type };
    renderCanvas();
    renderProperties();
    openPanelModal(label);
}

// ============================================
// PANEL MODAL
// ============================================
function openPanelModal(label) {
    state.selectedPanel = label;
    const panel = state.panels[label] || { type: 'empty' };

    elements.panelType.value = panel.type;
    updatePanelEditorVisibility();

    if (panel.type === 'image') {
        renderMiniImageGrid(panel.image_path);
        elements.imgTrim.checked = panel.trim || false;
        elements.imgAutoContrast.checked = panel.auto_contrast || false;
        elements.imgScaleBar.value = panel.scale_bar || '';
        elements.imgColormap.value = panel.colormap || '';
        elements.imgRotation.value = panel.rotation || 0;
        elements.imgBrightness.value = panel.brightness || 1;
        elements.imgContrast.value = panel.contrast || 1;
        elements.imgFlipH.checked = panel.flip_h || false;
        elements.imgFlipV.checked = panel.flip_v || false;
    } else if (panel.type === 'plot') {
        elements.plotTypeSelect.value = panel.plot_type || 'bar_plot';
    } else if (panel.type === 'custom_code') {
        elements.codeFileSelect.value = panel.code_path || '';
        elements.codeFunctionName.value = panel.function_name || 'plot';
    } else if (panel.type === 'text') {
        elements.panelTextContent.value = panel.text || '';
    }

    openModal(elements.panelModal);
}

function updatePanelEditorVisibility() {
    const type = elements.panelType.value;

    elements.imageSelection.classList.toggle('hidden', type !== 'image');
    elements.plotSelection.classList.toggle('hidden', type !== 'plot');
    elements.codeSelection.classList.toggle('hidden', type !== 'custom_code');
    elements.textContent.classList.toggle('hidden', type !== 'text');

    if (type === 'image') {
        renderMiniImageGrid();
    }
}

function renderMiniImageGrid(selectedPath = null) {
    elements.panelImageGrid.innerHTML = state.uploadedImages.map(img => `
        <div class="mini-image-item ${selectedPath === img.url ? 'selected' : ''}"
             data-url="${img.url}" data-filename="${img.filename}">
            <img src="${img.url}" alt="${img.filename}">
        </div>
    `).join('');

    document.querySelectorAll('.mini-image-item').forEach(item => {
        item.addEventListener('click', () => {
            document.querySelectorAll('.mini-image-item').forEach(i => i.classList.remove('selected'));
            item.classList.add('selected');
        });
    });
}

function savePanelSettings() {
    const label = state.selectedPanel;
    const type = elements.panelType.value;

    const panel = { type };

    if (type === 'image') {
        const selected = document.querySelector('.mini-image-item.selected');
        if (selected) {
            panel.image_path = `/static/uploads/${selected.dataset.filename}`;
            panel.image_url = selected.dataset.url;
            panel.filename = selected.dataset.filename;
        }
        panel.trim = elements.imgTrim.checked;
        panel.auto_contrast = elements.imgAutoContrast.checked;
        panel.scale_bar = elements.imgScaleBar.value;
        panel.colormap = elements.imgColormap.value;
        panel.rotation = parseInt(elements.imgRotation.value);
        panel.brightness = parseFloat(elements.imgBrightness.value);
        panel.contrast = parseFloat(elements.imgContrast.value);
        panel.flip_h = elements.imgFlipH.checked;
        panel.flip_v = elements.imgFlipV.checked;
    } else if (type === 'plot') {
        panel.plot_type = elements.plotTypeSelect.value;
    } else if (type === 'custom_code') {
        panel.code_path = elements.codeFileSelect.value;
        panel.function_name = elements.codeFunctionName.value;
    } else if (type === 'text') {
        panel.text = elements.panelTextContent.value;
    }

    state.panels[label] = panel;
    renderCanvas();
    renderProperties();
    closeModal(elements.panelModal);
}

// ============================================
// UPLOAD
// ============================================
function setupUploadModal(dropZone, fileInput, progressEl, type) {
    if (!dropZone) return;

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            uploadFiles(files, type, progressEl);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            uploadFiles(fileInput.files, type, progressEl);
        }
    });
}

async function uploadFiles(files, type, progressEl) {
    if (!progressEl) return;

    progressEl.classList.remove('hidden');
    const progressFill = progressEl.querySelector('.progress-fill');
    const progressText = progressEl.querySelector('.progress-text');

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const formData = new FormData();
        formData.append('file', file);

        if (progressText) progressText.textContent = `Uploading ${file.name}...`;
        if (progressFill) progressFill.style.width = `${((i + 0.5) / files.length) * 100}%`;

        const endpoint = type === 'image' ? '/api/upload' : '/api/upload-code';
        const result = await apiPost(endpoint, formData);

        if (!result.success) {
            alert(`Failed to upload ${file.name}: ${result.error}`);
        }
    }

    if (progressFill) progressFill.style.width = '100%';
    if (progressText) progressText.textContent = 'Upload complete!';

    setTimeout(() => {
        progressEl.classList.add('hidden');
        closeModal(type === 'image' ? elements.uploadImageModal : elements.uploadCodeModal);
        loadUploadedFiles();
    }, 500);
}

// ============================================
// ZOOM CONTROLS
// ============================================
function setupZoomControls() {
    const btnZoomIn = document.getElementById('btn-zoom-in');
    const btnZoomOut = document.getElementById('btn-zoom-out');
    const btnFit = document.getElementById('btn-fit');

    if (btnZoomIn) {
        btnZoomIn.addEventListener('click', () => {
            console.log('Zoom in button clicked');
            zoomIn();
        });
    }

    if (btnZoomOut) {
        btnZoomOut.addEventListener('click', () => {
            console.log('Zoom out button clicked');
            zoomOut();
        });
    }

    if (btnFit) {
        btnFit.addEventListener('click', () => {
            console.log('Fit button clicked');
            fitCanvasToContainer();
        });
    }

    if (elements.canvasContainer) {
        elements.canvasContainer.addEventListener('wheel', handleWheelZoom, { passive: false });
    }
}

function handleWheelZoom(e) {
    if (!e.ctrlKey && !e.metaKey) {
        return;
    }

    e.preventDefault();

    const delta = e.deltaY > 0 ? -zoomState.step : zoomState.step;
    const newScale = Math.max(zoomState.minScale, Math.min(zoomState.maxScale, zoomState.scale + delta));

    setCanvasScale(newScale);
}

function zoomIn() {
    const newScale = Math.min(zoomState.maxScale, zoomState.scale + zoomState.step);
    setCanvasScale(newScale);
}

function zoomOut() {
    const newScale = Math.max(zoomState.minScale, zoomState.scale - zoomState.step);
    setCanvasScale(newScale);
}

function setCanvasScale(scale) {
    zoomState.scale = Math.max(zoomState.minScale, Math.min(zoomState.maxScale, scale));
    zoomState.isFitToContainer = false;

    applyCanvasTransform();
    updateZoomDisplay();
}

function applyCanvasTransform() {
    if (!elements.figureCanvas) return;

    elements.figureCanvas.style.transform = `scale(${zoomState.scale})`;
    updateCanvasContainerSize();
}

function updateCanvasContainerSize() {
    if (!elements.figureCanvas || !state.layout) return;

    const canvasRect = elements.figureCanvas.getBoundingClientRect();
    const containerWidth = canvasRect.width * zoomState.scale;
    const containerHeight = canvasRect.height * zoomState.scale;

    elements.figureCanvas.style.minWidth = `${600 * zoomState.scale}px`;
    elements.figureCanvas.style.minHeight = `${400 * zoomState.scale}px`;
}

function updateZoomDisplay() {
    const zoomLevel = document.getElementById('zoom-level');
    if (zoomLevel) {
        const percentage = Math.round(zoomState.scale * 100);
        zoomLevel.textContent = `${percentage}%`;
    }
}

function fitCanvasToContainer() {
    if (!elements.figureCanvas || !elements.canvasContainer) return;

    const containerWidth = elements.canvasContainer.clientWidth - 40;
    const containerHeight = elements.canvasContainer.clientHeight - 40;

    const canvasWidth = elements.figureCanvas.clientWidth;
    const canvasHeight = elements.figureCanvas.clientHeight;

    const scaleX = containerWidth / canvasWidth;
    const scaleY = containerHeight / canvasHeight;
    const scale = Math.min(scaleX, scaleY, 1.0) * 0.95;

    zoomState.scale = Math.max(zoomState.minScale, Math.min(zoomState.maxScale, scale));
    zoomState.isFitToContainer = true;

    applyCanvasTransform();
    updateZoomDisplay();
}

function resetZoom() {
    zoomState.scale = 1.0;
    zoomState.isFitToContainer = false;
    applyCanvasTransform();
    updateZoomDisplay();
}

function setupWindowResize() {
    let resizeTimeout;

    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            handleWindowResize();
        }, 250);
    });
}

function handleWindowResize() {
    if (zoomState.isFitToContainer) {
        fitCanvasToContainer();
    } else {
        checkCanvasOverflow();
    }
}

function checkCanvasOverflow() {
    if (!elements.figureCanvas || !elements.canvasContainer || !state.layout) return;

    const containerWidth = elements.canvasContainer.clientWidth - 40;
    const canvasWidth = elements.figureCanvas.clientWidth * zoomState.scale;

    if (canvasWidth > containerWidth) {
        const newScale = (containerWidth / elements.figureCanvas.clientWidth) * 0.95;
        zoomState.scale = Math.max(zoomState.minScale, newScale);
        applyCanvasTransform();
        updateZoomDisplay();
    }
}

// ============================================
// PROJECT OPERATIONS
// ============================================
async function generatePreview() {
    if (!state.layout) {
        alert('Please select a layout template first');
        return;
    }

    openModal(elements.previewModal);
    elements.previewContainer.innerHTML = '<div class="loading">Generating preview...</div>';

    const config = buildProjectConfig();
    const result = await apiPost('/api/preview', config);

    if (result.success) {
        elements.previewContainer.innerHTML = `<img src="${result.data.preview}" alt="Preview">`;
        elements.previewInfo.textContent = `${result.data.width_mm} x ${result.data.height_mm} mm`;
    } else {
        elements.previewContainer.innerHTML = `<div class="loading">Error: ${result.error}</div>`;
    }
}

async function exportFigure() {
    const config = buildProjectConfig();
    config.format = elements.exportFormat.value;
    config.dpi = parseInt(elements.exportDpi.value);
    config.filename = elements.exportFilename.value || 'figure';

    const result = await apiPost('/api/export', config);

    if (result.success) {
        const link = document.createElement('a');
        link.href = result.data.url;
        link.download = result.data.filename;
        link.click();
        closeModal(elements.exportModal);
    } else {
        alert(`Export failed: ${result.error}`);
    }
}

function openProjectModal(mode) {
    elements.projectModalTitle.textContent = mode === 'save' ? 'Save Project' : 'Load Project';
    elements.saveProjectSection.classList.toggle('hidden', mode !== 'save');
    elements.loadProjectSection.classList.toggle('hidden', mode !== 'load');
    elements.btnConfirmProject.textContent = mode === 'save' ? 'Save' : 'Load';

    if (mode === 'load') {
        loadProjectsList();
    }

    openModal(elements.projectModal);
}

async function loadProjectsList() {
    const result = await apiGet('/api/list-projects');

    if (result.success && result.data.projects.length > 0) {
        elements.projectsList.innerHTML = result.data.projects.map(p => `
            <div class="project-item" data-filename="${p.filename}">
                <div class="project-name">${p.filename}</div>
                <div class="project-meta">${formatDate(p.modified)} - ${formatFileSize(p.size)}</div>
            </div>
        `).join('');

        document.querySelectorAll('.project-item').forEach(item => {
            item.addEventListener('click', () => {
                document.querySelectorAll('.project-item').forEach(i => i.classList.remove('selected'));
                item.classList.add('selected');
            });
        });
    } else {
        elements.projectsList.innerHTML = '<p class="hint">No saved projects found</p>';
    }
}

async function handleProjectAction() {
    const mode = elements.saveProjectSection.classList.contains('hidden') ? 'load' : 'save';

    if (mode === 'save') {
        const config = buildProjectConfig();
        config.project_name = elements.projectName.value || 'untitled';

        const result = await apiPost('/api/save-project', config);

        if (result.success) {
            closeModal(elements.projectModal);
            alert('Project saved successfully!');
        } else {
            alert(`Save failed: ${result.error}`);
        }
    } else {
        const selected = document.querySelector('.project-item.selected');

        if (selected) {
            const result = await apiGet(`/static/uploads/projects/${selected.dataset.filename}`);
            if (result) {
                loadProjectConfig(result);
                closeModal(elements.projectModal);
            }
        } else if (elements.projectFileInput.files.length > 0) {
            const file = elements.projectFileInput.files[0];
            const reader = new FileReader();
            reader.onload = (e) => {
                const config = JSON.parse(e.target.result);
                loadProjectConfig(config);
                closeModal(elements.projectModal);
            };
            reader.readAsText(file);
        }
    }
}

function handleProjectFileSelect() {
    document.querySelectorAll('.project-item').forEach(i => i.classList.remove('selected'));
}

function buildProjectConfig() {
    return {
        journal: state.journal,
        size: state.size,
        layout: state.layout,
        height_mm: state.height_mm,
        panels: state.panels
    };
}

function loadProjectConfig(config) {
    state.journal = config.journal || 'nature';
    state.size = config.size || 'double_column';
    state.layout = config.layout || '';
    state.height_mm = config.height_mm || 150;
    state.panels = config.panels || {};
    state.selectedPanel = null;

    elements.journalSelect.value = state.journal;
    elements.sizeSelect.value = state.size;

    renderCanvas();
    renderProperties();
}

// ============================================
// MISSING EVENTS BINDING
// ============================================
function bindMissingEvents() {
    console.log('Binding missing events...');

    // Language button
    const btnLanguage = document.getElementById('btn-language');
    if (btnLanguage) {
        btnLanguage.addEventListener('click', (e) => {
            console.log('Language button clicked');
            e.stopPropagation();
            const dropdown = document.getElementById('language-dropdown');
            if (dropdown) {
                dropdown.classList.toggle('active');
            }
        });
    }

    // Language options
    document.querySelectorAll('.language-option').forEach(option => {
        option.addEventListener('click', (e) => {
            const lang = e.target.dataset.lang;
            console.log('Language selected:', lang);
            if (lang && typeof i18n !== 'undefined') {
                i18n.setLanguage(lang);
                document.querySelectorAll('.language-option').forEach(opt => opt.classList.remove('active'));
                e.target.classList.add('active');
            }
            const dropdown = document.getElementById('language-dropdown');
            if (dropdown) {
                dropdown.classList.remove('active');
            }
        });
    });

    // Close language dropdown when clicking outside
    document.addEventListener('click', (e) => {
        const languageSwitcher = document.querySelector('.language-switcher');
        const dropdown = document.getElementById('language-dropdown');
        if (dropdown && languageSwitcher && !languageSwitcher.contains(e.target)) {
            dropdown.classList.remove('active');
        }
    });

    // Auto Layout button
    const btnAutoLayout = document.getElementById('btn-auto-layout');
    if (btnAutoLayout) {
        btnAutoLayout.addEventListener('click', () => {
            console.log('Auto layout button clicked');
            autoLayout();
        });
    }

    // Generate Sample button
    const btnGenerateSample = document.getElementById('btn-generate-sample');
    if (btnGenerateSample) {
        btnGenerateSample.addEventListener('click', () => {
            console.log('Generate sample button clicked');
            openSampleDataModal();
        });
    }

    // Export from Preview button
    const btnExportFromPreview = document.getElementById('btn-export-from-preview');
    if (btnExportFromPreview) {
        btnExportFromPreview.addEventListener('click', () => {
            console.log('Export from preview button clicked');
            closeModal(elements.previewModal);
            openModal(elements.exportModal);
        });
    }

    // Confirm Generate Sample button
    const btnConfirmGenerateSample = document.getElementById('btn-confirm-generate-sample');
    if (btnConfirmGenerateSample) {
        btnConfirmGenerateSample.addEventListener('click', () => {
            console.log('Confirm generate sample button clicked');
            generateSampleData();
        });
    }

    console.log('Missing events bound successfully');
}

// ============================================
// SAMPLE DATA FUNCTIONS
// ============================================
const sampleDataTypes = [
    {
        id: 'bar_chart',
        name: 'Bar Chart Data',
        description: 'Sample data for grouped bar chart with error bars',
        type: 'csv',
        content: 'group,value,error\nControl,10,1.5\nTreatment A,15,2.0\nTreatment B,12,1.8'
    },
    {
        id: 'scatter_plot',
        name: 'Scatter Plot Data',
        description: 'Sample data for scatter plot with regression',
        type: 'csv',
        content: 'x,y\n1.2,3.4\n2.1,4.5\n3.5,5.6\n4.2,6.1\n5.1,7.2'
    },
    {
        id: 'time_series',
        name: 'Time Series Data',
        description: 'Sample data for time series plot',
        type: 'csv',
        content: 'time,group,value\n0h,Control,100\n0h,Treatment,100\n24h,Control,110\n24h,Treatment,95\n48h,Control,115\n48h,Treatment,88'
    },
    {
        id: 'volcano_plot',
        name: 'Volcano Plot Data',
        description: 'Sample data for RNA-seq volcano plot',
        type: 'csv',
        content: 'gene,log2fc,pvalue\nGene1,2.5,0.001\nGene2,-1.8,0.01\nGene3,3.2,0.0001\nGene4,-0.5,0.3\nGene5,1.2,0.05'
    }
];

let selectedSampleType = null;

function openSampleDataModal() {
    console.log('Opening sample data modal');
    selectedSampleType = null;

    const grid = document.getElementById('sample-data-grid');
    if (grid) {
        grid.innerHTML = sampleDataTypes.map(type => `
            <div class="sample-data-card" data-type="${type.id}">
                <h4>${type.name}</h4>
                <p>${type.description}</p>
            </div>
        `).join('');

        document.querySelectorAll('.sample-data-card').forEach(card => {
            card.addEventListener('click', () => {
                document.querySelectorAll('.sample-data-card').forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                selectedSampleType = card.dataset.type;
                showSamplePreview(selectedSampleType);
            });
        });
    }

    openModal(document.getElementById('sample-data-modal'));
}

function showSamplePreview(typeId) {
    const preview = document.getElementById('sample-data-preview');
    const description = document.getElementById('sample-data-description');
    const sampleType = sampleDataTypes.find(t => t.id === typeId);

    if (preview && sampleType) {
        preview.innerHTML = `<pre class="sample-data-content">${escapeHtml(sampleType.content)}</pre>`;
    }
    if (description && sampleType) {
        description.textContent = sampleType.description;
    }
}

function generateSampleData() {
    if (!selectedSampleType) {
        showToast('请先选择一种样本数据类型', 'error');
        return;
    }

    const sampleType = sampleDataTypes.find(t => t.id === selectedSampleType);
    if (!sampleType) return;

    const blob = new Blob([sampleType.content], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${sampleType.id}.csv`;
    link.click();
    URL.revokeObjectURL(url);

    closeModal(document.getElementById('sample-data-modal'));
    showToast(`已生成样本数据: ${sampleType.name}`);
}

function autoLayout() {
    console.log('Auto layout called');
    const panelCount = Object.keys(state.panels).length;
    if (panelCount === 0) {
        showToast('没有面板需要布局', 'error');
        return;
    }

    const cols = Math.ceil(Math.sqrt(panelCount));
    const rows = Math.ceil(panelCount / cols);

    showToast(`自动布局: ${rows}x${cols} 网格`);
}

// ============================================
// UTILITY FUNCTIONS
// ============================================
function openModal(modal) {
    if (!modal) return;
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal(modal) {
    if (!modal) return;
    modal.classList.remove('active');
    document.body.style.overflow = '';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function formatDate(isoString) {
    const date = new Date(isoString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function getJournalWidth(journal, size) {
    const widths = {
        nature: { single_column: 89, mid: 120, double_column: 183 },
        science: { single_column: 55, mid: 120, double_column: 175 },
        cell: { single_column: 85, mid: 114, double_column: 178 },
        pnas: { single_column: 87, mid: 114, double_column: 178 },
        lancet: { single_column: 80, double_column: 170 },
        nejm: { single_column: 84, double_column: 175 },
        jama: { single_column: 86, double_column: 178 },
        elife: { single_column: 85, mid: 120, double_column: 178 }
    };

    const journalWidths = widths[journal] || widths.nature;
    return journalWidths[size] || journalWidths.double_column || 183;
}

function updateCanvasDimensions() {
    const width = getJournalWidth(state.journal, state.size);
    state.width_mm = width;

    if (elements.canvasDimensions) {
        elements.canvasDimensions.textContent = `${width} x ${state.height_mm} mm`;
    }

    const sizeDisplay = document.getElementById('current-size-display');
    if (sizeDisplay) {
        const sizeNames = {
            single_column: '单栏 (89mm)',
            mid: '1.5栏 (120mm)',
            double_column: '双栏 (183mm)'
        };
        sizeDisplay.textContent = sizeNames[state.size] || state.size;
    }

    const journalDisplay = document.getElementById('current-journal-display');
    if (journalDisplay) {
        journalDisplay.textContent = state.journal.charAt(0).toUpperCase() + state.journal.slice(1);
    }

    console.log('Canvas dimensions updated:', {
        journal: state.journal,
        size: state.size,
        width_mm: width,
        height_mm: state.height_mm
    });
}

// ============================================
// INITIALIZE ON DOM READY
// ============================================
document.addEventListener('DOMContentLoaded', init);

