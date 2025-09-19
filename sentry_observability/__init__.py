"""Lightweight helpers to reuse Sentry configuration across projects."""

from __future__ import annotations

from typing import Any, Dict, Optional

DEFAULT_TRACE_SAMPLE_RATE = 1.0


def instrument_application(
    dsn: str,
    *,
    traces_sample_rate: float = DEFAULT_TRACE_SAMPLE_RATE,
    environment: Optional[str] = None,
    service_name: Optional[str] = None,
    debug: Optional[bool] = None,
    **extra_config: Any,
) -> Dict[str, Any]:
    """Return the canonical configuration used to initialise Sentry.

    Parameters
    ----------
    dsn:
        DSN issued by Sentry. The value must be non-empty and non-blank.
    traces_sample_rate:
        Transaction sample rate. Defaults to 1.0 for full capture.
    environment:
        Environment name (for example, ``"development"`` or ``"production"``).
    service_name:
        Human-friendly name for the service reported to Sentry.
    debug:
        Explicitly enable Sentry debug mode when set.
    extra_config:
        Arbitrary additional keyword arguments forwarded to the SDK.

    Returns
    -------
    dict
        Dictionary ready to be passed to ``sentry_sdk.init``.
    """

    cleaned_dsn = (dsn or "").strip()
    if not cleaned_dsn:
        raise ValueError("The Sentry DSN cannot be empty")

    config: Dict[str, Any] = {
        "dsn": cleaned_dsn,
        "traces_sample_rate": traces_sample_rate,
    }

    if environment:
        config["environment"] = environment

    if service_name:
        config["server_name"] = service_name

    if debug is not None:
        config["debug"] = bool(debug)

    if extra_config:
        config.update(extra_config)

    return config


__all__ = ["instrument_application", "DEFAULT_TRACE_SAMPLE_RATE"]
