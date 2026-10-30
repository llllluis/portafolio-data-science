"""Integración con el LLM: construcción del prompt y cliente OpenRouter."""

from student_report.llm.client import OpenRouterClient, get_api_key, parse_json_response
from student_report.llm.prompt_builder import build_prompt

__all__ = ["OpenRouterClient", "build_prompt", "get_api_key", "parse_json_response"]
