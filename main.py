import pathlib

from filters.filter import speed_x, cut_to, cut_from
from filters.clip import Clip
from filters.timestamp import TimeStamp

clip = Clip("Бобёр", source=pathlib.Path("/Users/kozlov/Projects/TestDearPyGui/БОБЁР КРИЧИТ ААА (мем).mp4"))
f = speed_x(2.0)
print(f(clip).file_name())
