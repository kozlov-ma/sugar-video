import pathlib
from typing import Union, Callable, Any
import dearpygui.dearpygui as dpg
from ._node import add_node, Node, add_input, add_output, preview_node, nodes
from ..timestamp import TimeStamp
from ..filter import Filter, Noop, VideoInput, SpeedX, CutFrom, CutTo, Concat, ImageInput

WIDTH = 100
HEIGHT = 80


class NodeMenuBuilder:
    def __init__(self):
        self.nodes: dict[str, Callable[[Any, Any, int | str], int | str]] = {}

    def decorate(self, node_name: str):
        def decorator(function: Callable[[int | str], int]):
            self.nodes[node_name] = lambda _sender, _app_data, user_data: function(user_data)
            return function

        return decorator

    def build(self, node_editor_tag: str):
        with dpg.menu(label='Nodes'):
            for node_name in self.nodes:
                dpg.add_menu_item(label=node_name, callback=self.nodes[node_name],
                                  user_data=node_editor_tag)


def add_result_video(node_id: int | str) -> None:
    with dpg.node_attribute(label='Result Video', attribute_type=dpg.mvNode_Attr_Output) as attribute_id:
        dpg.add_text(default_value='Result Video')
        add_output(node_id, attribute_id)


def add_preview_video(node_id: int | str) -> None:
    with dpg.node_attribute(label='Preview Video', attribute_type=dpg.mvNode_Attr_Static):
        dpg.add_button(label='Preview video', callback=lambda: preview_node(node_id))


builder = NodeMenuBuilder()


@builder.decorate('Node')
def create_node(parent: Union[int, str] = None) -> int:
    with dpg.node(parent=parent) as node_id:
        add_node(Node(node_id, None))

    return node_id


@builder.decorate('Video Clip')
def create_video_clip_node(parent: Union[int, str] = None) -> Union[int, str]:
    node = None
    node_id = None

    def callback(sender, app_data):
        print(app_data)
        dpg.set_value(f'video_name_{node_id}', app_data['file_name'])
        node.source = app_data['file_path_name']
        node.name = app_data['file_path_name']
        print('aboba')

    def cancel_callback():
        print('Cancel...')

    with dpg.file_dialog(
            directory_selector=False, show=False, callback=callback, tag="video_file_dialog",
            cancel_callback=cancel_callback, width=700, height=400):
        dpg.add_file_extension('.mp4', color=(100, 250, 40))

    with dpg.node(label='Video Clip', parent=parent) as node_id:
        node = Node(node_id, VideoInput(pathlib.Path('./Бобер.mp4'), 'Бобер'))
        add_node(node)

        with dpg.node_attribute(label='Video Clip', attribute_type=dpg.mvNode_Attr_Output) as attribute_id:
            dpg.add_text(tag=f'video_name_{node_id}', default_value='Video not loaded')
            dpg.add_button(label='Load video file', callback=lambda: dpg.show_item("video_file_dialog"))
            add_output(node_id, attribute_id)

        add_preview_video(node_id)

    node = node.filter
    return node_id


@builder.decorate('Noop')
def create_noop_filter_node(parent: Union[int, str] = None) -> Union[int, str]:
    with dpg.node(label='Noop Filter', parent=parent) as node_id:
        add_node(Node(node_id, Noop()))

        with dpg.node_attribute(label='Source Video', attribute_type=dpg.mvNode_Attr_Input) as attribute_id:
            dpg.add_text(default_value='Source Video')
            add_input(node_id, attribute_id)

        add_result_video(node_id)
        add_preview_video(node_id)

    return node_id


@builder.decorate('Speed X')
def create_speed_x_filter_node(parent: Union[int, str] = None) -> Union[int, str]:
    node = None

    def input_callback(sender, app_data):
        node.x = app_data

    with dpg.node(label='Speed X Filter', parent=parent) as node_id:
        node = Node(node_id, SpeedX(1.0))
        add_node(node)

        with dpg.node_attribute(label='X', attribute_type=dpg.mvNode_Attr_Static):
            dpg.add_input_float(label='X', default_value=1, min_value=0.1, min_clamped=True,
                                max_value=10, max_clamped=True, step=0.05, width=WIDTH, callback=input_callback)

        with dpg.node_attribute(label='Source Video', attribute_type=dpg.mvNode_Attr_Input) as attribute_id:
            dpg.add_text(default_value='Source Video')
            add_input(node_id, attribute_id)

        add_result_video(node_id)
        add_preview_video(node_id)

    node = node.filter

    return node_id


