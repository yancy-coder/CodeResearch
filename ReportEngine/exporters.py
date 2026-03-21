"""
ReportEngine - 第三方软件格式导出
支持 NVivo、Atlas.ti 等主流质性分析软件
"""
import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List, Dict
from pathlib import Path
from datetime import datetime

from CodeEngine.ir.code_ir import CodeUnit, Category


class NVivoExporter:
    """NVivo 格式导出器
    
    NVivo 支持导入:
    - CSV 格式（代码和引用）
    - REFI-QDA 标准格式 (.qdpx)
    """
    
    def __init__(self):
        self.version = "1.0"
    
    def export(self, codes: List[CodeUnit], categories: List[Category], 
               output_dir: str) -> str:
        """导出到 NVivo 格式
        
        Args:
            codes: 代码列表
            categories: 类属列表
            output_dir: 输出目录
            
        Returns:
            输出目录路径
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 导出 CSV 格式
        self._export_csv(codes, str(output_path / "codes.csv"))
        
        # 导出 REFI-QDA 格式
        self._export_refi_qda(codes, categories, str(output_path / "project.qdpx"))
        
        return str(output_path)
    
    def _export_csv(self, codes: List[CodeUnit], output_path: str):
        """导出 CSV 格式（代码-文本映射）"""
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            # 写入表头
            writer.writerow([
                'Code Name', 'Code Description', 'Source', 'Coded Text',
                'Start Position', 'End Position', 'Created By', 'Confidence'
            ])
            
            for code in codes:
                writer.writerow([
                    code.code_label,
                    code.code_definition,
                    code.text_segment.source,
                    code.text_segment.content[:200],  # 限制长度
                    code.text_segment.position[0],
                    code.text_segment.position[1],
                    code.created_by.value,
                    f"{code.confidence:.2f}"
                ])
    
    def _export_refi_qda(self, codes: List[CodeUnit], categories: List[Category],
                         output_path: str):
        """导出 REFI-QDA 标准格式"""
        # 创建 QDPX 项目结构
        root = ET.Element("Project")
        root.set("xmlns", "urn:QDA-XML:project:1.0")
        root.set("name", "CoderResearch Export")
        
        # Codes 部分
        codes_elem = ET.SubElement(root, "Codes")
        
        # 添加类属作为父代码
        for cat in categories:
            code_elem = ET.SubElement(codes_elem, "Code")
            code_elem.set("guid", cat.id)
            code_elem.set("name", cat.name)
            
            desc = ET.SubElement(code_elem, "Description")
            desc.text = cat.definition
        
        # 添加开放编码
        for code in codes:
            code_elem = ET.SubElement(codes_elem, "Code")
            code_elem.set("guid", code.id)
            code_elem.set("name", code.code_label)
            if code.category:
                code_elem.set("parent", code.category)
            
            desc = ET.SubElement(code_elem, "Description")
            desc.text = code.code_definition
        
        # Sources 部分
        sources_elem = ET.SubElement(root, "Sources")
        
        # 按来源分组
        sources_dict: Dict[str, List[CodeUnit]] = {}
        for code in codes:
            source = code.text_segment.source
            if source not in sources_dict:
                sources_dict[source] = []
            sources_dict[source].append(code)
        
        for source_name, source_codes in sources_dict.items():
            source_elem = ET.SubElement(sources_elem, "TextSource")
            source_elem.set("guid", source_name)
            source_elem.set("name", source_name)
            
            # 编码引用
            for code in source_codes:
                ref = ET.SubElement(source_elem, "Coding")
                ref.set("guid", code.id)
                ref.set("start", str(code.text_segment.position[0]))
                ref.set("end", str(code.text_segment.position[1]))
        
        # 美化 XML 输出
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_str)


class AtlasTiExporter:
    """Atlas.ti 格式导出器
    
    Atlas.ti 支持:
    - Excel/CSV 格式
    - ATLAS.ti 原生 XML
    """
    
    def __init__(self):
        self.version = "1.0"
    
    def export(self, codes: List[CodeUnit], categories: List[Category],
               output_dir: str) -> str:
        """导出到 Atlas.ti 格式"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 导出 Excel/CSV 格式
        self._export_excel_format(codes, str(output_path))
        
        # 导出 XML 格式
        self._export_xml(codes, categories, str(output_path / "atlasti_export.xml"))
        
        return str(output_path)
    
    def _export_excel_format(self, codes: List[CodeUnit], output_dir: str):
        """导出 Atlas.ti 兼容的 CSV 格式"""
        # Codes 表
        codes_path = Path(output_dir) / "atlasti_codes.csv"
        with open(codes_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['Code Name', 'Code Comment', 'Group'])
            
            for code in codes:
                writer.writerow([
                    code.code_label,
                    code.code_definition,
                    code.category if code.category else 'Open Codes'
                ])
        
        # Quotations 表（编码引用）
        quotes_path = Path(output_dir) / "atlasti_quotations.csv"
        with open(quotes_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Document Name', 'Quotation Content', 'Start Position',
                'End Position', 'Codes', 'Comment'
            ])
            
            for code in codes:
                writer.writerow([
                    code.text_segment.source,
                    code.text_segment.content[:200],
                    code.text_segment.position[0],
                    code.text_segment.position[1],
                    code.code_label,
                    f"Confidence: {code.confidence:.2f}"
                ])
        
        # Memos 表
        memos_path = Path(output_dir) / "atlasti_memos.csv"
        with open(memos_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['Memo Name', 'Memo Content', 'Type', 'Linked To'])
            # 这里可以添加备忘录数据
    
    def _export_xml(self, codes: List[CodeUnit], categories: List[Category],
                    output_path: str):
        """导出 Atlas.ti XML 格式"""
        root = ET.Element("atlasti")
        root.set("version", "8.0")
        
        # Codes 部分
        codes_elem = ET.SubElement(root, "codes")
        
        for code in codes:
            code_elem = ET.SubElement(codes_elem, "code")
            code_elem.set("name", code.code_label)
            
            if code.code_definition:
                comment = ET.SubElement(code_elem, "comment")
                comment.text = code.code_definition
        
        # Primary Documents 部分
        docs_elem = ET.SubElement(root, "primaryDocuments")
        
        sources_dict: Dict[str, List[CodeUnit]] = {}
        for code in codes:
            source = code.text_segment.source
            if source not in sources_dict:
                sources_dict[source] = []
            sources_dict[source].append(code)
        
        for source_name, source_codes in sources_dict.items():
            doc = ET.SubElement(docs_elem, "primaryDocument")
            doc.set("name", source_name)
            
            # 编码引用
            quotations = ET.SubElement(doc, "quotations")
            for code in source_codes:
                quote = ET.SubElement(quotations, "quotation")
                quote.set("start", str(code.text_segment.position[0]))
                quote.set("end", str(code.text_segment.position[1]))
                quote.set("content", code.text_segment.content[:100])
                
                # 关联代码
                codes_ref = ET.SubElement(quote, "codes")
                code_ref = ET.SubElement(codes_ref, "code")
                code_ref.set("name", code.code_label)
        
        # 美化输出
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_str)


