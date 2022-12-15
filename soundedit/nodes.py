
from NodeGraphQt import (
	BaseNode, Port
)
from NodeGraphQt.widgets.node_widgets import (
	NodeLineEdit, NodeBaseWidget
)

from PySide2.QtWidgets import (
	QLineEdit
)
from PySide2.QtGui import (
	QDoubleValidator
)

from . import manifest


"""
Defines a generic sound operator
"""
class OperatorNode(BaseNode):
	
	NODE_NAME = 'new operator'
	__identifier__ = 'io.soundedit.operators'

	def __init__(self, type: str = None):
		super().__init__()
		self.in_ports = {}
		self.out_ports = {}


	def set_type(self, type: str):
		layout = manifest.get_current().get_node_types()[type]
		self.type = type
		
		self.in_ports = {}
		self.out_ports = {}

		for o in layout['outputs']:
			print(o)
			name = o['name']
			self.out_ports[name] = self.add_output(
				name=name,
				color=manifest.color_for_type(o['type'])
			)

		for i in layout['inputs']:
			name = i['name']
			self.in_ports[name] = self.add_input(
				name=name,
				color=manifest.color_for_type(i['type'])
			)
			self.add_text_input(
				name=name,
				label=name,
				tab=name,
				text='1.0' # TODO: Defaults!!!
			)


	def on_input_connected(self, in_port: Port, out_port: Port):
		w: QLineEdit = self.get_widget(in_port.name()).get_custom_widget()
		w.setDisabled(True)
		return super().on_input_connected(in_port, out_port)


	def on_input_disconnected(self, in_port, out_port):
		w: QLineEdit = self.get_widget(in_port.name()).get_custom_widget()
		w.setDisabled(False)
		return super().on_input_disconnected(in_port, out_port)


	def set_input_const(self, input: str, value: str):
		"""
		Set an input constant for the specified input
		This will set the line edit's value
		
		Args:
			str: Input name
			str: Value text
		"""
		w: QLineEdit = self.get_widget(input).get_custom_widget()
		w.setText(value)



	def get_input_port(self, name: str) -> Port:
		return self.in_ports[name]
		
		
	def get_output_port(self, name: str) -> Port:
		return self.out_ports[name]


	def __new__(metacls, typ: str = None):
		"""
		Returns new instance of OperatorNode.
		Generates a new metatype with a unique name so we can use this single class
		for multiple node types, dynamically added via the manifest.
		
		Args:
			str: The type of the operator node
		"""
		if typ is not None:
			# Generate new type
			metacls = type(f'Operator_{typ}', (OperatorNode,), {
				'opType_': typ,
				'__identifier__': f'io.soundedit.operators'
			})
		
		c = object.__new__(metacls)
		return c


"""
Defines a node that simply supplies a constant
"""
class FloatConstNode(BaseNode):
	
	__identifier__ = 'io.soundedit.consts'
	NODE_NAME = 'float const'
	
	def __init__(self):
		super().__init__()
		
		self.outPort_ = self.add_output(
			name='output',
			color=manifest.color_for_type('float')
		)
		
		self.add_text_input(
			name='value',
			label='value',
			text='1.0'
		)
		
		edit: QLineEdit = self.get_widget('value').get_custom_widget()
		edit.setValidator(QDoubleValidator(edit))


	def set_value(self, value: str):
		edit: QLineEdit = self.get_widget('value').get_custom_widget()
		edit.setText(value)


	def get_output_port(self):
		return self.outPort_
