import base64
import io
import os
from typing import Literal

from openai import OpenAI

_SIZE_PARAMS = Literal["1024x1024", "1536x1024", "1024x1536", "auto"]
_QUALITY_PARAMS = Literal["high", "medium", "low"]
_BACKGROUND_PARAMS = Literal["transparent", "opaque", "auto"]


class OpenAIImages:
    def __init__(self, api_key: str | None = None):

        self.api_key = api_key if api_key else os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError("API key is required")

        self.client = OpenAI(api_key=self.api_key)

        self.response = None
        self.cost = None

    def generate(
        self,
        prompt: str,
        size: _SIZE_PARAMS = "1024x1024",
        quality: _QUALITY_PARAMS = "high",
        background: _BACKGROUND_PARAMS = "auto",
    ) -> bytes:

        self.response = self.client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size=size,
            quality=quality,
            background=background,
            moderation="low",
        )

        self.cost = self._get_cost()
        return self._get_image()

    def edit(
        self,
        prompt: str,
        image: list[io.BufferedReader],
        size: _SIZE_PARAMS = "1024x1024",
        quality: _QUALITY_PARAMS = "high",
        background: _BACKGROUND_PARAMS = "auto",
    ) -> bytes:

        _ = background

        self.response = self.client.images.edit(
            model="gpt-image-1",
            image=image,
            prompt=prompt,
            size=size,
            quality=quality,
        )

        self.cost = self._get_cost()
        return self._get_image()

    def _get_image(self) -> bytes:
        if self.response is not None:
            image_bytes = base64.b64decode(self.response.data[0].b64_json)

            return image_bytes
        else:
            raise ValueError("No response received from OpenAI API")

    def _get_cost(self) -> float:
        if self.response is not None:

            tokens = self.response.model_dump()["usage"]

            output_cost = (tokens["output_tokens"] * 40) / 1_000_000
            image_cost = (
                tokens["input_tokens_details"]["image_tokens"] * 10
            ) / 1_000_000
            text_cost = (tokens["input_tokens_details"]["text_tokens"] * 5) / 1_000_000

            total_cost = output_cost + image_cost + text_cost

            return total_cost
        else:
            raise ValueError("No response received from OpenAI API")


class NamedBytesIO(io.BytesIO):
    def __init__(self, buffer: bytes, name: str):
        super().__init__(buffer)
        self.name = name


def get_memory_buffer(binary: bytes, name: str) -> io.BufferedReader:
    bytesio = NamedBytesIO(binary, name)
    buffer = io.BufferedReader(bytesio)

    return buffer
