"""Cliente mínimo para OpenRouter (API compatible con OpenAI)."""

from __future__ import annotations

import json
import os
from typing import Any

from student_report.config.settings import (
    LLM_EXTRA_BODY,
    LLM_MODEL,
    OPENROUTER_API_KEY_ENV,
    OPENROUTER_BASE_URL,
)

__all__ = ["get_api_key", "OpenRouterClient", "parse_json_response"]


def get_api_key(env_var: str = OPENROUTER_API_KEY_ENV) -> str | None:
    """Lee la clave de OpenRouter de la variable de entorno ``env_var``."""
    return os.getenv(env_var)


def parse_json_response(text: str) -> Any:
    """Convierte la respuesta textual del modelo en un objeto Python.

    Raises:
        json.JSONDecodeError: si el texto no es JSON válido.
    """
    return json.loads(text)


class OpenRouterClient:
    """Envoltorio fino sobre ``openai.OpenAI`` apuntando a OpenRouter.

    Args:
        api_key: clave de OpenRouter.
        model: identificador del modelo.
        base_url: URL base de la API.
        extra_body: parámetros extra enviados al endpoint.
    """

    def __init__(
        self,
        api_key: str,
        model: str = LLM_MODEL,
        base_url: str = OPENROUTER_BASE_URL,
        extra_body: dict[str, Any] | None = None,
    ) -> None:
        # Import diferido: el resto del paquete puede usarse sin `openai`.
        from openai import OpenAI

        self.model = model
        self.extra_body = LLM_EXTRA_BODY if extra_body is None else extra_body
        self._client = OpenAI(base_url=base_url, api_key=api_key)

    def complete(self, prompt: str) -> str:
        """Envía ``prompt`` como mensaje de usuario y devuelve el texto.

        Raises:
            ValueError: si el modelo devuelve una respuesta vacía.
        """
        completion = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            extra_body=self.extra_body,
        )
        content = completion.choices[0].message.content
        if not content:
            raise ValueError("El model no ha retornat cap resposta.")
        return content
