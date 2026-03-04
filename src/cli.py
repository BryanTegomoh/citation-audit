"""Command-line interface for Citation Verification Toolkit."""

import sys
from pathlib import Path
from typing import Optional

try:
    import click
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    HAS_CLI_DEPS = True
except ImportError:
    HAS_CLI_DEPS = False

from .extractors.markdown import extract_from_markdown, extract_from_directory
from .extractors.bibtex import extract_from_bibtex
from .extractors.plaintext import extract_from_plaintext
from .validators.doi_resolver import check_doi_exists
from .validators.crossref import get_crossref_metadata
from .validators.prefix_checker import validate_prefix, get_publisher_for_prefix, extract_prefix
from .verify import verify_citation, verify_citations, verify_doi, VerificationStatus
from .reporters.markdown import generate_markdown_report, save_report


def check_cli_deps():
    """Check if CLI dependencies are installed."""
    if not HAS_CLI_DEPS:
        print("CLI dependencies not installed. Run: pip install click rich")
        sys.exit(1)


# Only define CLI if dependencies are available
if HAS_CLI_DEPS:
    console = Console()

    @click.group()
    @click.version_option(version="1.0.0")
    def main():
        """Citation Verification Toolkit - Detect citation errors."""
        pass

    @main.command()
    @click.argument('doi')
    def verify(doi: str):
        """Verify a single DOI.

        DOI: The DOI to verify (e.g., 10.1038/s41591-020-1034-x)
        """
        console.print(f"\n[bold]Verifying DOI:[/bold] {doi}\n")

        with console.status("Checking DOI resolution..."):
            resolution = check_doi_exists(doi)

        if not resolution.exists:
            console.print(f"[red]❌ DOI does not exist[/red]")
            if resolution.error:
                console.print(f"   Error: {resolution.error}")
            console.print(f"   Status code: {resolution.status_code}")
            return

        console.print(f"[green]✓ DOI exists[/green]")

        with console.status("Fetching metadata from CrossRef..."):
            metadata = get_crossref_metadata(doi)

        if metadata:
            table = Table(title="Paper Metadata")
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="white")

            table.add_row("Title", metadata.title[:80] + "..." if len(metadata.title) > 80 else metadata.title)
            table.add_row("Authors", metadata.author_string)
            table.add_row("Year", str(metadata.year) if metadata.year else "Unknown")
            table.add_row("Journal", metadata.journal or "Unknown")
            table.add_row("Publisher", metadata.publisher or "Unknown")

            prefix = extract_prefix(doi)
            if prefix:
                publisher = get_publisher_for_prefix(prefix)
                table.add_row("DOI Prefix", f"{prefix} ({publisher or 'Unknown publisher'})")

            console.print(table)
        else:
            console.print("[yellow]⚠ Could not fetch metadata from CrossRef[/yellow]")

        console.print()

    @main.command()
    @click.argument('file_path', type=click.Path(exists=True))
    @click.option('--output', '-o', type=click.Path(), help='Output report file')
    @click.option('--format', '-f', type=click.Choice(['md', 'summary']), default='summary',
                  help='Output format')
    def check(file_path: str, output: Optional[str], format: str):
        """Check all citations in a file.

        FILE_PATH: Path to Markdown, BibTeX, or text file
        """
        path = Path(file_path)

        # Determine file type and extract citations
        console.print(f"\n[bold]Checking citations in:[/bold] {path.name}\n")

        with console.status("Extracting citations..."):
            if path.suffix.lower() in ['.md', '.qmd', '.markdown']:
                citations = extract_from_markdown(file_path)
            elif path.suffix.lower() == '.bib':
                citations = extract_from_bibtex(file_path)
            elif path.suffix.lower() == '.txt':
                citations = extract_from_plaintext(file_path)
            else:
                console.print(f"[red]Unsupported file type: {path.suffix}[/red]")
                return

        console.print(f"Found [bold]{len(citations)}[/bold] citations with DOIs\n")

        if not citations:
            console.print("[yellow]No citations found.[/yellow]")
            return

        # Verify citations with progress bar
        results = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Verifying citations...", total=len(citations))

            for citation in citations:
                result = verify_citation(citation)
                results.append(result)
                progress.advance(task)

        # Summarize results
        valid = sum(1 for r in results if r.status == VerificationStatus.VALID)
        warnings = sum(1 for r in results if r.status == VerificationStatus.WARNING)
        invalid = sum(1 for r in results if r.status == VerificationStatus.INVALID)
        errors = sum(1 for r in results if r.status == VerificationStatus.ERROR)

        # Display summary table
        table = Table(title="Verification Summary")
        table.add_column("Status", style="cyan")
        table.add_column("Count", justify="right")

        table.add_row("Valid", f"[green]{valid}[/green]")
        table.add_row("Warnings", f"[yellow]{warnings}[/yellow]")
        table.add_row("Invalid", f"[red]{invalid}[/red]")
        table.add_row("Errors", f"[red]{errors}[/red]")
        table.add_row("Total", str(len(results)))

        console.print(table)
        console.print()

        # Show invalid citations
        invalid_results = [r for r in results if r.status == VerificationStatus.INVALID]

        if invalid_results:
            console.print("[bold red]Invalid Citations:[/bold red]\n")

            for result in invalid_results:
                console.print(f"  • [red]{result.citation.doi}[/red]")
                if result.citation.text:
                    console.print(f"    Citation: {result.citation.text}")
                for issue in result.issues:
                    console.print(f"    [dim]- {issue.message}[/dim]")
                console.print()

        # Save report if requested
        if output:
            save_report(results, output, title=f"Verification Report: {path.name}")
            console.print(f"[green]Report saved to: {output}[/green]")

    @main.command()
    @click.argument('file_path', type=click.Path(exists=True))
    @click.option('--output', '-o', type=click.Path(), default='report.md',
                  help='Output report file')
    def batch(file_path: str, output: str):
        """Batch verify DOIs from a text file.

        FILE_PATH: Path to text file with one DOI per line
        """
        console.print(f"\n[bold]Batch verifying DOIs from:[/bold] {file_path}\n")

        with console.status("Extracting DOIs..."):
            citations = extract_from_plaintext(file_path)

        console.print(f"Found [bold]{len(citations)}[/bold] DOIs\n")

        if not citations:
            console.print("[yellow]No DOIs found.[/yellow]")
            return

        # Verify with progress
        results = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Verifying DOIs...", total=len(citations))

            for citation in citations:
                result = verify_citation(citation)
                results.append(result)
                progress.advance(task)

        # Generate and save report
        save_report(results, output, title="Batch DOI Verification Report")

        # Summary
        valid = sum(1 for r in results if r.status == VerificationStatus.VALID)
        invalid = sum(1 for r in results if r.status != VerificationStatus.VALID)

        console.print(f"\n[green]✓ {valid} valid[/green], [red]✗ {invalid} issues[/red]")
        console.print(f"\n[bold]Report saved to:[/bold] {output}")

    @main.command()
    @click.argument('file_path', type=click.Path(exists=True))
    @click.option('--format', '-f', type=click.Choice(['list', 'json']), default='list',
                  help='Output format')
    def extract(file_path: str, format: str):
        """Extract citations from a file without verifying.

        FILE_PATH: Path to Markdown, BibTeX, or text file
        """
        path = Path(file_path)

        # Extract based on file type
        if path.suffix.lower() in ['.md', '.qmd', '.markdown']:
            citations = extract_from_markdown(file_path)
        elif path.suffix.lower() == '.bib':
            citations = extract_from_bibtex(file_path)
        elif path.suffix.lower() == '.txt':
            citations = extract_from_plaintext(file_path)
        else:
            console.print(f"[red]Unsupported file type: {path.suffix}[/red]")
            return

        console.print(f"\n[bold]Found {len(citations)} citations[/bold]\n")

        if format == 'list':
            for citation in citations:
                console.print(f"• {citation.doi}")
                if citation.text:
                    console.print(f"  [dim]{citation.text}[/dim]")

        elif format == 'json':
            import json
            data = [
                {
                    'doi': c.doi,
                    'text': c.text,
                    'line': c.line_number,
                    'author': c.claimed_author,
                    'year': c.claimed_year,
                }
                for c in citations
            ]
            console.print(json.dumps(data, indent=2))

    @main.command()
    @click.argument('doi')
    def prefix(doi: str):
        """Check the publisher prefix of a DOI.

        DOI: The DOI to check
        """
        p = extract_prefix(doi)

        if not p:
            console.print(f"[red]Could not extract prefix from: {doi}[/red]")
            return

        publisher = get_publisher_for_prefix(p)

        console.print(f"\n[bold]DOI:[/bold] {doi}")
        console.print(f"[bold]Prefix:[/bold] {p}")
        console.print(f"[bold]Publisher:[/bold] {publisher or 'Unknown'}")


else:
    # Fallback if dependencies not installed
    def main():
        check_cli_deps()


if __name__ == '__main__':
    main()
