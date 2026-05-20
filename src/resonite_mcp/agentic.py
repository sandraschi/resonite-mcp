"""Resonite MCP Agentic Workflows — FastMCP 3.2+ ctx.sample() patterns.

Provides agentic planning and execution workflows that use LLM sampling
(ctx.sample()) to reason autonomously about Resonite tasks.

[RATIONALE] ctx.sample() enables the MCP server to make autonomous LLM
calls without requiring the client to orchestrate every step. This module
provides reusable agentic primitives.
"""

import json
import logging
from typing import Any

from fastmcp import Context

logger = logging.getLogger(__name__)


async def agentic_plan(
    ctx: Context,
    goal: str,
    available_tools: list[str] | None = None,
) -> str:
    """Use LLM sampling to plan a multi-step Resonite task.

    Calls the LLM via ctx.sample() to generate a step-by-step plan
    for achieving a given goal using the available MCP tools.

    Args:
        ctx: FastMCP Context with sampling capability
        goal: What the user wants to achieve
        available_tools: Optional list of tool names to constrain the plan

    Returns:
        The LLM-generated plan as a string
    """
    tools_hint = ""
    if available_tools:
        tools_hint = f"\nAvailable tools: {', '.join(available_tools)}"

    prompt = (
        f"You are a Resonite VR platform assistant. Create a step-by-step plan to:\n\n"
        f"GOAL: {goal}\n"
        f"{tools_hint}\n\n"
        f"Output a numbered plan with tool calls and expected outcomes."
    )

    result = await ctx.sample(
        messages=[
            {"role": "system", "content": "You are a precise VR automation planner."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1024,
    )

    plan = ""
    if hasattr(result, "content"):
        for block in result.content:
            if block.type == "text":
                plan += block.text
    elif isinstance(result, dict):
        plan = result.get("content", [{}])[0].get("text", str(result))
    else:
        plan = str(result)

    logger.info(f"Agentic plan generated for: {goal[:60]}...")
    return plan


async def agentic_execute(
    ctx: Context,
    plan: str,
    context_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute a plan using LLM reasoning and return structured results.

    Uses ctx.sample() to reason about the execution and determine
    the next appropriate tool calls.

    Args:
        ctx: FastMCP Context
        plan: The plan to execute (from agentic_plan)
        context_data: Optional runtime context (session state, etc.)

    Returns:
        Dict with execution results and status
    """
    context_str = json.dumps(context_data, indent=2) if context_data else "No additional context."

    prompt = (
        f"Execute the following plan for Resonite VR:\n\n{plan}\n\n"
        f"Current context:\n{context_str}\n\n"
        f"Determine the first tool call and provide the reason."
    )

    result = await ctx.sample(
        messages=[
            {"role": "system", "content": "You execute Resonite VR plans step by step."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=2048,
    )

    response_text = ""
    if hasattr(result, "content"):
        for block in result.content:
            if block.type == "text":
                response_text += block.text

    return {
        "success": True,
        "reasoning": response_text,
        "plan": plan,
    }


async def agentic_reason(
    ctx: Context,
    observation: str,
    question: str,
) -> str:
    """Use LLM sampling to reason about a Resonite state or error.

    Args:
        ctx: FastMCP Context
        observation: What was observed (sensor data, error message, etc.)
        question: What to reason about

    Returns:
        LLM reasoning response
    """
    prompt = (
        f"In Resonite VR:\n\n"
        f"Observation: {observation}\n"
        f"Question: {question}\n\n"
        f"Provide analysis and recommended actions."
    )

    result = await ctx.sample(
        messages=[
            {"role": "system", "content": "You diagnose and solve Resonite VR issues."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1024,
    )

    reasoning = ""
    if hasattr(result, "content"):
        for block in result.content:
            if block.type == "text":
                reasoning += block.text
    return reasoning or str(result)
