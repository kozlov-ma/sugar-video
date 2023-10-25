import dataclasses
import pathlib
import typing
from abc import ABC, abstractmethod

import ffmpeg

from filters.clip import Clip, path_from_actions, create_dirs
from filters.timestamp import TimeStamp


@dataclasses.dataclass
class Filter(ABC):
    @abstractmethod
    def __call__(self) -> Clip:
        pass


@dataclasses.dataclass(repr=True)
class VideoInput(Filter):
    source: pathlib.Path
    name: str

    def __call__(self) -> Clip:
        print("called input")
        return Clip(self.name, source=self.source, action_list=[repr(self)])


@dataclasses.dataclass(repr=True)
class ImageInput(Filter):
    source: pathlib.Path
    name: str
    duration_seconds: int

    def __call__(self) -> Clip:
        stream = ffmpeg.input(self.source)
        stream = stream.filter('loop', loop=1, size=self.duration_seconds * 25)
        out = Clip(self.name, path_from_actions(self.name, "mp4", [repr(self)]), [repr(self)])
        ffmpeg.overwrite_output().output(stream, out.source).run()

        return out


@dataclasses.dataclass
class Noop(Filter):
    def __call__(self) -> Clip:
        if self.filter is None:
            return None

        return self.filter()


@dataclasses.dataclass(repr=True)
class CutFrom(Filter):
    timestamp: TimeStamp
    filter: typing.Union[Filter, None] = None

    def __call__(self) -> Clip:
        if self.filter is None:
            return None

        in_clip = self.filter()

        new_clip = in_clip.create_new(repr(self))
        out_file = new_clip.source
        if new_clip.file_exists:
            return new_clip

        audio = ffmpeg.input(in_clip.source).audio
        video = ffmpeg.input(in_clip.source).video

        audio = audio.filter("atrim", start=f"{self.timestamp}").filter("asetpts", "PTS-STARTPTS")
        video = video.filter("trim", start=f"{self.timestamp}").filter("setpts", "PTS-STARTPTS")

        ffmpeg.output(video, audio, filename=out_file).overwrite_output().run()

        return new_clip


@dataclasses.dataclass(repr=True)
class CutTo(Filter):
    timestamp: TimeStamp
    filter: typing.Union[Filter, None] = None

    def __call__(self) -> Clip:
        if self.filter is None:
            return None

        in_clip = self.filter()

        new_clip = in_clip.create_new(repr(self))
        out_file = new_clip.source
        if new_clip.file_exists:
            return new_clip

        audio = ffmpeg.input(in_clip.source).audio
        video = ffmpeg.input(in_clip.source).video

        audio = audio.filter("atrim", end=f"{self.timestamp}").filter("asetpts", "PTS-STARTPTS")
        video = video.filter("trim", end=f"{self.timestamp}").filter("setpts", "PTS-STARTPTS")

        ffmpeg.output(video, audio, filename=out_file).overwrite_output().run()

        return new_clip


@dataclasses.dataclass(repr=True)
class SpeedX(Filter):
    x: float
    filter: typing.Union[Filter, None] = None

    def __call__(self) -> Clip:
        if self.filter is None:
            return None

        in_clip = self.filter()

        new_clip = in_clip.create_new(repr(self))
        out_file = new_clip.source
        if new_clip.file_exists:
            return new_clip

        audio = ffmpeg.input(in_clip.source).audio
        video = ffmpeg.input(in_clip.source).video

        video = ffmpeg.setpts(video, f"{1 / self.x}*PTS")
        audio = audio.filter("atempo", str(self.x))

        create_dirs(out_file)
        ffmpeg.output(video, audio, filename=out_file).overwrite_output().run()

        return new_clip


@dataclasses.dataclass(repr=True)
class Concat(Filter):
    first: Filter | None = None
    second: Filter | None = None

    def __call__(self) -> Clip:
        if self.first is None or self.second is None:
            return None

        in_first = self.first()
        in_second = self.second()

        stream_first = ffmpeg.input(in_first.source)
        stream_second = ffmpeg.input(in_second.source)

        new_name = f"{in_first.name} + {in_second.name}"
        new_actions = in_first.actions + in_second.actions + [repr(self)]
        new_clip = Clip(new_name, path_from_actions(new_name, "mp4", new_actions), new_actions)

        ffmpeg.concat(stream_first, stream_second).overwrite_output().output(new_clip.source).run()

        return new_clip
