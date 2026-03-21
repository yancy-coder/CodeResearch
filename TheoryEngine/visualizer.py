"""
TheoryEngine - 理论建构与可视化
"""
import json
from typing import List, Dict, Optional
from pathlib import Path

import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from CodeEngine.ir.code_ir import Category, Relationship, CodeUnit
from CodebookDB.db import CodebookDB


class CodeNetworkVisualizer:
    """编码网络可视化"""
    
    def __init__(self):
        self.db = CodebookDB()
    
    def build_network(self, categories: List[Category], relationships: List[Relationship]) -> nx.DiGraph:
        """构建网络图"""
        G = nx.DiGraph()
        
        # 添加节点
        for cat in categories:
            G.add_node(cat.name, 
                      definition=cat.definition,
                      code_count=len(cat.codes),
                      properties=cat.properties)
        
        # 添加边
        for rel in relationships:
            G.add_edge(rel.source_id, rel.target_id,
                      relation_type=rel.relation_type,
                      description=rel.description)
        
        return G
    
    def plot_static_network(self, categories: List[Category], 
                           relationships: List[Relationship],
                           output_path: str = "code_network.png"):
        """生成静态网络图（matplotlib）"""
        G = self.build_network(categories, relationships)
        
        plt.figure(figsize=(12, 10))
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # 节点大小根据包含的代码数量
        node_sizes = [G.nodes[n].get('code_count', 1) * 300 + 500 for n in G.nodes()]
        
        # 绘制
        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, 
                              node_color='lightblue', alpha=0.9)
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
        nx.draw_networkx_edges(G, pos, edge_color='gray', 
                              arrows=True, arrowsize=20,
                              connectionstyle='arc3,rad=0.1')
        
        # 边标签
        edge_labels = {(u, v): d['relation_type'] 
                      for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8)
        
        plt.title("编码关系网络图", fontsize=16)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def plot_interactive_network(self, categories: List[Category],
                                 relationships: List[Relationship],
                                 output_path: str = "code_network.html"):
        """生成交互式网络图（plotly）"""
        G = self.build_network(categories, relationships)
        
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # 准备节点数据
        node_x = []
        node_y = []
        node_text = []
        node_size = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            # 悬停文本
            info = G.nodes[node]
            text = f"<b>{node}</b><br>"
            text += f"定义: {info.get('definition', 'N/A')[:50]}...<br>"
            text += f"代码数: {info.get('code_count', 0)}<br>"
            text += f"属性: {', '.join(info.get('properties', []))}"
            node_text.append(text)
            
            node_size.append(info.get('code_count', 1) * 20 + 20)
        
        # 准备边数据
        edge_x = []
        edge_y = []
        edge_text = []
        
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_text.append(f"{edge[0]} → {edge[1]}: {edge[2].get('relation_type', '')}")
        
        # 创建图表
        fig = go.Figure()
        
        # 边
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='text',
            text=edge_text,
            mode='lines',
            name='关系'
        ))
        
        # 节点
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=list(G.nodes()),
            textposition='top center',
            textfont=dict(size=10),
            marker=dict(size=node_size, color='lightblue', line_width=2),
            hovertext=node_text,
            name='类属'
        ))
        
        fig.update_layout(
            title="编码关系网络（交互式）",
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        
        fig.write_html(output_path)
        return output_path
    
    def generate_code_map(self, categories: List[Category], output_path: str = "code_map.html"):
        """生成代码分布热力图"""
        # 统计每个类属的代码数
        data = {
            '类属': [c.name for c in categories],
            '代码数': [len(c.codes) for c in categories],
            '属性数': [len(c.properties) for c in categories]
        }
        
        fig = go.Figure(data=[
            go.Bar(name='代码数', x=data['类属'], y=data['代码数']),
            go.Bar(name='属性数', x=data['类属'], y=data['属性数'])
        ])
        
        fig.update_layout(
            title="类属代码分布",
            barmode='group',
            xaxis_tickangle=-45
        )
        
        fig.write_html(output_path)
        return output_path


class SaturationChecker:
    """理论饱和度检查器"""
    
    def __init__(self):
        self.db = CodebookDB()
    
    def calculate_coverage(self, segments_count: int, coded_segments: int) -> float:
        """计算编码覆盖率"""
        if segments_count == 0:
            return 0.0
        return coded_segments / segments_count
    
    def check_code_redundancy(self, codes: List[CodeUnit]) -> List[Dict]:
        """检查代码冗余（相似代码）"""
        # 简化实现：基于标签相似度
        redundant = []
        seen = {}
        
        for code in codes:
            key = code.code_label.lower()
            if key in seen:
                redundant.append({
                    "code1": seen[key],
                    "code2": code.id,
                    "label": code.code_label
                })
            else:
                seen[key] = code.id
        
        return redundant
    
    def generate_saturation_report(self, categories: List[Category],
                                    codes: List[CodeUnit],
                                    segments_count: int) -> Dict:
        """生成饱和度报告"""
        
        coded_count = len(set(c.text_segment.id for c in codes))
        coverage = self.calculate_coverage(segments_count, coded_count)
        redundancy = self.check_code_redundancy(codes)
        
        report = {
            "total_segments": segments_count,
            "coded_segments": coded_count,
            "coverage": round(coverage, 2),
            "total_codes": len(codes),
            "total_categories": len(categories),
            "redundant_codes": len(redundancy),
            "saturation_level": "高" if coverage > 0.8 else "中" if coverage > 0.5 else "低",
            "recommendations": []
        }
        
        if coverage < 0.8:
            report["recommendations"].append("建议增加编码覆盖率")
        if len(redundancy) > 0:
            report["recommendations"].append(f"发现 {len(redundancy)} 个可能冗余的代码，建议合并")
        if len(categories) > 15:
            report["recommendations"].append("类属数量较多，建议进一步整合")
        
        return report
