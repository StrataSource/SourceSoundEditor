
from PySide2.QtWidgets import (
	QApplication
)
from .soundedit import (
	SoundEdit
)
import sys

def main():
	app = QApplication(sys.argv)

	window = SoundEdit()
	
	if len(sys.argv) > 1:
		window.load_operator_stack(sys.argv[1])
	
	window.show()
	
	app.exec_()

main()