#**************************************************************************
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
#**************************************************************************

import os
import sys
import unittest
import FreeCAD
import FreeCADGui
import Part
import PartGui
from PySide import QtWidgets
import Sketcher

def findDockWidget(name):
    """ Get a dock widget by name """
    mw = FreeCADGui.getMainWindow()
    dws = mw.findChildren(QtWidgets.QDockWidget)
    for dw in dws:
        if dw.objectName() == name:
            return dw
    return None

"""
#---------------------------------------------------------------------------
# define the test cases to test the FreeCAD Part module
#---------------------------------------------------------------------------
"""
from parttests.ColorPerFaceTest import ColorPerFaceTest
from parttests.ColorTransparencyTest import ColorTransparencyTest


#class PartGuiTestCases(unittest.TestCase):
#    def setUp(self):
#        self.Doc = FreeCAD.newDocument("PartGuiTest")
#
#    def testBoxCase(self):
#        self.Box = self.Doc.addObject('Part::SketchObject','SketchBox')
#        self.Box.addGeometry(Part.LineSegment(FreeCAD.Vector(-99.230339,36.960674,0),FreeCAD.Vector(69.432587,36.960674,0)))
#        self.Box.addGeometry(Part.LineSegment(FreeCAD.Vector(69.432587,36.960674,0),FreeCAD.Vector(69.432587,-53.196629,0)))
#        self.Box.addGeometry(Part.LineSegment(FreeCAD.Vector(69.432587,-53.196629,0),FreeCAD.Vector(-99.230339,-53.196629,0)))
#        self.Box.addGeometry(Part.LineSegment(FreeCAD.Vector(-99.230339,-53.196629,0),FreeCAD.Vector(-99.230339,36.960674,0)))
#
#    def tearDown(self):
#        #closing doc
#        FreeCAD.closeDocument("PartGuiTest")
class PartGuiViewProviderTestCases(unittest.TestCase):
    def setUp(self):
        self.Doc = FreeCAD.newDocument("PartGuiTest")

    def testCanDropObject(self):
        # https://github.com/FreeCAD/FreeCAD/pull/6850
        box = self.Doc.addObject("Part::Box", "Box")
        with self.assertRaises(TypeError):
            box.ViewObject.canDragObject(0)
        with self.assertRaises(TypeError):
            box.ViewObject.canDropObject(0)
        box.ViewObject.canDropObject()
        with self.assertRaises(TypeError):
            box.ViewObject.dropObject(box, 0)

    def tearDown(self):
        #closing doc
        FreeCAD.closeDocument("PartGuiTest")

class SectionCutTestCases(unittest.TestCase):
    def setUp(self):
        self.Doc = FreeCAD.newDocument("SectionCut")

    def testOpenDialog(self):
        box = self.Doc.addObject("Part::Box", "SectionCutBoxX")
        comp = self.Doc.addObject("Part::Compound", "SectionCutCompound")
        comp.Links = box
        grp = self.Doc.addObject("App::DocumentObjectGroup", "SectionCutX")
        grp.addObject(comp)
        self.Doc.recompute()

        FreeCADGui.runCommand("Part_SectionCut")
        dw = findDockWidget("Section Cutting")
        if dw:
            box = dw.findChild(QtWidgets.QDialogButtonBox)
            button = box.button(QtWidgets.QDialogButtonBox.Close)
            button.click()
        else:
            print ("No Section Cutting panel found")



