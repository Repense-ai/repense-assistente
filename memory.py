"""
Redis Client Configuration

Create a redis client from configuration.
"""

import json
import logging
from typing import Any, Optional
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

class RedisManager():
    def __init__(self, redis: Any, memory_id: str):
        self.redis = redis
        self.id = memory_id
        self.memory_dict = self.redis.hgetall(name=self.id)

    def get_memory_dict(self) -> dict:
        new_memory_dict = {}

        for k, v in self.memory_dict.items():
            try:
                key = k.decode('utf-8') if isinstance(k, bytes) else k
                value = v.decode('utf-8') if isinstance(v, bytes) else v

                new_memory_dict[key] = json.loads(value)
            except json.JSONDecodeError:
                try:
                    new_memory_dict[key] = int(value)
                except ValueError:
                    new_memory_dict[key] = value
            except Exception as e:
                logger.warning(
                    f"Erro para coletar a memória: {e}\n\n Não conseguimos acessar a chave {key}: {value}"
                )
        return new_memory_dict

    def set_memory_dict(self, memory_dict: dict, expire_time: Optional[int] = None) -> None:
        """
        Set memory dictionary with optional expiration
        
        Args:
            memory_dict: Dictionary to store
            expire_time: Optional expiration time in seconds. If None, data persists indefinitely
        """
        try:
            new_memory_dict = {}

            for k, v in memory_dict.items():
                if isinstance(v, (list, dict)):
                    new_memory_dict[k] = json.dumps(v, default=self.convert_types)
                else:
                    new_memory_dict[k] = str(v)

            # Add timestamp for tracking
            new_memory_dict['_last_updated'] = datetime.now().isoformat()

            self.redis.hset(name=self.id, mapping=new_memory_dict)
            
            # Only set expiration if specified
            if expire_time is not None:
                self.redis.expire(name=self.id, time=expire_time)

            self.memory_dict = new_memory_dict
            
            # Force save to disk if this is persistent data
            if expire_time is None:
                self.force_save()

        except Exception as e:
            logger.warning(f"Erro para atualizar a memória: {e}")

    def force_save(self) -> bool:
        """Force Redis to save data to disk"""
        try:
            return self.redis.save()
        except Exception as e:
            logger.error(f"Error forcing save to disk: {e}")
            return False

    def get_last_save_time(self) -> Optional[datetime]:
        """Get the timestamp of the last successful save to disk"""
        try:
            timestamp = self.redis.lastsave()
            return datetime.fromtimestamp(timestamp)
        except Exception as e:
            logger.error(f"Error getting last save time: {e}")
            return None

    def reset_memory_dict(self):
        """Clear the memory dictionary"""
        self.redis.delete(self.id)

    @staticmethod
    def convert_types(number: Any):
        if isinstance(number, (np.int64, np.float64)):
            return number.item()