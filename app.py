"""
CoderResearch 主应用入口
完整的定性研究编码工作流

新特性：
- AI 编码人工审核机制
- 会话持久化到数据库
- 健康检查命令
"""
import os
from pathlib import Path
from typing import List, Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress
from rich.prompt import Prompt, Confirm

from config import settings
from ImportEngine.agent import ImportEngine, ImportConfig
from CodeEngine.open_coding.agent import (
    OpenCodingAgent, OpenCodingConfig, 
    ReviewStatus, SuggestedCode
)
from CodeEngine.axial_coding.agent import AxialCodingAgent
from CodeEngine.selective_coding.agent import SelectiveCodingAgent
from CodeEngine.ir.code_ir import CodeUnit
from ForumEngine.agent import ForumEngine
from CodebookDB.db import CodebookDB
from TheoryEngine.visualizer import CodeNetworkVisualizer, SaturationChecker
from MemoEngine.agent import MemoEngine, MemoType
from ReportEngine.generator import ReportEngine
from utils.llm_client import llm_client, LLMProvider
from utils.session_manager import SessionManager

console = Console()
app = typer.Typer(help="CoderResearch - 定性研究智能编码系统")

# 全局实例
import_engine = ImportEngine()
open_coding_agent = OpenCodingAgent()
axial_coding_agent = AxialCodingAgent()
selective_coding_agent = SelectiveCodingAgent()
forum_engine = ForumEngine()
db = CodebookDB()
visualizer = CodeNetworkVisualizer()
saturation_checker = SaturationChecker()
memo_engine = MemoEngine()
report_engine = ReportEngine()
session_manager = SessionManager()


@app.command()
def health():
    """系统健康检查"""
    console.print(Panel("[bold blue]系统健康检查[/bold blue]"))
    
    # LLM 健康检查
    llm_status = llm_client.health_check()
    
    table = Table(title="LLM 服务状态")
    table.add_column("组件", style="cyan")
    table.add_column("状态", style="green")
    table.add_column("详情", style="yellow")
    
    # 当前提供商
    current = llm_status["current_provider"]
    table.add_row(
        "当前提供商",
        "✓ 正常" if llm_status["providers"].get(current, {}).get("available", False) else "✗ 不可用",
        f"{current} / {llm_status['model']}"
    )
    
    # 各提供商状态
    for provider, status in llm_status["providers"].items():
        avail = "✓ 可用" if status.get("available") else "✗ 不可用"
        detail = status.get("model", status.get("host", "-"))
        if "error" in status:
            detail = status["error"][:30]
        elif "reason" in status:
            detail = status["reason"]
        table.add_row(provider, avail, detail)
    
    console.print(table)
    
    # 数据库检查
    try:
        codes = db.list_codes()
        rprint(f"\n[green]✓[/green] 数据库连接正常 (SQLite)")
        rprint(f"   当前代码本包含 {len(codes)} 个代码")
    except Exception as e:
        rprint(f"\n[red]✗[/red] 数据库连接失败: {e}")
    
    # 会话检查
    session = session_manager.load_session()
    if session:
        rprint(f"\n[green]✓[/green] 发现会话数据")
        rprint(f"   片段: {len(session.get('segments', []))}")
        rprint(f"   代码: {len(session.get('open_codes', []))}")
    else:
        rprint(f"\n[yellow]![/yellow] 无会话数据")


