import logging

from django.apps import AppConfig
from django.core.checks import Warning as CheckWarning, register


class GeminiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "gemini"

    def ready(self):
        register(check_llm_credentials, "llm")

        # The system check above only surfaces where someone runs
        # `manage.py check`, and CI runs it with DJANGO_DEBUG=True (which
        # correctly silences it). This log line is the one that actually
        # reaches the deployment: it fires on every gunicorn boot.
        from django.conf import settings

        if not getattr(settings, "DEBUG", False) and not str(
            getattr(settings, "OPENROUTER_API_KEY", "") or ""
        ).strip():
            logging.getLogger(__name__).warning(
                "OPENROUTER_API_KEY is not set - every AI endpoint will return 503. "
                "It replaced GOOGLE_API_KEY in the OpenRouter migration."
            )


def check_llm_credentials(app_configs, **kwargs):
    """Surface a missing OPENROUTER_API_KEY during `manage.py check`.

    Without this the only symptom is every AI endpoint quietly answering 503,
    which looks identical to an upstream outage. The provider swap renamed the
    credential, so a deployment carrying only the old GOOGLE_API_KEY secret
    lands in exactly that state.
    """
    from django.conf import settings

    if getattr(settings, "DEBUG", False):
        return []
    if str(getattr(settings, "OPENROUTER_API_KEY", "") or "").strip():
        return []
    return [
        CheckWarning(
            "OPENROUTER_API_KEY is not set; every AI endpoint will return 503.",
            hint=(
                "Set OPENROUTER_API_KEY in the deployment environment (GitHub "
                "secret + Azure app setting). It replaced GOOGLE_API_KEY."
            ),
            id="llm.W001",
        )
    ]
