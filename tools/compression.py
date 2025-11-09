"""
Context compression tool for managing conversation history.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any
from .project import get_active_project_folder


def compress_context_impl(
    messages: List[Any],
    client,
    model: str,
    keep_recent: int = 10
) -> Dict[str, Any]:
    """
    Compresses the conversation context by summarizing older messages.
    
    This function:
    1. Takes all messages except the most recent ones
    2. Calls the kimi API to create a comprehensive summary
    3. Saves the summary to a timestamped file
    4. Returns the compressed messages list and stats
    
    Args:
        messages: The full message history
        client: The OpenAI client instance
        model: The model to use for summarization
        keep_recent: Number of recent messages to keep uncompressed
        
    Returns:
        Dictionary containing:
        - compressed_messages: New message list with compression applied
        - summary_file: Path to saved summary file
        - tokens_before: Estimated tokens before compression
        - tokens_after: Estimated tokens after compression
    """
    if len(messages) <= keep_recent + 1:  # +1 for system message
        return {
            "compressed_messages": messages,
            "summary_file": None,
            "tokens_saved": 0,
            "message": "Not enough messages to compress."
        }
    
    # Separate system message, messages to compress, and recent messages
    system_message = messages[0] if messages and messages[0].get("role") == "system" else None
    
    if system_message:
        messages_to_compress = messages[1:-keep_recent]
        recent_messages = messages[-keep_recent:]
    else:
        messages_to_compress = messages[:-keep_recent]
        recent_messages = messages[-keep_recent:]
    
    # Create a detailed prompt for summarization
    summary_prompt = """You are summarizing a novel-writing session. Create a DETAILED summary that will allow the writing to continue seamlessly with perfect continuity. Include:

1. User's Original Request:
   - Preserve the COMPLETE original prompt/creative direction
   - Novel type, setting, characters, plot outline provided by the user
   - Any specific tone, style, or structural requirements requested

2. Novel Structure:
   - Total planned chapters and current progress (X of Y chapters completed)
   - Overall story arc stage

3. Chapters Written (detail each):
   - Chapter number and summary of key events
   - Character developments and revelations
   - Plot threads introduced or resolved
   - Any transitions or connections to next chapter

4. Narrative State (CRITICAL for continuity):
   - Character states: Where each character is, what they know, their emotional state
   - Active plot threads: Unresolved conflicts, mysteries, ongoing goals
   - World details established: Locations, rules, objects, relationships
   - Timeline: Current point in story

5. Files Created:
   - List all files written and their purposes

6. Next Steps:
   - Which chapter to write next
   - Plot points that need to be addressed

Format this as a reference document for seamless story continuation. Prioritize narrative continuity - include ALL details needed to maintain consistency.

Conversation history to summarize:
"""
    
    # Build the conversation text
    conversation_text = ""
    for msg in messages_to_compress:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        
        # Handle different message types
        if role == "assistant":
            # Check for reasoning_content
            if hasattr(msg, "reasoning_content"):
                reasoning = getattr(msg, "reasoning_content")
                if reasoning:
                    conversation_text += f"\n[Assistant Reasoning]: {reasoning[:500]}...\n"
            
            # Check for tool calls
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                tool_calls_info = []
                for tc in msg.tool_calls:
                    func_name = tc.function.name
                    args = tc.function.arguments
                    tool_calls_info.append(f"{func_name}({args})")
                conversation_text += f"\n[Assistant Tool Calls]: {', '.join(tool_calls_info)}\n"
            
            if content:
                conversation_text += f"\n[Assistant]: {content}\n"
        
        elif role == "tool":
            tool_name = msg.get("name", "unknown_tool")
            conversation_text += f"\n[Tool Result - {tool_name}]: {content[:200]}...\n"
        
        elif role == "user":
            conversation_text += f"\n[User]: {content}\n"
    
    # Call the API to get summary
    try:
        summary_response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a specialized summarization assistant for novel-writing projects. Your summaries must preserve ALL narrative details, character information, plot threads, and world-building elements necessary for seamless story continuation. Prioritize continuity over brevity."},
                {"role": "user", "content": summary_prompt + conversation_text}
            ],
            temperature=0.7,
            max_tokens=4096
        )
        
        summary = summary_response.choices[0].message.content
        
    except Exception as e:
        return {
            "compressed_messages": messages,
            "summary_file": None,
            "tokens_saved": 0,
            "message": f"Error during compression: {str(e)}"
        }
    
    # Save summary to file
    project_folder = get_active_project_folder()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if project_folder:
        summary_file = os.path.join(project_folder, f".context_summary_{timestamp}.md")
    else:
        # If no project folder, save in current directory
        summary_file = f".context_summary_{timestamp}.md"
    
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# Context Summary\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Messages Compressed:** {len(messages_to_compress)}\n\n")
            f.write(f"**Messages Retained:** {keep_recent}\n\n")
            f.write(f"---\n\n")
            f.write(summary)
    except Exception as e:
        summary_file = f"Error saving summary: {str(e)}"
    
    # Build the compressed message list
    compressed_messages = []
    
    # Add system message if it exists
    if system_message:
        compressed_messages.append(system_message)
    
    # Add the summary as a user message
    compressed_messages.append({
        "role": "user",
        "content": f"[CONTEXT SUMMARY - Previous conversation compressed]\n\n{summary}\n\n[END CONTEXT SUMMARY - Continuing from here...]"
    })
    
    # Add recent messages
    compressed_messages.extend(recent_messages)
    
    # Calculate token savings (rough estimate)
    original_length = sum(len(str(m)) for m in messages_to_compress)
    compressed_length = len(summary)
    estimated_tokens_saved = (original_length - compressed_length) // 4  # Rough estimate
    
    return {
        "compressed_messages": compressed_messages,
        "summary_file": summary_file,
        "tokens_saved": estimated_tokens_saved,
        "messages_compressed": len(messages_to_compress),
        "messages_retained": keep_recent,
        "message": f"Successfully compressed {len(messages_to_compress)} messages. Summary saved to {os.path.basename(summary_file)}."
    }