@builder.decorate('Cut From')
def create_cut_from_filter_node(parent: Union[int, str] = None) -> Union[int, str]:
    node = None

    def input_callback(sender, app_data: str):
        node.timestamp = TimeStamp.from_str(app_data)

    with dpg.node(label='Cut From Filter', parent=parent) as node_id:
        node = Node(node_id, CutFrom(TimeStamp.from_str("00:00:00")))
        add_node(node)

        with dpg.node_attribute(label='Timestamp', attribute_type=dpg.mvNode_Attr_Static):
            dpg.add_input_text(label='Timestamp', default_value='00:00:00', width=WIDTH, callback=input_callback)

        with dpg.node_attribute(label='Source Video', attribute_type=dpg.mvNode_Attr_Input) as attribute_id:
            dpg.add_text(default_value='Source Video')
            add_input(node_id, attribute_id)

        add_result_video(node_id)
        add_preview_video(node_id)

    node = nodes[node_id].filter

    return node_id


@builder.decorate('Cut To')
def create_cut_to_filter_node(parent: Union[int, str] = None) -> Union[int, str]:
    node = None

    def input_callback(sender, app_data: str):
        node.timestamp = TimeStamp.from_str(app_data)

    with dpg.node(label='Cut To Filter', parent=parent) as node_id:
        node = Node(node_id, CutTo(TimeStamp.from_str("00:00:00")))
        add_node(node)

        with dpg.node_attribute(label='Timestamp', attribute_type=dpg.mvNode_Attr_Static):
            dpg.add_input_text(label='Timestamp', default_value='00:00:00', width=WIDTH, callback=input_callback)

        with dpg.node_attribute(label='Source Video', attribute_type=dpg.mvNode_Attr_Input) as attribute_id:
            dpg.add_text(default_value='Source Video')
            add_input(node_id, attribute_id)

        add_result_video(node_id)
        add_preview_video(node_id)

    node = node.filter

    return node_id


@builder.decorate('Concat')
def create_concat(parent: int | str) -> int | str:
    node = None

    def smooth_concat_callback(sender: int | str, app_data: Any, user_data: Any) -> None:
        node.filter.smooth = app_data

    with dpg.node(label='Concat Filter', parent=parent) as node_id:
        node = Node(node_id, Concat())
        add_node(node)

        with dpg.node_attribute(label='First Video', attribute_type=dpg.mvNode_Attr_Input) as attribute_id:
            dpg.add_text(default_value='First Video')
            add_input(node_id, attribute_id)

        with dpg.node_attribute(label='Second Video', attribute_type=dpg.mvNode_Attr_Input) as attribute_id:
            dpg.add_text(default_value='Second Video')
            add_input(node_id, attribute_id)

        with dpg.node_attribute(label='Smooth Concat', attribute_type=dpg.mvNode_Attr_Static) as attribute_id:
            dpg.add_checkbox(label='Smooth Concat', callback=smooth_concat_callback)

        add_result_video(node_id)
        add_preview_video(node_id)

    return node_id


@builder.decorate('Image Input')
def create_image_filter(parent: int | str) -> int | str:
    filter = None
    node_id = None

    def callback(sender, app_data):
        print(app_data)
        dpg.set_value(f'image_name_{node_id}', app_data['file_name'])
        filter.source = app_data['file_path_name']
        filter.name = app_data['file_path_name']
        print('aboba')

    def cancel_callback():
        print('Cancel...')

    with dpg.file_dialog(
            directory_selector=False, show=False, callback=callback, tag="image_file_dialog",
            cancel_callback=cancel_callback, width=700, height=400):
        dpg.add_file_extension('.jpg', color=(200, 150, 40))
        dpg.add_file_extension('.png', color=(200, 150, 40))

    def duration_callback(sender: int | str, app_data: Any, user_data: Any) -> None:
        filter.duration_seconds = app_data

    with dpg.node(label='Image Input', parent=parent) as node_id:
        node = Node(node_id, ImageInput(pathlib.Path(''), '', 0))
        filter = node.filter
        add_node(node)

        with dpg.node_attribute(label='Duration', attribute_type=dpg.mvNode_Attr_Static) as attribute_id:
            dpg.add_input_int(label='Duration', callback=duration_callback, width=WIDTH)

        with dpg.node_attribute(label='Image', attribute_type=dpg.mvNode_Attr_Output) as attribute_id:
            dpg.add_text(tag=f'image_name_{node_id}', default_value='Image not loaded')
            dpg.add_button(label='Load image file', callback=lambda: dpg.show_item("image_file_dialog"))
            add_output(node_id, attribute_id)

        add_preview_video(node_id)

    return node_id
