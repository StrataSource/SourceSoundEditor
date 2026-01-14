from PySide6.QtWidgets import QApplication
import sys
from .soundedit import SoundEdit

def main():
	app = QApplication(sys.argv)

	window = SoundEdit()
	
	if len(sys.argv) > 1:
		window.load_operator_stack(sys.argv[1])
	
	window.show()
	
	app.exec_()