@app.command()
def import_data(
    file_path: str = typer.Argument(..., help="数据文件路径(.txt/.md)"),
    segment_type: str = typer.Option("paragraph", help="分段方式: paragraph/turn"),
    anonymize: bool = typer.Option(True, help="是否去标识化")
):
    """导入研究数据"""
    console.print(Panel(f"[bold blue]导入数据: {file_path}[/bold blue]"))
    
    try:
        config = ImportConfig(anonymize=anonymize)
        import_engine.config = config
        
        segments = import_engine.import_file(file_path, segment_type)
        
        table = Table(title=f"成功导入 {len(segments)} 个文本片段")
        table.add_column("ID", style="cyan", width=10)
        table.add_column("内容预览", style="green", width=50)
        table.add_column("来源", style="yellow")
        
        for seg in segments[:5]:
            preview = seg.content[:60] + "..." if len(seg.content) > 60 else seg.content
            table.add_row(seg.id, preview, seg.source)
        
        if len(segments) > 5:
            table.add_row("...", f"还有 {len(segments) - 5} 个片段", "")
        
        console.print(table)
        
        # 保存会话到数据库
        session_manager.save_session({
            'segments': segments,
            'source_file': file_path,
            'open_codes': [],
            'categories': [],
            'relationships': []
        })
        
        rprint(f"[green]✓[/green] 数据已导入并保存")
        
    except Exception as e:
        rprint(f"[red]✗[/red] 导入失败: {e}")


def _review_suggestions_interactive(suggestions: List[SuggestedCode]) -> List[str]:
    """交互式审核编码建议"""
    if not suggestions:
        return []
    
    rprint(f"\n[yellow]需要审核 {len(suggestions)} 个编码建议[/yellow]")
    
    approved_ids = []
    
    for i, sugg in enumerate(suggestions, 1):
        rprint(f"\n[cyan]--- 建议 {i}/{len(suggestions)} ---[/cyan]")
        rprint(f"[bold]文本片段:[/bold] {sugg.text_segment.content[:100]}...")
        rprint(f"[bold]AI 建议代码:[/bold] {sugg.code_label}")
        rprint(f"[bold]定义:[/bold] {sugg.code_definition}")
        rprint(f"[bold]置信度:[/bold] {sugg.confidence:.2f}")
        if sugg.ai_reasoning:
            rprint(f"[dim]AI 理由: {sugg.ai_reasoning}[/dim]")
        
        # 交互式选择
        choice = Prompt.choices(
            "审核操作",
            choices=["approve", "reject", "modify", "skip", "approve_all"],
            default="approve"
        )
        
        if choice == "approve":
            approved_ids.append(sugg.id)
            rprint("[green]✓ 已批准[/green]")
        
        elif choice == "reject":
            comment = Prompt.ask("拒绝理由（可选）", default="")
            open_coding_agent.review_manager.reject(sugg.id, comment)
            rprint("[red]✗ 已拒绝[/red]")
        
        elif choice == "modify":
            new_label = Prompt.ask("新代码标签", default=sugg.code_label)
            new_def = Prompt.ask("新定义", default=sugg.code_definition)
            comment = Prompt.ask("修改理由", default="")
            open_coding_agent.review_manager.modify_and_approve(
                sugg.id, new_label, new_def, comment
            )
            approved_ids.append(sugg.id)
            rprint("[green]✓ 已修改并批准[/green]")
        
        elif choice == "skip":
            rprint("[yellow]跳过[/yellow]")
        
        elif choice == "approve_all":
            remaining = [s.id for s in suggestions[i-1:]]
            approved_ids.extend(remaining)
            rprint(f"[green]✓ 批量批准剩余 {len(remaining)} 个[/green]")
            break
    
    return approved_ids


