from PyQt5.QtGui import QPainter, QBrush, QPen, QColor
from PyQt5.QtCore import Qt, pyqtSignal, QRect
from PyQt5.QtWidgets import QLabel


class LabelWithDrawRect(QLabel):

    # define a signal that will fire every time a rectangle is drawn ...
    rectangleDrawn = pyqtSignal(int, int, int, int)  # x, y, width, height

    x = 0
    y = 0
    width = 0
    height = 0
    started_draw = False

    def __init__(self, parent=None):
        QLabel.__init__(self, parent)
        print('LabelWithDrawRect created')

    def paintEvent(self, event):
        super().paintEvent(event)  # do all the normal qLabel drawing

        # draw rectangle if big enough ...
        if self.width != 0 and self.height != 0:
            painter = QPainter(self)
            painter.begin(self)

            if not self.started_draw:
                painter.setOpacity(0.5)
                painter.fillRect(self.x, self.y, self.width, self.height, QBrush(Qt.darkGreen, Qt.SolidPattern))
                painter.setOpacity(1.0)

            pen = QPen()
            pen.setWidth(3)
            pen.setColor(Qt.green)
            painter.setPen(pen)
            painter.drawRect(self.x, self.y, self.width, self.height)

            painter.end()
    def mousePressEvent(self, event):
        self.started_draw = True
        self.x = event.pos().x()
        self.y = event.pos().y()
        return

    def mouseMoveEvent(self, event):
        if self.started_draw:
            self.width = event.pos().x() - self.x
            self.height = event.pos().y() - self.y
            self.update()

    def mouseReleaseEvent(self, event):
        self.started_draw = False
        self.update()
        self.rectangleDrawn.emit(self.x, self.y, self.width, self.height)

    def set_rectangle(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.update()

    def get_rectangle(self):
        return self.x, self.y, self.width, self.height