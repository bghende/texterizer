#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
Demonstrates a variety of uses for ROI. This class provides a user-adjustable
region of interest marker. It is possible to customize the layout and 
function of the scale/rotate handles in very flexible ways. 
"""



import initExample ## Add path to library (just for examples; you do not need this)

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
from scipy import ndimage
from scipy import misc
from PIL import Image, ImageDraw, ImageFont

import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType
import pickle

roi = []

class ImProc:

    def __init__(self,cb):
        self.cb = cb
        self.saveName = ''
        self.sRed = MySlider(name='R',cb=cb,val=128)
        self.sGreen = MySlider(name='G',cb=cb,val=128)
        self.sBlue = MySlider(name='B',cb=cb,val=128)
        self.sDS = MySlider(name='Downsample',min=0,max=10,val=0,cb=cb)
        self.sUS = MySlider(name='Upsample',min=1,max=100,val=1,cb=cb)
        self.sFont = MySlider(name='Font Size',min=1,max=100,val=10,cb=cb)

        self.cbThresh = QtGui.QCheckBox()
        self.cbThresh.setText('Do Threshold')
        self.cbThresh.setStyleSheet("QCheckBox { color: white }")
        self.cbThresh.clicked.connect(cb)

        self.cbRender = QtGui.QCheckBox()
        self.cbRender.setText('Do Text Render')
        self.cbRender.setStyleSheet("QCheckBox { color: white }")
        self.cbRender.clicked.connect(cb)

        self.btnSave = QtGui.QPushButton()
        self.btnSave.setText("Save Images")
        self.btnSave.setMaximumWidth(150)
        self.btnSave.clicked.connect(self.cb_save_click)

        self.saveDialog = QtGui.QFileDialog()
        self.saveDialog.setModal(True)

    def cb_save_click(self):
        #fileName = QtGui.QFileDialog.getSaveFileName(parent=self, caption='Select ', dir='~', selectedFilter='*.*')
        self.saveName = str(QtGui.QFileDialog.getSaveFileName())
        self.cb()

    def populate_layout(self,layout):
        layout.addWidget(self.cbThresh)
        layout.addWidget(self.sRed.widget)
        layout.addWidget(self.sGreen.widget)
        layout.addWidget(self.sBlue.widget)
        layout.addWidget(self.sDS.widget)

        layout.addWidget(self.cbRender)
        layout.addWidget(self.sUS.widget)
        layout.addWidget(self.sFont.widget)
        layout.addWidget(self.btnSave)

    def proc_image(self, im):

        im_b = im.astype(np.uint8)

        pimg = Image.fromarray(im_b)

        dsfac = self.sDS.get_value()


        if self.sDS.get_value() > 1:
            new_size = []
            new_size.append(pimg.size[0] / dsfac)
            new_size.append(pimg.size[1] / dsfac)
            pimg = pimg.resize(new_size)

        data = np.asarray( pimg, dtype="uint8" )

        rds = data[:,:,0]
        gds = data[:,:,1]
        bds = data[:,:,2]

        if self.cbThresh.isChecked():
            r = rds > self.sRed.get_value()
            g = gds > self.sGreen.get_value()
            b = bds > self.sBlue.get_value()
        else:
            r = rds
            g = gds
            b = bds

        us = self.sUS.get_value()
        sz = []
        sz.append(rds.shape[0] *  us)
        sz.append(rds.shape[1] *  us)

        rtxt = Image.new('RGBA', sz, (255,255,255,255))
        gtxt = Image.new('RGBA', sz, (255,255,255,255))
        btxt = Image.new('RGBA', sz, (255,255,255,255))

        if self.cbRender.isChecked():
            fnt = ImageFont.truetype('Arial.ttf', self.sFont.get_value())
            # get a drawing context
            rd = ImageDraw.Draw(rtxt)
            gd = ImageDraw.Draw(gtxt)
            bd = ImageDraw.Draw(btxt)

            nrows = rds.shape[1]
            for i in range(rds.shape[0]):
                #for j in range(rds.shape[1]-1,-1,-1):
                for j in range(rds.shape[1]):
                    x = i*us
                    y = j*us
                    if r[i,nrows-1-j]:
                        rd.text((x,y), 'R', font=fnt, fill=(0,0,0,255))
                    if g[i,nrows-1-j]:
                        gd.text((x,y), 'G', font=fnt, fill=(0,0,0,255))
                    if b[i,nrows-1-j]:
                        bd.text((x,y), 'B', font=fnt, fill=(0,0,0,255))


        #rtxt.save('out.jpg')

        if self.saveName != '':
            print 'gonna save ' + self.saveName
            rtxt.save(self.saveName + '_r.tiff')
            gtxt.save(self.saveName + '_g.tiff')
            btxt.save(self.saveName + '_b.tiff')

        self.saveName = ''

        return r,g,b,np.asarray(rtxt),np.asarray(gtxt),np.asarray(btxt)



class MySlider:

    def __init__(self, name='slider', min=0, max=255, val=0, orient=1, cb=[]):
        self.lbl = QtGui.QLabel()
        self.lbl.setText(name)
        self.lbl.setStyleSheet("QLabel { color : white; }")

        self.val_lbl = QtGui.QLabel()
        self.val_lbl.setText('0')
        self.val_lbl.setStyleSheet("QLabel { color : white; }")

        self.slider = QtGui.QSlider(orient)
        self.slider.valueChanged[int].connect(self.val_lbl.setNum)
        self.slider.valueChanged.connect(cb)

        self.slider.setRange(min,max)
        self.slider.setValue(val)



        self.layout = QtGui.QHBoxLayout()
        self.layout.addWidget(self.lbl)
        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.val_lbl)

        self.widget = QtGui.QWidget()
        self.widget.setLayout(self.layout)




    def get_value(self):
        return self.slider.value()

    def set_value(self, value):
        self.slider.setValue(value)


## create GUI
app = QtGui.QApplication([])


def update_images():
    if roi == []:
        return;

    imReg = roi.getArrayRegion(l, img)
    r,g,b,rtxt,gtxt,btxt = set.proc_image(imReg)


    if set.cbThresh.isChecked():
        lvls=(0,1)
    else:
        lvls = (0,255)

    imgRed.setImage(r, levels=lvls)
    imgGreen.setImage(g, levels=lvls)
    imgBlue.setImage(b, levels=lvls)


    imgRedText.setImage(np.rot90(rtxt,3), levels=(0,255))
    imgGreenText.setImage(np.rot90(gtxt,3), levels=(0,255))
    imgBlueText.setImage(np.rot90(btxt,3), levels=(0,255))


    vRed.autoRange()
    vGreen.autoRange()
    vBlue.autoRange()

    vRedText.autoRange()
    vGreenText.autoRange()
    vBlueText.autoRange()

def update(roi):
    roi_ = roi
    #imReg = roi.getArrayRegion(l, img)
    update_images()

set = ImProc(cb=update_images)

l = misc.imread('monkey2.jpg')
l = np.rot90(l, 3)

maxval = l.max()
w = pg.GraphicsWindow(size=(1600,800), border=True)
layout = QtGui.QGridLayout()
w.setLayout(layout)

w1 = pg.GraphicsLayoutWidget()
layout.addWidget(w1,0,1,1,1)

left_layout = QtGui.QVBoxLayout()
left_side = QtGui.QWidget()
left_side.setLayout(left_layout)

set.populate_layout(left_layout)

left_layout.addStretch(0)

splitter = QtGui.QSplitter(1)

#splitter.addWidget(t)
splitter.addWidget(left_side)
splitter.addWidget(w1)

#w.setCentralWidget(splitter)
layout.addWidget(splitter,0,0,1,1)

w.setWindowTitle('Texterizer')

#label1 = w1.addLabel(text, row=0, col=0)
vImage = w1.addViewBox(row=0, col=0, rowspan=3, lockAspect=True)
img = pg.ImageItem(l)
vImage.addItem(img)
vImage.disableAutoRange('xy')
vImage.autoRange()

vRed = w1.addViewBox(row=0, col=1, lockAspect=True)
imgRed = pg.ImageItem()
vRed.addItem(imgRed)
vRed.disableAutoRange('xy')
vRed.autoRange()

vGreen = w1.addViewBox(row=1, col=1, lockAspect=True)
imgGreen = pg.ImageItem()
vGreen.addItem(imgGreen)
vGreen.disableAutoRange('xy')
vGreen.autoRange()

vBlue = w1.addViewBox(row=2, col=1, lockAspect=True)
imgBlue = pg.ImageItem()
vBlue.addItem(imgBlue)
vBlue.disableAutoRange('xy')
vBlue.autoRange()



vRedText = w1.addViewBox(row=0, col=2, lockAspect=True)
imgRedText = pg.ImageItem()
vRedText.addItem(imgRedText)
vRedText.disableAutoRange('xy')
vRedText.autoRange()

vGreenText = w1.addViewBox(row=1, col=2, lockAspect=True)
imgGreenText = pg.ImageItem()
vGreenText.addItem(imgGreenText)
vGreenText.disableAutoRange('xy')
vGreenText.autoRange()

vBlueText = w1.addViewBox(row=2, col=2, lockAspect=True)
imgBlueText = pg.ImageItem()
vBlueText.addItem(imgBlueText)
vBlueText.disableAutoRange('xy')
vBlueText.autoRange()

rois = []
rois.append(pg.RectROI([l.shape[0]/2-50, l.shape[1]/2-50], [100, 100], pen=(0,9)))
rois[-1].addRotateHandle([1,0], [0.5, 0.5])

roi_ = []



    
for roi in rois:
    roi.sigRegionChanged.connect(update)
    vImage.addItem(roi)

update(rois[-1])

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