@app.command()
def open_code(
    ai_assist: bool = typer.Option(True, help="是否启用 AI 辅助编码"),
    coding_style: str = typer.Option("descriptive", help="编码风格: descriptive/in_vivo/process"),
    require_review: bool = typer.Option(True, help="是否需要人工审核"),
    auto_approve: bool = typer.Option(False, help="高置信度自动通过")
):
    """开放编码 - 生成初始代码（支持人工审核）"""
    console.print(Panel("[bold blue]开放编码 (Open Coding)[/bold blue]"))
    
    session = session_manager.load_session()
    segments = session.get('segments', [])
    
    if not segments:
        rprint("[red]请先运行 import-data 导入数据[/red]")
        return
    
    rprint(f"对 {len(segments)} 个文本片段进行开放编码...")
    
    # 配置
    open_coding_agent.config = OpenCodingConfig(
        allow_ai_suggestion=ai_assist,
        coding_style=coding_style,
        require_human_review=require_review,
        auto_approve_high_confidence=auto_approve,
        batch_review=True
    )
    
    # 重置审核管理器
    open_coding_agent.review_manager = open_coding_agent.review_manager.__class__()
    
    # 批量编码
    def progress_callback(current, total, segment):
        pass  # Progress bar 在外面处理
    
    def review_callback(pending_suggestions):
        return _review_suggestions_interactive(pending_suggestions)
    
    all_codes: List[CodeUnit] = []
    
    with Progress() as progress:
        task = progress.add_task("[green]AI 编码中...", total=len(segments))
        
        for seg in segments:
            open_coding_agent.code_segment(seg, auto_review=False)
            progress.update(task, advance=1)
    
    # 审核阶段
    if require_review and open_coding_agent.review_manager.pending_reviews:
        approved_ids = _review_suggestions_interactive(
            open_coding_agent.review_manager.pending_reviews
        )
        open_coding_agent.review_manager.batch_approve(approved_ids)
    
    # 获取所有批准的代码
    all_codes = open_coding_agent.review_manager.approved_codes
    
    # 检测编码冲突
    conflicts = open_coding_agent.detect_coding_conflicts(all_codes)
    if conflicts:
        rprint(f"\n[yellow]⚠ 发现 {len(conflicts)} 个潜在编码冲突:[/yellow]")
        for conflict in conflicts[:5]:
            rprint(f"   - {conflict['code1']} vs {conflict['code2']}: {conflict['recommendation']}")
    
    # 显示结果
    table = Table(title=f"共批准 {len(all_codes)} 个初始代码")
    table.add_column("代码标签", style="cyan")
    table.add_column("定义", style="green")
    table.add_column("置信度", style="magenta")
    table.add_column("来源", style="yellow")
    
    for code in all_codes[:10]:
        source = "AI" if code.created_by.value == "ai" else "人机协作"
        table.add_row(
            code.code_label,
            code.code_definition[:40] + "..." if len(code.code_definition) > 40 else code.code_definition,
            f"{code.confidence:.2f}",
            source
        )
    
    if len(all_codes) > 10:
        table.add_row("...", f"还有 {len(all_codes) - 10} 个代码", "", "")
    
    console.print(table)
    
    # 保存到数据库和会话
    for code in all_codes:
        db.save_code({
            "id": code.id,
            "label": code.code_label,
            "definition": code.code_definition,
            "level": "open",
            "created_by": code.created_by.value
        })
    
    session['open_codes'] = all_codes
    session_manager.save_session(session)
    
    # 导出编码日志
    log_path = open_coding_agent.export_coding_log("outputs/coding_log.json")
    rprint(f"[green]✓[/green] 已保存 {len(all_codes)} 个代码")
    rprint(f"[dim]编码日志: {log_path}[/dim]")


@app.command()
def axial_code():
    """轴心编码 - 归类、找关系、建维度"""
    console.print(Panel("[bold blue]轴心编码 (Axial Coding)[/bold blue]"))
    
    session = session_manager.load_session()
    codes = session.get('open_codes', [])
    
    if not codes:
        rprint("[red]请先运行 open-code 完成开放编码[/red]")
        return
    
    rprint(f"对 {len(codes)} 个代码进行轴心编码...")
    
    with console.status("[bold green]AI 正在归类..."):
        categories = axial_coding_agent.categorize_codes(codes)
    
    rprint(f"[green]✓[/green] 识别 {len(categories)} 个类属")
    
    # 显示类属
    table = Table(title="类属结构")
    table.add_column("类属名称", style="cyan")
    table.add_column("定义", style="green")
    table.add_column("包含代码", style="yellow")
    
    for cat in categories:
        table.add_row(cat.name, cat.definition[:50], str(len(cat.codes)))
    
    console.print(table)
    
    # 找关系
    with console.status("[bold green]分析类属关系..."):
        relationships = axial_coding_agent.find_relationships(categories)
    
    rprint(f"[green]✓[/green] 识别 {len(relationships)} 个关系")
    
    # 构建编码矩阵
    matrix = axial_coding_agent.build_coding_matrix(codes, categories)
    
    # 保存
    session['categories'] = categories
    session['relationships'] = relationships
    session['coding_matrix'] = matrix
    session_manager.save_session(session)
    
    rprint("[green]✓[/green] 轴心编码完成")


