# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ThreeDiCustomizations
                                 A QGIS plugin
 SplashScreen and other customizations for the 3Di_Modeller_Interface
                             -------------------
        begin                : 2018-08-22
        Marco Duiker - MD-kwadraat
        email                : md@md-kwadraat.nl

        Adapted from All4GIS/Load-QSS and All4GIS/fake_splash
        Both by Francisco Raga
 ***************************************************************************/



/***************************************************************************
 *                                                                         *
 *   This program is free software you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation either version 2 of the License, or     *
 #   any later version.                                                    *
 *                                                                         *
 ***************************************************************************/
"""
import os
import re
import sys
import webbrowser

from qgis.PyQt.QtGui import QAction
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtCore import QFileSystemWatcher
from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtGui import QPixmap
from qgis.PyQt.QtWidgets import QApplication
from qgis.PyQt.QtWidgets import QMenu
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtWidgets import QSplashScreen
from qgis.PyQt.uic import loadUi

from qgis.utils import iface

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")


def reload_style(path):
    # Some applications will remove a file and rewrite it.  QFileSystemWatcher will
    # ignore the file if the file handle goes away so we have to keep adding it.
    watch.removePaths(watch.files())
    watch.addPath(path)
    with open(path, "r") as f:
        stylesheet = f.read()
        # Update the image paths to use full paths. Fixes image loading in styles
        path = os.path.dirname(path).replace("\\", "/")
        stylesheet = re.sub(r"url\((.*?)\)", r'url("{}/\1")'.format(path), stylesheet)
        QApplication.instance().setStyleSheet(stylesheet)


watch = QFileSystemWatcher()
watch.fileChanged.connect(reload_style)


class About3DiMIDialog(QDialog):
    def __init__(self, parent):
        super(About3DiMIDialog, self).__init__(parent)
        ui_fn = os.path.join(os.path.dirname(__file__), 'ui', 'About3DiMIDialog.ui')
        loadUi(ui_fn, self)


class SplashScreen(object):
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        self.windowTitle = "3Di Modeller Interface - Powered by QGIS"

        self.app = QApplication.instance()
        self.QApp = QCoreApplication.instance()

        if self.QApp is None:
            self.QApp = QApplication(sys.argv)

        self.QApp.startingUp()
        self.QApp.processEvents()
        self.app.startDragTime()

        self.iface.initializationCompleted.connect(self.customization)
        QApplication.instance().processEvents()

        self.applyStyle()

    def initGui(self):
        QSettings().setValue("/qgis/hideSplash", True)
        QApplication.instance().processEvents()

        icon = QIcon(os.path.join(IMAGES_DIR, "logo.png"))
        self.app.setWindowIcon(icon)
        self.iface.mainWindow().setWindowIcon(icon)

        self.iface.mainWindow().setWindowTitle(self.windowTitle)

        QApplication.instance().processEvents()

        if not self.iface.mainWindow().isVisible():
            self.splash_pix = QPixmap(os.path.join(IMAGES_DIR, "splash.png"))
            self.splash = QSplashScreen(self.splash_pix)
            self.splash.setMask(self.splash_pix.mask())
            self.splash.show()
            QApplication.instance().processEvents()
        self.applyStyle()
        self.addHelpMenuItem()

    def run(self):
        pass

    def unload(self):
        QApplication.instance().processEvents()
        self.iface.initializationCompleted.disconnect(self.customization)
        self.helpAction.deleteLater()

    def customization(self):
        self.splash.finish(self.iface.mainWindow())
        self.iface.mainWindow().setWindowTitle(self.windowTitle)
        QApplication.instance().processEvents()
        self.applyStyle()

    def applyStyle(self):
        path = os.path.abspath(
            os.path.join(self.plugin_dir, "Modeler Interface", "stylesheet.qss")
        )
        watch.removePaths(watch.files())
        reload_style(path)

    @staticmethod
    def open3DiHelp(self):
        webbrowser.open_new("https://docs.3di.live")

    @staticmethod
    def about_3di_mi_dialog():
        dialog = About3DiMIDialog(iface.mainWindow())
        dialog.exec()

    def find_3di_menu(self):
        for i, action in enumerate(self.iface.mainWindow().menuBar().actions()):
            if action.menu().objectName() == "m3Di":
                return action.menu()
        return None

    def addHelpMenuItem(self):
        menu = self.find_3di_menu()
        if not menu:
            menu = QMenu("&3Di", self.iface.mainWindow().menuBar())
            menu.setObjectName("m3Di")
            self.iface.mainWindow().menuBar().addMenu(menu)

        self.helpAction = QAction(
            QIcon(":/3Di_images/3Di_images/images/logo.png"),
            "Documentation",
            self.iface.mainWindow(),
        )
        self.helpAction.triggered.connect(self.open3DiHelp)
        self.helpAction.setWhatsThis("3Di Documentation")

        menu.addAction(self.helpAction)

        about_action = QAction(
            # QIcon(":/3Di_images/3Di_images/images/logo.png"),
            "About 3Di Modeller Interface",
            self.iface.mainWindow(),
        )
        about_action.triggered.connect(self.about_3di_mi_dialog)
        about_action.setWhatsThis("About 3Di Modeller Interface")

        menu.addAction(about_action)
