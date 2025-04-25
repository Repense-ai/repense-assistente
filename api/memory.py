"""
Redis Client Configuration

Create a redis client from configuration.
"""

import json
import logging

from typing import Any

import numpy as np

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

    def set_memory_dict(self, memory_dict: dict, expire_time: int = 120) -> None:
        try:
            new_memory_dict = {}

            for k, v in memory_dict.items():
                if isinstance(v, list) or isinstance(v, dict):
                    new_memory_dict[k] = json.dumps(v, default=self.convert_types)
                else:
                    new_memory_dict[k] = str(v)

            self.redis.hset(name=self.id, mapping=new_memory_dict)
            self.redis.expire(name=self.id, time=expire_time)

            self.memory_dict = new_memory_dict
        except Exception as e:
            logger.warning(f"Erro para atualizar a memória: {e}")

    def reset_memory_dict(self):
        self.redis.delete(self.id)

    @staticmethod
    def convert_types(number: Any):
        if isinstance(number, (np.int64, np.float64)):
            return number.item()
