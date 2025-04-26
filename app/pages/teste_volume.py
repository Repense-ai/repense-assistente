import os
import redis

import streamlit as st
from datetime import datetime

from memory import RedisManager

# Initialize Redis client
redis_client = redis.Redis.from_url(
    os.getenv('REDIS_URL', 'redis://localhost:6379'),
    decode_responses=True
)

# Initialize config manager
config_manager = RedisManager(redis_client, "config")

st.title("Hello World Config Test")

# Create a simple form for the hello world message
hello_message = st.text_input("Enter your hello world message:", "Hello, World!")

if st.button("Save Configuration"):
    # Create the config data
    config_data = {
        "hello_message": hello_message,
        "timestamp": datetime.now().isoformat()
    }
    
    # Save to Redis
    if config_manager.set_memory_dict(config_data):
        st.success("Configuration saved successfully!")
        
        # Display the current configuration
        st.write("Current configuration:")
        st.json(config_data)
    else:
        st.error("Failed to save configuration")

# Add a section to view the current configuration
st.subheader("Current Configuration")
current_config = config_manager.get_memory_dict()
if current_config:
    st.json(current_config)
else:
    st.info("No configuration found yet. Save a configuration first!")

# Add a section to show Redis connection status
st.subheader("Redis Connection Status")
try:
    if redis_client.ping():
        st.success("Connected to Redis successfully!")
except Exception as e:
    st.error(f"Redis connection error: {e}")