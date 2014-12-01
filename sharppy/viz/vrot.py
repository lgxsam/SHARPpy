import numpy as np
import os
from PySide import QtGui, QtCore
import sharppy.sharptab as tab
import sharppy.databases.inset_data as inset_data
from scipy.misc import bytescale
from sharppy.sharptab.constants import *

## routine written by Kelton Halbert and Greg Blumberg
## keltonhalbert@ou.edu and wblumberg@ou.edu

__all__ = ['backgroundVROT', 'plotVROT']

class backgroundVROT(QtGui.QFrame):
    '''
    Draw the background frame and lines for the Theta-E plot frame
    '''
    def __init__(self):
        super(backgroundVROT, self).__init__()
        self.initUI()


    def initUI(self):
        ## window configuration settings,
        ## sich as padding, width, height, and
        ## min/max plot axes
        self.setStyleSheet("QFrame {"
            "  background-color: rgb(0, 0, 0);"
            "  border-width: 1px;"
            "  border-style: solid;"
            "  border-color: #3399CC;}")
        if self.physicalDpiX() > 75:
            fsize = 10
        else:
            fsize = 11
        self.plot_font = QtGui.QFont('Helvetica', fsize + 1)
        self.box_font = QtGui.QFont('Helvetica', fsize)
        self.plot_metrics = QtGui.QFontMetrics( self.plot_font )
        self.box_metrics = QtGui.QFontMetrics(self.box_font)
        self.plot_height = self.plot_metrics.xHeight() + 5
        self.box_height = self.box_metrics.xHeight() + 5
        self.vrot_inset_data = inset_data.vrotData()
        self.lpad = 5.; self.rpad = 0.
        self.tpad = 25.; self.bpad = 15.
        self.wid = self.size().width() - self.rpad
        self.hgt = self.size().height() - self.bpad
        self.tlx = self.rpad; self.tly = self.tpad
        self.brx = self.wid; self.bry = self.hgt
        self.probmax = 70.; self.probmin = 0.
        self.vrotmax = 110.; self.vrotmin = 0
        self.EF01_color = "#006600"
        self.EF23_color = "#FFCC33"
        self.EF45_color = "#FF00FF"
        self.plotBitMap = QtGui.QPixmap(self.width()-2, self.height()-2)
        self.plotBitMap.fill(QtCore.Qt.black)
        self.plotBackground()

    def resizeEvent(self, e):
        '''
        Handles the event the window is resized
        '''
        self.initUI()
    
    def plotBackground(self):
        '''
        Handles painting the frame.
        '''
        ## initialize a painter object and draw the frame
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        self.draw_frame(qp)
        qp.end()

    def setBlackPen(self, qp):
        color = QtGui.QColor('#000000')
        color.setAlphaF(.5)
        pen = QtGui.QPen(color, 0, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(QtCore.Qt.SolidPattern)
        qp.setPen(pen)
        qp.setBrush(brush)
        return qp

    def draw_frame(self, qp):
        '''
        Draw the background frame.
        qp: QtGui.QPainter object
        '''
        ## set a new pen to draw with

        pen = QtGui.QPen(QtCore.Qt.white, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.plot_font)
        rect1 = QtCore.QRectF(1.5, 2, self.brx, self.plot_height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
            'Conditional EF-scale Probs based on Vrot')

        qp.setFont(QtGui.QFont('Helvetica', 9))
        color = QtGui.QColor(self.EF01_color)
        pen = QtGui.QPen(color, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        rect1 = QtCore.QRectF(self.vrot_to_pix(25), 2 + self.plot_height, 10, self.plot_height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
            'EF0-EF1')

        color = QtGui.QColor(self.EF23_color)
        pen = QtGui.QPen(color, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        rect1 = QtCore.QRectF(self.vrot_to_pix(50), 2 + self.plot_height, 10, self.plot_height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
            'EF2-EF3')

        color = QtGui.QColor(self.EF45_color)
        pen = QtGui.QPen(color, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        rect1 = QtCore.QRectF(self.vrot_to_pix(75), 2 + self.plot_height, 10, self.plot_height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
            'EF4-EF5')

        pen = QtGui.QPen(QtCore.Qt.blue, 1, QtCore.Qt.DashLine)
        qp.setPen(pen)

        # Plot all of the Y-ticks for the probabilities
        ytick_fontsize = 10
        y_ticks_font = QtGui.QFont('Helvetica', ytick_fontsize)
        qp.setFont(y_ticks_font)
        texts = self.vrot_inset_data['ytexts']
        spacing = self.bry / 10.
        y_ticks = np.arange(self.tpad, self.bry+spacing, spacing)
        for i in xrange(len(y_ticks)):
            pen = QtGui.QPen(QtGui.QColor("#0080FF"), 1, QtCore.Qt.DashLine)
            qp.setPen(pen)
            try:
                qp.drawLine(self.tlx, self.prob_to_pix(int(texts[i])), self.brx, self.prob_to_pix(int(texts[i])))
            except:
                continue
            color = QtGui.QColor('#000000')
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            ypos = spacing*(i+1) - (spacing/4.)
            ypos = self.prob_to_pix(int(texts[i])) - ytick_fontsize/2
            rect = QtCore.QRect(self.tlx, ypos, 20, ytick_fontsize)
            pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, texts[i])

        width = self.brx / 12
        texts = np.arange(10, 110, 10)

        # Draw the x tick marks
        
        qp.setFont(QtGui.QFont('Helvetica', 8))
        for i in xrange(texts.shape[0]):
            color = QtGui.QColor('#000000')
            color.setAlpha(0)
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
            rect = QtCore.QRectF(self.vrot_to_pix(texts[i]) - width/2, self.prob_to_pix(-2), width, 4)
            # Change to a white pen to draw the text below the box and whisker plot
            pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, str(texts[i]))
        
        xpts = self.vrot_inset_data['xpts']
        
        # Draw the EF1+ stuff
        ef01 = self.vrot_inset_data['EF0-EF1']
        color = QtGui.QColor(self.EF01_color)
        lastprob = ef01[0]
        if lastprob > 70:
            lastprob = 70
        for i in xrange(1, np.asarray(xpts).shape[0], 1):
            if ef01[i] > 70:
                prob = 70
                pen = QtGui.QPen(color, 2.5, QtCore.Qt.DotLine)
                qp.setPen(pen)
            else:
                pen = QtGui.QPen(color, 2.5, QtCore.Qt.SolidLine)
                qp.setPen(pen)
                prob = ef01[i]

            qp.drawLine(self.vrot_to_pix(xpts[i-1]), self.prob_to_pix(lastprob), self.vrot_to_pix(xpts[i]), self.prob_to_pix(prob))
            lastprob = prob

        # Draw the EF2-EF3 stuff
        ef23 = self.vrot_inset_data['EF2-EF3']
        color = QtGui.QColor(self.EF23_color)
        lastprob = ef23[0]
        if lastprob > 70:
            lastprob = 70
        for i in xrange(1, np.asarray(xpts).shape[0], 1):
            if ef23[i] > 70:
                prob = 70
                pen = QtGui.QPen(color, 2.5, QtCore.Qt.DotLine)
                qp.setPen(pen)
            else:
                pen = QtGui.QPen(color, 2.5, QtCore.Qt.SolidLine)
                qp.setPen(pen)
                prob = ef23[i]

            qp.drawLine(self.vrot_to_pix(xpts[i-1]), self.prob_to_pix(lastprob), self.vrot_to_pix(xpts[i]), self.prob_to_pix(prob))
            lastprob = prob

        # Draw the EF4-EF5 stuff
        ef45 = self.vrot_inset_data['EF4-EF5']
        color = QtGui.QColor(self.EF45_color)
        lastprob = ef45[0]
        for i in xrange(1, np.asarray(xpts).shape[0], 1):
            pen = QtGui.QPen(color, 2.5, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            prob = ef45[i]
            qp.drawLine(self.vrot_to_pix(xpts[i-1]), self.prob_to_pix(lastprob), self.vrot_to_pix(xpts[i]), self.prob_to_pix(prob))
            lastprob = prob
        
    def prob_to_pix(self, prob):
        scl1 = self.probmax - self.probmin
        scl2 = self.probmin + prob
        return self.bry - (scl2 / scl1) * (self.bry - self.tpad)

    def vrot_to_pix(self, vrot):
        '''
        Function to convert a wind speed value to a X pixel.
        
        Parameters
        ----------
        s: speed in kts
        '''
        scl1 = self.vrotmax - self.vrotmin
        scl2 = self.vrotmax - vrot
        return self.lpad + self.brx - (scl2 / scl1) * (self.brx - self.rpad)


class plotVROT(backgroundVROT):
    '''
    Plot the data on the frame. Inherits the background class that
    plots the frame.
    '''
    def __init__(self, prof):
        super(plotVROT, self).__init__()
        self.vrot = 0


    def resizeEvent(self, e):
        '''
        Handles when the window is resized
        '''
        super(plotVROT, self).resizeEvent(e)
        self.interp_vrot()
        self.plotData()

    def paintEvent(self, e):
        super(plotVROT, self).paintEvent(e)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPixmap(1, 1, self.plotBitMap)
        qp.end()
    
    def plotData(self):
        '''
        Handles painting on the frame
        '''
        ## this function handles painting the plot
        ## create a new painter obkect
        qp = QtGui.QPainter()
        self.draw_vrot(qp)

    def interp_vrot(self):
        self.probef01 = self.vrot_inset_data['EF0-EF1'][np.argmin(np.abs(self.vrot - self.vrot_inset_data['xpts']))]
        self.probef23 = self.vrot_inset_data['EF2-EF3'][np.argmin(np.abs(self.vrot - self.vrot_inset_data['xpts']))]
        self.probef45 = self.vrot_inset_data['EF4-EF5'][np.argmin(np.abs(self.vrot - self.vrot_inset_data['xpts']))]

    def mouseDoubleClickEvent(self, e):
        super(plotVROT, self).resizeEvent(e)
        self.openInputDialog()
        self.interp_vrot()
        self.plotData()
        self.update()

    def openInputDialog(self):
        """
        Opens the text version of the input dialog
        """
        text, result = QtGui.QInputDialog.getText(self, "VROT Input",
                                            "Enter the VROT:")
        if result:
            self.vrot = int(text)

    def draw_vrot(self, qp):
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        vrot_pix = self.vrot_to_pix(self.vrot)
        # plot the white dashed line
        pen = QtGui.QPen(QtGui.QColor("#FFFFFF"), 1.5, QtCore.Qt.DotLine)
        qp.setPen(pen)
        qp.drawLine(vrot_pix, self.prob_to_pix(0), vrot_pix, self.prob_to_pix(70))
        
        # Draw the probabilties.
        color = QtGui.QColor(self.EF01_color)
        pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        rect = QtCore.QRectF(self.vrot_to_pix(self.vrot-7), self.prob_to_pix(self.probef01), 4, 7)
        qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, tab.utils.INT2STR(self.probef01))

        color = QtGui.QColor(self.EF23_color)
        pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        rect = QtCore.QRectF(self.vrot_to_pix(self.vrot), self.prob_to_pix(self.probef23), 4, 7)
        qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, tab.utils.INT2STR(self.probef23))

        color = QtGui.QColor(self.EF45_color)
        pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        rect = QtCore.QRectF(self.vrot_to_pix(self.vrot), self.prob_to_pix(self.probef45), 4, 7)
        qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, tab.utils.INT2STR(self.probef45))
        qp.end()


