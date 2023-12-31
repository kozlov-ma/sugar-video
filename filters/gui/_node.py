import os
from dataclasses import dataclass
from typing import Union, List, Dict, Callable, Any
from enum import Enum
from ..filter import Filter, Noop, VideoInput, SpeedX, CutFrom, CutTo


class NodeType(Enum):
    NONE_TYPE = 0,
    VIDEO_CLIP = 1,
    NOOP_FILTER = 2,
    SPEED_X_FILTER = 3,
    CUT_FROM = 4,
    CUT_TO = 5


@dataclass
class Link:
    id: Union[int, str]
    output_id: Union[int, str]
    input_id: Union[int, str]


@dataclass
class Input:
    id: Union[int, str]
    owner_node: Union[int, str]
    linked_node: Union[int, str, None]


@dataclass
class Output:
    id: Union[int, str]
    owner_node: Union[int, str]
    linked_nodes: List[Union[int, str]]


@dataclass
class Node:
    id: Union[int, str]
    node_type: NodeType
    filter: Filter


links: Dict[Union[int, str], Link] = {}
nodes: Dict[Union[int, str], Node] = {}
inputs: Dict[Union[int, str], Input] = {}
outputs: Dict[Union[int, str], Output] = {}


def log_decorator(function: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        print(args, kwargs, function)
        result: Any = function(*args, **kwargs)

        print(links)
        print(nodes)

        return result

    return wrapper


@log_decorator
def add_node(node_id: Union[int, str], node_type: NodeType, **kwargs) -> None:
    f = None

    match node_type:
        case NodeType.VIDEO_CLIP:
            f = VideoInput(kwargs['path'])
        case NodeType.NOOP_FILTER:
            f = Noop()
        case NodeType.SPEED_X_FILTER:
            f = SpeedX(kwargs['x'])
        case NodeType.CUT_FROM:
            f = CutFrom(kwargs['timestamp'])
        case NodeType.CUT_TO:
            f = CutTo(kwargs['timestamp'])

    print(f)
    nodes[node_id] = Node(node_id, node_type, f)


@log_decorator
def add_input(node_id: Union[int, str], input_id: Union[int, str]) -> None:
    inputs[input_id] = Input(input_id, node_id, None)


@log_decorator
def add_output(node_id: Union[int, str], output_id: Union[int, str]) -> None:
    outputs[output_id] = Output(output_id, node_id, [])


@log_decorator
def add_link(link_id: Union[int, str], output_id: Union[int, str], input_id: Union[int, str]) -> None:
    link: Link = Link(link_id, output_id, input_id)
    links[link_id] = link
    outputs[output_id].linked_nodes.append(inputs[input_id].owner_node)
    inputs[input_id].linked_node = outputs[output_id].owner_node
    nodes[inputs[input_id].owner_node].filter.filter = nodes[outputs[output_id].owner_node].filter
    print('called add link', nodes[inputs[input_id].owner_node].filter.filter)


@log_decorator
def remove_link(link_id: Union[int, str]) -> None:
    link: Link = links.pop(link_id)
    outputs[link.output_id].linked_nodes.remove(inputs[link.input_id].owner_node)
    inputs[link.input_id].linked_node = None


@log_decorator
def preview_node(node_id: Union[int, str]) -> None:
    node: Node = nodes[node_id]
    file = node.filter().file_name()
    os.system(f'open "{file}"')
