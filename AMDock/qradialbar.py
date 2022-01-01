from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class QRadialBar(QWidget):
    def __init__(self, parent=None):
        super(QRadialBar, self).__init__(parent)

        self.setFixedSize(200, 200)

        self.min_value = 0
        self.max_value = 100
        self._value = 0

        self.dialwidth = 15

        self._BackgroundColor = Qt.transparent
        self._DialColor = QColor('white')#D1FFED')
        self._ProgressColor = QColor('blue')
        self._TextColor = QColor('black')
        self._SuffixText = "%"
        self._ShowText = True
        self._PenStyle = Qt.RoundCap
        self._TextFont = QFont()
        self._TextFont.setPointSize(14)

    def paintEvent(self, event):

        r = min(self.width(), self.height())
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(1, 1, r - 2, r - 2)

        pen = painter.pen()
        pen.setCapStyle(Qt.RoundCap) # rounded border
        pen.setBrush(self.palette().shadow().color())
        painter.setPen(QPen(self.palette().shadow().color(), 2))
        # painter.setBrush(self.palette().window())
        painter.drawEllipse(rect)

        startAngle = 90
        spanAngle = -360

        #Draw outer dial
        painter.save()
        pen.setWidth(self.dialwidth)
        pen.setColor(self._DialColor)
        painter.setPen(pen)
        offset = self.dialwidth / 2
        painter.drawArc(rect.adjusted(offset, offset, -offset, -offset), startAngle * 16, spanAngle * 16)
        painter.restore()

        #Draw background
        painter.save()
        painter.setBrush(self._BackgroundColor)
        # painter.setPen(self._BackgroundColor)
        inner = offset * 2
        painter.setPen(QPen(self.palette().shadow().color(), 1))
        # painter.setBrush(self.palette().window())
        painter.drawEllipse(rect.adjusted(inner, inner, -inner, -inner))
        painter.restore()

        #Draw progress text with suffix
        painter.save()
        painter.setFont(self._TextFont)
        pen.setColor(self._TextColor)
        painter.setPen(pen)
        if self._ShowText:
            painter.drawText(rect.adjusted(offset, offset, -offset, -offset), Qt.AlignCenter,
                             "{:.1f}".format(self._value) + self._SuffixText)
        else:
            painter.drawText(rect.adjusted(offset, offset, -offset, -offset), Qt.AlignCenter, self._SuffixText)
        painter.restore()

        #Draw progress bar
        painter.save()
        pen.setWidth(self.dialwidth)
        pen.setColor(self._ProgressColor)
        valueAngle = float(float(self._value - self.min_value)/float(self.max_value - self.min_value)) * float(spanAngle)  #Map _value to angle range
        painter.setPen(pen)
        painter.drawArc(rect.adjusted(offset, offset, -offset, -offset), startAngle * 16, valueAngle * 16)
        painter.restore()

    @pyqtSlot(float)
    def setValue(self, value):
        if self._value == value:
            return
        if value < self.min_value:
            self._value = self.min_value
        elif value > self.max_value:
            self._value = self.max_value
        else:
            self._value = value
        self.update()

    def value(self):
        return self._value
