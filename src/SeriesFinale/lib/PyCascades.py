# -*- coding: utf-8 -*-

import os
import sys
import time

from PySide.QtCore import *
from PySide.QtCascades import bb

class CApplication(QObject):
    def __init__(self):
        super(CApplication, self).__init__()
        try:
            self.app = bb.cascades.Application(sys.argv)
        finally:
            pass

    def exec_(self):
        try:
            self.app.exec_()
        finally:
            pass

    def rootContext(self):
        return self.qml.instance()

    def setSource(self, source):
        self.qml = bb.cascades.QmlDocument.create(source, True)
        self.qml.instance().load()

    def setWindowTitle(self, title):
        qDebug("Window title %s" % title)

    def showFullScreen(self):
        qml = self.qml.instance()
        if qml.hasErrors():
            qDebug("QML har errors")
        else:
            page = qml.createRootObject()
            if page:
                bb.cascades.Application.instance().setScene(page)
            else:
                qDebug("Could not create root node")
