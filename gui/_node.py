from dataclasses import dataclass
from typing import Union, List, Dict, Callable
from enum import Enum


class NodeType(Enum):
    NONE_TYPE = 0,
    VIDEO_CLIP = 1,
    NOOP_FILTER = 2


@dataclass
class Link:
    id: Union[int, str]
    output_id: Union[int, str]
    input_id: Union[int, str]
    
    
@dataclass
class Input:
    id: Union[int, str]
    linked_node: Union[int, str, None]
    

@dataclass
class Output:
    id: Union[int, str]
    linked_node: List[Union[int, str]]


@dataclass
class Node:
    id: Union[int, str]
    node_type: NodeType
    input_link: Dict[Union[int, str], Input]
    output_links: Dict[Union[int, str], Output]
    
    
links: Dict[Union[int, str], Link] = {}
nodes: Dict[Union[int, str], Node] = {}


def log_decorator(function: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        print(args, kwargs, function)
        result = function(*args, **kwargs)
        
        print(links)
        print(nodes)
        
        return result
    
    return wrapper


@log_decorator
def add_node(node_id: Union[int, str], node_type: NodeType) -> None:
    nodes[node_id] = Node(node_id, node_type, {}, {})
    
    
@log_decorator
def add_link(link_id: Union[int, str], output_id: Union[int, str], input_id: Union[int, str]) -> None:
    link = Link(link_id, output_id, input_id)
    links[link_id] = link
    # TODO: Связь связывает не ноды, а нод атрибуты. Надо переделать это на нод атрибуты
    # nodes[output_id].output_links.append(link)
    # nodes[input_id].input_link = link
    

@log_decorator
def remove_link(link_id: Union[int, str]) -> None:
    link = links.pop(link_id)
    # TODO: Связь связывает не ноды, а нод атрибуты. Надо переделать это
    # nodes[link.input_id].input_link = None
    # nodes[link.output_id].output_links.remove(link)
    