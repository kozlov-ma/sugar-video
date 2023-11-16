import dataclasses
import math
import pathlib
import subprocess
import typing
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
        stream = ffmpeg.input(self.source, loop=1, t=self.duration_seconds)
        audio = ffmpeg.input('anullsrc', f='lavfi').audio
        out = Clip(self.name)
        ffmpeg.output(stream, audio, shortest=None, vf="fps=30", vcodec='libx264', pix_fmt='yuv420p',
                      filename=out.source).overwrite_output().run()

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

        audio = audio.filter("atrim", start=f"{self.timestamp}").filter("asetpts", "PTS-STARTPTS")
        video = video.filter("trim", start=f"{self.timestamp}").filter("setpts", "PTS-STARTPTS")

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

        audio = audio.filter("atrim", end=f"{self.timestamp}").filter("asetpts", "PTS-STARTPTS")
        video = video.filter("trim", end=f"{self.timestamp}").filter("setpts", "PTS-STARTPTS")

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
    angle: float
    filter: typing.Union[Filter, None] = None

    def __call__(self) -> Clip:
        if self.filter is None:
            return None

        in_clip = self.filter()

        new_clip = in_clip.create_new()
        out_file = new_clip.source

        audio = ffmpeg.input(in_clip.source).audio
        video = ffmpeg.input(in_clip.source).video

        video = video.filter('rotate', angle=str(math.radians(self.angle)))

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

        return new_clip

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

        return new_clip

    def set_filter(self, filter: Filter | None = None, index=0):
        self.filter = filter


@dataclasses.dataclass(repr=True)
class UniteAudioVideo(Filter):
    audio: Filter | None = None
    video: Filter | None = None

    def __call__(self) -> Clip:
        audio_clip = self.audio()
        video_clip = self.video()

        if audio_clip is None or video_clip is None:
            return None

        audio_duration = audio_clip.duration
        video_duration = video_clip.duration

        if audio_duration < video_duration:
            audio_padded = audio_clip.create_new(new_name="padded_audio")
            ffmpeg.input(audio_clip.source).output(filename=audio_padded.source, t=video_duration,
                                                   shortest=None).overwrite_output().run()
            audio_clip = audio_padded

        if video_duration < audio_duration:
            video_padded = video_clip.create_new(new_name="padded_video")
            ffmpeg.input(video_clip.source).output(filename=video_padded.source, t=audio_duration,
                                                   shortest=None).overwrite_output().run()
            video_clip = video_padded

        out_clip = video_clip.create_new()
        out_file = out_clip.source
        create_dirs(out_file)

        audio = ffmpeg.input(audio_clip.source).audio
        video = ffmpeg.input(video_clip.source).video

        ffmpeg.output(video, audio, filename=out_file).overwrite_output().run()

        return out_clip

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
        first_clip = self.first()
        second_clip = self.second()

        if first_clip is None or second_clip is None:
            return None

        new_clip = Clip("")

        fade_duration = 0.35

        audio_first = ffmpeg.input(first_clip.source).audio
        audio_second = ffmpeg.input(second_clip.source).audio

        video_first = ffmpeg.input(first_clip.source).video
        video_second = ffmpeg.input(second_clip.source).video

        audio = ffmpeg.concat(audio_first, audio_second, a=1, v=0)
        out_file = new_clip.source

        if self.smooth:
            video_first = ffmpeg.filter(video_first, 'fade', t="out",
                                        st=first_clip.duration - fade_duration, d=fade_duration)

            video_second = ffmpeg.filter(video_second, 'fade', t="in",
                                         st=fade_duration, d=fade_duration)

            video = ffmpeg.concat(video_first, video_second, a=0, v=1)

            ffmpeg.output(video, audio, filename=out_file).overwrite_output().run()

            return new_clip

        else:
            video = ffmpeg.concat(video_first, video_second, v=1, a=0)

            create_dirs(out_file)

            ffmpeg.output(video, audio, filename=out_file).overwrite_output().run()

            return new_clip

    def set_filter(self, filter: Filter | None = None, index=0):
        match index:
            case 0:
                self.first = filter
                print("set filter 0")
            case 1:
                self.second = filter
                print("set filter 1")
