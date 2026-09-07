"""Parsers for different skill formats."""

import frontmatter
from pathlib import Path
from typing import Optional, Any
from app.models.skill import Skill

class MarkdownSkillParser:
    """Parses SKILL.md format (Agent Skills standard)."""
    
    @staticmethod
    def parse(path: Path) -> Skill:
        """
        Parse a SKILL.md file into a Skill object.
        
        Args:
            path: Path to the .md file
            
        Returns:
            Skill object populated from frontmatter and markdown body
        """
        post = frontmatter.load(path)
        metadata = post.metadata
        content = post.content
        
        # Extract required fields from frontmatter
        name = metadata.get("name")
        description = metadata.get("description")
        
        if not name or not description:
            raise ValueError(f"Missing required frontmatter fields (name, description) in {path}")
            
        # Extract optional metadata
        version = metadata.get("version", "1.0.0")
        author = metadata.get("author")
        if not author and "metadata" in metadata:
             author = metadata["metadata"].get("author")
        
        # Parse body for instructions and potentially schemas/examples if embedded
        # For now, we treat the entire body as instructions
        instructions = content.strip()
        
        return Skill(
            name=name,
            description=description,
            instructions=instructions,
            version=str(version),
            author=author,
            # Note: Schemas and examples might need to be inferred or looked up 
            # from separate files if adhering strictly to a specific convention alongside SKILL.md
            # For this MVP, we initialize them empty, to be populated by the TrainingDataGenerator
            input_schema={},
            output_schema={},
            examples=[] 
        )

    @staticmethod
    def save(skill: Skill, path: Path) -> None:
        """Save a Skill object to SKILL.md format."""
        
        metadata = {
            "name": skill.name,
            "description": skill.description,
            "version": skill.version,
        }
        
        if skill.author:
            metadata["metadata"] = {"author": skill.author}
            
        # Convert to frontmatter post
        post = frontmatter.Post(skill.instructions, **metadata)
        
        path.parent.mkdir(parents=True, exist_ok=True)
        # with open(path, "wb") as f:
        with open(path, "w", encoding="utf-8") as f:
            frontmatter.dump(post, f)

