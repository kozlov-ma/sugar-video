import functools
import os
import pathlib
import typing
import uuid
from dataclasses import dataclass

import ffmpeg

from filters.timestamp import TimeStamp

TEMP_DIR = "./temp/"


def create_dirs(path: pathlib.Path):
    dir_path = os.path.split(path)[0]
    if not os.path.exists(dir_path):
        print("DirPath", dir_path)
        os.makedirs(dir_path)


@dataclass
class Clip:
    name: str
    source: pathlib.Path

    @property
    def file_exists(self):
        return os.path.exists(self.source)

    @property
    def duration(self):
        if not self.file_exists:
            return -1

        return float(ffmpeg.probe(self.source)['format']['duration'])

    def __init__(self, name: str, source: pathlib.Path = None):
        self.name = name
        if name == "":
            name = str(uuid.uuid4())

        if source is None:
            source = pathlib.Path(f"{TEMP_DIR}{uuid.uuid4()}/{name}.mp4")
        self.source = source
        print(f"New clip: {self}")
        create_dirs(self.source)

    def create_new(self, new_name: str | None = None) -> typing.Self:
        new_name = new_name if new_name else self.name

        path = pathlib.Path(f"{TEMP_DIR}/{uuid.uuid4()}/{new_name}.mp4")
        return Clip(new_name, path)
