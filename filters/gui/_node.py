import os
from dataclasses import dataclass
from typing import Union, List, Dict, Callable, Any
from enum import Enum
from ..filter import Filter, Noop, VideoInput, SpeedX, CutFrom, CutTo


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
    filter: Filter
    inputs: list[Input]
    outputs: list[Output]

    def __init__(self, id: int | str, filter: Filter):
        self.id = id
        self.filter = filter
        self.inputs = []
        self.outputs = []


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
        print(inputs)
        print(outputs)

        return result

    return wrapper


@log_decorator
def add_node(node: Node) -> None:
    nodes[node.id] = node


@log_decorator
def add_input(node_id: Union[int, str], input_id: Union[int, str]) -> None:
    inputs[input_id] = Input(input_id, node_id, None)
    nodes[node_id].inputs.append(inputs[input_id])


@log_decorator
def add_output(node_id: Union[int, str], output_id: Union[int, str]) -> None:
    outputs[output_id] = Output(output_id, node_id, [])
    nodes[node_id].outputs.append(outputs[output_id])


@log_decorator
def add_link(link_id: Union[int, str], output_id: Union[int, str], input_id: Union[int, str]) -> None:
    link: Link = Link(link_id, output_id, input_id)
    links[link_id] = link
    outputs[output_id].linked_nodes.append(inputs[input_id].owner_node)
    inputs[input_id].linked_node = outputs[output_id].owner_node
    nodes[inputs[input_id].owner_node].filter.set_filter(nodes[outputs[output_id].owner_node].filter,
                                                  nodes[inputs[input_id].owner_node].inputs.index(inputs[input_id]))
    print('called add link', nodes[inputs[input_id].owner_node].filter)


@log_decorator
def remove_link(link_id: Union[int, str]) -> None:
    link: Link = links.pop(link_id)
    outputs[link.output_id].linked_nodes.remove(inputs[link.input_id].owner_node)
    inputs[link.input_id].linked_node = None


@log_decorator
def preview_node(node_id: Union[int, str]) -> None:
    node: Node = nodes[node_id]
    clip = node.filter()
    if clip is None:
        print('No content')
    file = clip.source
    os.system(f'open "{file}"')
