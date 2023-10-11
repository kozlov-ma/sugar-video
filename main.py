# import pathlib
#
# from filters.filter import speed_x, cut_to, cut_from
# from filters.clip import Clip
# from filters.timestamp import TimeStamp
#
# clip = Clip('Бобрик', source=pathlib.Path('Бобер.mp4'))
# f = speed_x(2.0, lambda: clip)
# print(f().file_name())

from filters.gui.window import run

run()
