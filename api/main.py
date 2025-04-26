"""
API for handling webhook events and managing Redis-based memory.

This module provides endpoints for webhook processing and configuration management.
"""

import logging
import os

import redis
import requests
from fastapi import FastAPI, Request

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

            phone = body["payload"]["from"]
            message = body["payload"]["body"]

            manager = RedisManager(redis_client, phone)
            memory = manager.get_memory_dict()

            if not memory:
                memory = {"messages": [message]}
            else:
                memory["messages"].append(message)

            manager.set_memory_dict(memory, expire_time=3600)

            payload = {
                "session": "default",
                "chatId": phone,
                "text": str(memory["messages"]),
                "linkPreview": False,
            }

            requests.post("http://waha:3000/api/sendText", json=payload)
            return {"status": "success"}
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn

    print("Starting server on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
