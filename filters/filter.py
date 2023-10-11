from __future__ import annotations
import dataclasses
import pathlib
import typing
from abc import ABC, abstractmethod

from filters.clip import Clip
from filters.timestamp import TimeStamp


class Filter(ABC):
    def __init__(self, f: typing.Union[Filter, None]):
        self.filter = f

    @abstractmethod
    def __call__(self) -> Clip:
        pass


class VideoClipFilter(Filter):
    def __init__(self, path: pathlib.Path):
        super().__init__(None)
        self.source = path

    def __call__(self) -> Clip:
        return Clip('Бобрик', source=self.source)


class NoopFilter(Filter):
    def __init__(self, f: typing.Union[Filter, None] = None):
        super().__init__(f)

    def __call__(self) -> Clip:
        if self.filter is None:
            return None

        return self.filter()


class SpeedXFilter(Filter):
    def __init__(self, x: float, f: typing.Union[Filter, None] = None):
        super().__init__(f)
        self.x = x

    def __call__(self) -> Clip:
        if self.filter is None:
            return None

        return self.filter().speed_x(self.x)


def noop(clip: Clip) -> Clip:
    return clip


def speed_x(x: float, f: typing.Callable[[], Clip] = noop) -> typing.Callable[[], Clip]:
    def wrapped() -> Clip:
        return f().speed_x(x)

    return wrapped


def cut_from(timestamp: TimeStamp, f: typing.Callable[[], Clip] = noop) -> typing.Callable[[], Clip]:
    def wrapped() -> Clip:
        return f().cut_from(timestamp)

    return wrapped


def cut_to(timestamp: TimeStamp, f: typing.Callable[[], Clip] = noop) -> typing.Callable[[], Clip]:
    def wrapped() -> Clip:
        return f().cut_to(timestamp)

    return wrapped
