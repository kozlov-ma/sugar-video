import dataclasses
import functools
import os
import pathlib
import typing
from abc import abstractmethod, ABC
from dataclasses import dataclass

import ffmpeg

from filters.timestamp import TimeStamp


@functools.lru_cache(512)
def temp_file_path(name: str, version: int | str, extension: str | None = None) -> pathlib.Path:
    TEMP_DIR = pathlib.Path("./temp/")
    if extension is not None:
        return pathlib.Path(f"{TEMP_DIR}/{name}/{version}.{extension}")

    return pathlib.Path(f"{TEMP_DIR}/{name}/{version}")


@functools.lru_cache(512)
def vclip_name(name: str) -> str:
    return f"{name}_vclip"


@dataclass
class BaseClip:
    name: str

    @abstractmethod
    def export_temp(self) -> pathlib.Path:
        pass

    @abstractmethod
    def export_as(self, path: pathlib.Path):
        pass


@dataclass
class VideoClip(BaseClip):
    source: pathlib.Path
    speed_x: float | None = None
    cut_from: TimeStamp | None = None
    cut_to: TimeStamp | None = None

    def export_as(self, path: pathlib.Path):
        stream = ffmpeg.input(self.source)

        if self.speed_x is not None:
            stream = ffmpeg.setpts(stream, f"{1 / self.speed_x}*PTS")

        if self.cut_from is not None:
            if self.cut_to is not None:
                stream = ffmpeg.trim(stream, start=str(self.cut_from), end=str(self.cut_to))
            else:
                stream = ffmpeg.trim(stream, start=str(self.cut_from))
        elif self.cut_to is not None:
            stream = ffmpeg.trim(stream, start="00:00:00", end=str(self.cut_to))

        stream.output(path).run()

    def export_temp(self) -> pathlib.Path:
        file = temp_file_path(self.name, hash(self), os.path.splitext(self.source)[1])
        self.export_as(file)

        return file

    @classmethod
    def from_clip(cls, clip: BaseClip) -> typing.Self:
        if not isinstance(clip, VideoClip):
            file = clip.export_temp()
            vclip = VideoClip(vclip_name(clip.name), file)
            return vclip

        else:
            return dataclasses.replace(clip)


@dataclass
class Filter(ABC):
    @abstractmethod
    def export_temp(self) -> pathlib.Path:
        pass

    @abstractmethod
    def export_as(self, path: pathlib.Path):
        pass
