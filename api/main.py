"""
API for handling webhook events and managing Redis-based memory.

This module provides endpoints for webhook processing and configuration management.
"""

import logging
import os
from datetime import datetime

import redis
import requests
from fastapi import FastAPI, Request
from openai import OpenAI

from app.prompts.atendimento import PROMPT_ASSISTENTE
from src.memory import RedisManager

logging.getLogger("uvicorn.access").addFilter(
    lambda record: "flutter_service_worker.js" not in record.getMessage()
)

app = FastAPI()

# Initialize Redis client
redis_client = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379"), decode_responses=True
)


@app.get("/hello")
async def hello_world() -> dict:
    """
    Return a hello message from the configuration.

    Returns:
        dict: A dictionary containing the configured message and timestamp.
    """
    config_manager = RedisManager(redis_client, "config")
    config = config_manager.get_memory_dict()
    if not config:
        return {"message": "No configuration found!"}
    return {
        "configured_message": config.get("hello_message", "No message configured"),
        "last_updated": config.get("timestamp", "Unknown"),
    }


@app.get("/")
async def root(request: Request) -> dict:
    """
    Root endpoint for the API.

    Args:
        request: The incoming request object.

    Returns:
        dict: A simple acknowledgment message.
    """
    _ = request
    return {"message": "Request received"}


@app.post("/webhook")
async def webhook(request: Request) -> dict:
    """
    Process incoming webhook events from the messaging service.

    Args:
        request: The incoming webhook request containing message data.

    Returns:
        dict: Status of the webhook processing.
    """
    print(f"Received webhook request from: {request.client}")
    try:
        body = await request.json()
        print(body)

        if body["event"] == "message":
            # Extract message data
            phone = body["payload"]["from"]
            message_content = body["payload"]["body"]

            # Get configuration
            config_manager = RedisManager(redis_client, "config")
            config = config_manager.get_memory_dict()

            # Initialize chat manager for this user
            chat_manager = RedisManager(redis_client, f"chat:{phone}")
            stored_messages = chat_manager.get_memory_dict()

            # Initialize or load message history
            if not stored_messages or "messages" not in stored_messages:
                messages = [
                    {"role": "system", "content": PROMPT_ASSISTENTE.format(**config)}
                ]
            else:
                messages = stored_messages["messages"]

            # Add user message
            messages.append({"role": "user", "content": message_content})

            # Get assistant response
            try:
                api_key = config.get("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY not found in Redis config")

                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4.1",
                    messages=messages,
                    temperature=0.7,
                )

                assistant_message = response.choices[0].message.content

                # Add assistant response to history
                messages.append({"role": "assistant", "content": assistant_message})

                # Save updated chat history
                chat_manager.set_memory_dict(
                    {"messages": messages, "last_updated": datetime.now().isoformat()},
                    expire_time=3600,
                )  # 1 hour expiration

                # Send response back to WhatsApp
                payload = {
                    "session": "default",
                    "chatId": phone,
                    "text": assistant_message,
                    "linkPreview": False,
                }

                requests.post("http://waha:3000/api/sendText", json=payload)
                return {"status": "success"}

            except Exception as e:
                print(f"Error getting assistant response: {e}")
                return {"status": "error", "message": str(e)}

        return {"status": "success", "message": "Non-message event ignored"}

    except Exception as e:
        print(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn

    print("Starting server on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
