
from NodeGraphQt import (
	BaseNode
)

from . import manifest


"""
Defines a generic sound operator
"""
class OperatorNode(BaseNode):
	
	NODE_NAME = 'new operator'
	__identifier__ = f'io.soundedit.operators'

	def __init__(self, type: str = None):
		super().__init__()
		
		layout = manifest.get_current().get_node_types()[__class__.opType_]
		
		self.in_ports = {}
		self.out_ports = {}

		for o in layout['outputs']:
			name = o['name']
			self.out_ports[name] = self.add_output(
				name,
				color=manifest.color_for_type(o['type'])
			)

		for i in layout['inputs']:
			name = i['name']
			self.in_ports[name] = self.add_input(
				name,
				color=manifest.color_for_type(i['type'])
			)


	def __new__(metacls, type: str = None):
		if type is not None:
			metacls.__identifier__ = f'io.soundedit.operators.{type}'
			metacls.opType_ = type
		c = object.__new__(metacls)
		return c


"""
Defines a node that simply supplies a constant
"""
class ConstNode(BaseNode):
	
	def __init__(self):
		super().__init__()
