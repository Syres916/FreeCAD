# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2023 Robert Schöftner <rs@unfoo.net>                    *
# *   Copyright (c) 2021 Russell Johnson (russ4262) <russ4262@gmail.com>    *
# *                                                                         *
# *   This file is part of the FreeCAD CAx development system.              *
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

import FreeCAD as App
import Part
import Path.Op.Drilling as PathDrilling
import Path.Main.Job as PathJob
import Sketcher
import TestSketcherApp
from Tests.PathTestUtils import PathTestBase
from Tests.TestPathAdaptive import getGcodeMoves

if App.GuiUp:
    import Path.Main.Gui.Job as PathJobGui
    import Path.Op.Gui.Drilling as PathDrillingGui


class TestPathDrillTopo(PathTestBase):
    """Unit tests for the Drill operation after TNP implementation.
    The main goal is to ensure that changing base geometry such as
    the size of the plate or changing a circle to construction hence
    reducing the number of holes by one still produces a valid path."""

    @classmethod
    def setUpClass(cls):
        """setUpClass()...
        This method is called upon instantiation of this test class.  Add code and objects here
        that are needed for the duration of the test() methods in this class.  In other words,
        set up the 'global' test environment here; use the `setUp()` method to set up a 'local'
        test environment.
        This method does not have access to the class `self` reference, but it
        is able to call static methods within this same class.
        """
        cls.needsInit = True

    @classmethod
    def initClass(cls):
        # Create FreeCAD document with test geometry
        cls.needsInit = False

        # Arrange
        cls.doc = App.newDocument("CAMDrillingTestTNP")
        cls.Body = cls.doc.addObject("PartDesign::Body", "Body")
        # Make first offset cube Pad
        cls.PadSketch = cls.doc.addObject("Sketcher::SketchObject", "Sketch")
        cls.Body.addObject(cls.PadSketch)
        TestSketcherApp.CreateRectangleSketch(cls.PadSketch, (-75, -50), (150, 100))
        TestSketcherApp.CreateRectangleSketch(cls.PadSketch, (-65, -40), (130, 80))
        cls.PadSketch.toggleConstruction(6)
        cls.PadSketch.toggleConstruction(7)
        cls.PadSketch.toggleConstruction(4)
        cls.PadSketch.toggleConstruction(5)
        cls.geoList = []
        cls.geoList.append(
            Part.Circle(
                App.Vector(-52.169476, 27.143223, 0.000000),
                App.Vector(0.000000, 0.000000, 1.000000),
                4.719386,
            )
        )
        cls.geoList.append(
            Part.Circle(
                App.Vector(-52.169476, -26.825031, 0.000000),
                App.Vector(0.000000, 0.000000, 1.000000),
                4.687248,
            )
        )
        cls.geoList.append(
            Part.Circle(
                App.Vector(54.497200, -26.825031, 0.000000),
                App.Vector(0.000000, 0.000000, 1.000000),
                4.465803,
            )
        )
        cls.geoList.append(
            Part.Circle(
                App.Vector(54.497200, 27.143223, 0.000000),
                App.Vector(0.000000, 0.000000, 1.000000),
                4.445692,
            )
        )
        cls.PadSketch.addGeometry(cls.geoList, False)
        del cls.geoList
        cls.constraintList = []
        cls.constraintList.append(Sketcher.Constraint("Coincident", 8, 3, 6, 2))
        cls.constraintList.append(Sketcher.Constraint("Coincident", 9, 3, 4, 1))
        cls.constraintList.append(Sketcher.Constraint("Coincident", 10, 3, 4, 2))
        cls.constraintList.append(Sketcher.Constraint("Coincident", 11, 3, 5, 2))
        cls.PadSketch.addConstraint(cls.constraintList)
        del cls.constraintList
        cls.PadSketch.addConstraint(Sketcher.Constraint("Equal", 8, 9))
        cls.PadSketch.addConstraint(Sketcher.Constraint("Equal", 9, 10))
        cls.PadSketch.addConstraint(Sketcher.Constraint("Equal", 10, 11))
        cls.PadSketch.addConstraint(Sketcher.Constraint("Diameter", 9, 5.2))
        cls.PadSketch.setDatum(31, App.Units.Quantity("5.200000 mm"))
        cls.doc.recompute()
        cls.Pad001 = cls.Body.newObject("PartDesign::Pad", "Pad001")
        cls.Pad001.Profile = (
            cls.doc.getObject("Sketch"),
            [
                "",
            ],
        )
        cls.Pad001.Length = 10
        cls.Pad001.TaperAngle = 0.000000
        cls.Pad001.UseCustomVector = 0
        cls.Pad001.Direction = (0, 0, 1)
        cls.Pad001.ReferenceAxis = (
            App.getDocument("CAMDrillingTestTNP").getObject("Sketch"),
            ["N_Axis"],
        )
        cls.Pad001.AlongSketchNormal = 1
        cls.Pad001.Type = 0
        cls.Pad001.UpToFace = None
        cls.Pad001.Reversed = 0
        cls.Pad001.Midplane = 0
        cls.Pad001.Offset = 0
        cls.doc.recompute()

    @classmethod
    def tearDownClass(cls):
        """tearDownClass()...
        This method is called prior to destruction of this test class.  Add code and objects here
        that cleanup the test environment after the test() methods in this class have been executed.
        This method does not have access to the class `self` reference.  This method
        is able to call static methods within this same class.
        """
        App.Console.PrintMessage("TestPathAdaptive.tearDownClass()\n")

        # Close geometry document without saving
        # if not cls.needsInit:
        #     App.closeDocument(cls.doc.Name)

    # Setup and tear down methods called before and after each unit test
    def setUp(self):
        """setUp()...
        This method is called prior to each `test()` method.  Add code and objects here
        that are needed for multiple `test()` methods.
        """
        if self.needsInit:
            self.initClass()

    def tearDown(self):
        """tearDown()...
        This method is called after each test() method. Add cleanup instructions here.
        Such cleanup instructions will likely undo those in the setUp() method.
        """
        pass

    # Unit tests
    def test00(self):
        """test00() Empty test."""
        return

    def test01(self):
        """test01() Verify path generated on Face18, outside, with tool compensation."""

        # Create Job object, adding geometry objects from file opened above
        self.job = PathJob.Create("Job", [self.doc.Body], None)
        self.job.GeometryTolerance.Value = 0.001
        if App.GuiUp:
            self.job.ViewObject.Proxy = PathJobGui.ViewProvider(self.job.ViewObject)
        self.doc.recompute()
        # Instantiate a Drill operation and set Base Geometry
        drill = PathDrilling.Create("Drilling")
        drill.Base = [
            (self.doc.Body, ["Face5", "Face6", "Face7", "Face8"])
        ]  # (base, subs_list)
        drill.Label = "drill"
        drill.Comment = "drill() Verify path generated for drilling four 5mm holes."
        drill.PeckEnabled = True

        _addViewProvider(drill)
        self.doc.recompute()

        moves = getGcodeMoves(drill.Path.Commands)
        operationMoves = ";  ".join(moves)
        self.doc.recompute()
        """ Currently TNP fails with:
        CircularHoleBase.ERROR: Feature Body.Face7 cannot be processed as a circular hole - please remove from Base geometry list.
        CircularHoleBase.ERROR: Feature Body.Face8 cannot be processed as a circular hole - please remove from Base geometry list.
        """

        expected_moves = (
            "G0 Z16.0;  G0 X65.0 Y-40.0;  G0 X65.0 Y40.0;  G0 X-65.0 Y40.0;"
            "  G0 X-65.0 Y-40.0;  G0 Z14.0;  G0 Z16.0"
        )
        self.assertTrue(
            expected_moves == operationMoves,
            "expected_moves: {}\noperationMoves: {}".format(
                expected_moves, operationMoves
            ),
        )

        """ Only when the above TNP issue has been fixed can the next section of the test be activated
        which is to change the sketch in order to get the drill operation to recalculate. """
        # Now the plate will be resized
        # self.PadSketch.setDatum(11,App.Units.Quantity('200.000000 mm'))
        # self.PadSketch.setDatum(23,App.Units.Quantity('180.000000 mm'))
        # self.PadSketch.setDatum(8,App.Units.Quantity('-100.000000 mm'))
        # self.PadSketch.setDatum(20,App.Units.Quantity('-90.000000 mm'))
        # self.doc.recompute()


def _addViewProvider(drillingOp):
    if App.GuiUp:
        PathOpGui = PathDrillingGui.PathOpGui
        cmdRes = PathDrillingGui.Command.res
        drillingOp.ViewObject.Proxy = PathOpGui.ViewProvider(
            drillingOp.ViewObject, cmdRes
        )
