from collections.abc import Callable

class Timer:
    def __init__(self, function: Callable, seconds: int, *args, **kwargs):
        self._remaining = seconds * 60
        self._task = function
        self._args = args
        self._kwargs = kwargs
        self._set = True


    @property
    def remaining(self) -> int:
        return self._remaining
    

    def tick(self):
        if self._set:
            if self._remaining > 0:
                self._remaining -= 1
            else:
                self._set = False
                return self._task(*self._args, *self._kwargs)