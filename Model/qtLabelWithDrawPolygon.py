from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QPolygon, QFont
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QPoint
from PyQt5.QtWidgets import QLabel


class LabelWithDrawPolygon(QLabel):

    # define a signal that will fire every time a polygon is drawn ...x
    # parameter is a QPolygon (look at method debug_polygon to see how to get data out of it)
    polygonDrawn = pyqtSignal('PyQt_PyObject')

    Allow_drawing= False  #used to track if draw polygons button has been pressed

    started_draw = False  # used to track that the polygon drawing has started

    # the cordinates of the mouse when the mouse is moving about and the last poligon line isnt deturmed yet (drawn in red)
    x = None
    y = None

    polygon = QPolygon()  # used to hold the polygon data
    polygon_dict = {}  # used to hold the polygon data in a dictionary format

    def __init__(self, parent=None):

        QLabel.__init__(self, parent)
        print('LabelWithDrawRect created')
        self.setMouseTracking(True)  # need to do this, so we get mouseMoveEvent without mouse buttons being pressed

        self.brush = QBrush(QColor(0, 255, 0, 100))  # the polygon fill colour - green - semi transparent

        # sides of polygon (whilst being draw) ..
        self.green_pen = QPen()
        self.green_pen.setWidth(3)
        self.green_pen.setColor(Qt.green)

        self.red_pen = QPen()
        self.red_pen.setWidth(2)
        self.red_pen.setColor(Qt.red)

        self.text_font = QFont('Arial', 12, QFont.Bold)

    def paintEvent(self, event):
        super().paintEvent(event)  # do all the normal qLabel drawing

        # draw polygon or lines if started ...loop through array of polygons
        if self.polygon is not None:
            painter = QPainter(self)
            painter.begin(self)
            painter.setBrush(self.brush)

            # draw complete filled poloygon (if not started) ...
            for zone,(polygon_coords, polygon) in self.polygon_dict.items():
                painter.drawPolygon(polygon) #draw the saved QT polygons (they are the second item in the dictionary)


            #draw the polygon zone number in the centre of the relevant polygon
                # Calculate the center of the polygon
                center_x = sum(x for x, y in polygon_coords) / len(polygon_coords)
                center_y = sum(y for x, y in polygon_coords) / len(polygon_coords)

                # Draw the zone number
                painter.setFont(self.text_font)
                text_position = QPoint(int(center_x), int(center_y))  # Create a QPoint object
                painter.drawText(text_position, str(zone))


            # draw polygon lines so far ...
            painter.setPen(self.green_pen)
            for i in range(self.polygon.size()):
                if i+1 < self.polygon.size():
                    painter.drawLine(self.polygon[i].x(), self.polygon[i].y(), self.polygon[i+1].x(), self.polygon[i+1].y())

            # draw the rubber band line (i.e. the line when mouse is just moving) ...
            if self.started_draw and self.x is not None and self.y is not None and self.polygon.size() > 0:
                painter.setPen(self.red_pen)
                painter.drawLine(self.polygon[self.polygon.size()-1].x(), self.polygon[self.polygon.size()-1].y(), self.x, self.y)

            painter.end()

    def mousePressEvent(self, event):
        if self.Allow_drawing: #if draw polygons button is pressed
            if event.button() == Qt.LeftButton:
                print("left mouse button pressed")
                if not self.started_draw:
                    self.polygon = QPolygon([QPoint(event.pos().x(), event.pos().y())])  # start a new polygon / amend to save polygon to array
                    self.started_draw = True
                else:
                    self.polygon.append(QPoint(event.pos().x(), event.pos().y())) # add to polygon
                self.update()

            if event.button() == Qt.RightButton:
                print("right mouse button pressed")
                if self.polygon.size() > 0:
                    self.started_draw = False
                    self.x = self.y = None
                    self.polygon.append(QPoint(self.polygon[0].x(), self.polygon[0].y()))
                    self.update()
                    # add completed polygon to polygon dictionary
                    polygon_coordinates = []
                    for i in range(self.polygon.size()):
                        polygon_coordinates.append((self.polygon[i].x(), self.polygon[i].y())) #get the coordinates from the QT polygon
                    self.polygon_dict[(len(self.polygon_dict) + 1)] = (polygon_coordinates, self.polygon) #save the coordaintes to the dictionary in a list format, plus save the original QT polygon
                    self.polygonDrawn.emit(self.polygon)  # output the completed polygon coordinates

    def mouseMoveEvent(self, event):
        if self.started_draw:
            self.x = event.pos().x()
            self.y = event.pos().y()
            self.update()

    def set_polygon(self, polygon): #amend to work with array of polygons
        self.started_draw = False
        self.x = None
        self.y = None
        self.polygon = polygon
        self.update()

    def get_polygon(self): #amend to work with array of polygons
        return self.polygon

    def debug_polygon(self): #amend to work with array of polygons

        for zone,poly in self.polygon_dict.items():
            print('PolygonZone {0}'.format(zone))
            print('no. of cordinates {0}'.format(len(poly)))
            print(poly[0]) #print polygon cordinates in (x,y) format