from copyreg import constructor
from pickle import FALSE

from PyQt6.QtWidgets  import QWidget
from PyQt6.QtCore import QPoint
from entities.board import Board
from entities.leftMenu import LeftMenu
from entities.operator import Operator


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

  def Grid4x4(self, hasValue=True):
    self.ClearOldBoard()
    self.board = Board(self, QPoint(4,4), QPoint(990, 280), 90, 60);
    self.board.SetupGame(hasValue)
    self.board.show()
    self.board.update()
    self.leftmenu.Board = self.board 
    self.board.update()

  def Grid5x5(self, hasValue=True):
    self.ClearOldBoard()
    self.board = Board(self, QPoint(5,5), QPoint(900, 190), 90, 60);
    self.board.SetupGame(hasValue)
    self.board.show()
    self.board.update()
    self.leftmenu.Board = self.board 
    self.board.update()

  def Grid7x7(self, hasValue=True):
    self.ClearOldBoard()
    self.board = Board(self, QPoint(7,7), QPoint(780, 80), 90, 50);
    self.board.SetupGame(hasValue)
    self.board.show()
    self.board.update()
    self.leftmenu.Board = self.board 
    self.board.update()

  def Grid9x9(self, hasValue=True):
    self.ClearOldBoard()
    self.board = Board(self, QPoint(9,9), QPoint(780, 80), 60, 50);
    self.board.SetupGame(hasValue)
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

  def LoadBoardFromFile(self, filePath):
    try:
        with open(filePath, 'r') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        if not lines:
            return None, [], [], []

        gridSize = int(lines[0])
        n = gridSize
        
        gridRaw = lines[1 : 1 + n]
        hRaw = lines[1 + n : 1 + 2 * n]
        vRaw = lines[1 + 2 * n : 1 + 2 * n + (n - 1)]

        gridArray = [int(x) for row in gridRaw for x in row.split(',')]
        hArray    = [int(x) for row in hRaw for x in row.split(',')]
        vArray    = [int(x) for row in vRaw for x in row.split(',')]

        if gridSize == 4:
           self.Grid4x4(hasValue=False)
        elif gridSize == 5:
           self.Grid5x5(hasValue=False)
        elif gridSize == 7:
           self.Grid7x7(hasValue=False)
        elif gridSize == 9:
           self.Grid9x9(hasValue=False)
        else: return

        self.board.grid_value = [0] * self.board.total_cells
        self.board.constraits = {i: [] for i in range(self.board.total_cells)}

        
        for i in range(len(gridArray)):
           if gridArray[i] != 0:
              self.board.grid_value[i] = gridArray[i] 
              self.board.gridItems[i].setText(str(gridArray[i]))
              self.board.gridItems[i].isConstance = True 
           else:
              self.board.gridItems[i].SetConstance()
              self.board.gridItems[i].isConstance = False
              self.board.gridItems[i].setText("")

        
        currentIndex = 0
        for j in range(len(hArray)):
          type_str = ""
          if hArray[j] == -1: type_str = ">"
          elif hArray[j] == 1: type_str = "<"
          else:
              
              if (j + 1) % (gridSize - 1) == 0: currentIndex += 2
              else: currentIndex += 1
              continue

          newOperator = Operator(
                self.board,
                self.board.gridItems[currentIndex],
                self.board.gridItems[currentIndex + 1],
                type_str,
            )
          newOperator.show()
          self.board.operator.append(newOperator)
          self.board.constraits[currentIndex].append({"neighbor": currentIndex + 1, "type": type_str})
          reverse_type = "<" if type_str == ">" else ">"
          self.board.constraits[currentIndex + 1].append({"neighbor": currentIndex, "type": reverse_type})

          if (j + 1) % (gridSize - 1) == 0: currentIndex += 2
          else: currentIndex += 1

        
        for j in range(len(vArray)):
          type_str = ""
          realtype = ''
          if vArray[j] == -1: 
             type_str = "v"
             realtype = ">"
          elif vArray[j] == 1: 
             type_str = "^"
             realtype = "<"
          else: continue

          idx_top = j
          idx_bottom = j + gridSize 

          newOperator = Operator(
                self.board,
                self.board.gridItems[idx_top],
                self.board.gridItems[idx_bottom],
                type_str,
            )
          newOperator.show()
          self.board.operator.append(newOperator)

          
          self.board.constraits[idx_top].append({"neighbor": idx_bottom, "type": realtype})
          reverse_type = "<" if realtype == ">" else ">"
          self.board.constraits[idx_bottom].append({"neighbor": idx_top, "type": reverse_type}) 


    except Exception as e:
        print(f"Lỗi đọc file: {e}")
        return None, [], [], []
    

