import os
import logging
from functools import wraps
from urllib.parse import urlparse

import sentry_sdk

try:  # Optional dependency installed via the "azure" extra
    import azure.functions as func
except ImportError:  # pragma: no cover - only triggered when the package is missing
    func = None

try:
    from exceptions import AppException  # type: ignore
except ImportError:  # pragma: no cover - a stub is used when it cannot be imported
    class AppException(Exception):
        """Simple fallback used when the application-specific exception is unavailable."""

        status_code = 500
        detail = "Unexpected error"

from pydantic import ValidationError
from sqlalchemy.exc import StatementError, DataError


# Sentry
SERVICE_NAME = os.getenv("SERVICE_NAME", "unknown")
SENTRY_DSN = os.getenv("SENTRY_DSN")
SENTRY_DEBUG = os.getenv("SENTRY_DEBUG", "False").lower() in {"1", "true", "yes"}
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")


if sentry_sdk.Hub.current.client is None:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=0.2,
        debug=SENTRY_DEBUG,
        environment=ENVIRONMENT,
        server_name=SERVICE_NAME,
    )


def handle_exceptions_azure_functions(endpoint_func):
    if func is None:  # pragma: no cover - depends on the optional installation
        raise RuntimeError(
            "azure-functions is not installed. Run"
            " 'pip install sentry-observability[azure]' to enable this helper."
        )

    @wraps(endpoint_func)
    def wrapper(*args, **kwargs):
        req = None
        context = None
        for a in list(args) + list(kwargs.values()):
            if isinstance(a, func.HttpRequest):
                req = a
            if hasattr(a, "function_name") and hasattr(a, "invocation_id"):
                context = a

        method = getattr(req, "method", None)
        url = getattr(req, "url", None)
        path = urlparse(url).path if url else None

        func_name = getattr(context, "function_name", None) or endpoint_func.__name__
        invocation_id = getattr(context, "invocation_id", None)

        service_name = os.getenv("SERVICE_NAME", SERVICE_NAME)
        environment = os.getenv("ENVIRONMENT", ENVIRONMENT)

        if method and path:
            sentry_sdk.set_transaction_name(f"{method} {path}")
        else:
            sentry_sdk.set_transaction_name(f"func {func_name}")

        with sentry_sdk.push_scope() as scope:
            if method:
                scope.set_tag("http.method", method)
            if path:
                scope.set_tag("http.route", path)
            if url:
                scope.set_tag("http.url", url)
            scope.set_tag("azure.function", func_name)
            if invocation_id:
                scope.set_tag("azure.invocation_id", invocation_id)

            if req is not None:
                try:
                    scope.set_context("http", {
                        "method": method,
                        "url": url,
                        "query_string": req.params,
                        "headers": dict(req.headers or {}),
                        "env": {"ENV": environment},
                    })
                except Exception:
                    pass

            try:
                return endpoint_func(*args, **kwargs)

            except (ValidationError, ValueError) as ve:
                sentry_sdk.capture_exception(ve)
                logging.warning(f"[{service_name}] {ve}")
                return func.HttpResponse(str(ve), status_code=400, mimetype='application/json')

            except AppException as ae:
                sentry_sdk.capture_exception(ae)
                logging.warning(f"[{service_name}] {ae.detail}")
                return func.HttpResponse(ae.detail, status_code=ae.status_code)

            except (StatementError, DataError) as se:
                sentry_sdk.capture_exception(se)
                logging.warning(f"[{service_name}] Invalid input: {se}")
                return func.HttpResponse(f"[{service_name}] Invalid input format: {se}", status_code=400)

            except Exception as e:
                sentry_sdk.capture_exception(e)
                logging.error(f"[{service_name}] {e}")
                return func.HttpResponse(
                    f"[{service_name}] Unexpected error: {e}",
                    status_code=500,
                )

    return wrapper
