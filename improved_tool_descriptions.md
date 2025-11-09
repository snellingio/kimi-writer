# Tool Description Improvements

## 2. Tool Descriptions (utils.py:79-135)

### Current Issues:
1. **write_file** description doesn't emphasize chapter completion
2. No guidance on when to use 'append' vs 'create'
3. Missing context about maintaining narrative flow

### Improved Tool Descriptions:

#### create_project (Currently adequate, minor improvement):
```python
{
    "name": "create_project",
    "description": "Creates a new project folder in the 'output' directory. ALWAYS call this FIRST before writing any files. The project name should reflect the novel's content (e.g., 'mystery_in_london', 'sci_fi_memory_wars'). Only one project can be active at a time.",
    "parameters": {
        "type": "object",
        "properties": {
            "project_name": {
                "type": "string",
                "description": "Descriptive name for the novel project (will be sanitized for filesystem compatibility)"
            }
        },
        "required": ["project_name"]
    }
}
```

**Improvements:**
- Added "ALWAYS call this FIRST" for clarity
- Provided examples of good project names
- Emphasized descriptiveness

---

#### write_file (Needs significant improvement):
```python
{
    "name": "write_file",
    "description": "Writes a complete chapter or supporting file to the active project. Each chapter should be 2,500-3,500 words of publication-quality prose, fully written with scenes, dialogue, and description. MODES: 'create' for new chapters (PREFERRED - write complete content in one call), 'append' for adding to existing files (use sparingly, only for corrections), 'overwrite' for replacing entire files.",
    "parameters": {
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": "Descriptive filename ending in .md. For chapters use 'chapter_01.md', 'chapter_02.md', etc. For supporting files use 'README.md', 'character_guide.md', 'outline.md'"
            },
            "content": {
                "type": "string",
                "description": "COMPLETE chapter content (2,500-3,500 words) with full scenes, dialogue, and narrative. NOT summaries or outlines. Include proper markdown formatting for readability."
            },
            "mode": {
                "type": "string",
                "enum": ["create", "append", "overwrite"],
                "description": "Write mode: 'create' = new file (use this for complete chapters), 'append' = add to end (use for corrections only), 'overwrite' = replace entire file"
            }
        },
        "required": ["filename", "content", "mode"]
    }
}
```

**Improvements:**
- Emphasizes "complete chapter" and word count in the description
- Explicitly states "PREFERRED" for 'create' mode
- Clarifies when to use 'append' (corrections only)
- Adds guidance on filename conventions
- Reminds about markdown formatting

---

#### compress_context (Currently adequate):
```python
{
    "name": "compress_context",
    "description": "INTERNAL TOOL - Automatically called by the system at 180K tokens (90% of limit). You should NEVER call this manually. It preserves plot, character, and progress details while compressing older messages.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}
```

**Improvements:**
- Added context about when it triggers (180K tokens)
- Mentions what it preserves (plot, character, progress)
- Stronger "NEVER call this manually" language
