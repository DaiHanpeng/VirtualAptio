# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AptioSystemReagent.ui'
#
# Created: Fri Jun 24 21:06:52 2016
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Aptio_System_Reagent(object):
    def setupUi(self, Aptio_System_Reagent):
        Aptio_System_Reagent.setObjectName(_fromUtf8("Aptio_System_Reagent"))
        Aptio_System_Reagent.resize(623, 348)
        self.gridLayout = QtGui.QGridLayout(Aptio_System_Reagent)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.treeWidget = QtGui.QTreeWidget(Aptio_System_Reagent)
        self.treeWidget.setColumnCount(2)
        self.treeWidget.setObjectName(_fromUtf8("treeWidget"))
        self.treeWidget.headerItem().setText(0, _fromUtf8("1"))
        self.treeWidget.headerItem().setText(1, _fromUtf8("2"))
        self.gridLayout.addWidget(self.treeWidget, 0, 0, 1, 1)

        self.retranslateUi(Aptio_System_Reagent)
        QtCore.QMetaObject.connectSlotsByName(Aptio_System_Reagent)

    def retranslateUi(self, Aptio_System_Reagent):
        Aptio_System_Reagent.setWindowTitle(_translate("Aptio_System_Reagent", "Aptio System Reagent and ThCG", None))
        self.treeWidget.setToolTip(_translate("Aptio_System_Reagent", "Aptio System Reagent", None))
        self.treeWidget.setWhatsThis(_translate("Aptio_System_Reagent", "Aptio System Reagent", None))

