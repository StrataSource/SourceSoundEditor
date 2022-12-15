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

from typing import Tuple


class SoundOperatorGraph(NodeGraph):
	
	def __init__(self, parent):
		super().__init__()
		self.nodes: dict = {}

		for type in manifest.current.get_node_types().keys():
			self.register_node(
				OperatorNode(type).__class__
			)
			
		self.register_node(
			FloatConstNode
		)


	def from_dict(self, opstack: dict):
		# Pass 1: create all nodes
		for node in opstack.keys():
			self._create_node(node, opstack)

		# Pass 2: resolve connections
		for node in opstack.keys():
			self._resolve(node, opstack)

		self.auto_layout_nodes()



	def _create_node(self, nodeName: str, opstack: dict):
		node = opstack[nodeName]
		operator = node['operator']
		n: OperatorNode = self.create_node(
			f'io.soundedit.operators.Operator_{operator}',
			name=operator
		)
		n.set_type(operator)
		self.nodes[nodeName] = n
		
		# Create any constant nodes for this node
		constNodeNum = 0
		for input in manifest.get_current().get_input_desc(operator):
			inpName = input['name']
			if not inpName in node:
				continue

			value: str = node[inpName]
			port: Port = n.get_input_port(inpName)
			if value.startswith('@'):
				continue
			
			constNodeType = 'FloatConstNode'
			if input['type'] == 'vec3':
				constNodeType = 'Vec3ConstNode'
			elif input['type'] == 'vec3x8':
				constNodeType = 'Vec3x8ConstNode'
			
			constNode: FloatConstNode = self.create_node(
				f'io.soundedit.consts.{constNodeType}'
			)
			constNode.set_value(value)
			constNode.set_name(f'const {constNodeNum}')
			
			constNodeNum += 1
			
			p = constNode.get_output_port()
			p.connect_to(
				port,
				push_undo=False
			)
			self.nodes[constNode.name()] = constNode


	def _resolve(self, nodeName: str, opstack: dict):
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