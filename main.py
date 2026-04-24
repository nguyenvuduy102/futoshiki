from PyQt6.QtWidgets import QApplication

import sys

from scene.game import Game

app = QApplication(sys.argv)

scene = Game()

scene.show()

app.exit(app.exec())
