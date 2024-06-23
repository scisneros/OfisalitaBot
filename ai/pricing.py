PRICING_PER_M_TOKENS = {
    # https://openai.com/api/pricing/
    "gpt-4o": {"input": 5, "output": 15},
    "gpt-4o-2024-05-13": {"input": 5, "output": 15},
    "gpt-3.5-turbo-0125": {"input": 0.5, "output": 1.5},
    "gpt-3.5-turbo-instruct": {"input": 1.5, "output": 2},
    # https://www.anthropic.com/pricing#anthropic-api
    "claude-3-5-sonnet": {"input": 3, "output": 15},
    "claude-3-sonnet": {"input": 3, "output": 15},
    "claude-3-opus": {"input": 15, "output": 75},
    "claude-3-haiku": {"input": 0.25, "output": 1.25},
}


def get_model_pricing(model: str) -> dict:
    if model in PRICING_PER_M_TOKENS:
        return PRICING_PER_M_TOKENS[model]
    else:
        for key in PRICING_PER_M_TOKENS:
            if model.startswith(key):
                return PRICING_PER_M_TOKENS[key]
    return {"input": 0, "output": 0}


def get_input_cost(model: str, input_tokens: int) -> float:
    return input_tokens * get_model_pricing(model)["input"] / 1000000


def get_output_cost(model: str, output_tokens: int) -> float:
    return output_tokens * get_model_pricing(model)["output"] / 1000000


def get_total_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    return (
        get_input_cost(model, input_tokens)
        + get_output_cost(model, output_tokens) / 1000000
    )
