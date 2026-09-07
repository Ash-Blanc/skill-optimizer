"""
Skill Optimizer CLI - Optimize agent skills using DSPy.

Usage:
    skill-optimizer analyze <skill_name>
    skill-optimizer optimize <skill_name> [--strategy=<strategy>] [--model=<model>]
    skill-optimizer compare <skill_a> <skill_b>
"""

import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import Optional
import json
import os
import dspy
from dotenv import load_dotenv

from app.models.skill import Skill
from app.pipeline.optimizer import SkillOptimizer
from app.pipeline.analyzer import OptimizationPotentialAnalyzer

# Load environment variables
load_dotenv(os.path.join(os.getcwd(), ".env"))

# Configure DSPy
def configure_dspy():
    """Configure DSPy LM from environment variables."""
    openai_key = os.getenv("OPENAI_API_KEY")
    mistral_key = os.getenv("MISTRAL_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    dspy_model = os.getenv("DSPY_MODEL")
    ollama_model = os.getenv("OLLAMA_MODEL")
    
    if dspy_model:
        # User specified model
        lm = dspy.LM(dspy_model)
        dspy.configure(lm=lm)
        return

    if ollama_model:
        # User specified model
        lm = dspy.LM(
            model=ollama_model,
            api_base=os.getenv("OLLAMA_API_BASE", "http://127.0.0.1:11434"),
            temperature=float(os.getenv("OLLAMA_TEMPERATURE", 0.2)),
            max_tokens=int(os.getenv("OLLAMA_MAX_TOKENS", 4096)),
            timeout=int(os.getenv("OLLAMA_TIMEOUT", 1800)),
        )
        dspy.configure(lm=lm)
        return 

    # Auto-detect
    if mistral_key:
        # User requested Mistral
        lm = dspy.LM("mistral/mistral-large-latest", api_key=mistral_key)
        dspy.configure(lm=lm)
    elif openai_key:
        lm = dspy.LM("openai/gpt-4o-mini", api_key=openai_key)
        dspy.configure(lm=lm)
    elif gemini_key:
        lm = dspy.LM("gemini/gemini-1.5-flash", api_key=gemini_key)
        dspy.configure(lm=lm)
    else:
        print("[yellow]Warning: No API keys found (MISTRAL_API_KEY, OPENAI_API_KEY or GEMINI_API_KEY). DSPy may fail.[/yellow]")

configure_dspy()


app = typer.Typer(
    name="skill-optimizer",
    help="Optimize agent skills using DSPy teleprompters",
    context_settings={"help_option_names": ["-h", "--help"]}
)
console = Console()


@app.command()
def analyze(
    skill_name: str = typer.Argument(..., help="Name of the skill to analyze"),
    skills_dir: str = typer.Option("skills", help="Directory containing skills")
):
    """Analyze a skill's optimization potential before optimizing."""
    try:
        skill = Skill.load(skill_name, skills_dir)
    except FileNotFoundError:
        console.print(f"[red]Skill '{skill_name}' not found in {skills_dir}/[/red]")
        raise typer.Exit(1)
    
    console.print(f"\n[bold]Analyzing skill: {skill.name}[/bold]\n")
    
    analyzer = OptimizationPotentialAnalyzer(skill)
    analysis = analyzer.analyze()
    
    # Display results
    table = Table(title="Optimization Potential Analysis")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Baseline Score", f"{analysis.baseline_score:.2%}")
    table.add_row("Estimated Ceiling", f"{analysis.estimated_ceiling:.2%}")
    table.add_row("Potential Improvement", f"{analysis.estimated_improvement:.1f}%")
    table.add_row("Score Variance", f"{analysis.variance:.4f}")
    table.add_row("Training Examples", str(analysis.sample_size))
    table.add_row("Recommended Strategy", analysis.recommended_strategy)
    
    console.print(table)
    
    if analysis.weakest_areas:
        console.print(f"\n[yellow]Weak areas:[/yellow] {', '.join(analysis.weakest_areas)}")
    
    console.print(Panel(analysis.recommendation, title="Recommendation"))


@app.command()
def optimize(
    skill_name: str = typer.Argument(..., help="Name of the skill to optimize"),
    strategy: str = typer.Option("auto", help="Optimization strategy (auto, bootstrap_fewshot, mipro_v2, gepa, simba, etc.)"),
    model: Optional[str] = typer.Option(None, help="Target model to optimize for"),
    skills_dir: str = typer.Option("skills", help="Directory containing skills"),
    output: Optional[str] = typer.Option(None, help="Output path for optimized skill")
):
    """Run optimization on a skill and save the result."""
    try:
        skill = Skill.load(skill_name, skills_dir)
    except FileNotFoundError:
        console.print(f"[red]Skill '{skill_name}' not found in {skills_dir}/[/red]")
        raise typer.Exit(1)
    
    console.print(f"\n[bold]Optimizing skill: {skill.name}[/bold]")
    console.print(f"Strategy: {strategy}")
    if model:
        console.print(f"Target model: {model}")
    
    optimizer = SkillOptimizer()
    
    with console.status("Running optimization..."):
        result = optimizer.optimize(skill, strategy=strategy, target_model=model)
    
    # Display comparison
    console.print("\n" + result.comparison.to_markdown_table())
    
    # Save optimized skill
    # Save optimized skill
    if output:
        output_path = Path(output)
    else:
        output_path = Path(skills_dir) / f"{skill_name}_optimized.md"
    
    # Use Markdown parser via Service or directly
    from app.pipeline.parsers import MarkdownSkillParser
    MarkdownSkillParser.save(result.optimized_skill, output_path)
    console.print(f"\n[green]Optimized skill saved to: {output_path}[/green]")


@app.command()
def compare(
    skill_a: str = typer.Argument(..., help="First skill name"),
    skill_b: str = typer.Argument(..., help="Second skill name"),
    skills_dir: str = typer.Option("skills", help="Directory containing skills"),
    output: Optional[str] = typer.Option(None, help="Output path for comparison report")
):
    """Compare two skill versions side-by-side."""
    try:
        skill_1 = Skill.load(skill_a, skills_dir)
        skill_2 = Skill.load(skill_b, skills_dir)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
    
    optimizer = SkillOptimizer()
    comparison = optimizer.compare(skill_1, skill_2)
    
    console.print("\n" + comparison.to_markdown_table())
    
    if output:
        Path(output).write_text(comparison.to_markdown_table())
        console.print(f"\n[green]Report saved to: {output}[/green]")


@app.command()
def create(
    name: str = typer.Argument(..., help="Name for the new skill"),
    description: str = typer.Option("", help="Skill description"),
    skills_dir: str = typer.Option("skills", help="Directory to create skill in")
):
    """Create a new skill template."""
    from app.services.skill_service import SkillService
    
    service = SkillService(skills_dir)
    skill, path = service.create_skill_template(name, description)
    
    console.print(f"[green]Created skill template at: {path}[/green]")
    console.print("  - SKILL.md: Skill definition (Markdown format)")
    console.print("  - TRAINING.json: Add training examples here (or use 'generate' command)")


@app.command()
def generate(
    skill_name: str = typer.Argument(..., help="Name of the skill"),
    count: int = typer.Option(5, help="Number of examples to generate"),
    skills_dir: str = typer.Option("skills", help="Directory containing skills"),
    output: Optional[str] = typer.Option(None, help="Path to save generated examples (default: TRAINING.json in skill dir)")
):
    """Generate synthetic training data for a skill using LLM."""
    try:
        skill = Skill.load(skill_name, skills_dir)
    except FileNotFoundError:
        console.print(f"[red]Skill '{skill_name}' not found in {skills_dir}/[/red]")
        raise typer.Exit(1)
        
    console.print(f"\n[bold]Generating {count} examples for: {skill.name}[/bold]")
    
    from app.pipeline.generator import TrainingDataGenerator
    generator = TrainingDataGenerator()
    
    with console.status("Generating examples..."):
        examples = generator.generate(skill, count=count)
    
    if not examples:
        console.print("[red]Failed to generate examples.[/red]")
        raise typer.Exit(1)
        
    # Convert back to json format for saving
    data = []
    for ex in examples:
        data.append({
            "input": ex.input,
            "expected_output": ex.expected_output,
            "reasoning": ex.reasoning
        })
        
    if output:
        out_path = Path(output)
    else:
        # Default to TRAINING.json in skill dir if structured, else alongside file
        if (Path(skills_dir) / skill_name).is_dir():
             out_path = Path(skills_dir) / skill_name / "TRAINING.json"
        else:
             out_path = Path(skills_dir) / f"{skill_name}_training.json"
             
    # If file exists, append or merge? For now, just save new set or warn
    if out_path.exists():
        console.print(f"[yellow]Warning: {out_path} already exists. Overwriting.[/yellow]")
        
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2))
    
    console.print(f"[green]Generated {len(examples)} examples saved to: {out_path}[/green]")


