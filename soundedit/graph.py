"""

Defines a visual representation of a sound operator stack

"""

from NodeGraphQt import (
    NodeGraph, BaseNode, Port
)
from PySide6.QtWidgets import (
    QTabWidget, QHBoxLayout
)
from PySide6 import QtCore

from vdf import VDFDict

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
        
        self._dirty = False

        self.property_changed.connect(lambda: self.mark_dirty())
        self.node_created.connect(lambda: self.mark_dirty())
        self.nodes_deleted.connect(lambda: self.mark_dirty())
        self.port_connected.connect(lambda: self.mark_dirty())
        self.port_disconnected.connect(lambda: self.mark_dirty())

    """Signaled when the dirty flag has been changed"""
    dirty_changed = QtCore.Signal(bool)

    def mark_dirty(self, dirty: bool = True, signal: bool = False) -> None:
        """
        Mark the dirty flag, signals the changed() event

        Parameters
        ----------
        dirty : bool
            True if dirty
        """
        self._dirty = dirty
        self.dirty_changed.emit(dirty)

    def dirty(self) -> bool:
        """Returns the status of the dirty flag"""
        return self._dirty

    def from_dict(self, opstack: VDFDict, all_opstacks: VDFDict):
        """
        Load an operator stack from a dict
        
        Parameters
        ----------
        opstack : dict
            The operator stack to load.
        """
        # Pass 0: find all import_stacks
        # TODO: Handling for this should be improved. import_stack's are a bit funny, they basically merge keyvalues sections
        #  for now we're just merging with no regard for the output. Not sure how else you'd represent this in the graph anyway
        for imp in opstack.get_all_for('import_stack'):
            data: VDFDict = all_opstacks[imp]
            for key in data.keys():
                if key in opstack:
                    opstack[key] = (0,data)
                else:
                    opstack[key] = data

        # Pass 1: create all nodes
        for node in opstack.keys():
            value = opstack[node]
            if isinstance(value, dict):
                self._create_node(node, opstack)
            elif isinstance(value, str):
                print('WARNING: unhandled import_stack operator')
                print(f'{node} = {opstack[node]}')

        # Pass 2: resolve connections
        for node in opstack.keys():
            value = opstack[node]
            if isinstance(value, dict):
                self._resolve(node, opstack)

        self.auto_layout_nodes()

    def _create_node(self, nodeName: str, opstack: VDFDict):
        """
        Creates a new named node from existing operator stack data
        
        Parameters
        ----------
        nodeName : str
            Name of the node
        opstack : VDFDict
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

    def _resolve(self, nodeName: str, opstack: VDFDict):
        """
        Resolves inter-node references
        
        Parameters
        ----------
        nodeName : str
            Name of the node
        opstack : VDFDict
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
