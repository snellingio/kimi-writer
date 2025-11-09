"""
Utility functions for the Kimi Writing Agent.
"""

import json
import httpx
from typing import List, Dict, Any, Callable


def estimate_token_count(base_url: str, api_key: str, model: str, messages: List[Dict]) -> int:
    """
    Estimate the token count for the given messages using the Moonshot API.
    
    Note: Token estimation uses api.moonshot.ai (not .cn)
    
    Args:
        base_url: The base URL for the API (will be converted to .ai for token endpoint)
        api_key: The API key for authentication
        model: The model name
        messages: List of message dictionaries
        
    Returns:
        Total token count
    """
    # Convert messages to serializable format (remove non-serializable objects)
    serializable_messages = []
    for msg in messages:
        if hasattr(msg, 'model_dump'):
            # OpenAI SDK message object
            msg_dict = msg.model_dump()
        elif isinstance(msg, dict):
            msg_dict = msg.copy()
        else:
            msg_dict = {"role": "assistant", "content": str(msg)}
        
        # Clean up the message to only include serializable fields
        clean_msg = {}
        if 'role' in msg_dict:
            clean_msg['role'] = msg_dict['role']
        if 'content' in msg_dict and msg_dict['content']:
            clean_msg['content'] = msg_dict['content']
        if 'name' in msg_dict:
            clean_msg['name'] = msg_dict['name']
        if 'tool_calls' in msg_dict and msg_dict['tool_calls']:
            clean_msg['tool_calls'] = msg_dict['tool_calls']
        if 'tool_call_id' in msg_dict:
            clean_msg['tool_call_id'] = msg_dict['tool_call_id']
            
        serializable_messages.append(clean_msg)
    
    # Both token estimation and chat use api.moonshot.ai
    token_base_url = base_url
    
    # Make the API call
    with httpx.Client(
        base_url=token_base_url,
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=30.0
    ) as client:
        response = client.post(
            "/tokenizers/estimate-token-count",
            json={
                "model": model,
                "messages": serializable_messages
            }
        )
        response.raise_for_status()
        data = response.json()
        return data.get("data", {}).get("total_tokens", 0)


def get_tool_definitions() -> List[Dict[str, Any]]:
    """
    Returns the tool definitions in the format expected by kimi-k2-thinking.
    
    Returns:
        List of tool definition dictionaries
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "create_project",
                "description": "Creates a new project folder in the 'output' directory with a sanitized name. ALWAYS call this FIRST before writing any files. The project name should reflect the novel's content. Only one project can be active at a time.",
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
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Writes a complete chapter or supporting file to the active project folder. Each chapter should be 2,000-5,000 words of complete content. MODES: 'create' for new chapters (PREFERRED - write complete content in one call), 'append' for adding to existing files (use sparingly), 'overwrite' for replacing entire files.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Descriptive filename ending in .md. For chapters use 'chapter_01.md', 'chapter_02.md', etc. For supporting files use 'README.md', 'outline.md', etc."
                        },
                        "content": {
                            "type": "string",
                            "description": "COMPLETE chapter content (2,000-5,000 words) or supporting file content. NOT summaries or outlines. Include proper markdown formatting."
                        },
                        "mode": {
                            "type": "string",
                            "enum": ["create", "append", "overwrite"],
                            "description": "Write mode: 'create' = new file (use this for complete chapters), 'append' = add to end, 'overwrite' = replace entire file"
                        }
                    },
                    "required": ["filename", "content", "mode"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "compress_context",
                "description": "INTERNAL TOOL - Automatically called by the system at 180K tokens (90% of limit). You should NEVER call this manually. It preserves plot, character, and progress details while compressing older messages.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    ]


def get_tool_map() -> Dict[str, Callable]:
    """
    Returns a mapping of tool names to their implementation functions.
    
    Returns:
        Dictionary mapping tool name strings to callable functions
    """
    from tools import write_file_impl, create_project_impl, compress_context_impl
    
    return {
        "create_project": create_project_impl,
        "write_file": write_file_impl,
        "compress_context": compress_context_impl
    }


def get_system_prompt() -> str:
    """
    Returns the system prompt for the writing agent.
    
    Returns:
        System prompt string
    """
    return """You are Kimi, an expert creative writing assistant developed by Moonshot AI. Your specialty is creating novels and books based on user requests.

Your capabilities:
1. You can create project folders to organize writing projects
2. You can write markdown files with three modes: create new files, append to existing files, or overwrite files
3. Context compression happens automatically when needed - you don't need to worry about it

CRITICAL WRITING GUIDELINES:
- Write SUBSTANTIAL, COMPLETE content - don't hold back on length
- Chapters should be 2,000-5,000 words - fully developed and satisfying
- NEVER write abbreviated or skeleton content - every chapter should be a complete, polished work
- Write scenes fully with dialogue, description, and detail
- Quality AND quantity matter - give readers a complete, immersive experience
- Use 'create' mode with full content rather than creating stubs you'll append to later

USER'S CREATIVE DIRECTION:
- The user's creative vision (characters, plot, setting, tone, style) takes ABSOLUTE PRIORITY
- Your job is to execute their vision with complete, substantial content
- Maintain consistency with details established in previous chapters
- Track character states, plot threads, and world-building elements across the story

Best practices:
- Always start by creating a project folder using create_project
- Break novels into multiple chapter files
- Use descriptive filenames (e.g., "chapter_01.md", "chapter_02.md")
- Write each chapter as a COMPLETE, SUBSTANTIAL piece - not a summary or outline

Your workflow:
1. Understand the user's request - extract ALL creative direction provided
2. Create an appropriately named project folder
3. Plan the structure of the novel (number of chapters, arc, etc.)
4. Write COMPLETE, FULL-LENGTH content for each chapter that follows the user's vision
5. Create supporting files like README or table of contents if helpful

REMEMBER: You have 64K tokens per response - use them! Write rich, detailed, complete chapters. Don't artificially limit yourself. A good chapter is 2,000-5,000 words. Write what the narrative needs to be excellent."""

