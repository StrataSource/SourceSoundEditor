
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
        self._load_manifest()


    def _load_manifest(self) -> None:
        with open(self.manifest, 'r') as fp:
            self.nodes: dict = json.load(fp)
            self.baseNode = self.get_node_type('__base')
            
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
                self.nodes[k] = n


    def get_node_type(self, type: str) -> NodeType|None:
        return self.get_node_types()[type] if type in self.get_node_types() else None


    def get_node_types(self) -> Dict[str, NodeType]:
        return self.nodes


    def get_input_desc(self, type: str) -> list[NodeInputType]:
        return self.nodes[type]['inputs']
        

    def get_output_desc(self, type: str) -> list[NodeOutputType]:
        return self.nodes[type]['outputs']


    def get_keyvalue_desc(self, type: str) -> list[NodeKeyValueType]:
        return self.nodes[type]['keyvalues']


                
GAMES = {
    'strata': Manifest(os.path.dirname(__file__) + '/games/strata.json')
}
current = GAMES['strata']


def set_current(name: str):
    global current
    current = GAMES[name]

    
def get_current() -> Manifest:
    global current
    return current


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
