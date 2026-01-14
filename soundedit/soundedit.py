#!/usr/bin/env python3

import os
import signal
import vdf
import sys

from typing import Tuple
from vdf import VDFDict
from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow,
    QFileDialog, QTreeWidget, QTreeWidgetItem,
    QDockWidget, QMessageBox, QTabWidget,
    QHBoxLayout
)
from PySide6.QtCore import Qt, QSettings
from NodeGraphQt import (
    NodesPaletteWidget
)

from .graph import SoundOperatorGraph
from .types import StackType
from . import manifest


class SoundEdit(QMainWindow):
    """
    The main window for Source Sound Editor
    Contains a tool box, actions bar, menu and the graph itself
    """
    def __init__(self):
        super().__init__()
        self.data: VDFDict = {}
        self.graphs = {}
        self._setup_ui()

    
    """
    Load a sound operator stack
    """
    def load_operator_stack(self, file: str) -> Tuple[bool,str]:
        try:
            with open(file, 'r') as fp:
                return (self._load_operator_stack(vdf.load(fp, mapper=VDFDict)), '')
        except Exception as e:
            return (False, str(e))


    def open_tab(self, type: StackType, name: str) -> bool:
        """
        Load the specified stack in a new tab
        
        Parameters
        ----------
        type : StackType
            Type of stack this is. Start or Update
        name : str
            Name of the tab
        """
        if name in self.graphs:
            self.graphs[name].widget.raise_()
            return True
        graph = SoundOperatorGraph(self)
        stacks = self.data['start_stacks' if type == StackType.Start else 'update_stacks']
        graph.from_dict(stacks[name], stacks)
        
        w = QWidget(self)
        w.setLayout(QHBoxLayout())
        w.layout().addWidget(graph.widget)
        
        self.tabs.addTab(w, name)
        
        self.graphs[name] = graph
        #graph.widget.raise_()
        return True


    def close_tab(self, type: StackType, name: str):
        pass

    
    def _load_operator_stack(self, data: VDFDict) -> bool:
        self.data = data
        self._populate_list()
        return True

    
    """
    Populate the left bar list of operator stacks
    """
    def _populate_list(self):
        if 'start_stacks' in self.data:
            for stackName in self.data['start_stacks'].keys():
                stack = self.data['start_stacks'][stackName]
                item = QTreeWidgetItem(self.stackListStartStacks)
                item.setText(0, stackName)
                item.setData(0, Qt.ItemDataRole.UserRole, (StackType.Start, stackName))
        if 'update_stacks' in self.data:
            for stackName in self.data['update_stacks'].keys():
                stack = self.data['update_stacks'][stackName]
                item = QTreeWidgetItem(self.stackListUpdateStacks)
                item.setText(0, stackName)
                item.setData(0, Qt.ItemDataRole.UserRole, (StackType.Update, stackName))


    """
    Setup all UI widgets and such
    """
    def _setup_ui(self):
        self._setup_menu()
        self._setup_stack_list()
        self._setup_tabs()
        self._setup_toolbox()


    def _setup_toolbox(self):
        #self.toolbox = NodesPaletteWidget(self)
        #dock = QDockWidget('Toolbox')
        #dock.setWidget(self.toolbox)
        #self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
        pass


    def _setup_tabs(self):
        self.tabs = QTabWidget(self)
        self.tabs.setTabsClosable(True)
        self.setCentralWidget(self.tabs)
        
        gettingStarted = QWidget(self)
        self.tabs.addTab(gettingStarted, 'Getting Started')


    def _setup_stack_list(self):
        self.stackList = QTreeWidget(self)
        self.stackList.header().hide()
        self.stackListStartStacks = QTreeWidgetItem(self.stackList)
        self.stackListStartStacks.setText(0, 'Start stacks')
        self.stackListUpdateStacks = QTreeWidgetItem(self.stackList)
        self.stackListUpdateStacks.setText(0, 'Update stacks')
        self.stackList.itemDoubleClicked.connect(self._on_item_open)
        
        self.stackListStartStacks.setExpanded(True)
        self.stackListUpdateStacks.setExpanded(True)

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
    Called when the user wants to open some item
    """
    def _on_item_open(self, item: QTreeWidgetItem, col: int):
        try:
            type, name = item.data(0, Qt.ItemDataRole.UserRole)
            self.open_tab(type, name)
        except Exception as e:
            raise e


    """
    Called when we want to open a file
    """
    def _on_open(self, checked: bool):
        s = QSettings()
        fileName, _ = QFileDialog.getOpenFileName(
            self, 'Open operator stack', s.value('FileOpenLastDir', os.getcwd()),
            'Sound Operator Stacks (sound_operator_stacks.txt *.sndstack)'
        )
        if len(fileName) == 0:
            return

        s.setValue('FileOpenLastDir', os.path.dirname(fileName))

        success,err = self.load_operator_stack(fileName)
        if not success:
            QMessageBox.warning(self, 'Could not load file',
                f'Could not load operator stacks: {err}')


    """
    Called when we want to exit
    """
    def _on_exit(self, checked: bool):
        QApplication.exit(0)
