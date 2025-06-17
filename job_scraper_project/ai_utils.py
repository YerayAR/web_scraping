"""Utility functions that leverage the OpenAI API to interpret and refine scraped data.

This module centralises calls to the OpenAI Chat Completion API.  The helper
functions are optional; the scrapers can still run without API access but when an
``OPENAI_API_KEY`` is configured, these utilities can assist with analysing raw
text, classifying content and translating or normalising information.
"""

from __future__ import annotations

import os
from typing import Dict, Optional

try:
    import openai
except Exception:
    openai = None  # ``openai`` package is optional


# Retrieve API key from environment variable.  In a real deployment this could
# be loaded from a more secure location.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if openai and OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY


def _call_openai(prompt: str, *, temperature: float = 0) -> str:
    """Internal helper to send a prompt to the Chat Completion API.

    Parameters
    ----------
    prompt : str
        Prompt text sent to the model.
    temperature : float, optional
        Sampling temperature for the model (defaults to 0 for deterministic
        output).
    """
    if not openai or not OPENAI_API_KEY:
        raise RuntimeError(
            "OpenAI package not installed or API key not provided; install the"
            " `openai` package and set the OPENAI_API_KEY environment"
            " variable to enable AI features."
        )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


def extract_fields_from_text(text: str) -> Dict[str, str]:
    """Attempt to extract structured fields from free-form text.

    The model is asked to return a JSON object with common fields such as
    ``price``, ``name``, ``category`` or ``date`` when it can infer them.
    """
    prompt = (
        "Extract key fields (price, name, category, stock, date, location, etc.) "
        "from the following text. Respond with a JSON object where any missing "
        "fields have empty strings.\n" + text
    )
    response = _call_openai(prompt)
    try:
        import json

        return json.loads(response)
    except Exception:
        # Fall back to returning the raw response if it cannot be parsed
        return {"raw": response}


def classify_content(text: str) -> str:
    """Classify a text snippet as product, advert, article or spam."""
    prompt = (
        "Classify the following text into one of the categories: product, advert, "
        "article, spam. Respond with the single category word.\n" + text
    )
    return _call_openai(prompt)


def translate_text(text: str, *, target_language: str = "English") -> str:
    """Translate arbitrary text into ``target_language``."""
    prompt = f"Translate the following text into {target_language}:\n{text}"
    return _call_openai(prompt)


def generalise_selector(description: str) -> str:
    """Suggest a generic CSS or XPath selector based on the page description."""
    prompt = (
        "Given the description of a web page element or repeated pattern, "
        "suggest a robust CSS selector or XPath that would match it.\n" + description
    )
    return _call_openai(prompt)


def normalise_date(text: str) -> str:
    """Normalise a date expression to ISO format (YYYY-MM-DD) using the model."""
    prompt = (
        "Normalise the following date or time expression to ISO YYYY-MM-DD "
        "format. If no date is detected return an empty string.\n" + text
    )
    return _call_openai(prompt)
