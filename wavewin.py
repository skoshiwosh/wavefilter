#!/usr/bin/env python3
"""
    Launch GUI to apply wave filter to source image file.
    
    File: waver.py
    Author: Suzanne Berger
    Date created: 02/15/2026
    Python Version: 3.9
"""

import sys
import os
import logging
import json
from pathlib import Path
from pprint import pprint

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6 import QtUiTools
from PIL import Image
from PIL.ImageQt import ImageQt

import filterimage as fltimg

#########################################################
# globals
#########################################################

VERSION = "V01"

logging.basicConfig(level=logging.INFO)
logging.info(f" {sys.argv[0]} Version {VERSION}")

WIDGET_WIDTH = 121
WIDGET_HEIGHT = 21

#########################################################
# WaveWin
#########################################################


class WaverWin(QtWidgets.QWidget):

    def __init__(self, parent=None):
        """ Create WaverWin object inherited from QWidget. """
        QtWidgets.QWidget.__init__(self, parent)
        
        self.jsondata = {}
        self.image_dir = self.image_file = None
        self.empty_pixmap = QtGui.QPixmap(800, 600)
        self.empty_pixmap.fill(QtGui.QColor(120, 120, 160))        

        # initialize user interface and signal slot connections
        self._initUI()
        self._connectSignals()
        self.show()

    def _initUI(self):
        """ Create widgets and layout. """       
        
        self.setGeometry(100, 100, 1000, 700)
        self.setWindowTitle('Waver')
        
        self.src_label = QtWidgets.QLabel('Source Image File')
        self.src_label.setFixedSize(131,21)
        self.src_lineEdit = QtWidgets.QLineEdit()
        self.src_lineEdit.setFixedHeight(21)
        self.src_lineEdit.setMinimumWidth(500)
        self.src_button = QtWidgets.QPushButton('Browse')
        self.src_button.setFixedSize(91, 35)

        src_layout = QtWidgets.QHBoxLayout()
        src_layout.addWidget(self.src_label)
        src_layout.addWidget(self.src_lineEdit)
        src_layout.addWidget(self.src_button)

        self.waveLabel = QtWidgets.QLabel("Wave Length")
        self.waveSpinBox = QtWidgets.QSpinBox()
        self.waveSpinBox.setMinimum(10)
        self.waveSpinBox.setMaximum(1000)
        self.waveSpinBox.setValue(100)

        self.ampLabel = QtWidgets.QLabel("Wave Amplitude")
        self.ampSpinBox = QtWidgets.QSpinBox()
        self.ampSpinBox.setMinimum(3)
        self.ampSpinBox.setMaximum(1000)
        self.ampSpinBox.setValue(20)

        self.directionLabel = QtWidgets.QLabel("Direction")
        self.directionCombo = QtWidgets.QComboBox()
        self.directionCombo.setFixedWidth(WIDGET_WIDTH)
        self.directionCombo.addItem("horizontal")
        self.directionCombo.addItem("vertical")
        self.directionCombo.addItem("both")

        self.numLabel = QtWidgets.QLabel("Number of Waves")
        self.numwavSpinBox = QtWidgets.QSpinBox()
        self.numwavSpinBox.setMinimum(1)
        self.numwavSpinBox.setMaximum(3)
        self.numwavSpinBox.setValue(2)

        self.phaseLabel = QtWidgets.QLabel("Wave Phase Offset")
        self.phaseSpinBox = QtWidgets.QSpinBox()
        self.phaseSpinBox.setMinimum(-40)
        self.phaseSpinBox.setMaximum(40)
        self.phaseSpinBox.setValue(0)

        self.wavit_button = QtWidgets.QPushButton('Wave It')
        self.wavit_button.setFixedSize(91, 35)

        parm_layout = QtWidgets.QVBoxLayout()
        parm_layout.setAlignment(QtCore.Qt.AlignTop)
        vspace = QtWidgets.QSpacerItem(0,40)
        parm_layout.addWidget(self.waveLabel)
        parm_layout.addWidget(self.waveSpinBox)
        parm_layout.addWidget(self.ampLabel)
        parm_layout.addWidget(self.ampSpinBox)
        parm_layout.addWidget(self.directionLabel)
        parm_layout.addWidget(self.directionCombo)
        parm_layout.addWidget(self.numLabel)
        parm_layout.addWidget(self.numwavSpinBox)
        parm_layout.addWidget(self.phaseLabel)
        parm_layout.addWidget(self.phaseSpinBox)
        parm_layout.addSpacerItem(vspace)
        parm_layout.addWidget(self.wavit_button)

        self.wavimg = QtWidgets.QLabel()
        self.wavimg.setPixmap(self.empty_pixmap)
        self.wavimg.setObjectName("wavimg_label")

        self.wavprm = QtWidgets.QGroupBox()
        self.wavprm.setLayout(parm_layout)

        wavpat_layout = QtWidgets.QHBoxLayout()
        wavpat_layout.addWidget(self.wavimg)
        wavpat_layout.addWidget(self.wavprm)

        status_label = QtWidgets.QLabel('Status')
        status_label.setFixedSize(61,21)
        self.status_lineEdit = QtWidgets.QLineEdit("Ready:")
        self.status_lineEdit.setFixedHeight(21)
        self.status_lineEdit.setMinimumWidth(600)
        status_layout = QtWidgets.QHBoxLayout()
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_lineEdit)
        
        self.buttonbox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Save |
                                                    QtWidgets.QDialogButtonBox.Reset |
                                                    QtWidgets.QDialogButtonBox.Close)
                                                    

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(src_layout)
        mainLayout.addLayout(parm_layout)
        mainLayout.addLayout(wavpat_layout)
        mainLayout.addLayout(status_layout)
        mainLayout.addWidget(self.buttonbox)    
        self.setLayout(mainLayout)

    def _connectSignals(self):
        """ Create signal slot connections. """
        self.src_button.clicked.connect(self.on_src_clicked)
        self.wavit_button.clicked.connect(self.on_wavit_clicked)
        self.buttonbox.rejected.connect(self.close)
        self.buttonbox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save)
        self.buttonbox.button(QtWidgets.QDialogButtonBox.Reset).clicked.connect(self.reset)    


    def closeEvent(self, event):
        event.accept()

    def save(self):
        self.status_lineEdit.setText("Saving filtered image")
        this_file = os.path.splitext(self.srcfile)[0] + "wav.json"
        logging.info(f"Saving json to {this_file}")
        jsonfile = open(this_file, 'w')
        json.dump(self.json_dict, jsonfile, indent=4)

        #this_wavimg = self.wavimg.grab()
        this_imgfile = os.path.splitext(self.srcfile)[0] + "wav.jpg"
        #this_wavimg.save(this_imgfile, quality = 100)
        self.wavimage.save(this_imgfile,'JPEG', quality = 100)
        

    def reset(self):
        logging.info("Resetting collage window")
        self.srcfile = ""
        self.src_lineEdit.clear()
        self.image_dir = self.image_file = None
        self.wavimg.setPixmap(self.empty_pixmap)
        self.status_lineEdit.setText("Reset")

    def on_src_clicked(self):
        """ Launch file selection dialog to load source image to be modified using wave filter. """
        self.srcfile = QtWidgets.QFileDialog.getOpenFileName(self,'Load Image File','/Users/suzanneberger/Pictures',
                                                     "image files (*.jpg *.png *.tif)")[0]

        if self.srcfile is not None:
            self.src_lineEdit.setText(self.srcfile)
            self.image_dir,self.image_file = os.path.split(self.srcfile)
            

    def on_wavit_clicked(self):
        """ Apply wave filter to input image """
        logging.info("Making Waves")
        self.status_lineEdit.setText("Making Waves")

        inimage = Image.open(self.srcfile)
        if inimage.mode != 'RGB':
            inimage = inimage.convert('RGB')

        self.json_dict = {}
        self.json_dict["wavelength"] = self.waveSpinBox.value()
        self.json_dict["amplitude"] = self.ampSpinBox.value()
        self.json_dict["direction"] = self.directionCombo.currentText()
        self.json_dict["number_of_waves"] = self.numwavSpinBox.value()
        self.json_dict["phase"] = self.phaseSpinBox.value()

        logging.info("Setting JSON dictionary")
        pprint(self.json_dict)

        self.wavimage = fltimg.dowavr(inimage, self.json_dict)
        q_image = ImageQt(self.wavimage)
        wavpix = QtGui.QPixmap.fromImage(q_image)
        self.wavimg.setPixmap(wavpix)
        

#########################################################
# main
#########################################################

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    wavwin = WaverWin()
    sys.exit(app.exec())
