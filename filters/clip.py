import os
import pathlib
import typing
from dataclasses import dataclass

import ffmpeg

from filters.timestamp import TimeStamp

TEMP_DIR = pathlib.Path("./temp/")


def ensure_tempdir_exists():
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

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
        stream = ffmpeg.input(self.source)
        stream = ffmpeg.setpts(stream, f"{1 / x}*PTS")

        ffmpeg.output(stream, filename=file).run()
        print('A')

        return Clip(self.name, file, self.version + 1)

    def cut_from(self, timestamp: TimeStamp):
        file = self.new_version_file_name()
        stream = ffmpeg.input(self.source)
        stream = ffmpeg.trim(stream, start=str(timestamp))

        ffmpeg.output(stream, file).run()

        return Clip(self.name, file, self.version + 1)

    def cut_to(self, timestamp: TimeStamp):
        file = self.new_version_file_name()
        stream = ffmpeg.input(self.source)
        stream = ffmpeg.trim(stream, end=str(timestamp))

        ffmpeg.output(stream, file).run()

        return Clip(self.name, file, self.version + 1)
