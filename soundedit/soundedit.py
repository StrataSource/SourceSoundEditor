#!/usr/bin/env python3

import os
import signal
import vdf
import sys

from typing import Tuple
from PyQt5 import Qt, QtCore, QtWidgets
from PyQt5.QtWidgets import (
	QApplication, QWidget, QMainWindow,
	QFileDialog, QTreeWidget, QTreeWidgetItem,
	QDockWidget, QMessageBox
)
from PyQt5.QtCore import Qt

from .graph import SoundOperatorGraph

class SoundEdit(QMainWindow):
	
	def __init__(self):
		super().__init__()
		self.data = {}
		self._setup_ui()
	
	"""
	Load a sound operator stack
	"""
	def load_file(self, file: str) -> Tuple[bool,str]:
		try:
			with open(file, 'r') as fp:
				return (self._load_dict(vdf.load(fp)), '')
		except Exception as e:
			return (False, str(e))

	
	def _load_dict(self, data: dict) -> bool:
		self.data = data
		self._populate_list()
		
	
	"""
	Populate the left bar list of operator stacks
	"""
	def _populate_list(self):
		if 'start_stacks' in self.data:
			for stackName, stack in self.data['start_stacks']:
				item = QTreeWidgetItem(self.stackListStartStacks)
				item.setText(0, stackName)
				item.setData(0, Qt.ItemDataRole.UserRole, stackName)
		if 'update_stacks' in self.data:
			for stackName, stack in self.data['update_stacks']:
				item = QTreeWidgetItem(self.stackListUpdateStacks)
				item.setText(0, stackName)
				item.setData(0, Qt.ItemDataRole.UserRole, stackName)
	
	
	def _setup_ui(self):
		self._setup_menu()
		self._setup_stack_list()


	def _setup_stack_list(self):
		self.stackList = QTreeWidget(self)
		self.stackList.header().hide()
		self.stackListStartStacks = QTreeWidgetItem(self.stackList)
		self.stackListStartStacks.setText(0, 'Start stacks')
		self.stackListUpdateStacks = QTreeWidgetItem(self.stackList)
		self.stackListUpdateStacks.setText(0, 'Update stacks')

		dock = QDockWidget('Operator Stacks', self)
		dock.setWidget(self.stackList)
		self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)


	"""
	Setup the top menu bar (File, Edit, Help, etc)
	"""
	def _setup_menu(self):
		self.fileMenu = self.menuBar().addMenu('File')
		self.fileMenu.addAction('Open').triggered.connect(self._on_open)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction('Exit').triggered.connect(self._on_exit)

		self.helpMenu = self.menuBar().addMenu('Help')
		self.helpMenu.addAction('About')
		self.helpMenu.addAction('About Qt').triggered.connect(QApplication.aboutQt)


	"""
	Called when we want to open a file
	"""
	def _on_open(self, checked: bool):
		fileName = QFileDialog.getOpenFileName(
			self, 'Open operator stack', os.getcwd(),
			'Sound Operator Stacks (*.txt *.sndstack)'
		)
		if len(fileName) == 0:
			return
		result = self.load_file(fileName)
		if not result[0]:
			QMessageBox.warning(self, 'Could not load file',
				f'Could not load operator stacks: {result[1]}')


	"""
	Called when we want to exit
	"""
	def _on_exit(self, checked: bool):
		QApplication.exit(0)



if __name__ == '__main__':
	app = QApplication(sys.argv)
	
	window = SoundEdit()
	window.show()
	
	app.exec_()