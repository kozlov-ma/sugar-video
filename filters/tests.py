import unittest
import ffmpeg
from filters.clip import Clip
from filters.filter import VideoInput, CutFrom, ImageInput
from filters.timestamp import TimeStamp


class FilterTests(unittest.TestCase):
    def test_VideoInput(self):
        source = 'Бобер.mp4'
        name = 'VideoInputTest'
        filter = VideoInput(source=source, name=name)

        clip = filter()

        self.assertIsInstance(clip, Clip)
        self.assertEqual(clip.source, source)
        self.assertEqual(clip.name, name)

        # Test duration
        probe = ffmpeg.probe(source)
        video_stream = next((stream for stream in probe['streams'] if
                             stream['codec_type'] == 'video'), None)
        duration = float(video_stream['duration'])
        self.assertAlmostEqual(clip.duration, duration, delta=0.1)

    def test_ImageInput(self):
        source = 'path/to/image.png'
        name = 'ImageInputTest'
        duration_seconds = 5
        filter = ImageInput(source=source, name=name,
                            duration_seconds=duration_seconds)

        clip = filter()

        self.assertIsInstance(clip, Clip)
        self.assertEqual(clip.name, name)

        # Test duration
        video_duration = clip.duration
        self.assertAlmostEqual(video_duration, duration_seconds,
                               delta=0.1)

    def test_CutFrom(self):
        timestamp = TimeStamp(seconds=5)

        # Create a test clip
        source = 'Бобер.mp4'
        name = 'TestClip'
        input_filter = VideoInput(source=source, name=name)
        clip = input_filter()

        # Apply CutFrom filter
        cut_filter = CutFrom(timestamp=timestamp, filter=input_filter)
        filtered_clip = cut_filter()

        self.assertIsInstance(filtered_clip, Clip)

        # Test duration
        probe = ffmpeg.probe(source)
        video_stream = next((stream for stream in probe['streams'] if
                             stream['codec_type'] == 'video'), None)

        original_duration = float(video_stream['duration'])
        filtered_duration = filtered_clip.duration

        expected_duration = original_duration - timestamp.to_seconds()

        self.assertAlmostEqual(filtered_duration, expected_duration,
                               delta=0.1)

    # Write similar test cases for the remaining filters

    def test_CutFrom(self):
        timestamp = TimeStamp(0, 0, 5)

        # Create a test clip
        source = 'Бобер.mp4'
        name = 'TestClip'
        input_filter = VideoInput(source=source, name=name)
        clip = input_filter()

        # Apply CutFrom filter
        cut_filter = CutFrom(timestamp=timestamp, filter=input_filter)
        filtered_clip = cut_filter()

        self.assertIsInstance(filtered_clip, Clip)

        # Test duration
        probe = ffmpeg.probe(source)
        video_stream = next((stream for stream in probe['streams'] if
                             stream['codec_type'] == 'video'), None)

        original_duration = float(video_stream['duration'])
        filtered_duration = filtered_clip.duration

        expected_duration = original_duration - timestamp.to_seconds()

        self.assertAlmostEqual(filtered_duration, expected_duration,
                               delta=0.1)


if __name__ == '__main__':
    unittest.main()