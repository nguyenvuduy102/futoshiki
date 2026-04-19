from PyQt6.QtWidgets import QLabel, QWidget, QGraphicsDropShadowEffect
from PyQt6.QtCore import QEvent, QPoint, Qt
from PyQt6.QtGui import QColor, QKeyEvent, QMouseEvent
from PyQt6.QtCore import QPropertyAnimation, QRect

class Block(QLabel):
    def __init__(
        self, parent: QLabel, position: QPoint, block_size: QPoint, color
    ) -> None:
        super().__init__(parent)
        self.move(position.x(), position.y())
        self.value = 0
        self.block_size = block_size
        self.isFocus = False
        self.resize(block_size.x(), block_size.y())

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.original_geometry = QRect(position.x(), position.y(), block_size.x(), block_size.y())
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self._color = color
        self.text_color = "black"
        self.border_color = "#FF37A6"
        if color == "#56876D":
            self.text_color = "white"
            self.border_color = "#FFFFFF"
        self.hover_color = color.lstrip("#")
        
        self.setStyleSheet(
            f"""
            .Block
            {{
            background-color: {color};
            color: {self.text_color};
            font-size: 28px;
            font-weight: 600;
            }}
            .Block:hover {{
            background-color: #{self.hover_color};
            border: 4px solid;
            border-color: {self.border_color};
            }}
            .Block:focus {{
            border: 4px solid;
            border-color: {self.border_color};
            }}
            """
        )
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.setGraphicsEffect(shadow)
        self.setText("")
        self.isConstance = True
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def Update(self, value):
        self.value = value
        if value == 0:
            self.setText("")
            return
        self.setText(f"{value}")

    def enterEvent(self, event):
        if self.isFocus:
            return
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(150) 
        current = self.geometry()
        self.anim.setEndValue(QRect(current.x()-6, current.y()-6, current.width()+12, current.height()+12))
        self.anim.start()

    def leaveEvent(self, a0):
        if self.isFocus:
            return
        self.anim.stop()
        
        self.anim.setEndValue(self.original_geometry)
        self.anim.start()
        super().leaveEvent(a0)
    
    def keyPressEvent(self, ev: QKeyEvent) : # type: ignore
        if self.isConstance:
            return
        key = ev.text()
        if key.isdigit():
            num = int(key)
            if 1 <= num <= 6:
                self.setText(f"{num}")
        elif ev.key() in [Qt.Key.Key_Backspace, Qt.Key.Key_Delete]:
            self.setText("")
        return super().keyPressEvent(ev)
    

    def mousePressEvent(self, ev: QMouseEvent | None) -> None:
        self.isFocus = True
        self.setFocus()
        super().mousePressEvent(ev)

    def focusOutEvent(self, event): # type: ignore
        
        self.is_focused = False
        self.anim.stop()
        self.anim.setEndValue(self.original_geometry)
        self.anim.start()
        super().focusOutEvent(event)

    
    def SetConstance(self):
        self.setStyleSheet(
            f"""
            .Block
            {{
            background-color: {self._color};
            color: #4FD0FF;
            font-size: 28px;
            font-weight: 600;
            }}
            .Block:hover {{
            background-color: #{self.hover_color};
            border: 4px solid;
            border-color: {self.border_color};
            }}
            .Block:focus {{
            border: 4px solid;
            border-color: {self.border_color};
            }}
            """
        )