"""Tests for lazy provider exports from pgflow.providers."""

from __future__ import annotations

import importlib
import sys


def test_importing_providers_package_is_lazy(monkeypatch) -> None:
    monkeypatch.delitem(sys.modules, "pgflow.providers", raising=False)
    monkeypatch.delitem(sys.modules, "pgflow.providers.anthropic_provider", raising=False)
    monkeypatch.delitem(sys.modules, "pgflow.providers.openai_compat_provider", raising=False)
    monkeypatch.delitem(sys.modules, "pgflow.providers.openai_codex_provider", raising=False)
    monkeypatch.delitem(sys.modules, "pgflow.providers.azure_openai_provider", raising=False)

    providers = importlib.import_module("pgflow.providers")

    assert "pgflow.providers.anthropic_provider" not in sys.modules
    assert "pgflow.providers.openai_compat_provider" not in sys.modules
    assert "pgflow.providers.openai_codex_provider" not in sys.modules
    assert "pgflow.providers.azure_openai_provider" not in sys.modules
    assert providers.__all__ == [
        "LLMProvider",
        "LLMResponse",
        "AnthropicProvider",
        "OpenAICompatProvider",
        "OpenAICodexProvider",
        "AzureOpenAIProvider",
    ]


def test_explicit_provider_import_still_works(monkeypatch) -> None:
    monkeypatch.delitem(sys.modules, "pgflow.providers", raising=False)
    monkeypatch.delitem(sys.modules, "pgflow.providers.anthropic_provider", raising=False)

    namespace: dict[str, object] = {}
    exec("from pgflow.providers import AnthropicProvider", namespace)

    assert namespace["AnthropicProvider"].__name__ == "AnthropicProvider"
    assert "pgflow.providers.anthropic_provider" in sys.modules
