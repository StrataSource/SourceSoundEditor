
from typing import TypedDict, Literal, Dict

class StackType:
    Start = 0
    Update = 1


class NodeKeyValueType(TypedDict):
    """
    Describes a single key value for a node
    """
    name: str
    type: Literal['bool', 'float', 'int', 'implcit_bool', 'enum']
    choices: list[str]|None
    default: str
    

class NodeIOType(TypedDict):
    """
    Describes an input or output for a node
    """
    name: str
    type: Literal['float', 'vec3', 'vec3x8', 'speakers']
    default: str
    

class NodeInputType(NodeIOType):
    """
    An input -- Unique type from NodeIOType to be more specific
    """
    pass


class NodeOutputType(NodeIOType):
    """
    An output -- Unique type from NodeIOType to be more specific
    """
    pass


class NodeType(TypedDict):
    """
    Describes a node's key values, inputs, outputs and any additional info
    """
    label: str
    desc: str|None
    inputs: list[NodeInputType]
    outputs: list[NodeOutputType]
    keyvalues: list[NodeKeyValueType]


class NodeManifest(TypedDict):
    """
    The node manifest
    """
    game: str
    nodes: Dict[str, NodeType]
    
