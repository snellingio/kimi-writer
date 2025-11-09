# Compression Prompt Improvements

## 3. Context Compression Prompt (tools/compression.py:59-67)

### Current Prompt:
```python
summary_prompt = """Please provide a comprehensive summary of the conversation history below. Include:
1. The main task or goal discussed
2. Key decisions made
3. Files created and their purposes
4. Progress made so far
5. Any important context for continuing the work

Conversation history to summarize:
"""
```

### Current Issues:
1. Doesn't specifically mention **narrative elements** (plot, characters, conflicts)
2. Missing **chapter-by-chapter tracking**
3. No emphasis on **maintaining continuity** (character states, plot threads, world details)
4. Doesn't preserve **user's original creative direction**
5. Too generic - works for any task, not optimized for novel writing

### Improved Compression Prompt:

```python
summary_prompt = """You are summarizing a novel-writing session. Create a DETAILED summary that will allow the writing to continue seamlessly. Include:

## 1. User's Original Request:
- Extract and preserve the COMPLETE original prompt/creative direction
- Novel type, setting, time period, tone, themes
- ALL specified characters (names, roles, traits, relationships)
- Plot outline or story beats provided by the user

## 2. Novel Structure:
- Total planned chapters
- Current progress (X of Y chapters completed)
- Story arc stage (setup, rising action, climax, etc.)

## 3. Chapters Written (detail each):
- Chapter number and title/summary
- Key events that occurred
- Character developments/revelations
- Plot threads introduced or resolved
- Cliffhanger or transition to next chapter

## 4. Narrative State (CRITICAL for continuity):
- Character states: Where each character is, what they know, their emotional state
- Active plot threads: Unresolved conflicts, mysteries, goals
- World details established: Locations described, rules explained, objects introduced
- Timeline: Current point in story timeline

## 5. Writing Patterns & Style:
- POV (first person, third limited, omniscient)
- Tense (past, present)
- Tone and atmosphere maintained
- Any recurring motifs or phrases

## 6. Next Steps:
- Which chapter to write next
- Plot points to address
- Character arcs to develop
- Loose ends to tie up

Format this as a reference document that would allow another AI (or yourself) to continue writing the novel with PERFECT continuity. Err on the side of including TOO MUCH detail rather than too little.

Conversation history to summarize:
"""
```

### Key Improvements:

1. **Novel-Specific Focus**: Tailored entirely for fiction writing, not generic tasks
2. **Narrative Continuity**: Explicitly tracks character states, plot threads, world details
3. **User Intent Preservation**: Section dedicated to preserving original creative direction
4. **Chapter-by-Chapter Detail**: Structured tracking of each completed chapter
5. **Style Consistency**: Tracks POV, tense, tone for consistent voice
6. **Continuity Emphasis**: "PERFECT continuity" and "TOO MUCH detail" instructions
7. **Next Steps Planning**: Helps agent pick up exactly where it left off

### Additional Improvement: Compression System Prompt

Currently (line 107):
```python
{"role": "system", "content": "You are a helpful assistant that creates comprehensive summaries of conversations."}
```

**Improved:**
```python
{"role": "system", "content": "You are a specialized summarization assistant for novel-writing projects. Your summaries must preserve ALL narrative details, character information, plot threads, and world-building elements necessary for seamless story continuation. Prioritize continuity over brevity."}
```

This change makes the compression agent understand it's working with creative fiction that requires perfect continuity, not just general task summaries.
