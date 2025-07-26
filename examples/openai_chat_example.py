
"""Minimal script to confirm your OpenAI key and connection."""
import logging
import os
from typing import Optional

from dotenv import load_dotenv
import openai

# Configure basic logging to a local file
logging.basicConfig(
    filename="openai_chat.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)

load_dotenv()  # Load variables from .env if present


def load_api_key() -> Optional[str]:
    """Return the OpenAI API key from the environment."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        logging.error("OPENAI_API_KEY not found")
        print("OpenAI API key is missing. Set OPENAI_API_KEY in your environment or .env file.")
        return None

    # Show only the first few characters so it's clear which key loaded
    print(f"Loaded OpenAI API key: {key[:5]}...")
    return key


def send_test_message(text: str = "Hello") -> str:
    """Send ``text`` to GPT-4 and return the response or error message."""
    api_key = load_api_key()
    if not api_key:
        return "Missing API key"

    try:
        request_opts = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": text}],
        }

        # Support both openai v1 and v0 style APIs
        if hasattr(openai, "OpenAI"):
            client = openai.OpenAI(api_key=api_key)
            resp = client.chat.completions.create(**request_opts)
            message = resp.choices[0].message.content
        else:
            openai.api_key = api_key
            resp = openai.ChatCompletion.create(**request_opts)
            message = resp.choices[0].message["content"]

        logging.info("API call succeeded")
        return message
    except (
        openai.AuthenticationError,
        openai.InvalidRequestError,
        openai.PermissionError,
    ) as exc:
        logging.exception("OpenAI request failed")
        return f"OpenAI API error: {exc}"
    except openai.APIConnectionError as exc:
        logging.exception("Network issue")
        return f"Network error: {exc}"
    except Exception as exc:  # pragma: no cover - unexpected failure
        logging.exception("Unexpected error")
        return f"Unexpected error: {exc}"


def main() -> None:
    """Run a simple test call."""
    response = send_test_message("Hello")
    print(f"Response: {response}")


if __name__ == "__main__":
    main()
