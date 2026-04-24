
from tkinter import Label
from typing import Self

from PyQt6.QtWidgets import QLabel, QWidget, QGraphicsDropShadowEffect, QPushButton, QFileDialog
from PyQt6.QtCore import QPointF, QPoint, Qt, QCoreApplication
from PyQt6.QtGui import QColor
import random
from entities.button import Button
from entities.block import Block
from entities.board import Board
from entities.operator import Operator



class LeftMenu(QLabel):
  def __init__(self,  parent: QWidget, Board : Board, Game) -> None:
    super().__init__( parent)
    self.move(0,0)
    self.setFixedSize(600, 1080)
    self.Board = Board
    self._parent = parent
    self._game = Game
    self.solverWindow = False
    self.gridWindows = False
    self.setStyleSheet(
      """
      .LeftMenu {
      background-color: #56876D
      }
        """)
  
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(15)
    shadow.setXOffset(10)
    shadow.setYOffset(10)
    shadow.setColor(QColor(0, 0, 0, 60))
    self.setGraphicsEffect(shadow)
    self.title = QLabel(self._parent)
    self.title.setText("Futoshiki")
    self.title.move(12, 40)
    self.title.setFixedSize(570, 100)
    self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.title.setStyleSheet("""
        color: white;
        font-size: 82px;
        background-color: transparent;
    """)

    self.newGameBtn = Button("New Game", [120, 240], self._parent , lambda: self.Board.SetupGame())
    self.quitGameBtn = Button("Quit Game", [120, 840], self._parent,QCoreApplication.quit)
    self.solveBtn = Button("Solve",  [120, 390],self._parent, self.SolverBtn)
    self.finishBtn = Button("Finish",  [120, 540],self._parent, lambda: self.Board.CheckWin())

    self.solverCtn = QLabel(self._parent)
    self.solverCtn.move(420, 300)
    self.solverCtn.setFixedSize(460,640)
    self.solverCtn.raise_()
    self.solverCtn.setStyleSheet("""
      border-radius: 8px;
      background-color: #56876D; """)
    solverCtnShadow = self.create_shadow()
    self.solverCtn.setGraphicsEffect(solverCtnShadow)


    self.solverBtnCtn = []

    self.brutalBtn = Button("Brutal Force",  [470, 360],self._parent ,self.BrutalForceSolver)
    self.solverBtnCtn.append(self.brutalBtn)
    self.aBtn = Button("A*",  [470, 500], self._parent, self.AStarSolver)
    self.solverBtnCtn.append(self.aBtn)
    self.forwardBtn = Button("Forward",  [470, 640], self._parent, self.ForwardCheckingSolver)
    self.solverBtnCtn.append(self.forwardBtn)
    self.backwardBtn = Button("BackWard",  [470, 780], self._parent,self.BackWardSolver)
    self.solverBtnCtn.append(self.backwardBtn)

    for i in range(len(self.solverBtnCtn)):
      self.solverBtnCtn[i].hide()
      self.solverCtn.hide()

    self.gridBtn = Button("Grid",  [120, 690],self._parent , self.GridBtn)
    

    self.gridCtn = QLabel(self._parent)
    self.gridCtn.move(420, 40)
    self.gridCtn.setFixedSize(460,880)
    self.gridCtn.raise_()
    self.gridCtn.setStyleSheet("""
      border-radius: 8px;
      background-color: #56876D; """)
    gridCtnShadow = self.create_shadow()
    self.gridCtn.setGraphicsEffect(gridCtnShadow)

    self.gridBtnCtn = []
    self.clearGrid = Button("Clear",  [470, 80],self._parent , self.ClearGrid)
    self.gridBtnCtn.append(self.clearGrid)
    self.inputGrid = Button("Input Grid", [470, 220], self._parent, self.OpenFileDialog)
    self.gridBtnCtn.append(self.inputGrid)
    self.FourxFour = Button("4 x 4",  [470, 360],self._parent ,self.Grid4x4)
    self.gridBtnCtn.append(self.FourxFour)
    self.FivexFive = Button("5 x 5",  [470, 500],self._parent ,self.Grid5x5)
    self.gridBtnCtn.append(self.FivexFive)
    self.SevenxSeven = Button("7 x 7",  [470, 640],self._parent ,self.Grid7x7)
    self.gridBtnCtn.append(self.SevenxSeven)
    self.NinexNine = Button("9 x 9",  [470, 780],self._parent , self.Grid9x9)
    self.gridBtnCtn.append(self.NinexNine)


    for i in range(len(self.gridBtnCtn)):
      self.gridBtnCtn[i].hide()
      self.gridCtn.hide()

    self.progressBoard = QLabel(self._parent)
    self.progressBoard.setText("Solving ... Please Wait")
    self.progressBoard.setStyleSheet("""background-color: #56876D; font-size: 38px; border-radius: 4px """)
    self.progressBoard.setFixedSize(500, 140)
    self.progressBoard.move(710, 0)
    self.progressBoard.setAlignment(Qt.AlignmentFlag.AlignCenter)
    progressShadow = self.create_shadow()
    self.progressBoard.setGraphicsEffect(progressShadow)
    self.progressBoard.hide()


  def GridBtn(self):
    self.gridWindows = not self.gridWindows
    if self.gridWindows:
      self.gridCtn.raise_()
      self.gridCtn.show()
      for i in range(len(self.gridBtnCtn)):
        self.gridBtnCtn[i].show()
        self.gridBtnCtn[i].raise_()
    else:
      for i in range(len(self.gridBtnCtn)):
        self.gridBtnCtn[i].hide()
      self.gridCtn.hide()

  def ClearGrid(self):
    self.Board.delete_all_values()
    self.GridBtn()

  def Grid4x4(self):
    self._game.Grid4x4()
    self.GridBtn()

  def Grid5x5(self):
    self._game.Grid5x5()
    self.GridBtn()

  def Grid7x7(self):
    self._game.Grid7x7()
    self.GridBtn()

  def Grid9x9(self):
    self._game.Grid9x9()
    self.GridBtn()


  def BrutalForceSolver(self):
    self.progressBoard.show()
    self.progressBoard.raise_()
    self.SolverBtn()
    QCoreApplication.processEvents()
    self.Board.BrutalForceSolver()
    self.progressBoard.hide()
    
    
  def ForwardCheckingSolver(self):
    self.progressBoard.show()
    self.progressBoard.raise_()
    self.SolverBtn()
    QCoreApplication.processEvents()
    self.Board.ForwardCheckingSolver()
    self.progressBoard.hide()
    

  def AStarSolver(self):
    self.progressBoard.show()
    self.progressBoard.raise_()
    self.SolverBtn()
    QCoreApplication.processEvents()
    self.Board.AStarSolver()
    self.progressBoard.hide()
    

  def BackWardSolver(self):
    self.progressBoard.show()
    self.progressBoard.raise_()
    self.SolverBtn()
    QCoreApplication.processEvents()
    self.Board.BackwardSolver()
    self.progressBoard.hide()
    


  def SolverBtn(self):
    self.solverWindow = not self.solverWindow
    if self.solverWindow:
      self.solverCtn.raise_()
      self.solverCtn.show()
      for i in range(len(self.solverBtnCtn)):
        self.solverBtnCtn[i].show()
        self.solverBtnCtn[i].raise_()
      
      
    else:
      for i in range(len(self.solverBtnCtn)):
        self.solverBtnCtn[i].hide()
      self.solverCtn.hide()


    

  def create_shadow(self):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(15)
    shadow.setXOffset(0)
    shadow.setYOffset(0)
    shadow.setColor(QColor(0, 0, 0, 120))
    return shadow
  

  def OpenFileDialog(self):
    fileName, _ = QFileDialog.getOpenFileName(
        self, 
        "Chọn file bàn cờ Futoshiki", 
        "", 
        "Text Files (*.txt);;All Files (*)"
    )
    
    if fileName:
        print(f"Đã chọn file: {fileName}")
        self.GridBtn()
        self._game.LoadBoardFromFile(fileName)
  

   