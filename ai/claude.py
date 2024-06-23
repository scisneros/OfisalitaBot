from anthropic import Anthropic
from time import time

from ai.base import AbstractGenAIClient, GenAIResponse, GenAIMessage

try:
    from config.auth import claude_key
except ImportError:
    claude_key = None


class ClaudeGPTClient(AbstractGenAIClient):
    def create_client(self):
        self.api_key = claude_key
        if self.api_key is None:
            raise ValueError("Claude API key not found.")
        return Anthropic(api_key=self.api_key)

    def generate(
        self, conversation: list[GenAIMessage], system: str = None, **kwargs
    ) -> GenAIResponse:
        max_tokens = kwargs.pop("max_tokens", 1000)
        request = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[msg.to_dict() for msg in conversation],
            **kwargs
        )
        response = self.parse_response(request)
        self.save_request(response)
        return response

    def parse_response(self, response: dict) -> GenAIResponse:
        return GenAIResponse(
            id=response.id,
            response=response,
            datetime=int(time()),
            message=response.content[0].text,
            model=response.model,
            usage={
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens,
            },
        )
