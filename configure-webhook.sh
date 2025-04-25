#!/bin/bash

# Wait for WAHA service to be ready
echo "Waiting for WAHA service to be available..."
until curl -s http://waha:3000/api/health > /dev/null; do
    sleep 5
done

echo "Configuring webhook..."
curl -X PUT http://waha:3000/api/sessions/default \
  -H "Content-Type: application/json" \
  -d '{
    "name": "default",
    "config": {
      "webhooks": [
        {
          "url": "http://fastapi:8000/webhook",
          "events": [
            "message",
            "session.status"
          ],
          "retries": {
            "policy": "constant",
            "delaySeconds": 30,
            "attempts": 2
          }          
        }
      ]
    }
  }'

echo "\nWebhook configuration completed"