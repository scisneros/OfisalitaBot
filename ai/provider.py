from ai.base import AbstractGenAIClient
from ai.openai import OpenAIGPTClient
from ai.claude import ClaudeGPTClient

def ai_client(model: str, user_id: int, username: str) -> AbstractGenAIClient:
  if model.startswith("gpt"):
    return OpenAIGPTClient(model, user_id, username)
  elif model.startswith("claude"):
    return ClaudeGPTClient(model, user_id, username)
  else:
    raise ValueError(f"Model {model} not supported.")
