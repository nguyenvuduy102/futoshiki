from PyQt6.QtWidgets  import QWidget
from PyQt6.QtCore import QPoint
from entities.board import Board
from entities.leftMenu import LeftMenu


class Game(QWidget):
  def __init__(self):
    super().__init__()
    self.setFixedSize(1920, 1080)
    self.setStyleSheet("""QWidget 
                    {
                    background-color: #EDF2EF;
                    }
                    """)
    self.board = Board(self, QPoint(4,4), QPoint(990, 280), 90, 60);
    
    self.SetupGame();
    self.leftmenu = LeftMenu(self, self.board, self)

    self.showFullScreen()

  
  def SetupGame(self):
    self.board.SetupGame() # type: ignore

  def Grid4x4(self):
    self.ClearOldBoard()
    self.board = Board(self, QPoint(4,4), QPoint(990, 280), 90, 60);
    self.board.SetupGame()
    self.board.show()
    self.board.update()
    self.leftmenu.Board = self.board 
    self.board.update()

  def Grid5x5(self):
    self.ClearOldBoard()
    self.board = Board(self, QPoint(5,5), QPoint(900, 190), 90, 60);
    self.board.SetupGame()
    self.board.show()
    self.board.update()
    self.leftmenu.Board = self.board 
    self.board.update()

  def Grid7x7(self):
    self.ClearOldBoard()
    self.board = Board(self, QPoint(7,7), QPoint(780, 80), 90, 50);
    self.board.SetupGame()
    self.board.show()
    self.board.update()
    self.leftmenu.Board = self.board 
    self.board.update()

  def Grid9x9(self):
    self.ClearOldBoard()
    self.board = Board(self, QPoint(9,9), QPoint(780, 80), 60, 50);
    self.board.SetupGame()
    self.board.show()
    self.board.update()
    self.leftmenu.Board = self.board 
    self.board.update()

  def ClearOldBoard(self):
    if hasattr(self, 'board') and self.board is not None:

        self.board.hide()
        self.board.deleteLater()
        self.board = None
    

    self.update()
 
  