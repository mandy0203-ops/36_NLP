---
id: prompt-<domain>-<intent>-v1
title: <Concise title>
summary: <purpose and when to use>
model: <openai:gpt-4o|anthropic:claude-3.5|google:gemini-1.5|generic>
owner: <user|agent|team>
version: v1
last_updated: YYYY-MM-DD
tags: [<domain>, <intent>, <safety>]
variables:
  - name: <var_name>
    description: <what it is>
    required: true|false
safety:
  constraints:
    - <e.g., no PII, no destructive ops>
  escalation:
    - <when to ask the user for confirmation>
---

## Usage
- When to use: <guidance>
- Invocation notes: <model quirks, rate limits>
- Expected outputs: <format, quality bar, target path under 03-outputs/<tool>/>

## Prompt
<Write the prompt body here. Use {{variables}} for substitutions.>

## Examples
- Input: <…> → Output: <…>

## Change-log
- v1 (YYYY-MM-DD): Initial version.
