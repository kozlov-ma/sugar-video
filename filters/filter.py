import dataclasses
import typing

from filters.clip import BaseClip, VideoClip
from filters.timestamp import TimeStamp


def noop(clip: BaseClip) -> BaseClip:
    return clip


def speed_x(x: float, f: typing.Callable[[BaseClip], BaseClip] = noop) -> typing.Callable[[BaseClip], VideoClip]:
    def wrapped(clip: BaseClip) -> VideoClip:
        vclip = VideoClip.from_clip(f(clip))
        return vclip.with_speed_x(x)

    return wrapped


def cut_from(timestamp: TimeStamp, f: typing.Callable[[BaseClip], BaseClip] = noop) -> typing.Callable[
    [BaseClip], VideoClip]:
    def wrapped(clip: BaseClip) -> VideoClip:
        vclip = VideoClip.from_clip(f(clip))
        return dataclasses.replace(vclip, cut_from=timestamp)

    return wrapped


def cut_to(timestamp: TimeStamp, f: typing.Callable[[BaseClip], BaseClip] = noop) -> typing.Callable[
    [BaseClip], VideoClip]:
    def wrapped(clip: BaseClip) -> VideoClip:
        vclip = VideoClip.from_clip(f(clip))
        return dataclasses.replace(vclip, cut_to=timestamp)

    return wrapped
