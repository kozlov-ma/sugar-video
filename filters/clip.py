import os
import pathlib
import typing
from dataclasses import dataclass

import ffmpeg

from filters.timestamp import TimeStamp

TEMP_DIR = pathlib.Path("./temp/")


def create_dirs(path: pathlib.Path):
    dir_path = os.path.split(path)[0]
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

@dataclass
class Clip:
    name: str
    source: pathlib.Path
    version: int = 0

    def file_name(self) -> pathlib.Path:
        if self.version == 0:
            return self.source

        extension = os.path.splitext(self.source)[1]
        if extension != "":
            return pathlib.Path(f"{TEMP_DIR}/{self.name}/{self.version}.{extension}")

        return pathlib.Path(f"{TEMP_DIR}/{self.name}/{self.version}")

    def new_version_file_name(self) -> pathlib.Path:
        version = self.version + 1
        extension = os.path.splitext(self.source)[1]

        if extension != "":
            return pathlib.Path(f"{TEMP_DIR}/{self.name}/{version}.{extension}")

        return pathlib.Path(f"{TEMP_DIR}/{self.name}/{version}")

    def speed_x(self, x: float) -> typing.Self:
        file = self.new_version_file_name()
        audio = ffmpeg.input(self.source).audio
        video = ffmpeg.input(self.source).video

        video = ffmpeg.setpts(video, f"{1 / x}*PTS")
        audio = audio.filter('atempo', f"{x}" )

        create_dirs(file)
        ffmpeg.output(video, audio, filename=file).overwrite_output().run()
        print('A')

        return Clip(self.name, file, self.version + 1)

    def cut_from(self, timestamp: TimeStamp):
        file = self.new_version_file_name()
        audio = ffmpeg.input(self.source).audio
        video = ffmpeg.input(self.source).video
        
        audio = audio.filter("atrim", start=f"{timestamp}").filter("asetpts", "PTS-STARTPTS")
        video = video.filter("trim", start=f"{timestamp}").filter("setpts", "PTS-STARTPTS")

        create_dirs(file)
        ffmpeg.output(video, audio, filename=file).overwrite_output().run()

        return Clip(self.name, file, self.version + 1)

    def cut_to(self, timestamp: TimeStamp):
        file = self.new_version_file_name()
        audio = ffmpeg.input(self.source).audio
        video = ffmpeg.input(self.source).video

        audio = audio.filter("atrim", end=f"{timestamp}").filter("asetpts", "PTS-STARTPTS")
        video = video.filter("trim", end=f"{timestamp}").filter("setpts", "PTS-STARTPTS")

        create_dirs(file)
        ffmpeg.output(video, audio, filename=file).overwrite_output().run()

        return Clip(self.name, file, self.version + 1)
