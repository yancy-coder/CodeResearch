"""CLI output formatters."""
from typing import List, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Use legacy_windows to avoid encoding issues on Windows
console = Console(legacy_windows=True)


def print_health_status(llm_status: dict, db_status: bool, session_info: dict):
    """Print health check status."""
    console.print(Panel("[bold blue]System Health Check[/bold blue]"))
    
    table = Table(title="LLM Service Status")
    table.add_column("Provider", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="yellow")
    
    providers = llm_status.get("providers", {})
    if providers:
        for provider, status in providers.items():
            avail = "[green]OK[/green]" if status.get("available") else "[red]FAIL[/red]"
            detail = status.get("model", status.get("host", "-"))
            if "reason" in status:
                detail = status["reason"][:30]
            table.add_row(provider, avail, detail)
    else:
        table.add_row("-", "No providers", "-")
    
    console.print(table)


def print_codes_table(codes: List[Any], title: str = "Code List"):
    """Print codes in a table format."""
    if not codes:
        console.print("[yellow]No codes found[/yellow]")
        return
    
    table = Table(title=f"{title} (Total: {len(codes)})")
    table.add_column("ID", style="dim", width=8)
    table.add_column("Label", style="cyan")
    table.add_column("Definition", style="green")
    table.add_column("Level", style="yellow", width=10)
    
    for code in codes[:20]:
        definition = code.definition[:40] + "..." if len(code.definition) > 40 else code.definition
        table.add_row(code.id, code.label, definition, code.level)
    
    if len(codes) > 20:
        table.add_row("...", f"{len(codes) - 20} more codes", "", "")
    
    console.print(table)


def print_segments_table(segments: List[Any], title: str = "Text Segments"):
    """Print text segments in a table format."""
    table = Table(title=f"{title} (Total: {len(segments)})")
    table.add_column("ID", style="cyan", width=10)
    table.add_column("Preview", style="green", width=50)
    table.add_column("Source", style="yellow")
    
    for seg in segments[:5]:
        preview = seg.content[:60] + "..." if len(seg.content) > 60 else seg.content
        table.add_row(seg.id, preview, seg.source)
    
    if len(segments) > 5:
        table.add_row("...", f"{len(segments) - 5} more segments", "")
    
    console.print(table)
