# ***************************************************************************
# *   Copyright (c) 2009, 2010 Yorik van Havre <yorik@uncreated.net>        *
# *   Copyright (c) 2009, 2010 Ken Cline <cline@frii.com>                   *
# *   Copyright (c) 2020 FreeCAD Developers                                 *
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
"""Provides the object code for the ShapeString object."""
## @package shapestring
# \ingroup draftobjects
# \brief Provides the object code for the ShapeString object.

## \addtogroup draftobjects
# @{
import math
from PySide.QtCore import QT_TRANSLATE_NOOP

import FreeCAD as App
import Part

from draftgeoutils import faces
from draftutils.messages import _wrn
from draftutils.translate import translate

from draftutils.params import get_param
from draftobjects.base import DraftObject

import fnmatch
import os.path
import platform
import re

class ShapeString(DraftObject):
    """The ShapeString object"""

    def __init__(self, obj):
        super().__init__(obj, "ShapeString")
        self.set_properties(obj)

    def set_properties(self, obj):
        """Add properties to the object and set them."""
        properties = obj.PropertiesList

        if "String" not in properties:
            _tip = QT_TRANSLATE_NOOP("App::Property", "Text string")
            obj.addProperty("App::PropertyString", "String", "Draft", _tip)

        if "FontFile" not in properties:
            _tip = QT_TRANSLATE_NOOP("App::Property", "Font file name")
            obj.addProperty("App::PropertyFile", "FontFile", "Draft", _tip)

        if "Size" not in properties:
            _tip = QT_TRANSLATE_NOOP("App::Property", "Height of text")
            obj.addProperty("App::PropertyLength", "Size", "Draft", _tip)

        if "Justification" not in properties:
            _tip = QT_TRANSLATE_NOOP("App::Property", "Horizontal and vertical alignment")
            obj.addProperty("App::PropertyEnumeration", "Justification", "Draft", _tip)
            obj.Justification = ["Top-Left", "Top-Center", "Top-Right",
                                 "Middle-Left", "Middle-Center", "Middle-Right",
                                 "Bottom-Left", "Bottom-Center", "Bottom-Right"]
            obj.Justification = "Bottom-Left"

        if "JustificationReference" not in properties:
            _tip = QT_TRANSLATE_NOOP("App::Property", "Height reference used for justification")
            obj.addProperty("App::PropertyEnumeration", "JustificationReference", "Draft", _tip)
            obj.JustificationReference = ["Cap Height", "Shape Height"]
            obj.JustificationReference = "Cap Height"

        if "KeepLeftMargin" not in properties:
            _tip = QT_TRANSLATE_NOOP("App::Property", "Keep left margin and leading white space when justification is left")
            obj.addProperty("App::PropertyBool", "KeepLeftMargin", "Draft", _tip).KeepLeftMargin = False

        if "ScaleToSize" not in properties:
            _tip = QT_TRANSLATE_NOOP("App::Property", "Scale to ensure cap height is equal to size")
            obj.addProperty("App::PropertyBool", "ScaleToSize", "Draft", _tip).ScaleToSize = True

        if "Tracking" not in properties:
            _tip = QT_TRANSLATE_NOOP("App::Property", "Inter-character spacing")
            obj.addProperty("App::PropertyDistance", "Tracking", "Draft", _tip)

        if "ObliqueAngle" not in properties:
            _tip = QT_TRANSLATE_NOOP("App::Property", "Oblique (slant) angle")
            obj.addProperty("App::PropertyAngle", "ObliqueAngle", "Draft", _tip)

        if "MakeFace" not in properties:
            _tip = QT_TRANSLATE_NOOP("App::Property", "Fill letters with faces")
            obj.addProperty("App::PropertyBool", "MakeFace", "Draft", _tip).MakeFace = True

        if "Fuse" not in properties:
            _tip = QT_TRANSLATE_NOOP("App::Property", "Fuse faces if faces overlap, usually not required (can be very slow)")
            obj.addProperty("App::PropertyBool", "Fuse", "Draft", _tip).Fuse = False

    def onDocumentRestored(self, obj):
        super().onDocumentRestored(obj)
        if not self.check_portable_folder(obj, True):
            return
        if hasattr(obj, "ObliqueAngle"): # several more properties were added
            return
        self.update_properties_1v0(obj)

    def update_properties_1v0(self, obj):
        """Update view properties."""
        old_tracking = obj.Tracking # no need for obj.getTypeIdOfProperty("Tracking")
        obj.removeProperty("Tracking")
        self.set_properties(obj)
        obj.KeepLeftMargin = True
        obj.ScaleToSize = False
        obj.Tracking = old_tracking
        _wrn("v1.0, " + obj.Label + ", "
             + translate("draft", "added 'Fuse', 'Justification', 'JustificationReference', 'KeepLeftMargin', 'ObliqueAngle' and 'ScaleToSize'  properties"))
        _wrn("v1.0, " + obj.Label + ", "
             + translate("draft", "changed 'Tracking' property type"))

    def execute(self, obj):
        if self.props_changed_placement_only():
            obj.positionBySupport()
            self.props_changed_clear()
            return

        if obj.String and obj.FontFile:
            if obj.Placement:
                plm = obj.Placement
            if not self.check_portable_folder(obj, False):
                return
            fill = obj.MakeFace
            if fill is True:
                # Test a simple letter to know if we have a sticky font or not.
                # If the font is sticky change fill to `False`.
                # The 0.03 total area minimum is based on tests with:
                # 1CamBam_Stick_0.ttf and 1CamBam_Stick_0C.ttf.
                # See the make_faces function for more information.
                char = Part.makeWireString("L", obj.FontFile, 1, 0)[0]
                shapes = self.make_faces(char)  # char is list of wires
                if not shapes:
                    fill = False
                else:
                    fill = sum([shape.Area for shape in shapes]) > 0.03\
                            and math.isclose(Part.Compound(char).BoundBox.DiagonalLength,
                                             Part.Compound(shapes).BoundBox.DiagonalLength,
                                             rel_tol=1e-7)

            chars = Part.makeWireString(obj.String, obj.FontFile, obj.Size, obj.Tracking)
            shapes = []

            for char in chars:
                if fill is False:
                    shapes.extend(char)
                elif char:
                    shapes.extend(self.make_faces(char))
            if shapes:
                if fill and obj.Fuse:
                    ss_shape = shapes[0].fuse(shapes[1:])
                    ss_shape = faces.concatenate(ss_shape)
                else:
                    ss_shape = Part.Compound(shapes)
                cap_char = Part.makeWireString("M", obj.FontFile, obj.Size, obj.Tracking)[0]
                cap_height = Part.Compound(cap_char).BoundBox.YMax
                if obj.ScaleToSize:
                    ss_shape.scale(obj.Size / cap_height)
                    cap_height = obj.Size
                if obj.ObliqueAngle:
                    if -80 <= obj.ObliqueAngle <= 80:
                        mtx = App.Matrix()
                        mtx.A12 = math.tan(math.radians(obj.ObliqueAngle))
                        ss_shape = ss_shape.transformGeometry(mtx)
                    else:
                        wrn = translate("draft", "ShapeString: oblique angle must be in the -80 to +80 degree range") + "\n"
                        App.Console.PrintWarning(wrn)
                just_vec = self.justification_vector(ss_shape,
                                                     cap_height,
                                                     obj.Justification,
                                                     obj.JustificationReference,
                                                     obj.KeepLeftMargin)
                shapes = ss_shape.SubShapes
                for shape in shapes:
                    shape.translate(just_vec)
                obj.Shape = Part.Compound(shapes)
            else:
                App.Console.PrintWarning(translate("draft", "ShapeString: string has no wires") + "\n")

            if plm:
                obj.Placement = plm

        obj.positionBySupport()
        self.props_changed_clear()

    def check_portable_folder(self, obj, on_restore):
        # We have been passed the correct location from the task panel
        if not on_restore and os.path.isfile(obj.FontFile):
            return True

        # We may have been passed an incorrect location from the task panel
        if not os.path.isfile(obj.FontFile) and not on_restore:
            App.Console.PrintWarning(
                translate(
                    "draft",
                    "ShapeString: font file does not exist, "
                    "use the ... button to select a font file",
                )
                + "\n"
            )
            return False

        # So the only things left are opening existing files
        unique_identifier = "%d"
        actual_param = get_param("FontFile")[2 : len(get_param("FontFile"))]
        number_of_chars_param = len(actual_param)
        if re.search(unique_identifier, get_param("FontFile"), re.IGNORECASE):
            if on_restore:
                App.Console.PrintLog(
                    translate(
                        "draft",
                        "ShapeString: changing font location to local "
                        "App.getUserAppDataDir() - "
                        + str(App.getUserAppDataDir())
                        + "\n",
                    )
                )
            specialF = str(App.getUserAppDataDir())
            if platform.system() == "Windows":
                # We now have to reverse the os.sep to check if file has come from a Windows box
                path = os.path.normpath(specialF)
                specialF = ""
                for each_str in path.split(os.sep):
                    specialF = specialF + each_str + "/"
        number_of_chars_base_dir = len(
            specialF
            + get_param("FontFile")[len(unique_identifier) : len(get_param("FontFile"))]
        )
        number_of_chars_font = len(obj.FontFile)
        existingFileInfo = (
            specialF
            + get_param("FontFile")[len(unique_identifier) : len(get_param("FontFile"))]
        )
        systemFileInfo = obj.FontFile[
            0 : len(App.getUserAppDataDir())
            + len(get_param("FontFile"))
            - len(unique_identifier)
        ]
        if existingFileInfo != systemFileInfo:
            # We have to iterate through the FontFile until we get the number_of_chars_param characters of Fonts/truetype
            path = os.path.normpath(obj.FontFile)
            existingFileInfo = ""
            for each_str in path.split(os.sep):
                existingFileInfo = existingFileInfo + each_str + "/"
            existingFileInfo = existingFileInfo[0 : len(existingFileInfo) - 1]
            number_of_chars_user_appdata_dir = len(App.getUserAppDataDir())
            for each_char in range(0, len(existingFileInfo)):
                if (
                    existingFileInfo[each_char : each_char + number_of_chars_param]
                    == actual_param
                ):
                    obj.FontFile = (
                        specialF
                        + actual_param
                        + obj.FontFile[
                            each_char + len(actual_param) : len(existingFileInfo)
                        ]
                    )
                    break

        if not os.path.isfile(obj.FontFile):
            App.Console.PrintWarning(
                translate(
                    "draft",
                    "ShapeString: opening existing shapestring, font file does not exist, "
                    "use the ... button to select a font file",
                )
                + "\n"
            )
            path = os.path.normpath(obj.FontFile)
            testList = []
            for each_str in path.split(os.sep):
                testList.append(each_str)
            if os.path.isdir(specialF + actual_param + "/" + testList[-2]):
                for file in os.listdir(specialF + actual_param + "/" + testList[-2]):
                    if fnmatch.fnmatch(
                        file, testList[-1][0:6] + "*" + obj.FontFile[-4:]
                    ):
                        App.Console.PrintWarning(
                            translate(
                                "draft",
                                "ShapeString: other simlar named font files found in the folder",
                            )
                            + "\n"
                        )
                        break
            else:
                App.Console.PrintWarning(
                    translate(
                        "draft",
                        "ShapeString: please browse for an appropriate font file",
                    )
                    + "\n"
                )
            return False
        return True

        return True
    def onChanged(self, obj, prop):
        self.props_changed_store(prop)

    def justification_vector(self, ss_shape, cap_height, just, just_ref, keep_left_margin): # ss_shape is a compound
        box = ss_shape.optimalBoundingBox()
        if keep_left_margin is True and "Left" in just:
            vec = App.Vector(0, 0, 0)
        else:
            vec = App.Vector(-box.XMin, 0, 0) # remove left margin caused by kerning and white space characters
        width  = box.XLength
        if "Shape" in just_ref:
            vec = vec + App.Vector(0, -box.YMin, 0)
            height = box.YLength
        else:
            height = cap_height
        if "Top" in just:
            vec = vec + App.Vector(0, -height, 0)
        elif "Middle" in just:
            vec = vec + App.Vector(0, -height/2, 0)
        if "Right" in just:
            vec = vec + App.Vector(-width, 0, 0)
        elif "Center" in just:
            vec = vec + App.Vector(-width/2, 0, 0)
        return vec

    def make_faces(self, wireChar):
        wrn = translate("draft", "ShapeString: face creation failed for one character") + "\n"

        wirelist = []
        for w in wireChar:
            compEdges = Part.Compound(w.Edges)
            compEdges = compEdges.connectEdgesToWires()
            if compEdges.Wires[0].isClosed():
                wirelist.append(compEdges.Wires[0])

        if not wirelist:
            App.Console.PrintWarning(wrn)
            return []

        # Some test fonts:
        # https://raw.githubusercontent.com/FreeCAD/FPA/main/images/freecad_logo_official.svg
        #     https://evolventa.github.io/
        #     not a problem font, but it is used by FreeCAD
        # https://forum.freecad.org/viewtopic.php?t=57774
        #     https://www.dafont.com/mutlu-ornamental.font
        # https://forum.freecad.org/viewtopic.php?t=65110&p=559810#p559886
        #     http://www.atelier-des-fougeres.fr/Cambam/Aide/Plugins/stickfonts.html

        # 1CamBam_Stick_0.ttf is actually not a stick font.

        # FaceMakerBullseye:
        #     1CamBam_Stick_0.ttf face validation problem with A, E, F, H, K, R, Y and y.
        # FaceMakerCheese:
        #     1CamBam_Stick_0.ttf face creation problem with: A, E, F, H, Q, R, e and y.
        #     All fonts: face creation problem in case of double-nested wires f.e. with: ©.
        # FaceMakerSimple:
        #     All fonts: overlapping faces in case of nested wires f.e. with: O.
        try:
            # print("try Bullseye")
            faces = Part.makeFace(wirelist, "Part::FaceMakerBullseye").Faces
            for face in faces:
                face.validate()
        except Part.OCCError:
            try:
                # print("try Cheese")
                faces = Part.makeFace(wirelist, "Part::FaceMakerCheese").Faces
                for face in faces:
                    face.validate()
            except Part.OCCError:
                try:
                    # print("try Simple")
                    faces = Part.makeFace(wirelist, "Part::FaceMakerSimple").Faces
                    for face in faces:
                        face.validate()
                except Part.OCCError:
                    App.Console.PrintWarning(wrn)
                    return []

        for face in faces:
            try:
                # some fonts fail here
                if face.normalAt(0, 0).z < 0: # Does not seem to occur for FaceMakerBullseye.
                    face.reverse()
            except Exception:
                pass

        return faces


# Alias for compatibility with v0.18 and earlier
_ShapeString = ShapeString

## @}
