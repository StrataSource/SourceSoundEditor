from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings
import sys
from .soundedit import SoundEdit

def main():
	app = QApplication(sys.argv)

	QApplication.setOrganizationName('Strata Source')
	QApplication.setApplicationName('Source Sound Editor')

    # Don't save to system registry on Windows
	QSettings.setDefaultFormat(QSettings.Format.IniFormat)

	window = SoundEdit()
	
	if len(sys.argv) > 1:
		window.load_operator_stack(sys.argv[1])
	
	window.show()
	
	app.exec_()
