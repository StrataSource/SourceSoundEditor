"""

Defines a visual representation of a sound operator stack

"""

from NodeGraphQt import (
	NodeGraph, BaseNode
)
from PySide2.QtWidgets import (
	QTabWidget, QHBoxLayout
)

from . import manifest, nodes, types
from . nodes import (
	OperatorNode
)

class SoundOperatorGraph(NodeGraph):
	
	def __init__(self, parent):
		super().__init__()
		
		for type in manifest.current.get_node_types().keys():
			self.register_node(
				nodes.OperatorNode(type).__class__
			)


	def from_dict(self, opstack: dict):
		# Pass 1: create all nodes
		nodes: list[OperatorNode] = []
		print(opstack)
		for node in opstack.keys():
			operator = opstack[node]['operator']
			n: BaseNode = self.create_node(
				f'io.soundedit.operators.{operator}.OperatorNode',
				name=node
			)
			nodes.append(n)
		self.auto_layout_nodes(nodes)

			
			
		
