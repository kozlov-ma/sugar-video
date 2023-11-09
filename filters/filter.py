import dataclasses
import pathlib
import typing
import uuid
from abc import ABC, abstractmethod

import ffmpeg

from filters.clip import Clip, create_dirs
from filters.timestamp import TimeStamp


@dataclasses.dataclass
class Filter(ABC):
    @abstractmethod
    def __call__(self) -> Clip:
        pass

    @abstractmethod
    def set_filter(self, filter: typing.Self | None = None, index=0):
        pass


@dataclasses.dataclass(repr=True)
class VideoInput(Filter):
    source: pathlib.Path
    name: str

    def __call__(self) -> Clip:
        print("called input")
        return Clip(self.name, source=self.source)

    def set_filter(self, filter: Filter | None = None, index=0):
        pass


@dataclasses.dataclass(repr=True)
class ImageInput(Filter):
    source: pathlib.Path
    name: str
    duration_seconds: int

    def __call__(self) -> Clip:
        stream = ffmpeg.input(self.source)
        stream = stream.filter('loop', loop=1, size=self.duration_seconds * 25)
        out = Clip(self.name)
        ffmpeg.output(stream, out.source).overwrite_output().run()

        return out

    def set_filter(self, filter: Filter | None = None, index=0):
        pass


@dataclasses.dataclass
class Noop(Filter):
    filter: Filter | None = None

    def __call__(self) -> Clip:
        if self.filter is None:
            return None

        return self.filter()

    def set_filter(self, filter: Filter | None = None, index=0):
        self.filter = filter


@dataclasses.dataclass(repr=True)
class CutFrom(Filter):
    timestamp: TimeStamp
    filter: typing.Union[Filter, None] = None

    def __call__(self) -> Clip:
        if self.filter is None:
            return None

        in_clip = self.filter()

        new_clip = in_clip.create_new()
        out_file = new_clip.source
        if new_clip.file_exists:
            return new_clip

        audio = ffmpeg.input(in_clip.source).audio
        video = ffmpeg.input(in_clip.source).video

        audio = audio.filter("atrim", start=f"{self.timestamp}").filter(
            "asetpts", "PTS-STARTPTS")
        video = video.filter("trim", start=f"{self.timestamp}").filter("setpts",
                                                                       "PTS-STARTPTS")

        ffmpeg.output(video, audio, filename=out_file).overwrite_output().run()

        return new_clip

    def set_filter(self, filter: Filter | None = None, index=0):
        self.filter = filter


@dataclasses.dataclass(repr=True)
class CutTo(Filter):
    timestamp: TimeStamp
    filter: typing.Union[Filter, None] = None

    def __call__(self) -> Clip:
        if self.filter is None:
            return None

        in_clip = self.filter()

        new_clip = in_clip.create_new()
        out_file = new_clip.source
        if new_clip.file_exists:
            return new_clip

        audio = ffmpeg.input(in_clip.source).audio
        video = ffmpeg.input(in_clip.source).video

        audio = audio.filter("atrim", end=f"{self.timestamp}").filter("asetpts",
                                                                      "PTS-STARTPTS")
        video = video.filter("trim", end=f"{self.timestamp}").filter("setpts",
                                                                     "PTS-STARTPTS")

        ffmpeg.output(video, audio, filename=out_file).overwrite_output().run()

        return new_clip

    def set_filter(self, filter: Filter | None = None, index=0):
        self.filter = filter


@dataclasses.dataclass(repr=True)
class SpeedX(Filter):
    x: float
    filter: typing.Union[Filter, None] = None

    def __call__(self) -> Clip:
        if self.filter is None:
            return None

        in_clip = self.filter()

        new_clip = in_clip.create_new()
        out_file = new_clip.source

        audio = ffmpeg.input(in_clip.source).audio
        video = ffmpeg.input(in_clip.source).video

        video = ffmpeg.setpts(video, f"{1 / self.x}*PTS")
        audio = audio.filter("atempo", str(self.x))

        create_dirs(out_file)
        ffmpeg.output(video, audio, filename=out_file).overwrite_output().run()

        return new_clip

    def set_filter(self, filter: Filter | None = None, index=0):
        self.filter = filter


