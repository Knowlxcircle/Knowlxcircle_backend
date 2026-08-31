"""Lazy, cached access to OpenRouter's chat-completions API.

This module still lives in the ``gemini`` app so that the public URL namespace
(``/api/v1/gemini/``) and the existing migrations stay untouched, but nothing in
here is Google-specific any more: every request goes to OpenRouter, which fronts
hundreds of models behind one OpenAI-compatible endpoint.  Pick the model with
the ``OPENROUTER_MODEL`` environment variable.

Nothing talks to the network, reads a setting or imports the SDK at module
import time.  ``gemini.urls`` -> ``gemini.views`` -> ``gemini.client`` is part of
the Django startup import chain (and ``article`` / ``dashboard`` import it as
well), so an eager client would take the whole application down whenever a key
is missing or the package is not installed.

Public surface (three names, relied on by the article and dashboard views):

    LLMUnavailable  -- raised for every configuration / transport / API failure
    get_client()    -- cached ``openai.OpenAI`` pointed at OpenRouter
    generate_text() -- prompt in, plain text out
"""

import logging
import threading

from django.conf import settings

logger = logging.getLogger(__name__)

__all__ = ["LLMUnavailable", "get_client", "generate_text"]

_DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
_DEFAULT_MODEL = "openai/gpt-5-mini"

_client = None
_client_api_key = None
_client_lock = threading.Lock()


class LLMUnavailable(RuntimeError):
    """The model backend is not configured, not installed or not answering."""


def _setting(name, default):
    """Read a setting, treating a missing or ``None`` value as the default."""
    value = getattr(settings, name, default)
    return default if value is None else value


def _api_key():
    """Return the configured OpenRouter API key, or an empty string."""
    return str(_setting("OPENROUTER_API_KEY", "")).strip()


def _model_name(model=None):
    """Return the model to call: the explicit one, the setting, or the default."""
    name = (model or "").strip()
    if name:
        return name
    name = str(_setting("OPENROUTER_MODEL", "")).strip()
    return name or _DEFAULT_MODEL


def _attribution_headers():
    """Optional headers that credit this app on the OpenRouter leaderboards."""
    headers = {}
    site_url = str(_setting("OPENROUTER_SITE_URL", "")).strip()
    site_name = str(_setting("OPENROUTER_SITE_NAME", "")).strip()
    if site_url:
        headers["HTTP-Referer"] = site_url
    if site_name:
        headers["X-OpenRouter-Title"] = site_name
    return headers or None


def get_client():
    """Return a cached OpenAI-SDK client pointed at OpenRouter, built on first use.

    Raises:
        LLMUnavailable: if no API key is configured, the ``openai`` package is
            missing, or the client cannot be constructed.
    """
    global _client, _client_api_key

    api_key = _api_key()
    if not api_key:
        raise LLMUnavailable("OPENROUTER_API_KEY is not configured.")

    with _client_lock:
        # Rebuild if the key changed (matters for tests and key rotation).
        if _client is not None and _client_api_key == api_key:
            return _client

        try:
            from openai import OpenAI
        except ImportError as exc:
            logger.error("The openai package is not installed: %s", exc)
            raise LLMUnavailable("The openai package is not installed.") from exc

        try:
            client = OpenAI(
                base_url=str(_setting("OPENROUTER_BASE_URL", _DEFAULT_BASE_URL)),
                api_key=api_key,
                timeout=float(_setting("OPENROUTER_TIMEOUT", 60.0)),
                max_retries=int(_setting("OPENROUTER_MAX_RETRIES", 2)),
            )
        except Exception as exc:
            logger.exception("Could not build the OpenRouter client.")
            raise LLMUnavailable("Could not build the OpenRouter client.") from exc

        _client = client
        _client_api_key = api_key
        return _client


def generate_text(prompt: str, *, model: str | None = None) -> str:
    """Send ``prompt`` to OpenRouter and return the plain response text.

    Args:
        prompt: the text prompt to send.
        model: optional OpenRouter model slug (e.g. ``"openai/gpt-5-mini"``);
            defaults to ``settings.OPENROUTER_MODEL``.

    Returns:
        The response text, always a non-empty ``str``.

    Raises:
        LLMUnavailable: on any configuration or transport failure, and when the
            model returns nothing usable (a routing error or a filtered answer
            can come back as a successful HTTP 200 with no content).
    """
    text_prompt = "" if prompt is None else str(prompt)
    if not text_prompt.strip():
        raise LLMUnavailable("An empty prompt cannot be sent to OpenRouter.")

    name = _model_name(model)

    try:
        client = get_client()
        completion = client.chat.completions.create(
            model=name,
            messages=[{"role": "user", "content": text_prompt}],
            extra_headers=_attribution_headers(),
        )
    except LLMUnavailable:
        raise
    except Exception as exc:
        logger.exception("OpenRouter chat completion failed (model=%s).", name)
        raise LLMUnavailable("The OpenRouter API call failed.") from exc

    # OpenRouter reports provider/routing errors inside an HTTP 200 body, in
    # which case `choices` is missing rather than the SDK raising.
    error = getattr(completion, "error", None)
    if error:
        message = error.get("message") if isinstance(error, dict) else str(error)
        logger.error("OpenRouter returned an error payload (model=%s): %s", name, message)
        raise LLMUnavailable("OpenRouter returned an error.")

    choices = getattr(completion, "choices", None) or []
    if not choices:
        logger.error("OpenRouter returned no choices (model=%s).", name)
        raise LLMUnavailable("OpenRouter returned an empty response.")

    message = getattr(choices[0], "message", None)
    text = getattr(message, "content", None)

    if not isinstance(text, str) or not text.strip():
        logger.error(
            "OpenRouter returned no usable text (model=%s, finish_reason=%s).",
            name,
            getattr(choices[0], "finish_reason", None),
        )
        raise LLMUnavailable("OpenRouter returned an empty response.")

    return text