@app.command()
def selective_code():
    """选择性编码 - 识别核心类属，构建理论"""
    console.print(Panel("[bold blue]选择性编码 (Selective Coding)[/bold blue]"))
    
    session = session_manager.load_session()
    categories = session.get('categories', [])
    codes = session.get('open_codes', [])
    
    if not categories:
        rprint("[red]请先运行 axial-code 完成轴心编码[/red]")
        return
    
    rprint("识别核心类属...")
    
    with console.status("[bold green]AI 分析中..."):
        core_category = selective_coding_agent.identify_core_category(categories)
        
        if core_category:
            rprint(f"[green]✓[/green] 核心类属: [bold]{core_category.name}[/bold]")
            
            # 构建故事线
            storyline = selective_coding_agent.build_storyline(core_category, categories)
            rprint(f"[green]✓[/green] 故事线: {storyline.title}")
            
            # 检查饱和度
            saturation = selective_coding_agent.check_saturation(codes, categories)
            rprint(f"饱和度评分: {saturation.get('saturation_score', 0)}")
            
            # 生成理论命题
            propositions = selective_coding_agent.generate_theoretical_propositions(storyline, categories)
            rprint(f"[green]✓[/green] 生成 {len(propositions)} 个理论命题")
            
            # 保存
            session['core_category'] = core_category
            session['storyline'] = storyline
            session['propositions'] = propositions
            session_manager.save_session(session)
            
            rprint("[green]✓[/green] 选择性编码完成，理论框架已构建")


