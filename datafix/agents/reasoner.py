from __future__ import annotations

import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


def get_openai_client() -> OpenAI:
    """Create an OpenAI client using the local environment variable."""

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured. Add it to the local .env file."
        )

    return OpenAI(api_key=api_key)

def test_llm_connection() -> str:
    """Make a minimal API call to verify the LLM connection."""

    client = get_openai_client()

    response = client.responses.create(
        model="gpt-5-mini",
        input=(
            "Reply with exactly this text and nothing else: "
            "DataFix AI connection successful"
        ),
    )

    return response.output_text.strip()

def build_reasoning_prompt(
    profile: dict,
    issues: list[dict],
    plan: list[dict],
) -> str:
    """Build a grounded prompt from deterministic DataFix findings."""

    return f"""
You are the reasoning component of DataFix Agent, a data-quality remediation system.

Your job is to interpret deterministic findings produced by DataFix tools.
Do not invent issues, statistics, columns, or remediation actions.

DATASET PROFILE:
{profile}

DETECTED QUALITY ISSUES:
{issues}

PROPOSED REMEDIATION PLAN:
{plan}

Provide a concise assessment that:
1. Summarizes the dataset's main quality risks.
2. Prioritizes the most important issues.
3. Explains why the proposed remediation actions are appropriate.
4. Identifies actions that deserve extra human caution.
5. Never claims that an action has been executed or approved.

Keep the response under 250 words.
""".strip()

def generate_reasoning(
    profile: dict,
    issues: list[dict],
    plan: list[dict],
) -> str:
    """Generate an LLM assessment grounded in deterministic findings."""

    client = get_openai_client()

    prompt = build_reasoning_prompt(
        profile,
        issues,
        plan,
    )

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt,
    )

    return response.output_text.strip()