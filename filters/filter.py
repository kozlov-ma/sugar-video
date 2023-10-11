import dataclasses
import typing

from filters.clip import Clip
from filters.timestamp import TimeStamp


def noop(clip: Clip) -> Clip:
    return clip


def speed_x(x: float, f: typing.Callable[[Clip], Clip] = noop) -> typing.Callable[[Clip], Clip]:
    def wrapped(clip: Clip) -> Clip:
        return clip.speed_x(x)

    return wrapped


def cut_from(timestamp: TimeStamp, f: typing.Callable[[Clip], Clip] = noop) -> typing.Callable[
    [Clip], Clip]:
    def wrapped(clip: Clip) -> Clip:
        return clip.cut_from(timestamp)

    return wrapped


def cut_to(timestamp: TimeStamp, f: typing.Callable[[Clip], Clip] = noop) -> typing.Callable[
    [Clip], Clip]:
    def wrapped(clip: Clip) -> Clip:
        return clip.cut_to(timestamp)

    return wrapped
