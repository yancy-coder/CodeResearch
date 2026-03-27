"""CLI command definitions."""
import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cli.dependencies import (
    get_coding_service, get_import_service,
    get_code_repository, get_session_repository, get_db
)
from cli.formatters import print_health_status, print_codes_table, print_segments_table
from utils.llm_client import llm_client

app = typer.Typer(help="CoderResearch - Qualitative Research Coding System")
console = Console(legacy_windows=True)


@app.command()
def health():
    """System health check"""
    llm_status = llm_client.health_check()
    
    db_ok = True
    db_count = 0
    try:
        db = get_db()
        codes = db.list_codes()
        db_count = len(codes)
    except Exception as e:
        db_ok = False
    
    session_repo = get_session_repository()
    session = session_repo.get("default")
    session_info = {
        "has_data": session is not None,
        "segments": len(session.data.get('segments', [])) if session else 0
    }
    
    print_health_status(llm_status, db_ok, session_info)
    
    if db_ok:
        rprint(f"\n[green]OK[/green] Database connection normal (SQLite)")
        rprint(f"   Current codebook contains {db_count} codes")
    else:
        rprint(f"\n[red]FAIL[/red] Database connection failed")
    
    if session_info['has_data']:
        rprint(f"\n[green]OK[/green] Session data found ({session_info['segments']} segments)")


@app.command()
def import_data(
    file_path: str = typer.Argument(..., help="Data file path (.txt/.md)"),
    segment_type: str = typer.Option("paragraph", help="Segmentation type"),
    anonymize: bool = typer.Option(True, help="Whether to anonymize")
):
    """Import research data"""
    service = get_import_service()
    segments = service.import_file(file_path, segment_type, anonymize)
    
    print_segments_table(segments, "Successfully imported text segments")
    rprint(f"[green]OK[/green] Data imported and saved")


@app.command()
def list_codes():
    """View codebook"""
    repo = get_code_repository()
    codes = repo.list()
    print_codes_table(codes)


@app.command()
def version():
    """Show version information"""
    rprint(Panel("""
[bold cyan]CoderResearch[/bold cyan] v2.0.0
Qualitative Research Coding System (Refactored)

Layered Architecture: CLI -> Service -> Engine -> Repository
    """, title="About"))


# Re-export app for main entry point
__all__ = ['app']
