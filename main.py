import pathlib

from filters.filter import speed_x, cut_to, cut_from
from filters.clip import VideoClip
from filters.timestamp import TimeStamp

clip = VideoClip("Бобёр", source=pathlib.Path("/Users/kozlov/Projects/TestDearPyGui/БОБЁР КРИЧИТ ААА (мем).mp4"))
f = speed_x(2.0)
f(clip).export_as("../Бобёр67.mp4",)
