# **************************************************************************
#   Copyright (c) 2011 Juergen Riegel <FreeCAD@juergen-riegel.net>        *
#                                                                         *
#   This file is part of the FreeCAD CAx development system.              *
#                                                                         *
#   This program is free software; you can redistribute it and/or modify  *
#   it under the terms of the GNU Lesser General Public License (LGPL)    *
#   as published by the Free Software Foundation; either version 2 of     *
#   the License, or (at your option) any later version.                   *
#   for detail see the LICENCE text file.                                 *
#                                                                         *
#   FreeCAD is distributed in the hope that it will be useful,            *
#   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#   GNU Library General Public License for more details.                  *
#                                                                         *
#   You should have received a copy of the GNU Library General Public     *
#   License along with FreeCAD; if not, write to the Free Software        *
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#   USA                                                                   *
# **************************************************************************

import FreeCAD
import FreeCADGui
import unittest
import Sketcher
import TestSketcherApp

App = FreeCAD
Gui = FreeCADGui


# ---------------------------------------------------------------------------
# define the test cases to test the FreeCAD Sketcher module
# ---------------------------------------------------------------------------


class SketcherGuiTestCases(unittest.TestCase):
    def setUp(self):
        self.Doc = FreeCAD.newDocument("SketcherGuiTest")

    def testSketchGetSubObjects(self):
        # Arrange
        Sketch = self.Doc.addObject("Sketcher::SketchObject", "Sketch")
        TestSketcherApp.CreateRectangleSketch(Sketch, (0, 0), (1, 1))
        # Act
        self.Doc.recompute()
        if Sketch.Shape.ElementMapVersion == "":  # Should be '4' as of Mar 2023.
            return
        Gui.Selection.addSelection(self.Doc.Name, "Sketch", "Edge1")
        self.assertEqual(len(Gui.Selection.getSelectionEx()[0].SubObjects), 1)
        if len(Gui.Selection.getSelectionEx()[0].SubObjects) == 1:
            self.assertEqual(
                App.Gui.Selection.getSelectionEx("", 0)[0].SubElementNames[0][-8:],
                "KT.Edge1",
            )

    def tearDown(self):
        FreeCAD.closeDocument("SketcherGuiTest")
