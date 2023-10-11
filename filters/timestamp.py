import functools
import typing
from dataclasses import dataclass

import parse
from parse import Parser, parse, compile


@dataclass
class TimeStamp:
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    milliseconds: int = 0

    def __init__(self, hours: int, minutes: int, seconds: int, milliseconds: int = 0):
        if hours < 0:
            raise ValueError("Hours must be positive")
        if minutes < 0 or minutes >= 59:
            raise ValueError("Minutes must be between '0' and '59'")
        if seconds < 0 or seconds >= 59:
            raise ValueError("Seconds must be between '0' and '59'")
        if milliseconds < 0 or milliseconds >= 1000:
            raise ValueError("Milliseconds must be between '0' and '999'")

        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.milliseconds = milliseconds

    @staticmethod
    @functools.cache
    def _parser_ms() -> Parser:
        return compile("{hours:d}:{minutes:d}:{seconds:d}:{milliseconds:d}")

    @staticmethod
    @functools.cache
    def _parser() -> Parser:
        return compile("{hours:d}:{minutes:d}:{seconds:d}")

    @classmethod
    def from_str(cls, s: str) -> typing.Self:
        with_ms = TimeStamp._parser_ms().parse(s)
        if with_ms:
            return TimeStamp(with_ms["hours"], with_ms["minutes"], with_ms["seconds"], with_ms["milliseconds"])

        res = TimeStamp._parser().parse(s)
        if res:
            return TimeStamp(res["hours"], res["minutes"], res["seconds"])

        raise ValueError("Wrong TimeStamp format")

    def __str__(self) -> str:
        if self.milliseconds == 0:
            return f"{self.hours}:{self.minutes}:{self.seconds}"
        else:
            return f"{self.hours}:{self.minutes}:{self.seconds}.{self.milliseconds}"