class ExcelExporter:
    """Excel 格式导出器（通用）"""
    
    def export_summary(self, codes: List[CodeUnit], categories: List[Category],
                       output_path: str):
        """导出摘要统计"""
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # 概览
            writer.writerow(['CoderResearch 导出摘要'])
            writer.writerow(['导出时间', datetime.now().isoformat()])
            writer.writerow(['总代码数', len(codes)])
            writer.writerow(['总类属数', len(categories)])
            writer.writerow([])
            
            # 代码列表
            writer.writerow(['代码列表'])
            writer.writerow(['ID', '标签', '定义', '来源', '置信度'])
            
            for code in codes:
                writer.writerow([
                    code.id,
                    code.code_label,
                    code.code_definition,
                    code.text_segment.source,
                    f"{code.confidence:.2f}"
                ])
            
            writer.writerow([])
            
            # 类属列表
            writer.writerow(['类属列表'])
            writer.writerow(['ID', '名称', '定义', '包含代码数'])
            
            for cat in categories:
                writer.writerow([
                    cat.id,
                    cat.name,
                    cat.definition,
                    len(cat.codes)
                ])


def export_all_formats(codes: List[CodeUnit], categories: List[Category],
                       output_dir: str) -> Dict[str, str]:
    """导出所有格式
    
    Returns:
        格式名称到路径的映射
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    # NVivo
    nvivo = NVivoExporter()
    results['nvivo'] = nvivo.export(codes, categories, str(output_path / "nvivo"))
    
    # Atlas.ti
    atlasti = AtlasTiExporter()
    results['atlasti'] = atlasti.export(codes, categories, str(output_path / "atlasti"))
    
    # Excel 摘要
    excel = ExcelExporter()
    summary_path = str(output_path / "summary.csv")
    excel.export_summary(codes, categories, summary_path)
    results['summary'] = summary_path
    
    return results
