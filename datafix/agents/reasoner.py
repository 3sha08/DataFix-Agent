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