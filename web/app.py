#!/usr/bin/env python3
"""
FigCombo Web Server - 内网访问服务
"""

import os
import sys
import json
import base64
import io
import uuid
import tempfile
from datetime import datetime
from pathlib import Path

# 添加父目录到路径以导入 figcombo
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# 导入 FigCombo
from figcombo import Figure, ImagePanel, PlotPanel, TextPanel, list_templates, list_plot_types

app = Flask(__name__)
CORS(app)

# 配置
UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
OUTPUT_FOLDER = Path(__file__).parent / 'outputs'
UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB 上传限制

# 存储会话数据
sessions = {}


@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')


@app.route('/static/<path:path>')
def send_static(path):
    """静态文件服务"""
    return send_from_directory('static', path)


@app.route('/api/templates', methods=['GET'])
def get_templates():
    """获取所有可用模板"""
    try:
        templates = list_templates()
        return jsonify({'success': True, 'templates': templates})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/plot-types', methods=['GET'])
def get_plot_types():
    """获取所有可用绘图类型"""
    try:
        plot_types = list_plot_types()
        return jsonify({'success': True, 'plot_types': plot_types})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/journals', methods=['GET'])
def get_journals():
    """获取支持的期刊列表"""
    try:
        from figcombo.knowledge.journal_specs import JOURNAL_SPECS
        journals = [
            {
                'id': key,
                'name': spec.get('name', key),
                'widths': spec.get('widths', {}),
                'dpi': spec.get('dpi', 300),
                'format': spec.get('format', 'pdf')
            }
            for key, spec in JOURNAL_SPECS.items()
        ]
        return jsonify({'success': True, 'journals': journals})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传图片文件"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有文件'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '文件名为空'}), 400

        # 生成唯一文件名
        ext = Path(file.filename).suffix.lower()
        allowed_ext = {'.png', '.jpg', '.jpeg', '.tif', '.tiff', '.gif', '.bmp'}
        if ext not in allowed_ext:
            return jsonify({'success': False, 'error': f'不支持的文件格式: {ext}'}), 400

        file_id = str(uuid.uuid4())[:8]
        filename = f"{file_id}{ext}"
        filepath = UPLOAD_FOLDER / filename
        file.save(filepath)

        # 获取图片信息
        with Image.open(filepath) as img:
            width, height = img.size
            mode = img.mode

        return jsonify({
            'success': True,
            'file_id': file_id,
            'filename': filename,
            'original_name': file.filename,
            'width': width,
            'height': height,
            'mode': mode,
            'url': f'/api/uploads/{filename}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/uploads/<filename>')
def serve_upload(filename):
    """提供上传的文件"""
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/api/generate', methods=['POST'])
def generate_figure():
    """生成图表"""
    try:
        data = request.get_json()

        # 获取参数
        layout = data.get('layout', 'ab/cd')
        journal = data.get('journal', 'nature')
        size = data.get('size', 'single')
        panels = data.get('panels', {})

        # 创建 FigCombo 图表
        fig = Figure(
            journal=journal,
            size=size,
            layout=layout,
            label_style=data.get('label_style', 'lowercase'),
            font_size=data.get('font_size')
        )

        # 添加面板
        for panel_id, panel_config in panels.items():
            panel_type = panel_config.get('type', 'image')

            if panel_type == 'image':
                # 图片面板
                filename = panel_config.get('filename')
                if filename:
                    filepath = UPLOAD_FOLDER / filename
                    if filepath.exists():
                        fig[panel_id] = ImagePanel(
                            str(filepath),
                            label=panel_config.get('label'),
                            crop=panel_config.get('crop'),
                            scale=panel_config.get('scale', 1.0)
                        )

            elif panel_type == 'plot':
                # 绘图面板 - 生成示例图
                plot_func = create_sample_plot(panel_config.get('plot_type', 'line'))
                fig[panel_id] = PlotPanel(
                    plot_func,
                    label=panel_config.get('label'),
                    title=panel_config.get('title', '')
                )

            elif panel_type == 'text':
                # 文本面板
                fig[panel_id] = TextPanel(
                    text=panel_config.get('text', ''),
                    label=panel_config.get('label')
                )

        # 渲染并保存
        output_id = str(uuid.uuid4())[:8]
        output_path = OUTPUT_FOLDER / f"{output_id}.png"

        # 使用 matplotlib 渲染
        fig_combo = fig.render()

        # 保存为高分辨率 PNG
        plt.savefig(output_path, dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close()

        # 转换为 base64 用于预览
        with open(output_path, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode('utf-8')

        return jsonify({
            'success': True,
            'output_id': output_id,
            'preview_url': f'/api/outputs/{output_id}.png',
            'base64_image': f'data:image/png;base64,{img_data}',
            'download_url': f'/api/download/{output_id}.png'
        })

    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/outputs/<filename>')
def serve_output(filename):
    """提供生成的输出文件"""
    return send_from_directory(OUTPUT_FOLDER, filename)


@app.route('/api/download/<filename>')
def download_output(filename):
    """下载输出文件"""
    filepath = OUTPUT_FOLDER / filename
    if filepath.exists():
        return send_file(filepath, as_attachment=True, download_name=f"figcombo_{filename}")
    return jsonify({'success': False, 'error': '文件不存在'}), 404


@app.route('/api/export/<format>', methods=['POST'])
def export_figure(format):
    """导出图表为特定格式"""
    try:
        data = request.get_json()
        output_id = data.get('output_id')

        if not output_id:
            return jsonify({'success': False, 'error': '缺少 output_id'}), 400

        # 这里可以实现 PDF/SVG/TIFF 导出
        # 暂时返回 PNG
        output_path = OUTPUT_FOLDER / f"{output_id}.png"

        if format == 'pdf':
            pdf_path = OUTPUT_FOLDER / f"{output_id}.pdf"
            # 转换逻辑...
            return jsonify({
                'success': True,
                'download_url': f'/api/download/{output_id}.pdf'
            })

        return jsonify({
            'success': True,
            'download_url': f'/api/download/{output_id}.png'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def create_sample_plot(plot_type='line'):
    """创建示例绘图函数"""
    def plot_func(ax):
        np.random.seed(42)

        if plot_type == 'line':
            x = np.linspace(0, 10, 100)
            y = np.sin(x) + np.random.normal(0, 0.1, 100)
            ax.plot(x, y, 'b-', linewidth=2)
            ax.set_xlabel('X axis')
            ax.set_ylabel('Y axis')
            ax.set_title('Sample Line Plot')

        elif plot_type == 'scatter':
            x = np.random.randn(50)
            y = np.random.randn(50)
            ax.scatter(x, y, alpha=0.6, s=50)
            ax.set_xlabel('X axis')
            ax.set_ylabel('Y axis')
            ax.set_title('Sample Scatter Plot')

        elif plot_type == 'bar':
            categories = ['A', 'B', 'C', 'D', 'E']
            values = np.random.randint(10, 100, 5)
            ax.bar(categories, values, color='steelblue')
            ax.set_ylabel('Values')
            ax.set_title('Sample Bar Plot')

        elif plot_type == 'histogram':
            data = np.random.randn(1000)
            ax.hist(data, bins=30, color='steelblue', edgecolor='white')
            ax.set_xlabel('Value')
            ax.set_ylabel('Frequency')
            ax.set_title('Sample Histogram')

        elif plot_type == 'box':
            data = [np.random.randn(100) for _ in range(4)]
            ax.boxplot(data, labels=['A', 'B', 'C', 'D'])
            ax.set_ylabel('Values')
            ax.set_title('Sample Box Plot')

        else:
            # 默认线图
            x = np.linspace(0, 10, 100)
            y = np.sin(x)
            ax.plot(x, y, 'b-', linewidth=2)
            ax.set_title(f'Sample {plot_type.title()} Plot')

    return plot_func


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'figcombo_available': True
    })


def get_local_ip():
    """获取本地 IP 地址"""
    import socket
    try:
        # 方法1: 获取主机名对应的 IP
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)

        # 方法2: 如果获取到的是 127.0.0.1，尝试其他方法
        if local_ip == '127.0.0.1':
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(('8.8.8.8', 80))
                local_ip = s.getsockname()[0]
            finally:
                s.close()

        return local_ip
    except Exception:
        return '127.0.0.1'


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='FigCombo Web Server')
    parser.add_argument('--host', default='0.0.0.0', help='监听地址 (默认: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='监听端口 (默认: 5000)')
    parser.add_argument('--debug', action='store_true', help='调试模式')

    args = parser.parse_args()

    local_ip = get_local_ip()

    print("=" * 60)
    print("🎨 FigCombo Web Server")
    print("=" * 60)
    print(f"本地访问: http://127.0.0.1:{args.port}")
    print(f"内网访问: http://{local_ip}:{args.port}")
    print("=" * 60)
    print("按 Ctrl+C 停止服务")
    print()

    app.run(host=args.host, port=args.port, debug=args.debug)