class RuledSurfaceTestCases(unittest.TestCase):
    def setUp(self):
        self.Doc = FreeCAD.newDocument("RuledSurfaceTest")

    def testXYPlaneRSCreate(self):
        self.RuledSurfaceSketch = self.Doc.addObject('Sketcher::SketchObject', 'SketchXY')
        self.RuledSurfaceSketch.Placement = FreeCAD.Placement(FreeCAD.Vector(0.000000, 0.000000, 0.000000), FreeCAD.Rotation(0.000000, 0.000000, 0.000000, 1.000000))
        self.RuledSurfaceSketch.MapMode = "Deactivated"
        geoList = []
        geoList.append(Part.ArcOfCircle(Part.Circle(FreeCAD.Vector(-46.406574, 4.004109, 0), FreeCAD.Vector(0, 0, 1), 28.798770), 1.570796, 4.712389))
        geoList.append(Part.ArcOfCircle(Part.Circle(FreeCAD.Vector(68.788506, 4.004109 ,0), FreeCAD.Vector(0, 0, 1), 28.798770), 4.712389, 7.853982))
        geoList.append(Part.LineSegment(FreeCAD.Vector(-46.406574, -24.794661, 0), FreeCAD.Vector(68.788506, -24.794661, 0)))
        geoList.append(Part.LineSegment(FreeCAD.Vector(68.788506, 32.802879, 0), FreeCAD.Vector(-46.406574, 32.802879, 0)))
        self.RuledSurfaceSketch.addGeometry(geoList, False)
        conList = []
        conList.append(Sketcher.Constraint('Tangent', 0, 2, 2, 1))
        conList.append(Sketcher.Constraint('Tangent', 2, 2, 1, 1))
        conList.append(Sketcher.Constraint('Tangent', 1, 2, 3, 1))
        conList.append(Sketcher.Constraint('Tangent', 3, 2, 0, 1))
        conList.append(Sketcher.Constraint('Equal', 0, 1))
        self.RuledSurfaceSketch.addConstraint(conList)
        del geoList, conList

        self.RuledSurfaceSketch.addConstraint(Sketcher.Constraint('Horizontal',3))

        self.RuledSurfaceSketch.addConstraint(Sketcher.Constraint('Radius',1,28.798770))
        self.RuledSurfaceSketch.setDatum(6,FreeCAD.Units.Quantity('30.000000 mm'))
        self.RuledSurfaceSketch.addConstraint(Sketcher.Constraint('DistanceX',2,1,2,2,115.195072))
        self.RuledSurfaceSketch.setDatum(7,FreeCAD.Units.Quantity('100.000000 mm'))
        self.RuledSurfaceSketch.addConstraint(Sketcher.Constraint('PointOnObject',0,3,-1))
        self.Doc.recompute()

        self.RuledSurfaceSketch.delConstraint(5)
        self.RuledSurfaceSketch.addConstraint(Sketcher.Constraint('Symmetric',0,3,1,3,-2))
        self.Doc.recompute()

        self.RuledSurface = self.Doc.addObject('Part::RuledSurface', 'Ruled SurfaceXY')
        self.RuledSurface.Curve1=(self.RuledSurfaceSketch,u'Edge1')
        self.RuledSurface.Curve2=(self.RuledSurfaceSketch,u'Edge3')
        self.Doc.recompute()

        self.assertAlmostEqual(self.RuledSurface.Shape.BoundBox.XMin, -80)
        self.assertAlmostEqual(self.RuledSurface.Shape.BoundBox.YMin, -30)
        self.assertAlmostEqual(self.RuledSurface.Shape.BoundBox.ZMin, 0)
        self.assertAlmostEqual(self.RuledSurface.Shape.BoundBox.XMax, 80)
        self.assertAlmostEqual(self.RuledSurface.Shape.BoundBox.YMax, 30)
        self.assertAlmostEqual(self.RuledSurface.Shape.BoundBox.ZMax, 0)

        self.assertAlmostEqual(self.RuledSurface.Shape.Area, 8827.433388208741)

        FreeCADGui.SendMsgToActiveView("ViewFit")


    def testXZPlaneRSCreate(self):
        self.RuledSurfaceSketch = self.Doc.addObject('Sketcher::SketchObject', 'SketchXZ')
        self.RuledSurfaceSketch.Placement = FreeCAD.Placement(FreeCAD.Vector(0.000000, 0.000000, 0.000000), FreeCAD.Rotation(FreeCAD.Vector(0.58,0.58,0.58),120))
        self.RuledSurfaceSketch.MapMode = "Deactivated"
        geoList = []
        geoList.append(Part.ArcOfCircle(Part.Circle(FreeCAD.Vector(-46.406574, 4.004109, 0), FreeCAD.Vector(0, 0, 1), 28.798770), 1.570796, 4.712389))
        geoList.append(Part.ArcOfCircle(Part.Circle(FreeCAD.Vector(68.788506, 4.004109 ,0), FreeCAD.Vector(0, 0, 1), 28.798770), 4.712389, 7.853982))
        geoList.append(Part.LineSegment(FreeCAD.Vector(-46.406574, -24.794661, 0), FreeCAD.Vector(68.788506, -24.794661, 0)))
        geoList.append(Part.LineSegment(FreeCAD.Vector(68.788506, 32.802879, 0), FreeCAD.Vector(-46.406574, 32.802879, 0)))
        self.RuledSurfaceSketch.addGeometry(geoList, False)
        conList = []
        conList.append(Sketcher.Constraint('Tangent', 0, 2, 2, 1))
        conList.append(Sketcher.Constraint('Tangent', 2, 2, 1, 1))
        conList.append(Sketcher.Constraint('Tangent', 1, 2, 3, 1))
        conList.append(Sketcher.Constraint('Tangent', 3, 2, 0, 1))
        conList.append(Sketcher.Constraint('Equal', 0, 1))
        self.RuledSurfaceSketch.addConstraint(conList)
        del geoList, conList

        self.RuledSurfaceSketch.addConstraint(Sketcher.Constraint('Horizontal',3))

        self.RuledSurfaceSketch.addConstraint(Sketcher.Constraint('Radius',1,28.798770))
        self.RuledSurfaceSketch.setDatum(6,FreeCAD.Units.Quantity('30.000000 mm'))
        self.RuledSurfaceSketch.addConstraint(Sketcher.Constraint('DistanceX',2,1,2,2,115.195072))
        self.RuledSurfaceSketch.setDatum(7,FreeCAD.Units.Quantity('100.000000 mm'))
        self.RuledSurfaceSketch.addConstraint(Sketcher.Constraint('PointOnObject',0,3,-1))
        self.Doc.recompute()

        self.RuledSurfaceSketch.delConstraint(5)
        self.RuledSurfaceSketch.addConstraint(Sketcher.Constraint('Symmetric',0,3,1,3,-2))
        self.Doc.recompute()

        self.RuledSurface = self.Doc.addObject('Part::RuledSurface', 'Ruled SurfaceXZ')
        self.RuledSurface.Curve1=(self.RuledSurfaceSketch,u'Edge1')
        self.RuledSurface.Curve2=(self.RuledSurfaceSketch,u'Edge3')
        self.Doc.recompute()

        self.assertAlmostEqual(self.RuledSurface.Shape.BoundBox.XMin, 0)
        self.assertAlmostEqual(self.RuledSurface.Shape.BoundBox.YMin, -83.6097)
        self.assertAlmostEqual(self.RuledSurface.Shape.BoundBox.ZMin, -30)
        self.assertAlmostEqual(self.RuledSurface.Shape.BoundBox.XMax, 0)
        self.assertAlmostEqual(self.RuledSurface.Shape.BoundBox.YMax, 83.6097)
        self.assertAlmostEqual(self.RuledSurface.Shape.BoundBox.ZMax, 30)

        self.assertAlmostEqual(self.RuledSurface.Shape.Area, 8827.433388208741)

        FreeCADGui.SendMsgToActiveView("ViewFit")

    def testYZPlaneRSCreate(self):
        self.RuledSurfaceSketch = self.Doc.addObject('Sketcher::SketchObject', 'SketchYZ')
        self.RuledSurfaceSketch.Placement = FreeCAD.Placement(FreeCAD.Vector(0.000000, 0.000000, 0.000000), FreeCAD.Rotation(FreeCAD.Vector(1.0,0,0),90))
        self.RuledSurfaceSketch.MapMode = "Deactivated"
        geoList = []
        geoList.append(Part.ArcOfCircle(Part.Circle(FreeCAD.Vector(-46.406574, 4.004109, 0), FreeCAD.Vector(0, 0, 1), 28.798770), 1.570796, 4.712389))
        geoList.append(Part.ArcOfCircle(Part.Circle(FreeCAD.Vector(68.788506, 4.004109 ,0), FreeCAD.Vector(0, 0, 1), 28.798770), 4.712389, 7.853982))
        geoList.append(Part.LineSegment(FreeCAD.Vector(-46.406574, -24.794661, 0), FreeCAD.Vector(68.788506, -24.794661, 0)))
        geoList.append(Part.LineSegment(FreeCAD.Vector(68.788506, 32.802879, 0), FreeCAD.Vector(-46.406574, 32.802879, 0)))
        self.RuledSurfaceSketch.addGeometry(geoList, False)
        conList = []
        conList.append(Sketcher.Constraint('Tangent', 0, 2, 2, 1))
        conList.append(Sketcher.Constraint('Tangent', 2, 2, 1, 1))
        conList.append(Sketcher.Constraint('Tangent', 1, 2, 3, 1))
        conList.append(Sketcher.Constraint('Tangent', 3, 2, 0, 1))
        conList.append(Sketcher.Constraint('Equal', 0, 1))
        self.RuledSurfaceSketch.addConstraint(conList)
        del geoList, conList

        self.RuledSurfaceSketch.addConstraint(Sketcher.Constraint('Horizontal',3))

        self.RuledSurfaceSketch.addConstraint(Sketcher.Constraint('Radius',1,28.798770))
        self.RuledSurfaceSketch.setDatum(6,FreeCAD.Units.Quantity('30.000000 mm'))
        self.RuledSurfaceSketch.addConstraint(Sketcher.Constraint('DistanceX',2,1,2,2,115.195072))
        self.RuledSurfaceSketch.setDatum(7,FreeCAD.Units.Quantity('100.000000 mm'))
        self.RuledSurfaceSketch.addConstraint(Sketcher.Constraint('PointOnObject',0,3,-1))
        self.Doc.recompute()

        self.RuledSurfaceSketch.delConstraint(5)
        self.RuledSurfaceSketch.addConstraint(Sketcher.Constraint('Symmetric',0,3,1,3,-2))
        self.Doc.recompute()

        self.RuledSurface = self.Doc.addObject('Part::RuledSurface', 'Ruled SurfaceYZ')
        self.RuledSurface.Curve1=(self.RuledSurfaceSketch,u'Edge1')
        self.RuledSurface.Curve2=(self.RuledSurfaceSketch,u'Edge3')
        self.Doc.recompute()

        self.assertAlmostEqual(self.RuledSurface.Shape.BoundBox.XMin, 0)
        self.assertAlmostEqual(self.RuledSurface.Shape.BoundBox.YMin, -83.6097)
        self.assertAlmostEqual(self.RuledSurface.Shape.BoundBox.ZMin, -30)
        self.assertAlmostEqual(self.RuledSurface.Shape.BoundBox.XMax, 0)
        self.assertAlmostEqual(self.RuledSurface.Shape.BoundBox.YMax, 83.6097)
        self.assertAlmostEqual(self.RuledSurface.Shape.BoundBox.ZMax, 30)

        self.assertAlmostEqual(self.RuledSurface.Shape.Area, 8827.433388208741)

        FreeCADGui.SendMsgToActiveView("ViewFit")


    def testSpecialPlaneRSCreate(self):
        self.RuledSurfaceSketch = self.Doc.addObject('Sketcher::SketchObject', 'SketchSpecial')
        self.RuledSurfaceSketch.Placement = FreeCAD.Placement(FreeCAD.Vector(3.595176185196667,0,1.753484587156312),FreeCAD.Rotation(FreeCAD.Vector(0.3361383527176155,0.6488071227438279,0.6826861103824818),310))
        self.RuledSurfaceSketch.MapMode = "Deactivated"
        geoList = []
        geoList.append(Part.ArcOfCircle(Part.Circle(FreeCAD.Vector(-46.406574, 4.004109, 0), FreeCAD.Vector(0, 0, 1), 28.798770), 1.570796, 4.712389))
        geoList.append(Part.ArcOfCircle(Part.Circle(FreeCAD.Vector(68.788506, 4.004109 ,0), FreeCAD.Vector(0, 0, 1), 28.798770), 4.712389, 7.853982))
        geoList.append(Part.LineSegment(FreeCAD.Vector(-46.406574, -24.794661, 0), FreeCAD.Vector(68.788506, -24.794661, 0)))
        geoList.append(Part.LineSegment(FreeCAD.Vector(68.788506, 32.802879, 0), FreeCAD.Vector(-46.406574, 32.802879, 0)))
        self.RuledSurfaceSketch.addGeometry(geoList, False)
        conList = []
        conList.append(Sketcher.Constraint('Tangent', 0, 2, 2, 1))
        conList.append(Sketcher.Constraint('Tangent', 2, 2, 1, 1))
        conList.append(Sketcher.Constraint('Tangent', 1, 2, 3, 1))
        conList.append(Sketcher.Constraint('Tangent', 3, 2, 0, 1))
        conList.append(Sketcher.Constraint('Equal', 0, 1))
        self.RuledSurfaceSketch.addConstraint(conList)
        del geoList, conList

        self.RuledSurfaceSketch.addConstraint(Sketcher.Constraint('Horizontal',3))

        self.RuledSurfaceSketch.addConstraint(Sketcher.Constraint('Radius',1,28.798770))
        self.RuledSurfaceSketch.setDatum(6,FreeCAD.Units.Quantity('30.000000 mm'))
        self.RuledSurfaceSketch.addConstraint(Sketcher.Constraint('DistanceX',2,1,2,2,115.195072))
        self.RuledSurfaceSketch.setDatum(7,FreeCAD.Units.Quantity('100.000000 mm'))
        self.RuledSurfaceSketch.addConstraint(Sketcher.Constraint('PointOnObject',0,3,-1))
        self.Doc.recompute()

        self.RuledSurfaceSketch.delConstraint(5)
        self.RuledSurfaceSketch.addConstraint(Sketcher.Constraint('Symmetric',0,3,1,3,-2))
        self.Doc.recompute()

        self.RuledSurface = self.Doc.addObject('Part::RuledSurface', 'Ruled SurfaceSpecial')
        self.RuledSurface.Curve1=(self.RuledSurfaceSketch,u'Edge1')
        self.RuledSurface.Curve2=(self.RuledSurfaceSketch,u'Edge3')
        self.Doc.recompute()

        self.assertAlmostEqual(self.RuledSurface.Shape.BoundBox.XMin, -83.6097)
        self.assertAlmostEqual(self.RuledSurface.Shape.BoundBox.YMin, -6.66134e-15)
        self.assertAlmostEqual(self.RuledSurface.Shape.BoundBox.ZMin, -30)
        self.assertAlmostEqual(self.RuledSurface.Shape.BoundBox.XMax, 83.6097)
        self.assertAlmostEqual(self.RuledSurface.Shape.BoundBox.YMax, 6.66134e-15)
        self.assertAlmostEqual(self.RuledSurface.Shape.BoundBox.ZMax, 30)

        self.assertAlmostEqual(self.RuledSurface.Shape.Area, 8827.433388208741)

        FreeCADGui.SendMsgToActiveView("ViewFit")


    def tearDown(self):
        print("No teardown yet")
        # FreeCAD.closeDocument("RuledSurfaceTest")
