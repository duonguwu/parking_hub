# -*- coding: utf-8 -*-
"""
Thread-safe Singleton Base Class.

Usage:
    class MyService(SingletonClass):
        def _singleton_init(self, host="localhost", port=8080):
            self.host = host
            self.port = port

    # Tao instance — luon tra ve cung 1 object
    service = MyService(host="10.0.0.1", port=9090)
    same_service = MyService()  # van la object cu, _singleton_init KHONG chay lai
"""
from abc import ABC, abstractmethod
from threading import Lock


class SingletonClass(ABC):
    """
    Thread-safe Singleton pattern.

    Subclass override _singleton_init() thay vi __init__().
    _singleton_init() chi chay 1 lan duy nhat.
    """
    _singleton_instance = None
    _singleton_lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._singleton_instance:
            with cls._singleton_lock:
                if not cls._singleton_instance:  # Double-check locking
                    cls._singleton_instance = super().__new__(cls)
        return cls._singleton_instance

    def __init__(self, **kwargs):
        if not getattr(self, "_singleton_init_done", False):
            self._singleton_init(**kwargs)
            self._singleton_init_done = True

    @abstractmethod
    def _singleton_init(self, **kwargs):
        """Override method nay de khoi tao tuy chinh."""
        pass
