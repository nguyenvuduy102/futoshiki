from PyQt6.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtCore import QPropertyAnimation, QRect, Qt
from PyQt6.QtGui import QColor

class Button(QPushButton):
    def __init__(self, text, pos, parent, callback):
        super().__init__(text, parent)
        

        self.setFixedSize(360, 100)
        self.move(pos[0], pos[1])
        self.original_geometry = QRect(pos[0], pos[1], 360, 100)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.setStyleSheet("""
            QPushButton {
                color: black;
                background-color: #F4F4F6;
                font-size: 36px;
                border-radius: 15px;
            }
            QPushButton:hover {
                border: 8px solid;
                border-color: #246EB9;
            }
        """)


        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(15)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(self.shadow)


        self.clicked.connect(callback)

    def enterEvent(self, event):
 
          self.anim = QPropertyAnimation(self, b"geometry")
          self.anim.setDuration(150) 
          current = self.geometry()
          self.anim.setEndValue(QRect(current.x()-6, current.y()-6, current.width()+12, current.height()+12))
          self.anim.start()

    def leaveEvent(self, a0):
          self.anim.stop()
          
          self.anim.setEndValue(self.original_geometry)
          self.anim.start()
          super().leaveEvent(a0)


