"""

Defines a visual representation of a sound operator stack

"""

from NodeGraphQt import (
    NodeGraph, BaseNode, Port
)
from PySide2.QtWidgets import (
    QTabWidget, QHBoxLayout
)

from . import manifest, nodes, types
from . nodes import (
    OperatorNode, FloatConstNode
)

from typing import Tuple, TypedDict


class SoundOperatorGraph(NodeGraph):
    """
    Main graph for the sound editor
    Registers all required node types and manages the editor
    """
    
    def __init__(self, parent):
        super().__init__()
        self.nodes: dict = {}

        # Register all node types
        for type in manifest.current.get_node_types().keys():
            self.register_node(
                OperatorNode(type).__class__
            )
            
        self.register_node(
            FloatConstNode
        )


    def from_dict(self, opstack: dict):
        """
        Load an operator stack from a dict
        
        Parameters
        ----------
        opstack : dict
            The operator stack to load.
        """
        # Pass 1: create all nodes
        for node in opstack.keys():
            self._create_node(node, opstack)

        # Pass 2: resolve connections
        for node in opstack.keys():
            self._resolve(node, opstack)

        self.auto_layout_nodes()



    def _create_node(self, nodeName: str, opstack: dict):
        """
        Creates a new named node from existing operator stack data
        
        Parameters
        ----------
        nodeName : str
            Name of the node
        opstack : dict
            Dictionary of operator stack data
        """
        node = opstack[nodeName]
        operator = node['operator']
        n: OperatorNode = self.create_node(
            f'io.soundedit.operators.Operator_{operator}',
            name=operator
        )
        n.set_type(operator)
        self.nodes[nodeName] = n
        
        # Create any constant nodes
        constNodeNum = 0
        for input in manifest.get_current().get_input_desc(operator):
            inpName = input['name']
            if not inpName in node:
                continue

            value: str = node[inpName]
            port: Port = n.get_input_port(inpName)
            if value.startswith('@'):
                continue
            
            n.set_input_const(inpName, value)
            
        # Set keyvalues
        for kv in manifest.get_current().get_keyvalue_desc(operator):
            if kv['name'] not in node:
                continue
            n.set_widget_value(kv['name'], node[kv['name']])


    def _resolve(self, nodeName: str, opstack: dict):
        """
        Resolves inter-node references
        
        Parameters
        ----------
        nodeName : str
            Name of the node
        opstack : dict
            Dictionary of operator stack data
        """
        operator = opstack[nodeName]['operator']
        node = opstack[nodeName]
        
        for input in manifest.get_current().get_input_desc(operator):
            inputName = input['name']
            if not inputName in node or not node[inputName].startswith('@'):
                continue
            
            value: str = node[inputName]
            otherName, outName = self._split_input_str(value)
            
            other: OperatorNode = self.nodes[otherName]
            p: Port = other.get_output_port(outName)
            i: Port = self.nodes[nodeName].get_input_port(inputName)
            p.connect_to(
                i,
                push_undo=False
            )
            
            
    def _split_input_str(self, value: str) -> Tuple[str, str]: # (nodeName, outputName)
        value = value.removeprefix('@')
        vals = value.split('.')
        return (vals[0], vals[1])