@app.command()
def visualize(
    output_format: str = typer.Option("html", help="输出格式: html/png")
):
    """生成编码可视化图表"""
    console.print(Panel("[bold blue]生成可视化图表[/bold blue]"))
    
    session = session_manager.load_session()
    categories = session.get('categories', [])
    relationships = session.get('relationships', [])
    
    if not categories:
        rprint("[red]请先完成编码分析[/red]")
        return
    
    output_dir = Path(settings.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    if output_format == "html":
        # 交互式网络图
        path = visualizer.plot_interactive_network(
            categories, relationships,
            str(output_dir / "code_network.html")
        )
        rprint(f"[green]✓[/green] 网络图: {path}")
        
        # 代码分布图
        path = visualizer.generate_code_map(
            categories,
            str(output_dir / "code_map.html")
        )
        rprint(f"[green]✓[/green] 分布图: {path}")
    else:
        # 静态图
        path = visualizer.plot_static_network(
            categories, relationships,
            str(output_dir / "code_network.png")
        )
        rprint(f"[green]✓[/green] 网络图: {path}")


@app.command()
def saturation():
    """检查理论饱和度"""
    console.print(Panel("[bold blue]理论饱和度检查[/bold blue]"))
    
    session = session_manager.load_session()
    categories = session.get('categories', [])
    codes = session.get('open_codes', [])
    segments = session.get('segments', [])
    
    if not codes:
        rprint("[red]请先完成编码[/red]")
        return
    
    report = saturation_checker.generate_saturation_report(
        categories, codes, len(segments)
    )
    
    table = Table(title="饱和度报告")
    table.add_column("指标", style="cyan")
    table.add_column("值", style="green")
    
    table.add_row("总文本片段", str(report['total_segments']))
    table.add_row("已编码片段", str(report['coded_segments']))
    table.add_row("编码覆盖率", f"{report['coverage']:.1%}")
    table.add_row("总代码数", str(report['total_codes']))
    table.add_row("总类属数", str(report['total_categories']))
    table.add_row("饱和度等级", report['saturation_level'])
    
    console.print(table)
    
    if report['recommendations']:
        rprint("\n[yellow]建议:[/yellow]")
        for rec in report['recommendations']:
            rprint(f"  - {rec}")


@app.command()
def memo(
    memo_type: str = typer.Argument(..., help="备忘录类型: code/theoretical/reflective"),
    target: str = typer.Option(None, help="关联的代码/类属名称")
):
    """撰写备忘录"""
    console.print(Panel("[bold blue]备忘录撰写[/bold blue]"))
    
    session = session_manager.load_session()
    
    if memo_type == "code":
        codes = session.get('open_codes', [])
        if not target or not codes:
            rprint("[red]请指定代码标签或先完成编码[/red]")
            return
        
        code = next((c for c in codes if c.code_label == target), None)
        if code:
            memo_obj = memo_engine.create_code_memo(
                code.code_label,
                code.code_definition,
                [code.text_segment.content]
            )
            rprint(f"[green]✓[/green] 代码备忘录已生成: {memo_obj.id}")
            rprint(Panel(memo_obj.content[:500] + "...", title="预览"))
    
    elif memo_type == "theoretical":
        categories = session.get('categories', [])
        if not categories:
            rprint("[red]请先完成轴心编码[/red]")
            return
        
        cat = categories[0]  # 简化处理
        memo_obj = memo_engine.create_theoretical_memo(
            cat.name,
            [c for c in cat.codes],
            "初步分析"
        )
        rprint(f"[green]✓[/green] 理论备忘录已生成: {memo_obj.id}")
    
    elif memo_type == "reflective":
        content = typer.prompt("请输入反思内容")
        memo_obj = memo_engine.create_reflective_memo("general", content)
        rprint(f"[green]✓[/green] 反思备忘录已保存: {memo_obj.id}")


@app.command()
def report(
    title: str = typer.Option("定性研究报告", help="报告标题"),
    format: str = typer.Option("markdown", help="格式: markdown/docx/nvivo/atlasti")
):
    """生成研究报告（支持多种格式）"""
    console.print(Panel("[bold blue]生成研究报告[/bold blue]"))
    
    session = session_manager.load_session()
    codes = session.get('open_codes', [])
    categories = session.get('categories', [])
    core_category = session.get('core_category')
    storyline = session.get('storyline')
    propositions = session.get('propositions', [])
    
    if not core_category:
        rprint("[red]请先完成选择性编码[/red]")
        return
    
    output_dir = Path(settings.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    if format in ["markdown", "docx"]:
        # 生成完整报告
        content = report_engine.generate_full_report(
            title=title,
            research_question="待填写",
            codes=codes,
            categories=categories,
            core_category=core_category,
            storyline=storyline,
            propositions=propositions
        )
        
        if format == "markdown":
            path = report_engine.save_report(content, "final_report.md")
            rprint(f"[green]✓[/green] 报告已保存: {path}")
        else:
            md_path = report_engine.save_report(content, "temp.md")
            docx_path = report_engine.export_to_docx(content, str(output_dir / "final_report.docx"))
            rprint(f"[green]✓[/green] Word 报告已保存: {docx_path}")
    
    elif format == "nvivo":
        # 导出 NVivo 格式
        from ReportEngine.exporters import NVivoExporter
        exporter = NVivoExporter()
        path = exporter.export(codes, categories, str(output_dir / "nvivo_export"))
        rprint(f"[green]✓[/green] NVivo 导出完成: {path}")
    
    elif format == "atlasti":
        # 导出 Atlas.ti 格式
        from ReportEngine.exporters import AtlasTiExporter
        exporter = AtlasTiExporter()
        path = exporter.export(codes, categories, str(output_dir / "atlasti_export"))
        rprint(f"[green]✓[/green] Atlas.ti 导出完成: {path}")


@app.command()
def discuss(
    code_id: str = typer.Argument(..., help="要讨论的代码ID")
):
    """发起编码讨论"""
    console.print(Panel("[bold blue]编码讨论论坛[/bold blue]"))
    
    code_data = db.get_code(code_id)
    if not code_data:
        rprint(f"[red]未找到代码: {code_id}[/red]")
        return
    
    rprint(f"讨论主题: [bold]{code_data['label']}[/bold]\n")
    
    # 模拟讨论
    rprint("[cyan]研究者:[/cyan] 我对这段文本编码为 '{}', 定义为：{}".format(
        code_data['label'], code_data['definition']
    ))
    
    rprint("\n[red]质疑者:[/red] 为什么选择这个代码？还有其他可能的理解吗？")
    rprint("这个代码定义是否太宽泛？能否更具体？")
    
    rprint("\n[green]AI助手:[/green] 建议检查与已有代码本的一致性。")


@app.command()
def list_codes(
    level: str = typer.Option("all", help="筛选级别: all/open/axial/selective")
):
    """查看代码本"""
    console.print(Panel("[bold blue]当前代码本[/bold blue]"))
    
    lvl = None if level == "all" else level
    codes = db.list_codes(lvl)
    
    if not codes:
        rprint("[yellow]暂无代码[/yellow]")
        return
    
    table = Table(title=f"共 {len(codes)} 个代码")
    table.add_column("ID", style="dim", width=8)
    table.add_column("代码标签", style="cyan")
    table.add_column("定义", style="green")
    table.add_column("层级", style="yellow", width=10)
    
    for code in codes[:20]:
        table.add_row(
            code["id"],
            code["label"],
            code["definition"][:40] + "..." if len(code["definition"]) > 40 else code["definition"],
            code["level"]
        )
    
    console.print(table)


@app.command()
def workflow(
    file_path: str = typer.Argument(..., help="数据文件路径"),
    research_question: str = typer.Option("待研究问题", help="研究问题"),
    skip_review: bool = typer.Option(False, help="跳过人工审核（快速模式）")
):
    """一键运行完整编码工作流"""
    console.print(Panel(f"[bold blue]完整编码工作流: {file_path}[/bold blue]"))
    
    # 1. 导入
    rprint("\n[bold]步骤 1: 导入数据[/bold]")
    import_data(file_path)
    
    # 2. 开放编码
    rprint("\n[bold]步骤 2: 开放编码[/bold]")
    open_code(require_review=not skip_review)
    
    # 3. 轴心编码
    rprint("\n[bold]步骤 3: 轴心编码[/bold]")
    axial_code()
    
    # 4. 选择性编码
    rprint("\n[bold]步骤 4: 选择性编码[/bold]")
    selective_code()
    
    # 5. 可视化
    rprint("\n[bold]步骤 5: 生成可视化[/bold]")
    visualize()
    
    # 6. 报告
    rprint("\n[bold]步骤 6: 生成报告[/bold]")
    report(title=f"{research_question}研究报告")
    
    rprint("\n[green bold]✓ 完整工作流执行完毕！[/green bold]")


@app.command()
def version():
    """显示版本信息"""
    rprint(Panel("""
[bold cyan]CoderResearch[/bold cyan] v1.1.0
定性研究智能编码系统

基于扎根理论方法论
支持开放编码 → 轴心编码 → 选择性编码

新特性:
• AI 编码人工审核机制
• 多 LLM 提供商支持 (OpenAI/Moonshot/Ollama)
• 会话持久化到数据库
• NVivo/Atlas.ti 格式导出

LLM 支持: Moonshot (Kimi) / OpenAI / Ollama (本地)
    """, title="关于"))


if __name__ == "__main__":
    app()
