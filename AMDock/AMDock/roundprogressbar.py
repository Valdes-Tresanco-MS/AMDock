
##############################################################
# This is a modified version by Mario S. Valdes Tresanco (Valdes-Tresanco-MS)
# Original is in https://sourceforge.net/projects/qroundprogressbar and
# https://github.com/ozmartian/QRoundProgressBar
#############################################################
#
# Copyright 2017 Pete Alexandrou
#
# Ported to Python from the original works in C++ by:
#
#     Sintegrial Technologies (c) 2015
#     https://sourceforge.net/projects/qroundprogressbar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#######################################################

import operator
from PyQt4.QtCore import pyqtSlot, QPointF, Qt, QRectF
from PyQt4.QtGui import (QPalette, QConicalGradient, QGradient, QRadialGradient,
                         QFontMetricsF, QFont, QPainter, QPen, QPainterPath, QImage,
                         QPaintEvent, QWidget, QApplication, QBrush, QColor, QPushButton, QHBoxLayout)

class QRoundProgressBar(QWidget):

    # CONSTANTS
    PositionLeft = 180
    PositionTop = 90
    PositionRight = 0
    PositionBottom = -90

    # CONSTRUCTOR ---------------------------------------------------

    def __init__(self, parent=None):
        super(QRoundProgressBar, self).__init__(parent)
        self.m_min = 0.
        self.m_max = 100.
        self.m_value = 0.
        self.m_nullPosition = QRoundProgressBar.PositionTop
        self.m_outlinePenWidth = 1
        self.m_dataPenWidth = 1
        self.m_rebuildBrush = False
        self.m_format = '%p%'
        self.m_decimals = 2
        self.m_updateFlags = self.UpdateFlags.PERCENT
        self.m_gradientData = None

    # ENUMS ---------------------------------------------------------
    class UpdateFlags():
        VALUE = 0,
        PERCENT = 1,
        MAX = 2

    # GETTERS -------------------------------------------------------
    def value(self):
        return self.m_value

    def minimum(self):
        return self.m_min

    def maximum(self):
        return self.m_max

    # SETTERS -------------------------------------------------------

    def setNullPosition(self, position):
        if position != self.m_nullPosition:
            self.m_nullPosition = position
            self.m_rebuildBrush = True
            self.update()

    def setOutlinePenWidth(self, width):
        if width != self.m_outlinePenWidth:
            self.m_outlinePenWidth = width
            self.update()

    def setDataPenWidth(self, width):
        if width != self.m_dataPenWidth:
            self.m_dataPenWidth = width
            self.update()

    def setDataColors(self, stopPoints):
        if stopPoints != self.m_gradientData:
            self.m_gradientData = stopPoints
            self.m_rebuildBrush = True
            self.update()

    def setFormat(self, val):
        if val != self.m_format:
            self.m_format = val
            self.valueFormatChanged()

    def resetFormat(self):
        self.m_format = None
        self.valueFormatChanged()

    def setDecimals(self, count):
        if count >= 0 and count != self.m_decimals:
            self.m_decimals = count
            self.valueFormatChanged()

    # SLOTS ---------------------------------------------------------

    @pyqtSlot(float, float)
    def setRange(self, minval, maxval):
        self.m_min = minval
        self.m_max = maxval
        if self.m_max < self.m_min:
            self.m_min = maxval
            self.m_max = minval
        if self.m_value < self.m_min:
            self.m_value = self.m_min
        elif self.m_value > self.m_max:
            self.m_value = self.m_max
        self.m_rebuildBrush = True
        self.update()

    @pyqtSlot(float)
    def setMinimum(self, val):
        self.setRange(val, self.m_max)

    @pyqtSlot(float)
    def setMaximum(self, val):
        self.setRange(self.m_min, val)

    @pyqtSlot(int)
    def setValue(self, val):
        if self.m_value != val:
            if val < self.m_min:
                self.m_value = self.m_min
            elif val > self.m_max:
                self.m_value = self.m_max
            else:
                self.m_value = val
            self.update()

    # PAINTING ------------------------------------------------------

    def paintEvent(self, event):
        outerRadius = min(self.width(), self.height())
        baseRect = QRectF(1, 1, outerRadius - 2, outerRadius - 2)
        buffer = QImage(outerRadius, outerRadius, QImage.Format_ARGB32_Premultiplied)
        p = QPainter(buffer)
        p.setRenderHint(QPainter.Antialiasing)
        self.rebuildDataBrushIfNeeded()
        self.drawBackground(p, buffer.rect())
        self.drawBase(p, baseRect)
        if self.m_value > 0:
            delta = (self.m_max - self.m_min) / (self.m_value - self.m_min)
        else:
            delta = 0
        self.drawValue(p, baseRect, self.m_value, delta)
        innerRect, innerRadius = self.calculateInnerRect(outerRadius)
        self.drawInnerBackground(p, innerRect)
        self.drawText(p, innerRect, innerRadius, self.m_value)
        p.end()
        painter = QPainter(self)
        painter.fillRect(baseRect, self.palette().base())
        painter.drawImage(0, 0, buffer)

    def drawBackground(self, p, baseRect):
        p.fillRect(baseRect, self.palette().base())

    def drawBase(self, p, baseRect):
        p.setPen(QPen(self.palette().shadow().color(), self.m_outlinePenWidth))
        p.setBrush(self.palette().window())
        p.drawEllipse(baseRect)

    def drawValue(self, p, baseRect, value, delta):
        if value == self.m_min:
            return
        dataPath = QPainterPath()
        dataPath.setFillRule(Qt.WindingFill)
        if value == self.m_max:
            dataPath.addEllipse(baseRect)
        else:
            arcLength = 360 / delta
            dataPath.moveTo(baseRect.center())
            dataPath.arcTo(baseRect, self.m_nullPosition, -arcLength)
            dataPath.lineTo(baseRect.center())
        p.setBrush(self.palette().highlight())
        p.setPen(QPen(self.palette().shadow().color(), self.m_dataPenWidth))
        p.drawPath(dataPath)

    def calculateInnerRect(self, outerRadius):
        innerRadius = outerRadius * 0.75
        delta = (outerRadius - innerRadius) / 2
        innerRect = QRectF(delta, delta, innerRadius, innerRadius)
        return innerRect, innerRadius

    def drawInnerBackground(self, p, innerRect):
        p.setBrush(self.palette().base())
        p.drawEllipse(innerRect)

    def drawText(self, p, innerRect, innerRadius, value):
        if not self.m_format:
            return
        f = QFont(self.font())
        f.setPixelSize(10)
        fm = QFontMetricsF(f)
        maxWidth = fm.width(self.valueToText(self.m_max))
        delta = innerRadius / maxWidth
        fontSize = f.pixelSize() * delta * 0.75
        f.setPixelSize(int(fontSize))
        p.setFont(f)
        textRect = QRectF(innerRect)
        p.setPen(self.palette().text().color())
        p.drawText(textRect, Qt.AlignCenter, self.valueToText(value))

    def valueToText(self, value):
        textToDraw = self.m_format
        if self.m_updateFlags == self.UpdateFlags.VALUE:
            textToDraw = textToDraw.replace('%v', str(round(value, self.m_decimals)))
        if self.m_updateFlags == self.UpdateFlags.PERCENT:
            procent = (value - self.m_min) / (self.m_max - self.m_min) * 100
            textToDraw = textToDraw.replace('%p', str(round(procent, self.m_decimals)))
        if self.m_updateFlags == self.UpdateFlags.MAX:
            textToDraw = textToDraw.replace('%m', str(round(self.m_max - self.m_min + 1, self.m_decimals)))
        return textToDraw

    def valueFormatChanged(self):
        if operator.contains(self.m_format, '%v'):
            self.m_updateFlags = self.UpdateFlags.VALUE
        if operator.contains(self.m_format, '%p'):
            self.m_updateFlags = self.UpdateFlags.PERCENT
        if operator.contains(self.m_format, '%m'):
            self.m_updateFlags = self.UpdateFlags.MAX
        self.update()

    def rebuildDataBrushIfNeeded(self):
        if not self.m_rebuildBrush or not self.m_gradientData:
            return
        self.m_rebuildBrush = False
        p = self.palette()
        dataBrush = QConicalGradient(QPointF(0.5, 0.5), self.m_nullPosition)
        dataBrush.setCoordinateMode(QGradient.StretchToDeviceMode)
        for i in range(0, len(self.m_gradientData)):
            dataBrush.setColorAt(1 - self.m_gradientData[i][0], self.m_gradientData[i][1])
            p.setBrush(QPalette.Highlight, dataBrush)
        self.setPalette(p)