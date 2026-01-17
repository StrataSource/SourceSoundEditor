
import json
import os

from typing import Tuple, Dict

from .types import NodeType, NodeInputType, NodeOutputType, NodeManifest, NodeKeyValueType

class Manifest:
    """
    A game-specific manifest
    Describes all available nodes, their inputs, outputs and keyvalues
    """
    def __init__(self, file: str):
        self.manifest = file
        self._categories = set()
        self._load_manifest()

    def _load_manifest(self) -> None:
        with open(self.manifest, 'r') as fp:
            self.nodes: dict = json.load(fp)
            self.baseNode = self.node_type('__base')
            
            if self.baseNode is None:
                return

            # Unify __base with all other node types
            for k in self.nodes.keys():
                if k == '__base':
                    continue
                n = self.nodes[k]
                n['keyvalues'] += self.baseNode['keyvalues']
                n['outputs'] += self.baseNode['outputs']
                n['inputs'] += self.baseNode['inputs']
                if 'category' in n:
                    self._categories.add(n['category'])
                self.nodes[k] = n

    def node_type(self, type: str) -> NodeType|None:
        return self.node_types()[type] if type in self.node_types() else None

    def node_types(self) -> Dict[str, NodeType]:
        return self.nodes

    def input_desc(self, type: str) -> list[NodeInputType]:
        return self.nodes[type]['inputs']

    def output_desc(self, type: str) -> list[NodeOutputType]:
        return self.nodes[type]['outputs']

    def keyvalue_desc(self, type: str) -> list[NodeKeyValueType]:
        return self.nodes[type]['keyvalues']

    def categories(self) -> set[str]:
        return self._categories

                
GAMES = {
    'strata': Manifest(os.path.dirname(__file__) + '/games/strata.json')
}
_current = GAMES['strata']


def set_current(name: str):
    global _current
    _current = GAMES[name]


def current() -> Manifest:
    global _current
    return _current

def node_types() -> Dict[str, NodeType]:
    return current().nodes

def color_for_type(type: str) -> Tuple[int, int, int]:
    match type:
        case 'vec3':
            return (0, 255, 0)
        case 'float':
            return (255, 255, 0)
        case 'speakers':
            return (255, 0, 0)
        case 'vec3x8':
            return (255, 0, 255)
        case _:
            raise Exception('Invalid type name')
