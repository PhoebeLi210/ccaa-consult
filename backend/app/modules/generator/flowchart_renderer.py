"""
流程图渲染模块
负责将流程图数据渲染为图像，并集成到作业指导书生成中
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Polygon, Circle, FancyArrowPatch
import numpy as np
from PIL import Image
import io
import base64
from typing import Dict, List, Any, Optional, Tuple
from docx import Document
from docx.shared import Inches, Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os


class FlowchartRenderer:
    """流程图渲染器类"""

    def __init__(self):
        """初始化渲染器"""
        self.node_colors = {
            'start': '#90EE90',      # 浅绿色 - 开始
            'end': '#FFB6C1',        # 浅粉色 - 结束
            'process': '#87CEEB',    # 浅蓝色 - 处理
            'decision': '#FFD700',   # 金黄色 - 判断
            'input': '#DDA0DD',      # 梅红色 - 输入/输出
            'subprocess': '#F0E68C', # 卡其色 - 子流程
        }
        self.node_shapes = {
            'start': 'ellipse',
            'end': 'ellipse',
            'process': 'rectangle',
            'decision': 'diamond',
            'input': 'parallelogram',
            'subprocess': 'rectangle',
        }

    def render_to_image(
        self,
        flowchart_data: Dict[str, Any],
        format: str = 'png',
        width: int = 12,
        height: int = 8,
        dpi: int = 150
    ) -> bytes:
        """
        将流程图渲染为图像

        Args:
            flowchart_data: 流程图数据，包含nodes和edges
            format: 输出格式，支持 'png', 'jpg', 'jpeg', 'bmp', 'tiff'
            width: 图像宽度（英寸）
            height: 图像高度（英寸）
            dpi: 图像分辨率

        Returns:
            图像字节数据
        """
        fig, ax = self._create_flowchart_figure(flowchart_data, width, height)

        # 保存到内存
        buf = io.BytesIO()
        fig.savefig(buf, format=format, dpi=dpi, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buf.seek(0)
        image_data = buf.read()
        buf.close()
        plt.close(fig)

        return image_data

    def render_to_base64(
        self,
        flowchart_data: Dict[str, Any],
        format: str = 'png'
    ) -> str:
        """
        将流程图渲染为Base64编码的图像

        Args:
            flowchart_data: 流程图数据
            format: 输出格式

        Returns:
            Base64编码的图像字符串
        """
        image_data = self.render_to_image(flowchart_data, format)
        return base64.b64encode(image_data).decode('utf-8')

    def render_to_svg(self, flowchart_data: Dict[str, Any]) -> str:
        """
        将流程图渲染为SVG格式

        Args:
            flowchart_data: 流程图数据

        Returns:
            SVG字符串
        """
        fig, ax = self._create_flowchart_figure(flowchart_data, 12, 8)

        # 保存到内存
        buf = io.BytesIO()
        fig.savefig(buf, format='svg', bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buf.seek(0)
        svg_data = buf.read().decode('utf-8')
        buf.close()
        plt.close(fig)

        return svg_data

    def _create_flowchart_figure(
        self,
        flowchart_data: Dict[str, Any],
        width: int,
        height: int
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        创建流程图图形

        Args:
            flowchart_data: 流程图数据
            width: 宽度
            height: 高度

        Returns:
            (fig, ax) 元组
        """
        fig, ax = plt.subplots(figsize=(width, height))
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.set_aspect('equal')
        ax.axis('off')

        nodes = flowchart_data.get('nodes', [])
        edges = flowchart_data.get('edges', [])

        # 计算节点位置（如果没有提供）
        node_positions = self._calculate_node_positions(nodes)

        # 绘制边（连接线）
        for edge in edges:
            self._draw_edge(ax, edge, node_positions)

        # 绘制节点
        for node in nodes:
            self._draw_node(ax, node, node_positions.get(node.get('id')))

        return fig, ax

    def _calculate_node_positions(
        self,
        nodes: List[Dict[str, Any]]
    ) -> Dict[str, Tuple[float, float]]:
        """
        计算节点位置

        Args:
            nodes: 节点列表

        Returns:
            节点ID到位置的映射
        """
        positions = {}

        for i, node in enumerate(nodes):
            node_id = node.get('id')
            # 如果有预设位置，使用预设位置
            if 'x' in node and 'y' in node:
                positions[node_id] = (node['x'], node['y'])
            else:
                # 使用简单的网格布局
                col = i % 4
                row = i // 4
                x = 15 + col * 25
                y = 85 - row * 20
                positions[node_id] = (x, y)

        return positions

    def _draw_node(
        self,
        ax: plt.Axes,
        node: Dict[str, Any],
        position: Optional[Tuple[float, float]]
    ):
        """
        绘制单个节点

        Args:
            ax: 坐标轴
            node: 节点数据
            position: 节点位置
        """
        if position is None:
            return

        node_id = node.get('id', '')
        node_type = node.get('type', 'process')
        label = node.get('label', node_id)
        x, y = position

        # 获取节点样式
        color = node.get('color', self.node_colors.get(node_type, '#87CEEB'))
        shape = node.get('shape', self.node_shapes.get(node_type, 'rectangle'))

        # 根据形状绘制
        if shape == 'rectangle' or shape == 'subprocess':
            rect = FancyBboxPatch(
                (x - 8, y - 4), 16, 8,
                boxstyle="round,pad=0.02,rounding_size=0.5",
                facecolor=color,
                edgecolor='#333333',
                linewidth=1.5
            )
            ax.add_patch(rect)

        elif shape == 'ellipse' or shape == 'circle':
            ellipse = mpatches.Ellipse(
                (x, y), 14, 8,
                facecolor=color,
                edgecolor='#333333',
                linewidth=1.5
            )
            ax.add_patch(ellipse)

        elif shape == 'diamond':
            diamond = Polygon(
                [(x, y + 6), (x + 10, y), (x, y - 6), (x - 10, y)],
                facecolor=color,
                edgecolor='#333333',
                linewidth=1.5
            )
            ax.add_patch(diamond)

        elif shape == 'parallelogram':
            parallelogram = Polygon(
                [(x - 10, y - 4), (x + 6, y - 4),
                 (x + 10, y + 4), (x - 6, y + 4)],
                facecolor=color,
                edgecolor='#333333',
                linewidth=1.5
            )
            ax.add_patch(parallelogram)

        # 添加文本标签
        ax.text(x, y, label, ha='center', va='center',
               fontsize=9, fontweight='bold', color='#333333',
               wrap=True)

    def _draw_edge(
        self,
        ax: plt.Axes,
        edge: Dict[str, Any],
        node_positions: Dict[str, Tuple[float, float]]
    ):
        """
        绘制边（连接线）

        Args:
            ax: 坐标轴
            edge: 边数据
            node_positions: 节点位置映射
        """
        source = edge.get('source')
        target = edge.get('target')
        label = edge.get('label', '')

        if source not in node_positions or target not in node_positions:
            return

        x1, y1 = node_positions[source]
        x2, y2 = node_positions[target]

        # 计算连接点（从节点边缘开始）
        dx = x2 - x1
        dy = y2 - y1
        dist = np.sqrt(dx**2 + dy**2)

        if dist > 0:
            # 调整起点和终点到节点边缘
            offset = 9
            x1_adj = x1 + (dx / dist) * offset
            y1_adj = y1 + (dy / dist) * offset
            x2_adj = x2 - (dx / dist) * offset
            y2_adj = y2 - (dy / dist) * offset

            # 绘制箭头
            arrow = FancyArrowPatch(
                (x1_adj, y1_adj), (x2_adj, y2_adj),
                arrowstyle='->',
                mutation_scale=15,
                linewidth=1.5,
                color='#555555'
            )
            ax.add_patch(arrow)

            # 添加边标签
            if label:
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                ax.text(mid_x, mid_y + 2, label, ha='center', va='bottom',
                       fontsize=8, color='#666666',
                       bbox=dict(boxstyle='round,pad=0.3',
                                facecolor='white', edgecolor='none', alpha=0.8))

    def generate_instruction_from_flowchart(
        self,
        flowchart_data: Dict[str, Any],
        node_configs: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        根据流程图生成作业指导书文本

        Args:
            flowchart_data: 流程图数据
            node_configs: 节点配置，包含每个节点的详细说明

        Returns:
            作业指导书内容字典
        """
        if node_configs is None:
            node_configs = {}

        nodes = flowchart_data.get('nodes', [])
        edges = flowchart_data.get('edges', [])

        # 构建节点映射
        node_map = {node['id']: node for node in nodes}

        # 构建邻接表
        adjacency = {}
        for edge in edges:
            source = edge.get('source')
            target = edge.get('target')
            if source not in adjacency:
                adjacency[source] = []
            adjacency[source].append({
                'target': target,
                'label': edge.get('label', '')
            })

        # 找到开始节点
        start_nodes = [n for n in nodes if n.get('type') == 'start']
        if not start_nodes:
            start_nodes = nodes[:1] if nodes else []

        # 生成步骤
        steps = []
        step_number = 1
        visited = set()

        def traverse_node(node_id: str, condition: str = ''):
            nonlocal step_number

            if node_id in visited or node_id not in node_map:
                return

            visited.add(node_id)
            node = node_map[node_id]
            node_type = node.get('type', 'process')
            node_label = node.get('label', node_id)

            # 获取节点配置
            config = node_configs.get(node_id, {})
            description = config.get('description', '')
            precautions = config.get('precautions', [])
            tools = config.get('tools', [])
            standards = config.get('standards', [])

            # 生成步骤内容
            step_content = {
                'step_number': step_number,
                'title': node_label,
                'node_type': node_type,
                'condition': condition,
                'description': description or f'执行操作: {node_label}',
                'precautions': precautions,
                'tools': tools,
                'standards': standards,
            }

            # 根据节点类型调整内容
            if node_type == 'start':
                step_content['description'] = description or f'开始流程: {node_label}'
            elif node_type == 'end':
                step_content['description'] = description or f'流程结束: {node_label}'
            elif node_type == 'decision':
                step_content['description'] = description or f'进行判断: {node_label}'

            steps.append(step_content)
            step_number += 1

            # 遍历后续节点
            if node_id in adjacency:
                for next_node in adjacency[node_id]:
                    traverse_node(
                        next_node['target'],
                        next_node.get('label', '')
                    )

        # 从开始节点遍历
        for start_node in start_nodes:
            traverse_node(start_node['id'])

        # 处理未访问的节点（孤立节点）
        for node in nodes:
            if node['id'] not in visited:
                traverse_node(node['id'])

        # 生成完整的作业指导书内容
        instruction = {
            'title': flowchart_data.get('title', '作业指导书'),
            'version': flowchart_data.get('version', '1.0'),
            'description': flowchart_data.get('description', ''),
            'steps': steps,
            'total_steps': len(steps),
            'flowchart_image': None,  # 可以后续填充
        }

        return instruction

    def create_flowchart_docx(
        self,
        flowchart_data: Dict[str, Any],
        output_path: str,
        node_configs: Optional[Dict[str, Dict[str, Any]]] = None,
        include_image: bool = True,
        template_path: Optional[str] = None
    ) -> str:
        """
        生成带流程图的Word文档

        Args:
            flowchart_data: 流程图数据
            output_path: 输出文件路径
            node_configs: 节点配置
            include_image: 是否包含流程图图像
            template_path: Word模板路径（可选）

        Returns:
            生成的文件路径
        """
        # 生成作业指导书内容
        instruction = self.generate_instruction_from_flowchart(
            flowchart_data, node_configs
        )

        # 创建文档
        if template_path and os.path.exists(template_path):
            doc = Document(template_path)
        else:
            doc = Document()

        # 设置文档标题
        title = doc.add_heading(instruction['title'], level=0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # 添加版本信息
        version_para = doc.add_paragraph()
        version_para.add_run(f'版本: {instruction["version"]}').bold = True
        version_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # 添加描述
        if instruction['description']:
            doc.add_paragraph(instruction['description'])

        doc.add_paragraph()  # 空行

        # 添加流程图图像
        if include_image:
            doc.add_heading('流程图', level=1)

            # 渲染流程图为图像
            image_data = self.render_to_image(flowchart_data, 'png', width=10, height=6)

            # 保存临时图像
            temp_image_path = output_path.replace('.docx', '_temp_flowchart.png')
            with open(temp_image_path, 'wb') as f:
                f.write(image_data)

            # 插入图像
            doc.add_picture(temp_image_path, width=Inches(6))

            # 删除临时文件
            os.remove(temp_image_path)

            doc.add_paragraph()  # 空行

        # 添加操作步骤
        doc.add_heading('操作步骤', level=1)

        for step in instruction['steps']:
            # 步骤标题
            step_title = f"步骤 {step['step_number']}: {step['title']}"
            if step['condition']:
                step_title += f" ({step['condition']})"

            doc.add_heading(step_title, level=2)

            # 步骤描述
            doc.add_paragraph(step['description'])

            # 使用工具
            if step['tools']:
                tools_para = doc.add_paragraph()
                tools_para.add_run('所需工具/设备: ').bold = True
                tools_para.add_run(', '.join(step['tools']))

            # 注意事项
            if step['precautions']:
                precautions_para = doc.add_paragraph()
                precautions_para.add_run('注意事项:').bold = True
                for precaution in step['precautions']:
                    doc.add_paragraph(precaution, style='List Bullet')

            # 执行标准
            if step['standards']:
                standards_para = doc.add_paragraph()
                standards_para.add_run('执行标准:').bold = True
                for standard in step['standards']:
                    doc.add_paragraph(standard, style='List Bullet')

            doc.add_paragraph()  # 空行

        # 添加页脚
        doc.add_paragraph()
        footer_para = doc.add_paragraph()
        footer_para.add_run('--- 作业指导书结束 ---').italic = True
        footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # 保存文档
        doc.save(output_path)

        return output_path

    def create_simple_flowchart(
        self,
        steps: List[str],
        title: str = '流程图'
    ) -> Dict[str, Any]:
        """
        从简单步骤列表创建流程图数据

        Args:
            steps: 步骤列表
            title: 流程图标题

        Returns:
            流程图数据字典
        """
        nodes = []
        edges = []

        # 添加开始节点
        nodes.append({
            'id': 'start',
            'type': 'start',
            'label': '开始'
        })

        # 添加步骤节点
        prev_id = 'start'
        for i, step in enumerate(steps):
            node_id = f'step_{i + 1}'
            nodes.append({
                'id': node_id,
                'type': 'process',
                'label': step
            })
            edges.append({
                'source': prev_id,
                'target': node_id
            })
            prev_id = node_id

        # 添加结束节点
        nodes.append({
            'id': 'end',
            'type': 'end',
            'label': '结束'
        })
        edges.append({
            'source': prev_id,
            'target': 'end'
        })

        return {
            'title': title,
            'nodes': nodes,
            'edges': edges
        }


# 示例用法
if __name__ == '__main__':
    # 创建渲染器实例
    renderer = FlowchartRenderer()

    # 示例流程图数据
    flowchart_data = {
        'title': '产品检验流程',
        'version': '1.0',
        'description': '产品质量检验的标准作业流程',
        'nodes': [
            {'id': 'start', 'type': 'start', 'label': '开始'},
            {'id': 'receive', 'type': 'process', 'label': '接收产品'},
            {'id': 'check', 'type': 'decision', 'label': '外观检查'},
            {'id': 'measure', 'type': 'process', 'label': '尺寸测量'},
            {'id': 'test', 'type': 'process', 'label': '性能测试'},
            {'id': 'pass', 'type': 'process', 'label': '合格入库'},
            {'id': 'reject', 'type': 'process', 'label': '不合格处理'},
            {'id': 'end', 'type': 'end', 'label': '结束'},
        ],
        'edges': [
            {'source': 'start', 'target': 'receive'},
            {'source': 'receive', 'target': 'check'},
            {'source': 'check', 'target': 'measure', 'label': '合格'},
            {'source': 'check', 'target': 'reject', 'label': '不合格'},
            {'source': 'measure', 'target': 'test'},
            {'source': 'test', 'target': 'pass', 'label': '通过'},
            {'source': 'test', 'target': 'reject', 'label': '未通过'},
            {'source': 'pass', 'target': 'end'},
            {'source': 'reject', 'target': 'end'},
        ]
    }

    # 节点配置
    node_configs = {
        'receive': {
            'description': '从生产线接收待检验产品，核对产品型号和批次号',
            'tools': ['扫码枪', '产品清单'],
            'precautions': ['确保产品标识清晰可读', '核对批次信息准确']
        },
        'check': {
            'description': '对产品进行外观检查，查看是否有划痕、变形等缺陷',
            'precautions': ['在标准光源下检查', '注意检查产品所有表面']
        },
        'measure': {
            'description': '使用测量工具对产品关键尺寸进行测量',
            'tools': ['卡尺', '千分尺', '高度规'],
            'standards': ['尺寸公差±0.1mm']
        },
        'test': {
            'description': '进行产品性能测试，确保功能正常',
            'tools': ['测试设备', '标准样品'],
            'standards': ['性能指标符合技术规范']
        },
    }

    # 渲染为图像
    image_data = renderer.render_to_image(flowchart_data, 'png')
    print(f"图像数据大小: {len(image_data)} bytes")

    # 生成Base64
    base64_image = renderer.render_to_base64(flowchart_data)
    print(f"Base64编码长度: {len(base64_image)} chars")

    # 生成作业指导书
    instruction = renderer.generate_instruction_from_flowchart(
        flowchart_data, node_configs
    )
    print(f"\n作业指导书: {instruction['title']}")
    print(f"总步骤数: {instruction['total_steps']}")
    for step in instruction['steps']:
        print(f"  {step['step_number']}. {step['title']}")

    # 生成Word文档
    output_path = r'C:\Users\毛蛋\ccaa-consult-v13\backend\app\modules\generator\flowchart_example.docx'
    renderer.create_flowchart_docx(flowchart_data, output_path, node_configs)
    print(f"\nWord文档已生成: {output_path}")
