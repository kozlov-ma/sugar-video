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
    actions: list[str]

    @property
    def file_exists(self):
        return os.path.exists(self.source)

    def __init__(self, name: str, source: pathlib.Path, action_list: list[str] = None):
        self.name = name
        self.source = source
        self.actions = action_list if action_list else list()
        create_dirs(self.source)

    def create_new(self, action: str, new_name: str | None = None) -> typing.Self:
        new_name = new_name if new_name else self.name

        new_action_list = self.actions + [action]
        path = path_from_actions(new_name, 'mp4', new_action_list)
        return Clip(new_name, path, new_action_list)
