---
id: prompt-template-v1
title: Prompt Template
summary: A template for creating new prompts.
model: generic
owner: system
version: v1
last_updated: 2025-11-23
tags: [template, example]
variables:
  - name: topic
    description: The topic of the prompt.
    required: true
safety:
  constraints:
    - no harmful content
  escalation:
    - none
---

## Usage
- When to use: When creating a new prompt file.
- Invocation notes: Copy this file and fill in the details.
- Expected outputs: A valid prompt file.

## Prompt
Write a prompt about {{topic}}.

## Examples
- Input: topic="coding" → Output: A coding prompt.
