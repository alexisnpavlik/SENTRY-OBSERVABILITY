from sentry_observability import instrument_application


def test_instrument_application_returns_config():
    config = instrument_application("https://example.com/123")
    assert config["dsn"] == "https://example.com/123"
    assert config["traces_sample_rate"] == 1.0


def test_instrument_application_requires_dsn():
    try:
        instrument_application("")
    except ValueError as exc:
        assert "cannot be empty" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected ValueError when the DSN is empty")
