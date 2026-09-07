"""Automated training data generator using LLM."""

import dspy
from typing import List, Any
from app.models.skill import Skill, Example
import json

class TrainingDataSignature(dspy.Signature):
    """Generate diverse training examples for a given skill."""
    
    skill_name = dspy.InputField(desc="Name of the skill")
    skill_description = dspy.InputField(desc="Description of the skill's purpose")
    skill_instructions = dspy.InputField(desc="The instructions for the skill")
    input_schema = dspy.InputField(desc="JSON schema for the input")
    output_schema = dspy.InputField(desc="JSON schema for the output")
    num_examples = dspy.InputField(desc="Number of examples to generate")
    
    examples = dspy.OutputField(desc="List of examples in JSON format. Each example must have 'input' and 'expected_output' fields.")

class TrainingDataGenerator:
    """
    Generates synthetic training data for skills using an LLM.
    
    This automates the "manual" step of creating examples for DSPy optimization.
    """
    
    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        self.generator = dspy.ChainOfThought(TrainingDataSignature)

    
    def _normalize_data(self, data: Any, key_name: str = "value") -> dict:
        """Ensure data is a dictionary."""
        if isinstance(data, dict):
            return data
        return {key_name: data}

    def generate(self, skill: Skill, count: int = 5) -> List[Example]:
        """
        Generate training examples for a skill.
        
        Args:
            skill: The skill to generate data for
            count: Number of examples to generate
            
        Returns:
            List of generated Example objects
        """
        
        # Format schemas for prompt
        input_schema_str = json.dumps(skill.input_schema, indent=2) if skill.input_schema else "Any text input"
        output_schema_str = json.dumps(skill.output_schema, indent=2) if skill.output_schema else "Any text output"
        
        try:
            prediction = self.generator(
                skill_name=skill.name,
                skill_description=skill.description,
                skill_instructions=skill.instructions,
                input_schema=input_schema_str,
                output_schema=output_schema_str,
                num_examples=str(count)
            )
            
            # Parse the output
            # DSPy might return a string or list depending on the output field handling
            # We expect a JSON string or list of dicts.
            
            raw_examples = prediction.examples
            if isinstance(raw_examples, str):
                # valid json?
                # remove markdown code blocks if present
                clean_json = (
                    raw_examples.replace("```json", "")
                    .replace("```", "")
                    .replace(r"\.", r"\\.")
                    .strip()
                )
                try:
                    data = json.loads(clean_json)
                except json.JSONDecodeError as e:
                    print(f"Failed to decode JSON: {clean_json[:100]}...")
                    print(f"Error: {e}")
                    return []
            else:
                data = raw_examples

            examples = []
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict) and "examples" in data:
                 items = data["examples"]
            else:
                items = []

            for item in items:
                input_data = self._normalize_data(item.get("input", {}), "input")
                output_data = self._normalize_data(item.get("expected_output", {}), "output")
                
                examples.append(Example(
                    input=input_data,
                    expected_output=output_data,
                    reasoning=item.get("reasoning")
                ))
            
            return examples

        except Exception as e:
            print(f"Error generating training data: {e}")
            return []
