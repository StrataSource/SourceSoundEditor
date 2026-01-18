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
        self.file = None
        self.dirty = None
        self._setup_ui()

    def load_operator_stack(self, file: str) -> Tuple[bool,str]:
        """
        Load a sound operator stack
        """
        try:
            with open(file, 'r') as fp:
                return (self._load_operator_stack(vdf.load(fp, mapper=VDFDict)), '')
        except Exception as e:
            return (False, str(e))


    def _update_window_title(self) -> None:
        """
        Updates the window title reflecting currently open file and "dirty" status
        """
        if self.file is None:
            self.setWindowTitle('Source Sound Editor - No File')
        else:
            self.setWindowTitle(f'Source Sound Editor - [{self.file}{"*" if self.dirty else ""}]')

    def mark_dirty(self, dirty: bool) -> None:
        """
        Mark the document as a whole dirty
        """
        self.dirty = dirty
        self._update_window_title()

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
        w.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        w.setLayout(QHBoxLayout())
        w.layout().addWidget(graph.widget)

        graph.dirty_changed.connect(lambda dirty: self.mark_dirty(dirty))

        self.tabs.addTab(w, name)
        
        self.graphs[name] = graph
        graph.widget.raise_()
        return True

    
    def _load_operator_stack(self, data: VDFDict) -> bool:
        self.data = data
        self._populate_list()
        return True


    def _populate_list(self):
        """Populate the left bar list of operator stacks"""
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

    def _setup_ui(self):
        """Setup the UI"""
        self._setup_menu()
        self._setup_stack_list()
        self._setup_tabs()
        self._update_window_title()

    def _setup_tabs(self):
        self.tabs = QTabWidget(self)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.setCentralWidget(self.tabs)
        
        gettingStarted = QWidget(self)
        self.tabs.addTab(gettingStarted, 'Getting Started')

    def _close_tab(self, tab: int):
        """Close a tab and remove the widget"""
        w = self.tabs.widget(tab)
        self.tabs.removeTab(tab)
        w.close()

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

    def _update_recents_menu(self):
        """Update entries on the recent files menu"""
        s = QSettings()
        recents = s.value('RecentFiles', [''])
        if isinstance(recents, list):
            recents.reverse()
        else:
            recents = []

        # Remove previously existing actions
        for a in self.recents_menu.actions():
            self.recents_menu.removeAction(a)

        for l in recents:
            if len(l) > 0:
                self.recents_menu.addAction(l).triggered.connect(lambda c, x=l: self._open_file(x))

    def _setup_menu(self):
        """
        Setup the top menu bar (File, Edit, Help, etc)
        """
        self.fileMenu = self.menuBar().addMenu('File')
        self.fileMenu.addAction('Open').triggered.connect(self._on_open)
        self.recents_menu = self.fileMenu.addMenu('Recent Files')
        self._update_recents_menu()
        self.fileMenu.addSeparator()
        self.fileMenu.addAction('Exit').triggered.connect(self._on_exit)

        self.helpMenu = self.menuBar().addMenu('Help')
        self.helpMenu.addAction('About')
        self.helpMenu.addAction('About Qt').triggered.connect(QApplication.aboutQt)


    def _on_item_open(self, item: QTreeWidgetItem, col: int):
        """Called when the user wants to open some item"""
        try:
            type, name = item.data(0, Qt.ItemDataRole.UserRole)
            self.open_tab(type, name)
        except Exception as e:
            raise e

    def _ask_save(self) -> bool:
        """
        Pops up an "ask save" dialog and returns if the caller should continue with their logic

        Returns
        -------
        bool :
            True if the user saved/discarded their changes, or if the file isn't dirty, and you may continue
        """
        if not self.dirty:
            return True

        return QMessageBox.question(
            self, 'Save Changes?', 'You have unsaved changes, would you like to save?',
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
        ) != QMessageBox.StandardButton.Cancel

    def _add_recent_file(self, file: str):
        """Add an entry to the recent files list"""
        s = QSettings()
        l = s.value('RecentFiles', [''])
        if not isinstance(l, list): # Safeguard, should never happen unless something is really borked
            l = [''] # Need to force a list of at least 2 length, otherwise list gets turned into a single string...
        while file in l: l.remove(file)
        l.append(file)
        s.setValue('RecentFiles', l)
        
    def _remove_recent_file(self, file: str):
        """Remove recent file from list"""
        s = QSettings()
        l = s.value('RecentFiles', ['', ''])
        if isinstance(l, list):
            l.remove(file)
        else:
            l = ['', '']
        s.setValue('RecentFiles', l)
        
    def _open_file(self, file: str) -> bool:
        """
        Open a specific file
        On success, adds the file to the 'recent files' list, updates the window title.
        Shows a message box on failure, and removes the entry from the recent files list.

        Returns
        -------
        bool :
            True on success
        """

        if not self._ask_save():
            return False

        self.file = None

        success, err = self.load_operator_stack(file)
        if not success:
            self._remove_recent_file(file)
            QMessageBox.warning(
                self, 'Could not load file',
                f'Could not load operator stacks: {err}'
            )
            return False

        self.file = file
        self._add_recent_file(file)
        self._update_window_title()
        self._update_recents_menu()
        return True

    def _on_open(self, checked: bool):
        """Called when we want to open a file"""

        if not self._ask_save():
            return

        s = QSettings()
        fileName, _ = QFileDialog.getOpenFileName(
            self, 'Open operator stack', s.value('FileOpenLastDir', os.getcwd()),
            'Sound Operator Stacks (sound_operator_stacks.txt *.sndstack)'
        )
        if len(fileName) == 0:
            return

        self._open_file(fileName)

    def _on_exit(self, checked: bool):
        """Called when we want to exit"""
        if self._ask_save():
            QApplication.exit(0)
