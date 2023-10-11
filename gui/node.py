from typing import Union
import dearpygui.dearpygui as dpg
from _node import add_node, NodeType, add_input, add_output


def create_node(parent: Union[int, str] = None) -> int:
    with dpg.node(parent=parent) as node_id:
        pass
    
    add_node(node_id, NodeType.NONE_TYPE)
    
    return node_id


def create_video_clip_node(parent: Union[int, str] = None) -> Union[int, str]:
    with dpg.node(label='Video Clip', parent=parent) as node_id:
        with dpg.node_attribute(label='Video Clip', attribute_type=dpg.mvNode_Attr_Output) as attribute_id:
            dpg.add_text(default_value='Video not loaded')
            dpg.add_button(label='Load video file')
            add_output(node_id, attribute_id)
            
        with dpg.node_attribute(label='Preview Video', attribute_type=dpg.mvNode_Attr_Static):
            dpg.add_button(label='Preview video')
    
    add_node(node_id, NodeType.VIDEO_CLIP)
    
    return node_id


def create_noop_filter_node(parent: Union[int, str] = None) -> Union[int, str]:
    with dpg.node(label='Noop Filter', parent=parent) as node_id:
        with dpg.node_attribute(label='Source Video', attribute_type=dpg.mvNode_Attr_Input) as attribute_id:
            dpg.add_text(default_value='Source Video')
            add_input(node_id, attribute_id)
            
        with dpg.node_attribute(label='Result Video', attribute_type=dpg.mvNode_Attr_Output) as attribute_id:
            dpg.add_text(default_value='Result Video')
            add_output(node_id, attribute_id)

        with dpg.node_attribute(label='Preview Video', attribute_type=dpg.mvNode_Attr_Static):
            dpg.add_button(label='Preview video')
            
    add_node(node_id, NodeType.NOOP_FILTER)

    return node_id