@dataclasses.dataclass(repr=True)
class Rotate(Filter):
    clockwise: bool
    flip: bool
    filter: typing.Union[Filter, None] = None

    def __call__(self) -> Clip:
        if self.filter is None:
            return None

        in_clip = self.filter()

        new_clip = in_clip.create_new()
        out_file = new_clip.source

        audio = ffmpeg.input(in_clip.source).audio
        video = ffmpeg.input(in_clip.source).video

        ftype = "clock" if self.clockwise else "cclock" + "_flip" if self.flip else ""

        video = video.filter("transpose", ftype)

        create_dirs(out_file)
        ffmpeg.output(video, audio, filename=out_file).overwrite_output().run()

        return new_clip

    def set_filter(self, filter: Filter | None = None, index=0):
        self.filter = filter


@dataclasses.dataclass(repr=True)
class VideoTrack(Filter):
    filter: typing.Union[Filter, None] = None

    def __call__(self) -> Clip:
        if self.filter is None:
            return None

        in_clip = self.filter()

        new_clip = in_clip.create_new()
        out_file = new_clip.source
        create_dirs(out_file)

        video = ffmpeg.input(in_clip.source).video
        ffmpeg.output(video, filename=out_file).overwrite_output().run()

    def set_filter(self, filter: Filter | None = None, index=0):
        self.filter = filter


@dataclasses.dataclass(repr=True)
class AudioTrack(Filter):
    filter: typing.Union[Filter, None] = None

    def __call__(self) -> Clip:
        if self.filter is None:
            return None

        in_clip = self.filter()

        new_clip = in_clip.create_new()
        out_file = new_clip.source
        create_dirs(out_file)

        audio = ffmpeg.input(in_clip.source).audio
        ffmpeg.output(audio, filename=out_file).overwrite_output().run()

    def set_filter(self, filter: Filter | None = None, index=0):
        self.filter = filter


@dataclasses.dataclass(repr=True)
class UniteAudioVideo(Filter):
    audio: Filter | None = None
    video: Filter | None = None

    def __call__(self) -> Clip:
        if self.audio is None or self.video is None:
            return None

        in_audio = ffmpeg.input(self.audio()).audio
        in_video = ffmpeg.input(self.video()).video

        new_name = f"{in_audio.name} + {in_video.name}"
        new_clip = Clip(new_name)

        ffmpeg.output(in_video, in_audio, filename=new_clip.source).overwrite_output().run()

        return new_clip

    def set_filter(self, filter: Filter | None = None, index=0):
        match index:
            case 0:
                self.audio = filter
                print("set filter 0")
            case 1:
                self.video = filter
                print("set filter 1")


@dataclasses.dataclass(repr=True)
class Concat(Filter):
    first: Filter | None = None
    second: Filter | None = None
    smooth: bool = False

    def __call__(self) -> Clip:
        if self.first is None or self.second is None:
            return None

        in_first = self.first()
        in_second = self.second()

        duration1 = ffmpeg.probe(in_first.source)['format']['duration']
        duration2 = ffmpeg.probe(in_second.source)['format']['duration']

        audio_first = ffmpeg.input(in_first.source).audio
        video_first = ffmpeg.input(in_first.source).video

        audio_second = ffmpeg.input(in_second.source).audio
        video_second = ffmpeg.input(in_second.source).video

        new_name = f"{in_first.name} + {in_second.name}"
        new_clip = Clip(new_name)

        audio = ffmpeg.concat(audio_first, audio_second, a=1, v=0)
        if self.smooth:
            fade_duration = 1
            fade_in = f"fade=t=in:st=0:d={fade_duration}"
            fade_out = f"fade=t=out:st={duration2 - fade_duration}:d={fade_duration}"

            filter_graph = f"[0:v] {fade_out} [fv]; [1:v] {fade_in} [nextv]; [fv][nextv] overlay=eof_action=pass[outv]"
            video = ffmpeg.concat(video_first, video_second)

            ffmpeg.output(video, audio, filename=new_clip.source, filter_complex=filter_graph).overwrite_output().run()
        else:
            video = ffmpeg.concat(video_first, video_second)

            ffmpeg.output(video, audio, filename=new_clip.source).overwrite_output().run()

        return new_clip

    def set_filter(self, filter: Filter | None = None, index=0):
        match index:
            case 0:
                self.first = filter
                print("set filter 0")
            case 1:
                self.second = filter
                print("set filter 1")
