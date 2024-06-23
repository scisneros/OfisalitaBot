from abc import ABC, abstractmethod

from data import AIRequests
from ai.pricing import get_model_pricing, get_total_cost


class GenAIMessage:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    def to_dict(self):
        return {"role": self.role, "content": self.content}


class GenAIResponse:
    def __init__(
        self,
        id: str,
        response: dict,
        datetime: str,
        message: str,
        model: str,
        usage: dict[str, int],
    ):
        self.id = id
        self.response = response
        self.datetime = datetime
        self.message = message
        self.model = model
        self.usage = usage
        self.pricing = get_model_pricing(model)
        self.cost = get_total_cost(
            model,
            usage["input"],
            usage["output"],
        )


class AbstractGenAIClient(ABC):
    def __init__(self, model: str, user_id: int, username: str):
        self.model = model
        self.user_id = user_id
        self.username = username
        self.api_key = None
        self.client = self.create_client()

    @abstractmethod
    def create_client(self):
        pass

    @abstractmethod
    def generate(
        self, conversation: list[GenAIMessage], system: str = None, **kwargs
    ) -> GenAIResponse:
        # Remember to call self.save_request(response) after parsing the response
        pass

    @abstractmethod
    def parse_response(self, response) -> GenAIResponse:
        pass

    def save_request(self, response: GenAIResponse):
        AIRequests.add(
            datetime=response.datetime,
            user_id=self.user_id,
            username=self.username,
            model=response.model,
            input_tokens=response.usage["input"],
            output_tokens=response.usage["output"],
            input_price_per_m=response.pricing["input"],
            output_price_per_m=response.pricing["output"],
            cost=response.cost,
        )
