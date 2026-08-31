

# 🚀 Skill Optimizer

A powerful framework for optimizing AI agent skills (prompts, tools, configurations) using **DSPy** optimization algorithms and **Agno** agents.

Transform underperforming prompts into high-quality, production-ready skills with data-driven optimization.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Skill Analysis** | Evaluate skills before optimization to understand improvement potential |
| **Multiple Strategies** | BootstrapFewShot, MIPROv2, BootstrapRS optimizers |
| **Auto-Training Data** | Generate synthetic training examples using LLMs |
| **Side-by-Side Comparison** | Compare original vs optimized skills with detailed metrics |
| **Flexible Formats** | Support for YAML and Markdown skill definitions |
| **CLI & Programmatic API** | Use via command line or integrate into your Python code |

---

## 📦 Installation

### Prerequisites

- Python 3.13+
- [`uv`](https://docs.astral.sh/uv/) package manager

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Ash-Blanc/skill-optimizer.git
cd skill-optimizer

# Install as a CLI tool (recommended)
uv tool install .

# Set up environment variables
cp .env.example .env
# Add your OPENAI_API_KEY, MISTRAL_API_KEY, or GEMINI_API_KEY
```

After installation, the `skill-optimizer` command is available globally:

```bash
skill-optimizer --help
```

> **Note**: If you prefer not to install globally, you can use `uv run skill-optimizer` instead.

---

## 🎯 Quick Usage

### CLI Commands

```bash
# Analyze a skill's optimization potential
skill-optimizer analyze email_summarizer

# Generate training data for a skill
skill-optimizer generate email_summarizer --count 10

# Optimize a skill
skill-optimizer optimize email_summarizer --strategy bootstrap_fewshot

# Compare two skill versions
skill-optimizer compare email_summarizer email_summarizer_optimized

# Create a new skill template (Creates skills/my_new_skill/SKILL.md)
skill-optimizer create my_new_skill

# Generate synthetic training data (saves to skills/my_new_skill/TRAINING.json)
skill-optimizer generate my_new_skill --count 10

# Optimize skill (automatically selects best strategy)
skill-optimizer optimize my_new_skill
```

### 🛠️ Common Commands

**Generate Training Data**:
If you don't have enough examples, generate them using an LLM (requires an API key):

```bash
# Generate 10 examples and save to the default TRAINING.json
skill-optimizer generate email_summarizer --count 10

# Save to a specific file (useful for creating validation sets)
skill-optimizer generate email_summarizer --count 20 --output validation_set.json
```

### ✨ Agno Integration

**Dynamic Few-Shot Learning**:
Export optimized skills to Agno Knowledge Base to let your agents retrieve relevant examples at runtime:

```bash
skill-optimizer export-knowledge email_summarizer --vector-db lancedb
```

This generates a code snippet you can paste directly into your Agno agent application.

**Enhanced Agent**:
The included `SkillOptimizerAgent` now supports:
- **Persistent Memory**: Remembers conversation context across sessions (SQLite backend).
- **Structured Output**: Returns analysis results as Pydantic models.
- **Reasoning**: Uses Chain-of-Thought for complex optimization tasks.

### 🚀 Advanced Optimizers

Now supports state-of-the-art DSPy strategies:
- **Auto-Optimizer**: Automatically selects the best strategy (`auto`).
- **GEPA** (Grounded Explanation-based Prompt Alignment): Uses explanations to improve prompts.
- **MIPROv2**: Jointly optimizes instructions and examples using a metric.
- **SIMBA**: Signature-Based Multi-step Bootstrapping for complex reasoning.
- **BetterTogether**: Combines multiple strategies for best results.
- **KNNFewShot**: Selects examples based on semantic similarity.
- **COPRO**: Contrastive Prompt Optimization.



### Example Output

```
$ skill-optimizer analyze email_summarizer

┌────────────────────────────────────────┐
│ Optimization Potential Analysis        │
├────────────────────┬───────────────────┤
│ Metric             │ Value             │
├────────────────────┼───────────────────┤
│ Baseline Score     │ 72.50%            │
│ Estimated Ceiling  │ 89.00%            │
│ Potential Improve  │ 22.8%             │
│ Recommended        │ bootstrap_fewshot │
└────────────────────┴───────────────────┘

Recommendation: Good candidate for optimization. 
BootstrapFewShot should yield 10-20% improvement.
```

---

## 📖 Python API Usage

### Basic Optimization Flow

```python
from app import Skill, SkillService, create_skill_optimizer_agent

# Load a skill
service = SkillService(skills_dir="skills")
skill = service.load("email_summarizer")

# Analyze before optimizing
from app.pipeline import OptimizationPotentialAnalyzer

analyzer = OptimizationPotentialAnalyzer(skill)
analysis = analyzer.analyze()
print(f"Baseline: {analysis.baseline_score:.2%}")
print(f"Potential improvement: {analysis.estimated_improvement:.1f}%")

# Optimize the skill
from app.pipeline import SkillOptimizer

optimizer = SkillOptimizer()
result = optimizer.optimize(skill, strategy="bootstrap_fewshot")

# Save the optimized skill
service.save_optimized(result.optimized_skill)
print(result.comparison.to_markdown_table())
```

### Using the Agent

```python
from app import create_skill_optimizer_agent

# Create the optimizer agent
agent = create_skill_optimizer_agent(skills_dir="skills")

# Ask the agent to optimize a skill
response = agent.run("Analyze the email_summarizer skill and tell me if it's worth optimizing")
print(response.content)

# Or interactively
agent.print_response("Optimize the text_classifier skill using MIPROv2", stream=True)
```

### Generate Training Data

```python
from app import Skill, SkillService
from app.pipeline import TrainingDataGenerator

service = SkillService()
skill = service.load("email_summarizer")

generator = TrainingDataGenerator()
examples = generator.generate(skill, count=10)

# Save the training data
service.save_training_data("email_summarizer", examples)
```

---

## 📂 Project Structure

```
skill-optimizer/
├── app/
│   ├── agent.py          # Agno agent with optimization tools
│   ├── cli.py            # Command-line interface
│   ├── models/           # Pydantic models (Skill, Example, Metrics)
│   ├── pipeline/         # Core optimization logic
│   │   ├── analyzer.py   # Pre-optimization analysis
│   │   ├── evaluator.py  # Baseline evaluation
│   │   ├── generator.py  # Training data generation
│   │   └── optimizer.py  # DSPy optimization engine
│   └── services/         # Centralized skill management
├── skills/               # Skill definitions
│   ├── email_summarizer/
│   │   ├── SKILL.md      # Skill definition
│   │   └── TRAINING.json # Training examples
│   └── text_classifier/
│       └── SKILL.md      # Markdown format skill
├── prompts/              # LangWatch prompts
├── tests/                # Test suite
└── .env                  # API keys (not committed)
```

---

## 📝 Defining Skills

Skills can be defined in **YAML** or **Markdown** format.

### YAML Format (Recommended)

```yaml
# skills/my_skill/SKILL.md
name: my_skill
description: What this skill does
instructions: |
  Detailed instructions for the LLM.
  Be specific about the task and expected output format.

input_schema:
  type: object
  properties:
    input_text:
      type: string
      description: The text to process

output_schema:
  type: object
  properties:
    result:
      type: string
      description: The processed result

examples:
  - input:
      input_text: "Hello world"
    expected_output:
      result: "Processed: Hello world"

version: "1.0.0"
tags: [example, demo]
```

### Markdown Format

```markdown
---
name: my-skill
description: What this skill does
version: "1.0"
---

# Instructions

Your detailed instructions here.
The body of the markdown becomes the instructions.
```

---

## ⚙️ Optimization Strategies

| Strategy | Best For | Description |
|----------|----------|-------------|
| `bootstrap_fewshot` | Most cases | Selects optimal few-shot examples from your training data |
| `mipro_v2` | Low baseline | Optimizes both instructions AND examples simultaneously |
| `bootstrap_rs` | Large datasets | Random search with bootstrapping for best example selection |

### Choosing a Strategy

```bash
# Default: BootstrapFewShot (recommended starting point)
skill-optimizer optimize my_skill

# For skills with poor instructions
skill-optimizer optimize my_skill --strategy mipro_v2

# For skills with many training examples
skill-optimizer optimize my_skill --strategy bootstrap_rs
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file with your API keys:

```bash
# Required: At least one LLM provider
OPENAI_API_KEY=sk-...
MISTRAL_API_KEY=...
GEMINI_API_KEY=...

# Optional: Specify default model for DSPy
DSPY_MODEL=openai/gpt-4o-mini
```

### Model Priority

The optimizer automatically selects a model in this order:
1. `DSPY_MODEL` environment variable (if set)
2. Mistral (if `MISTRAL_API_KEY` present) ← **Primary**
3. OpenAI (if `OPENAI_API_KEY` present)
4. Gemini (if `GEMINI_API_KEY` present)

---

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/scenarios/test_optimizer.py -v
```

---

## 📚 Development Guide

See [AGENTS.md](AGENTS.md) for detailed development guidelines, including:
- Scenario testing best practices
- Prompt management with LangWatch
- Agno framework patterns
- Project contribution workflow

---

## 🔗 Resources

- [DSPy Documentation](https://dspy-docs.vercel.app/)
- [Agno Documentation](https://docs.agno.com/)
- [LangWatch Platform](https://app.langwatch.ai/)

---

## License

MIT License - See [LICENSE](LICENSE) for details.
