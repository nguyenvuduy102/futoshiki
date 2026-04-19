import random

from PyQt6.QtWidgets import QLabel, QWidget, QGraphicsDropShadowEffect
from PyQt6.QtCore import QEvent, QPoint, Qt
class Operator(QLabel):
    def __init__(self, parent, blockA, blockB, type=">"):
        super().__init__(parent)
        self.blockA = blockA 
        self.blockB = blockB
        self.type = type     
        
        self.setFixedSize(16, 40)
        self.setStyleSheet("""
        .Operator {
          color: black;
          font-size: 26px;
            background-color: none;
                           font-weight: bold;
        }
        """)

        self.setText(self.type)
        self.CalculatePosition() 


    def CalculatePosition(self):

        rectA = self.blockA.geometry()
        rectB = self.blockB.geometry()
        

        centerA_X = rectA.x() + rectA.width() // 2
        centerA_Y = rectA.y() + rectA.height() // 2
        
        centerB_X = rectB.x() + rectB.width() // 2
        centerB_Y = rectB.y() + rectB.height() // 2
        
        # 3. Tính trung điểm giữa hai tâm
        midX = (centerA_X + centerB_X) // 2
        midY = (centerA_Y + centerB_Y) // 2
        

        self.move(midX - self.width() // 2, midY - self.height() // 2)