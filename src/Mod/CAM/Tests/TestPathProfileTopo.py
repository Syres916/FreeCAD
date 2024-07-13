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
import Path.Op.Profile as PathProfile
import Path.Main.Job as PathJob
import Sketcher
import TestSketcherApp
from Tests.PathTestUtils import PathTestBase
from Tests.TestPathAdaptive import getGcodeMoves

if App.GuiUp:
    import Path.Main.Gui.Job as PathJobGui
    import Path.Op.Gui.Profile as PathProfileGui


class TestPathProfileTopo(PathTestBase):
    """Unit tests for the Profile operation after TNP implementation.
    The main goal is to ensure that changing base geometry such as
    the size of the plate or changing a sharp corner to one with a radius hence
    increasing the number of faces by one still produces a valid path."""

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
        cls.doc = App.newDocument("CAMProfileTestTopo")
        cls.Body = cls.doc.addObject("PartDesign::Body", "Body")
        # Make frame Pad with sharp corners
        cls.PadSketch = cls.doc.addObject("Sketcher::SketchObject", "Sketch")
        cls.Body.addObject(cls.PadSketch)
        TestSketcherApp.CreateRectangleSketch(cls.PadSketch, (-75, -50), (150, 100))
        TestSketcherApp.CreateRectangleSketch(cls.PadSketch, (-65, -40), (130, 80))
        cls.doc.recompute()
        cls.Pad = cls.Body.newObject("PartDesign::Pad", "Pad")
        cls.Pad.Profile = (
            cls.doc.getObject("Sketch"),
            [
                "",
            ],
        )
        cls.Pad.Length = 10
        cls.Pad.TaperAngle = 0.000000
        cls.Pad.UseCustomVector = 0
        cls.Pad.Direction = (0, 0, 1)
        cls.Pad.ReferenceAxis = (
            App.getDocument("CAMProfileTestTopo").getObject("Sketch"),
            ["N_Axis"],
        )
        cls.Pad.AlongSketchNormal = 1
        cls.Pad.Type = 0
        cls.Pad.UpToFace = None
        cls.Pad.Reversed = 0
        cls.Pad.Midplane = 0
        cls.Pad.Offset = 0
        cls.doc.recompute()

        cls.PadSketch001 = cls.doc.addObject("Sketcher::SketchObject", "Sketch001")
        cls.Body.addObject(cls.PadSketch001)
        TestSketcherApp.CreateRectangleSketch(cls.PadSketch001, (-75, -50), (150, 100))
        TestSketcherApp.CreateRectangleSketch(cls.PadSketch001, (-70, -45), (140, 90))
        cls.doc.recompute()
        # cls.PadSketch001.AttachmentOffset = App.Placement(
        #     App.Vector(0, 0, 10), App.Rotation(App.Vector(0, 0, 1), 0)
        # )
        cls.doc.recompute()
        cls.Pad001 = cls.Body.newObject("PartDesign::Pad", "Pad001")
        cls.Pad001.Profile = (
            cls.doc.getObject("Sketch001"),
            [
                "",
            ],
        )
        cls.Pad001.Length = 10
        cls.Pad001.TaperAngle = 0.000000
        cls.Pad001.UseCustomVector = 0
        cls.Pad001.Direction = (0, 0, 1)
        cls.Pad001.ReferenceAxis = (
            App.getDocument("CAMProfileTestTopo").getObject("Sketch001"),
            ["N_Axis"],
        )
        cls.Pad001.AlongSketchNormal = 1
        cls.Pad001.Type = 0
        cls.Pad001.UpToFace = None
        cls.Pad001.Reversed = 0
        cls.Pad001.Midplane = 0
        cls.Pad001.Offset = 0
        cls.doc.recompute()

        # Create Job object, adding geometry objects from file opened above
        cls.job = PathJob.Create("Job", [cls.doc.Body], None)
        cls.job.GeometryTolerance.Value = 0.001
        if App.GuiUp:
            cls.job.ViewObject.Proxy = PathJobGui.ViewProvider(cls.job.ViewObject)
        cls.doc.recompute()
        # Instantiate a Profile operation and set Base Geometry
        cls.profile = PathProfile.Create("Profile")
        cls.profile.Base = [(cls.doc.Body, ["Face5"])]  # (base, subs_list)
        cls.profile.Label = "profile"
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
        """test01() Verify path generated on Face5, outside, with tool compensation."""

        self.profile.Comment = (
            "profile() Verify path generated for internal and external rectangles."
        )

        _addViewProvider(self.profile)
        self.doc.recompute()

        moves = getGcodeMoves(self.profile.Path.Commands)
        operationMoves = ";  ".join(moves)
        self.doc.recompute()

        expected_moves = (
            "G0 Z16.0;  G0 X76.77 Y51.77;  G0 Z14.0;  G1 X76.77 Y51.77 Z6.0;  G2 I-1.77 J-1.77 K0.0 X77.5 Y50.0 Z6.0;"
            "  G1 X77.5 Y-50.0 Z6.0;  G2 I-2.5 J0.0 K0.0 X75.0 Y-52.5 Z6.0;  G1 X-75.0 Y-52.5 Z6.0;  G2 I0.0 J2.5 K0.0 X-77.5 Y-50.0 Z6.0;"
            "  G1 X-77.5 Y50.0 Z6.0;  G2 I2.5 J-0.0 K0.0 X-75.0 Y52.5 Z6.0;  G1 X75.0 Y52.5 Z6.0;  G2 I-0.0 J-2.5 K0.0 X76.77 Y51.77 Z6.0;"
            "  G1 X76.77 Y51.77 Z1.0;  G2 I-1.77 J-1.77 K0.0 X77.5 Y50.0 Z1.0;  G1 X77.5 Y-50.0 Z1.0;  G2 I-2.5 J0.0 K0.0 X75.0 Y-52.5 Z1.0;"
            "  G1 X-75.0 Y-52.5 Z1.0;  G2 I0.0 J2.5 K0.0 X-77.5 Y-50.0 Z1.0;  G1 X-77.5 Y50.0 Z1.0;  G2 I2.5 J-0.0 K0.0 X-75.0 Y52.5 Z1.0;"
            "  G1 X75.0 Y52.5 Z1.0;  G2 I-0.0 J-2.5 K0.0 X76.77 Y51.77 Z1.0;  G1 X76.77 Y51.77 Z0.0;  G2 I-1.77 J-1.77 K0.0 X77.5 Y50.0 Z0.0;"
            "  G1 X77.5 Y-50.0 Z0.0;  G2 I-2.5 J0.0 K0.0 X75.0 Y-52.5 Z0.0;  G1 X-75.0 Y-52.5 Z0.0;  G2 I0.0 J2.5 K0.0 X-77.5 Y-50.0 Z0.0;"
            "  G1 X-77.5 Y50.0 Z0.0;  G2 I2.5 J-0.0 K0.0 X-75.0 Y52.5 Z0.0;  G1 X75.0 Y52.5 Z0.0;  G2 I-0.0 J-2.5 K0.0 X76.77 Y51.77 Z0.0;"
            "  G0 Z16.0;  G0 Z16.0"
        )

        self.assertTrue(
            expected_moves == operationMoves,
            "expected_moves: {}\noperationMoves: {}".format(
                expected_moves, operationMoves
            ),
        )

    def test02(self):
        """test02() Verify inside path changing a sharp corner to one with a radius"""
        print(dir(self))
        self.profile.Base = [
            (self.doc.Body, ["Edge15", "Edge16", "Edge13", "Edge14", "Face10"])
        ]  # (base, subs_list)
        self.profile.Side = "Inside"
        App.getDocument("CAMProfileTestTopo").getObject("Sketch").fillet(
            6,
            5,
            App.Vector(58.045578, -40.000000, 0),
            App.Vector(65.000000, -35.194954, 0),
            5.263866,
            True,
            True,
            False,
        )
        self.doc.recompute()

        """ Currently TNP fails with:
        File "/home/john/freecad-main-build763/Mod/CAM/Path/Op/Base.py", line 786, in execute
          self.sanitizeBase(obj)
        File "/home/john/freecad-main-build763/Mod/CAM/Path/Op/Base.py", line 745, in sanitizeBase
          o.Shape.getElement(sub)
        <class 'ValueError'>: Invalid subelement name
           profile: Invalid subelement name
        """

    def test03(self):
        """test03() Verify inside path with step model using mixture of Edges and Face"""
        # now move Sketch001 up to create a step but only when test02 has been fixed
        # self.doc.Sketch001.Placement = App.Placement(App.Vector(0,0,10),App.Rotation(App.Vector(0,0,1),0))
        # self.doc.recompute()


def _addViewProvider(profileOp):
    if App.GuiUp:
        PathOpGui = PathProfileGui.PathOpGui
        cmdRes = PathProfileGui.Command.res
        profileOp.ViewObject.Proxy = PathOpGui.ViewProvider(
            profileOp.ViewObject, cmdRes
        )