@app.command("export-knowledge")
def export_knowledge(
    skill_name: str = typer.Argument(..., help="Name of the skill to export"),
    format: str = typer.Option("json", help="Export format: json or markdown"),
    output: Optional[str] = typer.Option(None, help="Output path"),
    vector_db: str = typer.Option("lancedb", help="Vector DB for config snippet: lancedb, pgvector, qdrant"),
    skills_dir: str = typer.Option("skills", help="Directory containing skills")
):
    """Export skill examples to Agno Knowledge Base format for dynamic few-shot learning."""
    try:
        skill = Skill.load(skill_name, skills_dir)
    except FileNotFoundError:
        console.print(f"[red]Skill '{skill_name}' not found in {skills_dir}/[/red]")
        raise typer.Exit(1)
    
    if not skill.examples:
        console.print(f"[yellow]Warning: Skill has no examples to export. Run 'generate' first.[/yellow]")
        raise typer.Exit(1)
    
    from app.pipeline.knowledge_exporter import KnowledgeExporter, create_agno_knowledge_config
    
    exporter = KnowledgeExporter(skill)
    
    console.print(f"\n[bold]Exporting knowledge for: {skill.name}[/bold]")
    console.print(f"Examples: {len(skill.examples)}")
    
    if format == "json":
        out_path = Path(output) if output else None
        path = exporter.export_json(out_path)
        console.print(f"\n[green]✓ Exported to: {path}[/green]")
    elif format == "markdown":
        out_dir = Path(output) if output else None
        paths = exporter.export_documents(out_dir)
        console.print(f"\n[green]✓ Exported {len(paths)} documents to: {paths[0].parent}/[/green]")
    else:
        console.print(f"[red]Unknown format: {format}. Use 'json' or 'markdown'.[/red]")
        raise typer.Exit(1)
    
    # Show usage snippet
    console.print("\n[bold cyan]Agno Integration Code:[/bold cyan]")
    config_code = create_agno_knowledge_config(skill, vector_db=vector_db)
    console.print(Panel(config_code, title=f"Usage with {vector_db}", border_style="blue"))


def main():
    app()



if __name__ == "__main__":
    main()
