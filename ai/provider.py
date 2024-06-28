from ai.base import AbstractGenAIClient
from ai.openai import OpenAIGPTClient
from ai.claude import ClaudeGPTClient

SUPPORTED_MODELS = {
    "openai": [
        "gpt-4o",
        "gpt-4o-2024-05-13",
        "gpt-3.5-turbo-0125",
        "gpt-3.5-turbo-instruct",
    ],
    "claude": [
        "claude-3-5-sonnet-20240620",
        "claude-3-5-sonnet-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-opus-20240229",
        "claude-3-haiku-20240307",
    ],
}


def ai_client(model: str, user_id: int, username: str) -> AbstractGenAIClient:
    # Find by specific model name
    # e.g. model = "claude-3-5-sonnet-20240620"
    for _brand in SUPPORTED_MODELS:
        for _model in SUPPORTED_MODELS[_brand]:
            if model == _model:
                return get_client(_brand)(model, user_id, username)

    # Find by model brand and get the latest version
    # e.g. model = "claude"
    for _brand in SUPPORTED_MODELS:
        if model == _brand:
            return get_client(_brand)(SUPPORTED_MODELS[_brand][0], user_id, username)

    # Find by model name prefix
    # e.g. model = "claude-3-5-sonnet"
    for _brand in SUPPORTED_MODELS:
        for _model in SUPPORTED_MODELS[_brand]:
            if _model.startswith(model):
                return get_client(_brand)(_model, user_id, username)
    
    raise ValueError(f"Model '{model}' not found")


def get_client(brand: str) -> type[AbstractGenAIClient]:
    if brand == "openai":
        return OpenAIGPTClient
    elif brand == "claude":
        return ClaudeGPTClient
    else:
        raise ValueError(f"Model brand '{brand}' not supported.")
