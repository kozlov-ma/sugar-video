from __future__ import annotations
import pathlib
from enum import Enum
from typing import Union, Callable, Any
import dearpygui.dearpygui as dpg
from ._node import add_node, Node, add_input, add_output, preview_node
from ..timestamp import TimeStamp
from ..filter import Filter, Noop, VideoInput, SpeedX, CutFrom, CutTo, Concat

WIDTH = 100
HEIGHT = 80


class NodeMenuBuilder:
    def __init__(self):
        self.nodes: dict[str, Callable[[Any, Any, int | str], int | str]] = {}

    def decorate(self, node_name: str):
        if node_name in self.nodes:
            raise ValueError

        def decorator(function: Callable[[int | str], int]):
            self.nodes[node_name] = lambda _sender, _app_data, user_data: function(user_data)
            return function

        return decorator

    def build(self, node_editor_tag: str):
        with dpg.menu(label='Nodes'):
            for node_name in self.nodes:
                dpg.add_menu_item(label=node_name, callback=self.nodes[node_name],
                                  user_data=node_editor_tag)


class NodeAttributeType(Enum):
    STATIC: int = dpg.mvNode_Attr_Static
    INPUT: int = dpg.mvNode_Attr_Input
    OUTPUT: int = dpg.mvNode_Attr_Output


class NodeAttributeContentType(Enum):
    TEXT = 0
    BUTTON = 1
    INPUT_TEXT = 2
    INPUT_FLOAT = 3


class NodeAttributeCallbackType(Enum):
    NONE = 0
    PREVIEW = 1
    SET_FIELD = 2
    LOAD_FILE = 3


class NodeAttribute:
    def __init__(self, name: str, filter_field: str | None, type: NodeAttributeType,
                 content_type: NodeAttributeContentType, callback_type: NodeAttributeCallbackType,
                 set_field_cast: Callable[[Any], Any] = lambda arg: arg):
        self.name: str = name
        self.filter_field: str | None = filter_field
        self.type: NodeAttributeType = type
        self.content_type = content_type
        self.callback_type = callback_type
        self.set_field_cast: Callable[[Any], Any] = set_field_cast


class NodeBuilder:
    def __init__(self, node_name: str, filter_creator: Callable[[], Filter]):
        self.node_name: str = node_name
        self.attributes: list[NodeAttribute] = []
        self.filter_creator: Callable[[], Filter] = filter_creator

    def add_input(self, text: str) -> NodeBuilder:
        self.attributes.append(NodeAttribute(text, None, NodeAttributeType.INPUT,
                                             NodeAttributeContentType.TEXT, NodeAttributeCallbackType.NONE))
        return self

    def add_output(self, text: str) -> NodeBuilder:
        self.attributes.append(NodeAttribute(text, None, NodeAttributeType.OUTPUT,
                                             NodeAttributeContentType.TEXT, NodeAttributeCallbackType.NONE))
        return self

    def add_static(self, text: str, *, filter_field: str | None = None,
                   set_field_cast: Callable[[Any], Any] = lambda arg: arg,
                   content_type: NodeAttributeContentType = NodeAttributeContentType.TEXT,
                   callback_type: NodeAttributeCallbackType = NodeAttributeCallbackType.NONE) -> NodeBuilder:
        self.attributes.append(NodeAttribute(text, filter_field, NodeAttributeType.STATIC,
                                             content_type, callback_type, set_field_cast))
        return self

    def build(self, parent: int | str) -> int:
        filter = self.filter_creator()

        with dpg.node(label=self.node_name, parent=parent) as node_id:
            add_node(Node(node_id, filter))
            for attribute in self.attributes:
                with dpg.node_attribute(label=attribute.name, attribute_type=attribute.type.value) as attribute_id:
                    self._add_content(attribute, node_id, attribute_id, filter)
                    self._add_attribute(attribute, node_id, attribute_id, filter)

        return node_id

    def _add_content(self, attribute: NodeAttribute, node_id: int | str,
                     attribute_id: int | str, filter: Filter):
        match attribute.content_type:
            case NodeAttributeContentType.TEXT:
                dpg.add_text(default_value=attribute.name)
            case NodeAttributeContentType.BUTTON:
                dpg.add_button(label=attribute.name,
                               callback=self._get_callback(attribute, node_id, attribute_id, filter))
            case NodeAttributeContentType.INPUT_TEXT:
                dpg.add_input_text(label=attribute.name, default_value='00:00:00', width=WIDTH,
                                   callback=self._get_callback(attribute, node_id, attribute_id, filter))
            case NodeAttributeContentType.INPUT_FLOAT:
                dpg.add_input_float(label=attribute.name, default_value=1, min_value=0.1, min_clamped=True,
                                    max_value=10, max_clamped=True, step=0.05, width=WIDTH,
                                    callback=self._get_callback(attribute, node_id, attribute_id, filter))

    def _get_callback(self, attribute: NodeAttribute, node_id: int | str,
                      attribute_id: int | str, filter: Filter) -> Callable[[Any, Any, Any], None]:
        match attribute.callback_type:
            case NodeAttributeCallbackType.NONE:
                return lambda _sender, _app_data, _user_data: None
            case NodeAttributeCallbackType.PREVIEW:
                return lambda _sender, _app_data, _user_data: preview_node(node_id)
            case NodeAttributeCallbackType.SET_FIELD:
                return lambda _sender, _app_data, _user_data: (
                    setattr(filter, attribute.filter_field, attribute.set_field_cast(_app_data)))
            case NodeAttributeCallbackType.LOAD_FILE:
                def callback(_, app_data):
                    dpg.set_value(f'video_name_{node_id}', app_data['file_name'])
                    filter.source = app_data['file_path_name']
                    filter.name = app_data['file_path_name'].split('.')[0].split('/')[-1]

                def cancel_callback():
                    print('Cancel...')

                with dpg.file_dialog(
                        directory_selector=False, show=False, callback=callback, tag=f"file_dialog_{node_id}",
                        cancel_callback=cancel_callback, width=700, height=400):
                    dpg.add_file_extension('.mp4', color=(100, 250, 40))

                return lambda: dpg.show_item(f"file_dialog_{node_id}")

    def _add_attribute(self, attribute: NodeAttribute, node_id: int | str,
                       attribute_id: int | str, filter: Filter) -> None:
        match attribute.type:
            case NodeAttributeType.INPUT:
                add_input(node_id, attribute_id)
            case NodeAttributeType.OUTPUT:
                add_output(node_id, attribute_id)


