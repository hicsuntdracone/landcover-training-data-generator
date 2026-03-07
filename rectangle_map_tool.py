from qgis.gui import QgsMapTool, QgsRubberBand
from qgis.core import QgsWkbTypes, QgsGeometry, QgsPointXY, QgsFeature, QgsRectangle
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor


class RectangleMapTool(QgsMapTool):
    
    def __init__(self,canvas):
        super().__init__(canvas)
        self.canvas = canvas
        self.start_point = None
        self.rubber_band = None
    
    def canvasPressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = self.toMapCoordinates(event.pos())
            self.rubber_band = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
            self.rubber_band.setColor(QColor(255, 0, 0, 100))
            self.rubber_band.setWidth(2)

    def canvasMoveEvent(self, event):
        if self.start_point is None:
            return
        end_point = self.toMapCoordinates(event.pos())
        self.rubber_band.reset(QgsWkbTypes.PolygonGeometry)
        self.rubber_band.addPoint(QgsPointXY(self.start_point.x(), self.start_point.y()))
        self.rubber_band.addPoint(QgsPointXY(end_point.x(), self.start_point.y()))
        self.rubber_band.addPoint(QgsPointXY(end_point.x(), end_point.y()))
        self.rubber_band.addPoint(QgsPointXY(self.start_point.x(), end_point.y()))

    def canvasReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.start_point is None:
                return
            end_point = self.toMapCoordinates(event.pos())
            
            x1, y1 = self.start_point.x(), self.start_point.y()
            x2, y2 = end_point.x(), end_point.y()
            
            geometry = QgsGeometry.fromRect(
                QgsRectangle(min(x1,x2), min(y1,y2), max(x1,x2), max(y1,y2))
            )
            
            layer = self.canvas.currentLayer()
            if layer is None or not layer.isEditable():
                return
            
            feature = QgsFeature(layer.fields())
            feature.setGeometry(geometry)
            layer.addFeature(feature)
            layer.triggerRepaint()
            
            self.rubber_band.reset()
            self.start_point = None
