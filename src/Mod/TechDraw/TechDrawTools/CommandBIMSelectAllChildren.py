# ***************************************************************************
# *   Copyright (c) 2025 Syres                                              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************
"""
Assists the user in selecting all BIM objects below the selected Site/Building/Wall etc
"""

__title__ = "TechDrawTools.CommandBIMSelectAllChildren"
__author__ = "Syres"
__url__ = "https://www.freecad.org"
__version__ = "00.01"
__date__ = "2025/02/09"

from PySide.QtCore import QT_TRANSLATE_NOOP

import FreeCAD as App
import FreeCADGui as Gui

import TechDrawTools.TDToolsUtil as Utils

import TechDraw

import PySide
from PySide import QtGui, QtCore
from PySide.QtGui import *
from PySide.QtCore import *

docName = App.ActiveDocument.Name
mw = Gui.getMainWindow()

selectedList = []
addToSelectionList = []


class CommandBIMSelectAllChildren:
    """Select objects under a BIM object such as Site, Building, Wall"""

    def __init__(self):
        """Initialize variables for the command that must exist at all times."""
        pass

    def GetResources(self):
        """Return a dictionary with data that will be used by the button or menu item."""
        return {
            "Pixmap": "TechDraw_BIMSelectAllChildren.svg",
            "Accel": "",
            "MenuText": QT_TRANSLATE_NOOP(
                "TechDraw_BIMSelectAllChildren", "BIM Select All Children"
            ),
            "ToolTip": QT_TRANSLATE_NOOP(
                "TechDraw_BIMSelectAllChildren",
                "Selects all child objects below the BIM Site, Building, Wall etc<br>",
            ),
        }

    def Activated(self):
        """Run the following code when the command is activated (button press)."""
        prefs = App.ParamGet("User parameter:BaseApp/Preferences/Document")
        if prefs.GetBool("DuplicateLabels", False):
            App.Console.PrintWarning(
                "This macro does not work with documents having multiple objects with the same label\n\n"
            )

        modelview = mw.findChild(QtGui.QDockWidget, "Model")
        if modelview:  # standard Combo View after 0.21
            tree = modelview.findChildren(QtGui.QTreeWidget)[0]
        else:
            treeview = mw.findChild(QtGui.QDockWidget, "Tree view")
            if treeview:  # Treeview and Properties view after 0.21
                tree = treeview.findChildren(QtGui.QTreeWidget)[0]
            else:  # 0.21 and before Combo view
                tab = mw.findChild(QtGui.QTabWidget, "combiTab")
                tree = tab.widget(0).findChildren(QtGui.QTreeWidget)[0]
        top = tree.invisibleRootItem().child(0)

        # get selected objectsApp.ActiveDocument.
        sels = Gui.Selection.getSelection()
        if not sels:  # not sels
            App.Console.PrintWarning("Select something first!\n\n")
        elif len(sels) > 1:
            App.Console.PrintWarning("Only select one object!\n\n")
        else:  # sels
            for obj in sels:
                currentSelectedName = obj.Label
            App.Console.PrintLog(
                "Selecting all visible objects of "
                + docName
                + " - "
                + currentSelectedName
                + "\n"
            )
            # find the treeitem for ActiveDocument
            for idx in range(top.childCount()):
                doc = top.child(idx)
                if doc.data(0, 0) == App.ActiveDocument.Label:
                    top = doc

            # store a list of selected items
            for sel in tree.selectedItems():
                current = sel
                selectedList.append(current.data(0, 0))

            self.traverseFindSelected(top, "")

        for newSel in addToSelectionList:
            Gui.Selection.addSelection(docName, newSel)

    def IsActive(self):
        """Return True when the command should be active or False when it should be disabled (greyed)."""
        if App.ActiveDocument and Gui.Selection.getSelection():
            return Utils.havePage() and Utils.haveView()
        else:
            return False

    # try to get internal object associated with QTreeWidgetItem
    def getInternalObject(self, treeItem):
        """ """
        # first looks by Label
        obj = App.ActiveDocument.getObjectsByLabel(treeItem.data(0, 0))
        if len(obj) > 0:
            return obj[0]
        else:
            # if not found, looks by Name
            return App.ActiveDocument.getObject(treeItem.data(0, 0))
        pass

    def getObjFromTreeItem(self, item):
        """ """
        name = item.data(0, 0)
        return self.getInternalObject(item)

    # for each object in treeview
    def traverse(self, list, pad):
        """ """
        # for each child
        for idx in range(list.childCount()):
            item = list.child(idx)
            obj = self.getObjFromTreeItem(item)
            if (
                not obj.Name in addToSelectionList
                and obj.TypeId != "App::DocumentObjectGroup"
                and hasattr(obj, "Visibility")
                and obj.Visibility == True
            ):
                addToSelectionList.append(obj.Name)
            self.traverse(item, pad + "  ")

    # for each object in treeview
    def traverseFindSelected(self, list, pad):
        """ """
        # for each child
        for idx in range(list.childCount()):
            item = list.child(idx)
            obj = self.getObjFromTreeItem(item)
            if not obj.Label in selectedList:
                self.traverseFindSelected(item, pad + "  ")
            break
        self.traverse(item, pad + "  ")


#
# The command must be "registered" with a unique name by calling its class.
Gui.addCommand("TechDraw_BIMSelectAllChildren", CommandBIMSelectAllChildren())