builder = NodeMenuBuilder()


builder.decorate('New Video Clip')(
    NodeBuilder('New Video Clip', lambda: VideoInput(pathlib.Path(''), ''))
    .add_static('Load video', content_type=NodeAttributeContentType.BUTTON,
                callback_type=NodeAttributeCallbackType.LOAD_FILE)
    .add_output('Result Video')
    .add_static('Preview Video', content_type=NodeAttributeContentType.BUTTON,
                callback_type=NodeAttributeCallbackType.PREVIEW)
    .build
)


@builder.decorate('Video Clip')
def create_video_clip_node(parent: Union[int, str] = None) -> Union[int, str]:
    filter = VideoInput(pathlib.Path('./Бобер.mp4'), 'Beaver')
    node_id = None

    def callback(_, app_data):
        print(app_data)
        dpg.set_value(f'video_name_{node_id}', app_data['file_name'])
        filter.source = app_data['file_path_name']
        filter.name = app_data['file_path_name'].split('.')[0].split('/')[-1]
        print(filter.name)
        print('aboba')

    def cancel_callback():
        print('Cancel...')

    with dpg.file_dialog(
            directory_selector=False, show=False, callback=callback, tag="file_dialog_id",
            cancel_callback=cancel_callback, width=700, height=400):
        dpg.add_file_extension('.mp4', color=(100, 250, 40))

    with dpg.node(label='Video Clip', parent=parent) as node_id:
        node = Node(node_id, filter)
        add_node(node)

        with dpg.node_attribute(label='Video Clip', attribute_type=dpg.mvNode_Attr_Output) as attribute_id:
            dpg.add_text(tag=f'video_name_{node_id}', default_value='Video not loaded')
            dpg.add_button(label='Load video file', callback=lambda: dpg.show_item("file_dialog_id"))
            add_output(node_id, attribute_id)

        with dpg.node_attribute(label='Preview Video', attribute_type=dpg.mvNode_Attr_Static):
            dpg.add_button(label='Preview video', callback=lambda: preview_node(node_id))

    return node_id


builder.decorate('Noop')(
    NodeBuilder('Noop', lambda: Noop())
    .add_input('Source Video')
    .add_output('Result Video')
    .add_static('Preview Video', content_type=NodeAttributeContentType.BUTTON,
                callback_type=NodeAttributeCallbackType.PREVIEW)
    .build
)

builder.decorate('Speed X')(
    NodeBuilder('Speed X', lambda: SpeedX(1.0))
    .add_static('X', filter_field='x', content_type=NodeAttributeContentType.INPUT_FLOAT,
                callback_type=NodeAttributeCallbackType.SET_FIELD)
    .add_input('Source')
    .add_output('Result')
    .add_static('Preview', content_type=NodeAttributeContentType.BUTTON,
                callback_type=NodeAttributeCallbackType.PREVIEW)
    .build
)

builder.decorate('Cut From')(
    NodeBuilder('Cut From', lambda: CutFrom(TimeStamp.from_str("00:00:00")))
    .add_static('Timestamp', filter_field='timestamp', set_field_cast=TimeStamp.from_str,
                content_type=NodeAttributeContentType.INPUT_TEXT,
                callback_type=NodeAttributeCallbackType.SET_FIELD)
    .add_input('Source Video')
    .add_output('Result Video')
    .add_static('Preview', content_type=NodeAttributeContentType.BUTTON,
                callback_type=NodeAttributeCallbackType.PREVIEW)
    .build
)

builder.decorate('Cut To')(
    NodeBuilder('Cut To', lambda: CutTo(TimeStamp.from_str("00:00:00")))
    .add_static('Timestamp', filter_field='timestamp', set_field_cast=TimeStamp.from_str,
                content_type=NodeAttributeContentType.INPUT_TEXT,
                callback_type=NodeAttributeCallbackType.SET_FIELD)
    .add_input('Source Video')
    .add_output('Result Video')
    .add_static('Preview', content_type=NodeAttributeContentType.BUTTON,
                callback_type=NodeAttributeCallbackType.PREVIEW)
    .build
)

builder.decorate('Concat')(
    NodeBuilder('Concat', lambda: Concat())
    .add_input('First Video')
    .add_input('Second Video')
    .add_output('Result Video')
    .add_static('Preview', content_type=NodeAttributeContentType.BUTTON,
                callback_type=NodeAttributeCallbackType.PREVIEW)
    .build
)
