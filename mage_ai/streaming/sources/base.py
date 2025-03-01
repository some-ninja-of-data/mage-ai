from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, Dict
import json


class SourceConsumeMethod(str, Enum):
    BATCH_READ = 'BATCH_READ'
    READ = 'READ'
    READ_ASYNC = 'READ_ASYNC'


class BaseSource(ABC):
    config_class = None
    consume_method = SourceConsumeMethod.BATCH_READ

    def __init__(self, config: Dict, **kwargs):
        if self.config_class is not None:
            if 'connector_type' in config:
                config.pop('connector_type')
            self.config = self.config_class.load(config=config)
        self.checkpoint_path = kwargs.get('checkpoint_path')
        self.checkpoint = self.read_checkpoint()
        self.init_client()

    def init_client(self):
        pass

    def destroy(self):
        """
        Close connections and destroy threads
        """
        pass

    @abstractmethod
    def read(self, handler: Callable):
        pass

    async def read_async(self, handler: Callable):
        self._print('Start consuming messages asynchronously.')
        return self.read(handler)

    @abstractmethod
    def batch_read(self, handler: Callable):
        pass

    def read_checkpoint(self):
        checkpoint = None
        if self.checkpoint_path is None:
            return None
        try:
            with open(self.checkpoint_path) as fp:
                checkpoint = json.load(fp)
        except Exception:
            pass
        return checkpoint

    def update_checkpoint(self):
        if self.checkpoint_path is None or self.checkpoint is None:
            return
        try:
            with open(self.checkpoint_path, 'w') as fp:
                json.dump(self.checkpoint, fp)
        except Exception:
            pass

    def test_connection(self):
        return True

    def _print(self, msg):
        print(f'[{self.__class__.__name__}] {msg}')
