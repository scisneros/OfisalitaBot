from openai import OpenAI

from ai.base import AbstractGenAIClient, GenAIResponse, GenAIMessage

try:
    from config.auth import openai_key
except ImportError:
    openai_key = None


class OpenAIGPTClient(AbstractGenAIClient):
    def create_client(self):
        self.api_key = openai_key
        if self.api_key is None:
            raise ValueError("OpenAI API key not found.")
        return OpenAI(api_key=self.api_key)

    def generate(
        self, conversation: list[GenAIMessage], system: str = None, **kwargs
    ) -> GenAIResponse:
        request = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system}]
            + [msg.to_dict() for msg in conversation],
            **kwargs
        )
        response = self.parse_response(request)
        self.save_request(response)
        return response

    def parse_response(self, response) -> GenAIResponse:
        return GenAIResponse(
            id=response.id,
            response=response,
            datetime=response.created,
            message=response.choices[0].message.content,
            model=response.model,
            usage={
                "input": response.usage.prompt_tokens,
                "output": response.usage.completion_tokens,
            },
        )
